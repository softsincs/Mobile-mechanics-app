"""Pytest coverage for ratings app."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from bookings.models import Booking, BookingStatus
from services.models import Service, ServiceCategory
from .models import BookingReview

User = get_user_model()


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(phone_number='+923001111111', email='customer@test.com', password='SecurePass123!')


@pytest.fixture
def mechanic_user(db):
    return User.objects.create_user(phone_number='+923002222222', email='mechanic@test.com', password='SecurePass123!')


@pytest.fixture
def other_customer(db):
    return User.objects.create_user(phone_number='+923003333333', email='other@test.com', password='SecurePass123!')


@pytest.fixture
def customer_auth_client(customer_user):
    client = APIClient()
    token = Token.objects.create(user=customer_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def mechanic_auth_client(mechanic_user):
    client = APIClient()
    token = Token.objects.create(user=mechanic_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def service_category(db):
    return ServiceCategory.objects.create(name='Maintenance', description='Maintenance services', is_active=True)


@pytest.fixture
def service_item(service_category):
    return Service.objects.create(
        category=service_category,
        name='Oil Change',
        description='Change engine oil',
        estimated_duration=30,
        base_price=Decimal('1200.00'),
        min_price=Decimal('1000.00'),
        max_price=Decimal('1500.00'),
        is_active=True,
    )


@pytest.fixture
def completed_booking(customer_user, mechanic_user, service_item):
    scheduled_datetime = timezone.now() + timedelta(days=2)
    return Booking.objects.create(
        customer=customer_user,
        mechanic=mechanic_user,
        service=service_item,
        service_location='123 Main St, Lahore',
        city='Lahore',
        latitude=31.5204,
        longitude=74.3587,
        scheduled_date=scheduled_datetime.date(),
        scheduled_time=scheduled_datetime.time(),
        estimated_duration=30,
        base_price=Decimal('1200.00'),
        tax_amount=Decimal('120.00'),
        total_amount=Decimal('1320.00'),
        payment_method='CASH',
        status=BookingStatus.COMPLETED,
    )


@pytest.fixture
def other_completed_booking(other_customer, mechanic_user, service_item):
    scheduled_datetime = timezone.now() + timedelta(days=2)
    return Booking.objects.create(
        customer=other_customer,
        mechanic=mechanic_user,
        service=service_item,
        service_location='456 Side St, Lahore',
        city='Lahore',
        latitude=31.6204,
        longitude=74.4587,
        scheduled_date=scheduled_datetime.date(),
        scheduled_time=scheduled_datetime.time(),
        estimated_duration=30,
        base_price=Decimal('1200.00'),
        tax_amount=Decimal('120.00'),
        total_amount=Decimal('1320.00'),
        payment_method='CASH',
        status=BookingStatus.COMPLETED,
    )


def results(data):
    return data['results'] if isinstance(data, dict) and 'results' in data else data


@pytest.mark.django_db
class TestBookingReviewModels:
    def test_review_creation(self, completed_booking, customer_user, mechanic_user):
        review = BookingReview.objects.create(
            booking=completed_booking,
            customer=customer_user,
            mechanic=mechanic_user,
            service_rating=5,
            mechanic_rating=4,
            comment='Good service',
        )
        assert review.is_verified is True
        assert review.overall_rating == 4.5


@pytest.mark.django_db
class TestBookingReviewAPI:
    def test_customer_can_create_review(self, customer_auth_client, completed_booking):
        response = customer_auth_client.post(
            reverse('booking-review-list'),
            {
                'booking_id': str(completed_booking.id),
                'service_rating': 5,
                'mechanic_rating': 4,
                'comment': 'Good service',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['service_rating'] == 5
        completed_booking.refresh_from_db()
        assert completed_booking.status == BookingStatus.RATED

    def test_cannot_review_incomplete_booking(self, customer_auth_client, service_item, customer_user, mechanic_user):
        scheduled_datetime = timezone.now() + timedelta(days=2)
        booking = Booking.objects.create(
            customer=customer_user,
            mechanic=mechanic_user,
            service=service_item,
            service_location='123 Main St',
            city='Lahore',
            latitude=31.5204,
            longitude=74.3587,
            scheduled_date=scheduled_datetime.date(),
            scheduled_time=scheduled_datetime.time(),
            estimated_duration=30,
            base_price=Decimal('1200.00'),
            tax_amount=Decimal('120.00'),
            total_amount=Decimal('1320.00'),
            payment_method='CASH',
            status=BookingStatus.IN_PROGRESS,
        )
        response = customer_auth_client.post(
            reverse('booking-review-list'),
            {
                'booking_id': str(booking.id),
                'service_rating': 5,
                'mechanic_rating': 4,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_customer_sees_only_own_reviews(self, customer_auth_client, completed_booking, other_completed_booking, customer_user, other_customer, mechanic_user):
        BookingReview.objects.create(
            booking=completed_booking,
            customer=customer_user,
            mechanic=mechanic_user,
            service_rating=5,
            mechanic_rating=5,
        )
        BookingReview.objects.create(
            booking=other_completed_booking,
            customer=other_customer,
            mechanic=mechanic_user,
            service_rating=4,
            mechanic_rating=4,
        )
        response = customer_auth_client.get(reverse('booking-review-list'))
        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert len(data) == 1

    def test_mechanic_can_view_received_reviews(self, mechanic_auth_client, completed_booking, customer_user, mechanic_user):
        BookingReview.objects.create(
            booking=completed_booking,
            customer=customer_user,
            mechanic=mechanic_user,
            service_rating=5,
            mechanic_rating=4,
        )
        response = mechanic_auth_client.get(reverse('booking-review-list'))
        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert len(data) == 1
