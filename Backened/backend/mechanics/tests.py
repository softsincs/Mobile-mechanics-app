from datetime import time

import pytest
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from bookings.models import Booking, BookingStatus
from services.models import Service, ServiceCategory
from users.models import User

from .models import MechanicAvailability, MechanicJobPhoto, MechanicProfile


@pytest.fixture
def mechanic_user(db):
    return User.objects.create_user(
        phone_number='+923001111111',
        email='mechanic@example.com',
        password='password123',
        first_name='Ahmed',
        last_name='Khan',
    )


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        phone_number='+923002222222',
        email='customer@example.com',
        password='password123',
        first_name='Sara',
        last_name='Ali',
    )


@pytest.fixture
def mechanic_client(mechanic_user):
    client = APIClient()
    token = Token.objects.create(user=mechanic_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def service(db):
    category = ServiceCategory.objects.create(name='Maintenance', description='Maintenance services')
    return Service.objects.create(
        category=category,
        name='Oil Change',
        estimated_duration=45,
        base_price='2500.00',
    )


@pytest.fixture
def assigned_booking(customer_user, mechanic_user, service):
    return Booking.objects.create(
        customer=customer_user,
        service=service,
        mechanic=mechanic_user,
        status=BookingStatus.MECHANIC_ASSIGNED,
        service_location='123 Main Street',
        city='Lahore',
        latitude=31.5204,
        longitude=74.3587,
        scheduled_date='2026-05-09',
        scheduled_time='10:00:00',
        estimated_duration=45,
        base_price='2500.00',
        total_amount='2875.00',
        payment_method='CASH',
    )


@pytest.mark.django_db
def test_mechanic_registers_profile():
    client = APIClient()
    response = client.post(reverse('mechanics-register'), {
        'first_name': 'Bilal',
        'last_name': 'Ahmed',
        'email': 'bilal@example.com',
        'phone_number': '+923003333333',
        'password': 'password123',
        'years_experience': 7,
        'emergency_contact': '+923009999999',
        'bio': 'Roadside repair specialist',
        'service_area_city': 'Lahore',
        'service_radius_km': 30,
        'max_concurrent_jobs': 4,
    }, format='json')

    assert response.status_code == 201
    assert response.data['is_approved'] is False
    assert response.data['is_active'] is False
    assert MechanicProfile.objects.filter(user__email='bilal@example.com').exists()


@pytest.mark.django_db
def test_mechanic_can_view_and_update_profile(mechanic_user, mechanic_client):
    profile = MechanicProfile.objects.create(user=mechanic_user, years_experience=5, service_area_city='Karachi')

    response = mechanic_client.get(reverse('mechanics-me'))
    assert response.status_code == 200
    assert response.data['service_area_city'] == 'Karachi'

    response = mechanic_client.patch(reverse('mechanics-me'), {'years_experience': 8, 'bio': 'Updated bio'}, format='json')
    assert response.status_code == 200
    profile.refresh_from_db()
    assert profile.years_experience == 8
    assert profile.bio == 'Updated bio'


@pytest.mark.django_db
def test_mechanic_can_manage_availability(mechanic_user, mechanic_client):
    MechanicProfile.objects.create(user=mechanic_user, is_approved=True, is_active=True)

    response = mechanic_client.post(reverse('mechanics-availability'), {
        'day_of_week': 0,
        'start_time': '09:00:00',
        'end_time': '17:00:00',
        'is_available': True,
        'notes': 'Weekday shift',
    }, format='json')
    assert response.status_code == 201
    assert MechanicAvailability.objects.count() == 1

    response = mechanic_client.get(reverse('mechanics-availability'))
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_mechanic_cannot_manage_availability_before_approval(mechanic_user, mechanic_client):
    MechanicProfile.objects.create(user=mechanic_user)

    response = mechanic_client.post(reverse('mechanics-availability'), {
        'day_of_week': 0,
        'start_time': '09:00:00',
        'end_time': '17:00:00',
        'is_available': True,
        'notes': 'Weekday shift',
    }, format='json')
    assert response.status_code == 403
    assert 'pending admin approval' in response.data['detail'].lower()


@pytest.mark.django_db
def test_mechanic_job_lifecycle(mechanic_user, mechanic_client, assigned_booking):
    MechanicProfile.objects.create(user=mechanic_user, is_approved=True, is_active=True, current_active_jobs=0, max_concurrent_jobs=3)

    response = mechanic_client.get(reverse('mechanic-jobs-jobs'))
    assert response.status_code == 200
    assert len(response.data) == 1

    response = mechanic_client.put(reverse('mechanic-jobs-accept', kwargs={'pk': assigned_booking.pk}), {}, format='json')
    assert response.status_code == 200
    assigned_booking.refresh_from_db()
    assert assigned_booking.status == BookingStatus.MECHANIC_ACCEPTED

    response = mechanic_client.put(reverse('mechanic-jobs-start', kwargs={'pk': assigned_booking.pk}), {}, format='json')
    assert response.status_code == 200
    assigned_booking.refresh_from_db()
    assert assigned_booking.status == BookingStatus.IN_PROGRESS

    response = mechanic_client.post(reverse('mechanic-jobs-upload-photos', kwargs={'pk': assigned_booking.pk}), {
        'photo_type': 'BEFORE',
        'caption': 'Before service',
        'photo_urls': ['https://example.com/before-1.jpg', 'https://example.com/before-2.jpg'],
    }, format='json')
    assert response.status_code == 201
    assert MechanicJobPhoto.objects.filter(booking=assigned_booking).count() == 2

    response = mechanic_client.put(reverse('mechanic-jobs-complete', kwargs={'pk': assigned_booking.pk}), {
        'mechanic_notes': 'Oil changed successfully',
        'issues_found': 'None',
    }, format='json')
    assert response.status_code == 200
    assigned_booking.refresh_from_db()
    assert assigned_booking.status == BookingStatus.COMPLETED
    assert assigned_booking.mechanic_notes.startswith('Oil changed successfully')
