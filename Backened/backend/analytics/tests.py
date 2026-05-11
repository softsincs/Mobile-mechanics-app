from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from bookings.models import Booking, BookingStatus
from ratings.models import BookingReview
from services.models import Service, ServiceCategory
from users.models import User

from .models import DashboardMetrics
from .services import AnalyticsService


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        phone_number='+923004444444',
        email='admin@example.com',
        password='password123',
        first_name='Admin',
        last_name='User',
        is_staff=True,
    )


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    token = Token.objects.create(user=admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        phone_number='+923005555555',
        email='customer-analytics@example.com',
        password='password123',
        first_name='Ayesha',
        last_name='Khan',
    )


@pytest.fixture
def mechanic_user(db):
    mechanic = User.objects.create_user(
        phone_number='+923006666666',
        email='mechanic-analytics@example.com',
        password='password123',
        first_name='Omar',
        last_name='Ali',
    )
    profile = mechanic.mechanic_profile if hasattr(mechanic, 'mechanic_profile') else None
    if profile is None:
        from mechanics.models import MechanicProfile
        MechanicProfile.objects.create(user=mechanic, current_active_jobs=1, current_rating=4.8, acceptance_rate=96)
    return mechanic


@pytest.fixture
def service(db):
    category = ServiceCategory.objects.create(name='Electrical', description='Electrical services')
    return Service.objects.create(
        category=category,
        name='Battery Replacement',
        estimated_duration=30,
        base_price='4500.00',
    )


@pytest.fixture
def completed_booking(customer_user, mechanic_user, service):
    return Booking.objects.create(
        customer=customer_user,
        service=service,
        mechanic=mechanic_user,
        status=BookingStatus.COMPLETED,
        service_location='456 Market Road',
        city='Lahore',
        latitude=31.5204,
        longitude=74.3587,
        scheduled_date='2026-05-01',
        scheduled_time='09:00:00',
        estimated_duration=30,
        base_price='4500.00',
        total_amount='5175.00',
        completed_at='2026-05-01T09:30:00Z',
        payment_method='CASH',
    )


@pytest.fixture
def cancelled_booking(customer_user, mechanic_user, service):
    return Booking.objects.create(
        customer=customer_user,
        service=service,
        mechanic=mechanic_user,
        status=BookingStatus.CANCELLED,
        service_location='789 Canal Road',
        city='Lahore',
        latitude=31.5000,
        longitude=74.3000,
        scheduled_date='2026-05-02',
        scheduled_time='11:00:00',
        estimated_duration=30,
        base_price='4500.00',
        total_amount='0.00',
        cancellation_reason='CUSTOMER_CHANGED_MIND',
        payment_method='CASH',
    )


@pytest.mark.django_db
def test_dashboard_metrics_service_layer(completed_booking, cancelled_booking):
    metrics = AnalyticsService.get_dashboard_snapshot()
    assert metrics['bookings']['total'] >= 2
    assert Decimal(metrics['revenue']['total']) >= Decimal('4500.00')


@pytest.mark.django_db
def test_dashboard_endpoint_requires_admin(customer_user):
    client = APIClient()
    token = Token.objects.create(user=customer_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    response = client.get(reverse('analytics-dashboard'))
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_dashboard_endpoint(admin_client, completed_booking, cancelled_booking):
    response = admin_client.get(reverse('analytics-dashboard'))
    assert response.status_code == 200
    assert response.data['bookings']['total'] >= 2


@pytest.mark.django_db
def test_booking_analytics_by_service(admin_client, completed_booking, cancelled_booking):
    response = admin_client.get(reverse('analytics-bookings'), {'group_by': 'service'})
    assert response.status_code == 200
    assert response.data['group_by'] == 'service'
    assert len(response.data['results']) >= 1


@pytest.mark.django_db
def test_revenue_analytics(admin_client, completed_booking, cancelled_booking):
    response = admin_client.get(reverse('analytics-revenue'), {'period': 'monthly'})
    assert response.status_code == 200
    assert 'current' in response.data
    assert response.data['current']['booking_count'] >= 2


@pytest.mark.django_db
def test_mechanic_analytics(admin_client, completed_booking, cancelled_booking):
    response = admin_client.get(reverse('analytics-mechanics'), {'sort_by': 'rating'})
    assert response.status_code == 200
    assert isinstance(response.data['results'], list)


@pytest.mark.django_db
def test_customer_analytics(admin_client, completed_booking, cancelled_booking):
    response = admin_client.get(reverse('analytics-customers'), {'metric': 'clv'})
    assert response.status_code == 200
    assert isinstance(response.data['results'], list)


@pytest.mark.django_db
def test_refresh_daily_metrics_persists_row(completed_booking, cancelled_booking):
    metric = AnalyticsService.refresh_daily_metrics()
    assert metric.date is not None
    assert DashboardMetrics.objects.filter(date=metric.date).exists()
