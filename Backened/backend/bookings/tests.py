"""Pytest coverage for the bookings app."""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from services.models import Service, ServiceCategory, ServicePrice
from .models import Booking, BookingStatus, BookingAddOn, BookingStatusHistory

User = get_user_model()


@pytest.fixture
def customer_user(db):
	"""Create a customer user."""
	return User.objects.create_user(
		phone_number='+923001111111',
		email='customer@example.com',
		password='SecurePass123!',
	)


@pytest.fixture
def mechanic_user(db):
	"""Create a mechanic user."""
	return User.objects.create_user(
		phone_number='+923002222222',
		email='mechanic@example.com',
		password='SecurePass123!',
	)


@pytest.fixture
def customer_auth_client(customer_user):
	"""Authenticated API client for customer."""
	client = APIClient()
	token = Token.objects.create(user=customer_user)
	client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
	return client


@pytest.fixture
def mechanic_auth_client(mechanic_user):
	"""Authenticated API client for mechanic."""
	client = APIClient()
	token = Token.objects.create(user=mechanic_user)
	client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
	return client


@pytest.fixture
def service_category(db):
	"""Create a service category."""
	return ServiceCategory.objects.create(
		name='Maintenance',
		description='Maintenance services',
		is_active=True,
	)


@pytest.fixture
def service_item(service_category):
	"""Create a service."""
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
def service_price(service_item):
	"""Create service price."""
	return ServicePrice.objects.create(
		service=service_item,
		city='Lahore',
		peak_multiplier=Decimal('1.50'),
		off_peak_multiplier=Decimal('1.00'),
		weekend_multiplier=Decimal('1.25'),
		valid_from=timezone.now() - timedelta(days=1),
	)


@pytest.fixture
def add_on(db):
	"""Create a booking add-on."""
	return BookingAddOn.objects.create(
		name='Inspection',
		description='Full inspection',
		price=Decimal('500.00'),
		is_active=True,
	)


@pytest.fixture
def booking(customer_user, service_item):
	"""Create a booking."""
	scheduled_datetime = timezone.now() + timedelta(days=2)
	return Booking.objects.create(
		customer=customer_user,
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
		status=BookingStatus.PENDING_CONFIRMATION,
	)


def results(data):
	"""Extract results from paginated response."""
	return data['results'] if isinstance(data, dict) and 'results' in data else data


@pytest.mark.django_db
class TestBookingModels:
	"""Test booking model functionality."""
    
	def test_booking_str(self, booking):
		assert 'Oil Change' in str(booking)
		assert 'PENDING_CONFIRMATION' in str(booking)
    
	def test_booking_is_cancellable(self, booking):
		assert booking.is_cancellable is True
		booking.status = BookingStatus.COMPLETED
		assert booking.is_cancellable is False
    
	def test_booking_can_be_confirmed(self, booking):
		assert booking.can_be_confirmed is True
		booking.status = BookingStatus.CONFIRMED
		assert booking.can_be_confirmed is False
    
	def test_booking_calculate_total_amount(self, booking):
		booking.surge_multiplier = Decimal('1.5')
		booking.discount_amount = Decimal('100')
		expected = (Decimal('1200.00') * Decimal('1.5')) - Decimal('100') + Decimal('120.00')
		assert booking.calculate_total_amount() == expected


@pytest.mark.django_db
class TestBookingPermissions:
	"""Test booking access permissions."""
    
	def test_unauthenticated_booking_list_is_denied(self):
		client = APIClient()
		response = client.get(reverse('booking-list'))
		assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
	def test_customer_can_list_own_bookings(self, customer_auth_client, booking):
		response = customer_auth_client.get(reverse('booking-list'))
		assert response.status_code == status.HTTP_200_OK
		data = results(response.data)
		assert len(data) == 1
		assert data[0]['id'] == str(booking.id)


@pytest.mark.django_db
class TestBookingCreateAPI:
	"""Test booking creation."""
    
	def test_create_booking_with_valid_data(self, customer_auth_client, service_item):
		scheduled_datetime = timezone.now() + timedelta(days=2)
		before_count = Booking.objects.count()
		response = customer_auth_client.post(
			reverse('booking-list'),
			{
				'service_id': service_item.id,
				'service_location': '123 Main St',
				'city': 'Lahore',
				'latitude': 31.5204,
				'longitude': 74.3587,
				'scheduled_date': scheduled_datetime.date(),
				'scheduled_time': scheduled_datetime.time(),
				'estimated_duration': 30,
				'base_price': '1200.00',
				'tax_amount': '120.00',
				'total_amount': '1320.00',
				'payment_method': 'CASH',
			},
			format='json',
		)
		assert response.status_code == status.HTTP_201_CREATED
		assert Booking.objects.count() == before_count + 1
		created_booking = Booking.objects.order_by('-created_at').first()
		assert created_booking is not None
		assert created_booking.status == BookingStatus.PENDING_CONFIRMATION


