"""Pytest coverage for dispatch app."""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from bookings.models import Booking, BookingStatus, BookingStatusHistory
from services.models import Service, ServiceCategory
from .models import JobOffer, JobOfferStatus, MechanicAssignmentHistory

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
def mechanic_user_2(db):
    """Create a second mechanic user for fallback testing."""
    return User.objects.create_user(
        phone_number='+923003333333',
        email='mechanic2@test.com',
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
def booking(customer_user, service_item):
    """Create a confirmed booking."""
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
        status=BookingStatus.CONFIRMED,
    )


def results(data):
    """Extract results from paginated response."""
    return data['results'] if isinstance(data, dict) and 'results' in data else data


@pytest.mark.django_db
class TestJobOfferModels:
    """Test job offer model functionality."""
    
    def test_job_offer_creation(self, booking, mechanic_user):
        """Test creating a job offer."""
        expires_at = timezone.now() + timedelta(seconds=60)
        job_offer = JobOffer.objects.create(
            booking=booking,
            mechanic=mechanic_user,
            expires_at=expires_at,
            status=JobOfferStatus.PENDING,
            matching_score=85.5,
            proximity_score=90.0,
            availability_score=80.0,
        )
        assert job_offer.status == JobOfferStatus.PENDING
        assert job_offer.is_accepted is False
        assert job_offer.is_expired is False
    
    def test_job_offer_accept(self, booking, mechanic_user):
        """Test accepting a job offer."""
        expires_at = timezone.now() + timedelta(seconds=60)
        job_offer = JobOffer.objects.create(
            booking=booking,
            mechanic=mechanic_user,
            expires_at=expires_at,
            status=JobOfferStatus.PENDING,
        )
        
        job_offer.accept()
        assert job_offer.status == JobOfferStatus.ACCEPTED
        assert job_offer.response_time is not None
        assert job_offer.is_accepted is True
    
    def test_job_offer_reject(self, booking, mechanic_user):
        """Test rejecting a job offer."""
        expires_at = timezone.now() + timedelta(seconds=60)
        job_offer = JobOffer.objects.create(
            booking=booking,
            mechanic=mechanic_user,
            expires_at=expires_at,
            status=JobOfferStatus.PENDING,
        )
        
        job_offer.reject(reason='Too far away')
        assert job_offer.status == JobOfferStatus.REJECTED
        assert job_offer.rejection_reason == 'Too far away'
        assert job_offer.response_time is not None


