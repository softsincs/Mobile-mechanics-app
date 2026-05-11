"""Aggregation helpers for admin analytics endpoints."""
from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from bookings.models import Booking, BookingStatus
from ratings.models import BookingReview
from users.models import User

from .models import DashboardMetrics


def _parse_datetime(value):
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


class AnalyticsService:
    """Compute live analytics from bookings, reviews, and users."""

    @staticmethod
    def get_range(start_date=None, end_date=None, period='monthly'):
        end = _parse_datetime(end_date) or timezone.now()
        if start_date:
            start = _parse_datetime(start_date)
        elif period == 'daily':
            start = end - timedelta(days=1)
        elif period == 'weekly':
            start = end - timedelta(days=7)
        elif period == 'yearly':
            start = end - timedelta(days=365)
        else:
            start = end - timedelta(days=30)
        return start, end

    @staticmethod
    def get_dashboard_snapshot():
        start, end = AnalyticsService.get_range(period='monthly')
        bookings = Booking.objects.filter(created_at__gte=start, created_at__lte=end)
        reviews = BookingReview.objects.filter(reviewed_at__gte=start, reviewed_at__lte=end)

        total_revenue = bookings.aggregate(total=Sum('total_amount')).get('total') or Decimal('0')
        completed = bookings.filter(status=BookingStatus.COMPLETED).count()
        cancelled = bookings.filter(status=BookingStatus.CANCELLED).count()
        average_rating = reviews.aggregate(avg=Avg('service_rating')).get('avg') or 0

        return {
            'period': {'start': start.isoformat(), 'end': end.isoformat()},
            'bookings': {
                'total': bookings.count(),
                'completed': completed,
                'cancelled': cancelled,
            },
            'revenue': {
                'total': total_revenue,
                'average_booking_value': (total_revenue / bookings.count()) if bookings.count() else Decimal('0'),
            },
            'users': {
                'total_customers': User.objects.filter(is_staff=False).count(),
                'total_mechanics': User.objects.filter(mechanic_profile__isnull=False).count(),
            },
            'ratings': {
                'average_service_rating': round(float(average_rating), 2) if average_rating else 0,
            },
        }

    @staticmethod
    def get_booking_analytics(start_date=None, end_date=None, group_by='service'):
        start, end = AnalyticsService.get_range(start_date=start_date, end_date=end_date)
        queryset = Booking.objects.filter(created_at__gte=start, created_at__lte=end)

        if group_by == 'mechanic':
            grouped = queryset.values('mechanic__id', 'mechanic__phone_number').annotate(
                total_bookings=Count('id'),
                completed_bookings=Count('id', filter=Q(status=BookingStatus.COMPLETED)),
                cancelled_bookings=Count('id', filter=Q(status=BookingStatus.CANCELLED)),
                total_revenue=Sum('total_amount'),
            ).order_by('-total_bookings')
        elif group_by == 'city':
            grouped = queryset.values('city').annotate(
                total_bookings=Count('id'),
                completed_bookings=Count('id', filter=Q(status=BookingStatus.COMPLETED)),
                cancelled_bookings=Count('id', filter=Q(status=BookingStatus.CANCELLED)),
                total_revenue=Sum('total_amount'),
            ).order_by('-total_bookings')
        elif group_by == 'day':
            grouped = queryset.annotate(day=TruncDate('created_at')).values('day').annotate(
                total_bookings=Count('id'),
                total_revenue=Sum('total_amount'),
            ).order_by('day')
        else:
            grouped = queryset.values('service__id', 'service__name').annotate(
                total_bookings=Count('id'),
                completed_bookings=Count('id', filter=Q(status=BookingStatus.COMPLETED)),
                cancelled_bookings=Count('id', filter=Q(status=BookingStatus.CANCELLED)),
                total_revenue=Sum('total_amount'),
            ).order_by('-total_bookings')

        return {
            'period': {'start': start.isoformat(), 'end': end.isoformat()},
            'group_by': group_by,
            'results': list(grouped),
        }

    @staticmethod
    def get_revenue_analytics(period='monthly'):
        start, end = AnalyticsService.get_range(period=period)
        previous_start = start - (end - start)
        bookings = Booking.objects.filter(created_at__gte=start, created_at__lte=end)
        previous_bookings = Booking.objects.filter(created_at__gte=previous_start, created_at__lt=start)

        total_revenue = bookings.aggregate(total=Sum('total_amount')).get('total') or Decimal('0')
        previous_total = previous_bookings.aggregate(total=Sum('total_amount')).get('total') or Decimal('0')
        growth = Decimal('0')
        if previous_total:
            growth = ((total_revenue - previous_total) / previous_total) * Decimal('100')

        by_status = bookings.values('status').annotate(total=Count('id'), revenue=Sum('total_amount')).order_by('-total')

        return {
            'period': period,
            'range': {'start': start.isoformat(), 'end': end.isoformat()},
            'current': {'total_revenue': total_revenue, 'booking_count': bookings.count()},
            'previous': {'total_revenue': previous_total, 'booking_count': previous_bookings.count()},
            'growth_percent': round(float(growth), 2) if growth else 0,
            'by_status': list(by_status),
        }

    @staticmethod
    def get_mechanic_analytics(sort_by='performance'):
        queryset = User.objects.filter(mechanic_profile__isnull=False).select_related('mechanic_profile')
        data = []
        for user in queryset:
            bookings = Booking.objects.filter(mechanic=user)
            reviews = BookingReview.objects.filter(mechanic=user)
            profile = user.mechanic_profile
            data.append({
                'mechanic_id': str(user.id),
                'phone_number': user.phone_number,
                'name': user.get_full_name() or user.phone_number,
                'total_bookings': bookings.count(),
                'completed_bookings': bookings.filter(status=BookingStatus.COMPLETED).count(),
                'acceptance_rate': float(profile.acceptance_rate),
                'cancellation_rate': float(profile.cancellation_rate),
                'average_rating': round(float(reviews.aggregate(avg=Avg('service_rating')).get('avg') or 0), 2),
                'current_active_jobs': profile.current_active_jobs,
            })

        if sort_by == 'rating':
            data.sort(key=lambda item: item['average_rating'], reverse=True)
        elif sort_by == 'jobs':
            data.sort(key=lambda item: item['total_bookings'], reverse=True)
        else:
            data.sort(key=lambda item: (item['acceptance_rate'], item['average_rating']), reverse=True)

        return {'sort_by': sort_by, 'results': data}

    @staticmethod
    def get_customer_analytics(metric='clv'):
        queryset = User.objects.filter(is_staff=False).exclude(mechanic_profile__isnull=False)
        data = []
        for user in queryset:
            bookings = Booking.objects.filter(customer=user)
            completed = bookings.filter(status=BookingStatus.COMPLETED)
            total_spend = completed.aggregate(total=Sum('total_amount')).get('total') or Decimal('0')
            reviews = BookingReview.objects.filter(customer=user)
            data.append({
                'customer_id': str(user.id),
                'phone_number': user.phone_number,
                'name': user.get_full_name() or user.phone_number,
                'bookings': bookings.count(),
                'completed_bookings': completed.count(),
                'total_spend': total_spend,
                'average_rating_given': round(float(reviews.aggregate(avg=Avg('service_rating')).get('avg') or 0), 2),
            })

        if metric == 'bookings':
            data.sort(key=lambda item: item['bookings'], reverse=True)
        else:
            data.sort(key=lambda item: item['total_spend'], reverse=True)

        return {'metric': metric, 'results': data}

    @staticmethod
    def refresh_daily_metrics(day=None):
        day = day or timezone.localdate()
        start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
        end = start + timedelta(days=1)
        bookings = Booking.objects.filter(created_at__gte=start, created_at__lt=end)
        reviews = BookingReview.objects.filter(reviewed_at__gte=start, reviewed_at__lt=end)
        total_revenue = bookings.aggregate(total=Sum('total_amount')).get('total') or Decimal('0')
        average_rating = reviews.aggregate(avg=Avg('service_rating')).get('avg') or 0

        metrics, _ = DashboardMetrics.objects.update_or_create(
            date=day,
            defaults={
                'total_bookings': bookings.count(),
                'completed_bookings': bookings.filter(status=BookingStatus.COMPLETED).count(),
                'cancelled_bookings': bookings.filter(status=BookingStatus.CANCELLED).count(),
                'total_revenue': total_revenue,
                'platform_commission': total_revenue * Decimal('0.10'),
                'mechanic_payouts': total_revenue * Decimal('0.75'),
                'new_customers': User.objects.filter(created_at__gte=start, created_at__lt=end, is_staff=False).count(),
                'new_mechanics': User.objects.filter(created_at__gte=start, created_at__lt=end, mechanic_profile__isnull=False).count(),
                'active_customers': User.objects.filter(is_staff=False, bookings_as_customer__created_at__gte=start, bookings_as_customer__created_at__lt=end).distinct().count(),
                'active_mechanics': User.objects.filter(mechanic_profile__isnull=False, bookings_as_mechanic__created_at__gte=start, bookings_as_mechanic__created_at__lt=end).distinct().count(),
                'average_rating': round(float(average_rating), 2) if average_rating else 0,
                'customer_satisfaction_score': round(float(average_rating * 20), 2) if average_rating else 0,
            },
        )
        return metrics
