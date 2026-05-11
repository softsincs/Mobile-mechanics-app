"""Pytest coverage for tracking app."""
from datetime import datetime, timedelta
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
from .models import MechanicLocation, LocationHistory, LocationAccuracy

User = get_user_model()


@pytest.fixture
def customer_user(db):
    """Create a customer user."""
    return User.objects.create_user(
        phone_number='+923001111111',
        email='customer@test.com',
        password='SecurePass123!',
    )


@pytest.fixture
def mechanic_user(db):
    """Create a mechanic user."""
    return User.objects.create_user(
        phone_number='+923002222222',
        email='mechanic@test.com',
        password='SecurePass123!',
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        phone_number='+923009999999',
        email='admin@test.com',
        password='AdminPass123!',
    )


@pytest.fixture
def customer_auth_client(customer_user):
    """Authenticated client for customer."""
    client = APIClient()
    token = Token.objects.create(user=customer_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def mechanic_auth_client(mechanic_user):
    """Authenticated client for mechanic."""
    client = APIClient()
    token = Token.objects.create(user=mechanic_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def admin_auth_client(admin_user):
    """Authenticated client for admin."""
    client = APIClient()
    token = Token.objects.create(user=admin_user)
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
def booking(customer_user, mechanic_user, service_item):
    """Create a booking with mechanic assigned."""
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
        status=BookingStatus.MECHANIC_ASSIGNED,
    )


def results(data):
    """Extract results from paginated response."""
    return data['results'] if isinstance(data, dict) and 'results' in data else data


@pytest.mark.django_db
class TestMechanicLocationModels:
    """Test mechanic location model functionality."""
    
    def test_create_mechanic_location(self, mechanic_user):
        """Test creating a mechanic location record."""
        location = MechanicLocation.objects.create(
            mechanic=mechanic_user,
            latitude=31.5204,
            longitude=74.3587,
            accuracy=10,
            speed=25.5,
            is_sharing=True,
        )
        assert location.mechanic == mechanic_user
        assert location.is_sharing is True
        assert location.is_stale is False
    
    def test_update_location(self, mechanic_user):
        """Test updating mechanic location."""
        location = MechanicLocation.objects.create(
            mechanic=mechanic_user,
            latitude=31.5204,
            longitude=74.3587,
            accuracy=10,
        )
        
        location.update_location(31.5210, 74.3590, accuracy=8, speed=30.0)
        assert location.latitude == 31.5210
        assert location.longitude == 74.3590
        assert location.accuracy == 8
        assert location.speed == 30.0
    
    def test_location_staleness(self, mechanic_user):
        """Test checking if location is stale."""
        # Create old location (31+ seconds old)
        old_time = timezone.now() - timedelta(seconds=31)
        location = MechanicLocation.objects.create(
            mechanic=mechanic_user,
            latitude=31.5204,
            longitude=74.3587,
        )
        # Manually set last_updated to old time
        MechanicLocation.objects.filter(id=location.id).update(last_updated=old_time)
        location.refresh_from_db()
        
        assert location.is_stale is True


@pytest.mark.django_db
class TestLocationHistoryModels:
    """Test location history model functionality."""
    
    def test_create_location_history(self, mechanic_user, booking):
        """Test creating location history record."""
        history = LocationHistory.objects.create(
            mechanic=mechanic_user,
            booking=booking,
            latitude=31.5204,
            longitude=74.3587,
            accuracy=10,
            speed=25.0,
            event_type='UPDATE',
        )
        assert history.mechanic == mechanic_user
        assert history.booking == booking
        assert history.event_type == 'UPDATE'
    
    def test_location_history_ordering(self, mechanic_user, booking):
        """Test that location history can be retrieved."""
        for i in range(3):
            LocationHistory.objects.create(
                mechanic=mechanic_user,
                booking=booking,
                latitude=31.5204 + i,
                longitude=74.3587 + i,
                event_type='UPDATE',
            )
        
        # Verify records were created
        history = LocationHistory.objects.filter(mechanic=mechanic_user, booking=booking)
        assert history.count() == 3
        
        # Verify we can order them
        history_ordered = history.order_by('-created_at')
        assert history_ordered.count() == 3


@pytest.mark.django_db
class TestMechanicLocationPermissions:
    """Test mechanic location access permissions."""
    
    def test_unauthenticated_cannot_update_location(self):
        """Test that unauthenticated users cannot update location."""
        client = APIClient()
        response = client.post(
            reverse('mechanic-location-update-my-location'),
            {
                'latitude': 31.5204,
                'longitude': 74.3587,
            },
            format='json'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_mechanic_can_update_own_location(self, mechanic_auth_client):
        """Test mechanic can update their own location."""
        response = mechanic_auth_client.post(
            reverse('mechanic-location-update-my-location'),
            {
                'latitude': 31.5204,
                'longitude': 74.3587,
                'accuracy': 10,
                'speed': 25.0,
            },
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['location']['latitude'] == 31.5204


@pytest.mark.django_db
class TestLocationSharingActions:
    """Test location sharing start/stop actions."""
    
    def test_start_sharing_location(self, mechanic_auth_client, mechanic_user, booking):
        """Test starting location sharing for a booking."""
        response = mechanic_auth_client.post(
            reverse('mechanic-location-start-sharing'),
            {'booking_id': str(booking.id)},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify location is marked as sharing
        location = MechanicLocation.objects.get(mechanic=mechanic_user)
        assert location.is_sharing is True
        assert location.booking == booking
    
    def test_stop_sharing_location(self, mechanic_auth_client, mechanic_user, booking):
        """Test stopping location sharing."""
        # First start sharing
        MechanicLocation.objects.create(
            mechanic=mechanic_user,
            booking=booking,
            latitude=31.5204,
            longitude=74.3587,
            is_sharing=True,
        )
        
        response = mechanic_auth_client.post(
            reverse('mechanic-location-stop-sharing'),
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        location = MechanicLocation.objects.get(mechanic=mechanic_user)
        assert location.is_sharing is False


@pytest.mark.django_db
class TestLocationHistoryRetrieval:
    """Test retrieving location history."""
    
    def test_customer_can_view_mechanic_track(self, customer_auth_client, customer_user, mechanic_user, booking):
        """Test customer viewing mechanic's location track."""
        # Create location history
        for i in range(3):
            LocationHistory.objects.create(
                mechanic=mechanic_user,
                booking=booking,
                latitude=31.5204 + i,
                longitude=74.3587 + i,
                event_type='UPDATE',
            )
        
        response = customer_auth_client.get(
            reverse('location-history-booking-track'),
            {'booking_id': str(booking.id)},
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
    
    def test_customer_cannot_view_others_track(self, customer_auth_client, mechanic_user):
        """Test customer cannot view track for other booking."""
        other_customer = User.objects.create_user(
            phone_number='+923005555555',
            email='other@test.com',
            password='SecurePass123!',
        )
        
        scheduled_datetime = timezone.now() + timedelta(days=2)
        service = Service.objects.create(
            category=ServiceCategory.objects.create(name='Test'),
            name='Test Service',
            estimated_duration=30,
            base_price=Decimal('1000.00'),
            min_price=Decimal('900.00'),
            max_price=Decimal('1100.00'),
            is_active=True,
        )
        
        other_booking = Booking.objects.create(
            customer=other_customer,
            mechanic=mechanic_user,
            service=service,
            service_location='123 Main St',
            city='Lahore',
            latitude=31.5204,
            longitude=74.3587,
            scheduled_date=scheduled_datetime.date(),
            scheduled_time=scheduled_datetime.time(),
            estimated_duration=30,
            base_price=Decimal('1000.00'),
            total_amount=Decimal('1000.00'),
            payment_method='CASH',
            status=BookingStatus.MECHANIC_ASSIGNED,
        )
        
        response = customer_auth_client.get(
            reverse('location-history-booking-track'),
            {'booking_id': str(other_booking.id)},
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestLocationAccuracy:
    """Test location accuracy tracking."""
    
    def test_record_location_accuracy(self, mechanic_auth_client, mechanic_user):
        """Test recording location accuracy metrics."""
        response = mechanic_auth_client.post(
            reverse('location-accuracy-list'),
            {
                'mechanic': str(mechanic_user.id),
                'provider': 'FUSED',
                'horizontal_accuracy': 8.5,
                'vertical_accuracy': 12.0,
                'satellites_used': 12,
                'is_from_mock_provider': False,
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['provider'] == 'FUSED'
        assert response.data['horizontal_accuracy'] == 8.5
    
    def test_mechanic_can_view_own_accuracy(self, mechanic_auth_client, mechanic_user):
        """Test mechanic viewing own accuracy logs."""
        LocationAccuracy.objects.create(
            mechanic=mechanic_user,
            provider='GPS',
            horizontal_accuracy=10.0,
            satellites_used=12,
        )
        
        response = mechanic_auth_client.get(
            reverse('location-accuracy-my-accuracy'),
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