@pytest.mark.django_db
class TestJobOfferPermissions:
    """Test job offer access permissions."""
    
    def test_unauthenticated_cannot_list_offers(self):
        """Test that unauthenticated users cannot list offers."""
        client = APIClient()
        response = client.get(reverse('joboffer-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_mechanic_sees_only_own_offers(self, mechanic_auth_client, mechanic_user, booking):
        """Test that mechanics only see their own offers."""
        expires_at = timezone.now() + timedelta(seconds=60)
        JobOffer.objects.create(
            booking=booking,
            mechanic=mechanic_user,
            expires_at=expires_at,
            status=JobOfferStatus.PENDING,
        )
        
        response = mechanic_auth_client.get(reverse('joboffer-list'))
        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert len(data) == 1


@pytest.mark.django_db
class TestJobOfferActions:
    """Test job offer accept/reject actions."""
    
    def test_mechanic_can_accept_offer(self, mechanic_auth_client, mechanic_user, booking):
        """Test mechanic accepting an offer."""
        expires_at = timezone.now() + timedelta(seconds=60)
        job_offer = JobOffer.objects.create(
            booking=booking,
            mechanic=mechanic_user,
            expires_at=expires_at,
            status=JobOfferStatus.PENDING,
        )
        
        response = mechanic_auth_client.post(
            reverse('joboffer-accept', args=[job_offer.id]),
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['offer']['status'] == JobOfferStatus.ACCEPTED
        
        # Verify booking status changed
        booking.refresh_from_db()
        assert booking.status == BookingStatus.MECHANIC_ASSIGNED
        assert booking.mechanic == mechanic_user
    
    def test_mechanic_can_reject_offer(self, mechanic_auth_client, mechanic_user, booking):
        """Test mechanic rejecting an offer."""
        expires_at = timezone.now() + timedelta(seconds=60)
        job_offer = JobOffer.objects.create(
            booking=booking,
            mechanic=mechanic_user,
            expires_at=expires_at,
            status=JobOfferStatus.PENDING,
        )
        
        response = mechanic_auth_client.post(
            reverse('joboffer-reject', args=[job_offer.id]),
            {'reason': 'Too far away'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['offer']['status'] == JobOfferStatus.REJECTED
        assert response.data['offer']['rejection_reason'] == 'Too far away'
    
    def test_cannot_accept_expired_offer(self, mechanic_auth_client, mechanic_user, booking):
        """Test that expired offers cannot be accepted."""
        expires_at = timezone.now() - timedelta(seconds=10)
        job_offer = JobOffer.objects.create(
            booking=booking,
            mechanic=mechanic_user,
            expires_at=expires_at,
            status=JobOfferStatus.PENDING,
        )
        
        response = mechanic_auth_client.post(
            reverse('joboffer-accept', args=[job_offer.id]),
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'expired' in response.data['error'].lower()


@pytest.mark.django_db
class TestPendingOffersAction:
    """Test pending offers endpoint."""
    
    def test_get_pending_offers(self, mechanic_auth_client, mechanic_user, booking):
        """Test getting pending offers for mechanic."""
        expires_at = timezone.now() + timedelta(seconds=60)
        JobOffer.objects.create(
            booking=booking,
            mechanic=mechanic_user,
            expires_at=expires_at,
            status=JobOfferStatus.PENDING,
        )
        
        # Create an accepted offer (shouldn't appear in pending)
        booking2 = Booking.objects.create(
            customer=booking.customer,
            service=booking.service,
            service_location='456 Side St',
            city='Lahore',
            latitude=31.5204,
            longitude=74.3587,
            scheduled_date=booking.scheduled_date,
            scheduled_time=booking.scheduled_time,
            estimated_duration=30,
            base_price=Decimal('1200.00'),
            tax_amount=Decimal('120.00'),
            total_amount=Decimal('1320.00'),
            payment_method='CASH',
            status=BookingStatus.CONFIRMED,
        )
        JobOffer.objects.create(
            booking=booking2,
            mechanic=mechanic_user,
            expires_at=expires_at,
            status=JobOfferStatus.ACCEPTED,
        )
        
        response = mechanic_auth_client.get(reverse('joboffer-pending'))
        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert len(data) == 1  # Only pending offer


@pytest.mark.django_db
class TestAssignmentHistory:
    """Test mechanic assignment history tracking."""
    
    def test_create_assignment_history(self, booking, mechanic_user):
        """Test creating assignment history record."""
        history = MechanicAssignmentHistory.objects.create(
            booking=booking,
            assignment_round=1,
            available_mechanics_count=5,
            top_mechanics_considered=3,
            assigned_mechanic=mechanic_user,
            assignment_result='SUCCESS',
        )
        
        assert history.assignment_round == 1
        assert history.assigned_mechanic == mechanic_user
        assert history.assignment_result == 'SUCCESS'
    
    def test_admin_can_view_assignment_history(self, admin_auth_client, booking):
        """Test admin viewing assignment history."""
        MechanicAssignmentHistory.objects.create(
            booking=booking,
            assignment_round=1,
            available_mechanics_count=5,
        )
        
        response = admin_auth_client.get(reverse('assignment-history-list'))
        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert len(data) >= 1
    
    def test_non_admin_cannot_view_assignment_history(self, mechanic_auth_client, booking):
        """Test that non-admin cannot view assignment history."""
        MechanicAssignmentHistory.objects.create(
            booking=booking,
            assignment_round=1,
        )
        
        response = mechanic_auth_client.get(reverse('assignment-history-list'))
        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert len(data) == 0