@pytest.mark.django_db
class TestBookingConfirmAPI:
	"""Test booking confirmation workflow."""
    
	def test_confirm_pending_booking(self, customer_auth_client, booking):
		response = customer_auth_client.post(
			reverse('booking-confirm', args=[booking.id]),
			{'payment_method': 'JAZZCASH'},
			format='json',
		)
		assert response.status_code == status.HTTP_200_OK
		assert response.data['status'] == BookingStatus.CONFIRMED
        
		# Verify status history
		booking.refresh_from_db()
		assert booking.confirmed_at is not None
		history = BookingStatusHistory.objects.filter(booking=booking).first()
		assert history.new_status == BookingStatus.CONFIRMED


@pytest.mark.django_db
class TestBookingCancelAPI:
	"""Test booking cancellation."""
    
	def test_customer_cancel_booking(self, customer_auth_client, booking):
		response = customer_auth_client.post(
			reverse('booking-cancel', args=[booking.id]),
			{
				'reason': 'CUSTOMER_REQUEST',
				'notes': 'Emergency came up'
			},
			format='json',
		)
		assert response.status_code == status.HTTP_200_OK
		assert response.data['status'] == BookingStatus.CANCELLED
        
		booking.refresh_from_db()
		assert booking.cancellation_reason == 'CUSTOMER_REQUEST'
		assert 'Emergency' in booking.cancellation_notes
    
	def test_cannot_cancel_completed_booking(self, customer_auth_client, booking):
		booking.status = BookingStatus.COMPLETED
		booking.save()
        
		response = customer_auth_client.post(
			reverse('booking-cancel', args=[booking.id]),
			{'reason': 'CUSTOMER_REQUEST'},
			format='json',
		)
		assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestBookingWorkflow:
	"""Test complete booking workflow."""
    
	def test_complete_booking_workflow(self, customer_auth_client, mechanic_auth_client, booking, mechanic_user):
		# Step 1: Confirm booking
		response = customer_auth_client.post(
			reverse('booking-confirm', args=[booking.id]),
			{'payment_method': 'CASH'},
			format='json',
		)
		assert response.status_code == status.HTTP_200_OK
        
		# Step 2: Assign mechanic
		booking.mechanic = mechanic_user
		booking.status = BookingStatus.MECHANIC_ACCEPTED
		booking.save()
        
		# Step 3: Mechanic starts job
		response = mechanic_auth_client.post(
			reverse('booking-start', args=[booking.id]),
			format='json',
		)
		assert response.status_code == status.HTTP_200_OK
		assert response.data['status'] == BookingStatus.IN_PROGRESS
        
		# Step 4: Mechanic completes job
		response = mechanic_auth_client.post(
			reverse('booking-complete', args=[booking.id]),
			{'mechanic_notes': 'Oil changed successfully'},
			format='json',
		)
		assert response.status_code == status.HTTP_200_OK
		assert response.data['status'] == BookingStatus.COMPLETED


@pytest.mark.django_db
class TestBookingAddOnAPI:
	"""Test booking add-ons."""
    
	def test_list_available_add_ons(self, customer_auth_client, add_on):
		response = customer_auth_client.get(reverse('booking-addon-list'))
		assert response.status_code == status.HTTP_200_OK
		data = results(response.data)
		assert len(data) >= 1
		assert data[0]['name'] == 'Inspection'


@pytest.mark.django_db
class TestMyBookingsAction:
	"""Test my-bookings custom action."""
    
	def test_get_my_bookings_as_customer(self, customer_auth_client, booking):
		response = customer_auth_client.get(reverse('booking-my-bookings'))
		assert response.status_code == status.HTTP_200_OK
		data = response.data
		assert len(data) == 1
		assert data[0]['id'] == str(booking.id)
    
	def test_get_my_bookings_as_mechanic(self, mechanic_auth_client, booking, mechanic_user):
		booking.mechanic = mechanic_user
		booking.save()
        
		response = mechanic_auth_client.get(reverse('booking-my-bookings'))
		assert response.status_code == status.HTTP_200_OK
		data = response.data
		assert len(data) == 1
		assert data[0]['id'] == str(booking.id)
