"""Staff analytics endpoints."""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import AnalyticsService


class StaffAnalyticsPermission(permissions.IsAdminUser):
    pass


class AnalyticsDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        return Response(AnalyticsService.get_dashboard_snapshot())


class BookingAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        group_by = request.query_params.get('group_by', 'service')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        return Response(AnalyticsService.get_booking_analytics(start_date=start_date, end_date=end_date, group_by=group_by))


class RevenueAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'monthly')
        return Response(AnalyticsService.get_revenue_analytics(period=period))


class MechanicAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        sort_by = request.query_params.get('sort_by', 'performance')
        return Response(AnalyticsService.get_mechanic_analytics(sort_by=sort_by))


class CustomerAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        metric = request.query_params.get('metric', 'clv')
        return Response(AnalyticsService.get_customer_analytics(metric=metric))
