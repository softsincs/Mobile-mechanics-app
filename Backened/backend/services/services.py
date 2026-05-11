"""Business logic and helpers for the services app."""

from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone

from .models import Service, ServicePrice, ServicePromotion


TAX_RATE = Decimal(getattr(settings, 'SERVICES_TAX_RATE', '0.15'))


def get_active_services(city=None):
    queryset = Service.objects.filter(is_active=True).order_by('-created_at')
    if city:
        queryset = queryset.filter(availability_slots__city__iexact=city, availability_slots__is_available=True).distinct()
    return queryset


def get_applicable_price_profile(service, city, booking_datetime=None):
    booking_datetime = booking_datetime or timezone.now()
    profiles = ServicePrice.objects.filter(service=service, city__iexact=city)
    if not profiles.exists():
        return None

    current_profile = None
    for profile in profiles.order_by('-valid_from'):
        if profile.valid_from <= booking_datetime and (profile.valid_to is None or booking_datetime <= profile.valid_to):
            current_profile = profile
            break

    return current_profile or profiles.order_by('-valid_from').first()


def get_time_multiplier(price_profile, booking_datetime):
    booking_datetime = booking_datetime or timezone.now()
    hour = booking_datetime.hour
    is_weekend = booking_datetime.weekday() >= 5

    if price_profile is None:
        return Decimal('1.0')

    if is_weekend:
        return Decimal(str(price_profile.weekend_multiplier))

    if 6 <= hour < 9 or 17 <= hour < 20:
        return Decimal(str(price_profile.peak_multiplier))

    return Decimal(str(price_profile.off_peak_multiplier))


def get_mechanic_multiplier(mechanic, service):
    if not mechanic:
        return Decimal('1.0')

    specialty = getattr(mechanic, 'service_specialties', None)
    if specialty is None:
        return Decimal('1.0')

    record = specialty.filter(service=service, is_active=True).first()
    if not record:
        return Decimal('1.0')

    if record.proficiency_level == 'EXPERT':
        return Decimal('1.15')
    if record.proficiency_level == 'INTERMEDIATE':
        return Decimal('1.08')
    return Decimal('1.02')


def get_demand_multiplier(city, service):
    value = cache.get(f'demand:{city}:{service.id}')
    if value is None:
        return Decimal('1.0')
    return Decimal(str(value))


def get_promotion(service, city, promo_code, booking_datetime=None):
    if not promo_code:
        return None

    booking_datetime = booking_datetime or timezone.now()
    queryset = ServicePromotion.objects.filter(code__iexact=promo_code, is_active=True)
    if service:
        queryset = queryset.filter(models.Q(service=service) | models.Q(service__isnull=True))
    if city:
        queryset = queryset.filter(models.Q(city__iexact=city) | models.Q(city__isnull=True))

    for promo in queryset.order_by('-created_at'):
        if promo.valid_from <= booking_datetime and (promo.valid_to is None or booking_datetime <= promo.valid_to):
            return promo

    return None


def calculate_service_price(service, city, booking_datetime=None, mechanic=None, promo_code=None):
    booking_datetime = booking_datetime or timezone.now()
    base_price = Decimal(str(service.base_price))

    price_profile = get_applicable_price_profile(service, city, booking_datetime)
    time_multiplier = get_time_multiplier(price_profile, booking_datetime)
    demand_multiplier = get_demand_multiplier(city, service)
    mechanic_multiplier = get_mechanic_multiplier(mechanic, service)

    subtotal = base_price * time_multiplier * demand_multiplier * mechanic_multiplier

    promotion = get_promotion(service, city, promo_code, booking_datetime)
    discount_amount = Decimal('0')
    if promotion and subtotal >= promotion.min_booking_amount:
        discount_amount = promotion.calculate_discount(subtotal)

    taxable_amount = subtotal - discount_amount
    tax_amount = taxable_amount * TAX_RATE
    total_amount = taxable_amount + tax_amount

    return {
        'service_id': str(service.id),
        'city': city,
        'booking_datetime': booking_datetime.isoformat(),
        'base_price': base_price,
        'time_multiplier': time_multiplier,
        'demand_multiplier': demand_multiplier,
        'mechanic_multiplier': mechanic_multiplier,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'tax_rate': TAX_RATE,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'promotion_code': promotion.code if promotion else None,
        'pricing_profile': {
            'id': price_profile.id if price_profile else None,
            'peak_multiplier': getattr(price_profile, 'peak_multiplier', None),
            'off_peak_multiplier': getattr(price_profile, 'off_peak_multiplier', None),
            'weekend_multiplier': getattr(price_profile, 'weekend_multiplier', None),
        },
    }
