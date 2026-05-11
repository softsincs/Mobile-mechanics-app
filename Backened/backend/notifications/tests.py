"""Pytest coverage for notifications app."""
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Notification, NotificationPreference

User = get_user_model()


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(phone_number='+923001111111', email='customer@test.com', password='SecurePass123!')


@pytest.fixture
def mechanic_user(db):
    return User.objects.create_user(phone_number='+923002222222', email='mechanic@test.com', password='SecurePass123!')


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


@pytest.mark.django_db
class TestNotificationModels:
    def test_create_notification(self, customer_user):
        notification = Notification.objects.create(
            user=customer_user,
            title='Booking confirmed',
            message='Your booking was confirmed.',
            notification_type='BOOKING',
            channel='IN_APP',
        )
        assert notification.is_read is False
        assert notification.is_sent is False

    def test_notification_preferences_default(self, customer_user):
        prefs = NotificationPreference.objects.create(user=customer_user)
        assert prefs.email_enabled is True
        assert prefs.sms_enabled is True
        assert prefs.push_enabled is True
        assert prefs.in_app_enabled is True


@pytest.mark.django_db
class TestNotificationAPI:
    def test_customer_can_create_notification(self, customer_auth_client):
        response = customer_auth_client.post(
            reverse('notification-list'),
            {
                'title': 'Test alert',
                'message': 'Hello from MobileMechanic',
                'notification_type': 'SYSTEM',
                'channel': 'IN_APP',
                'metadata': {'source': 'test'},
                'related_object_id': 'abc123',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Test alert'

    def test_unread_endpoint_filters_unread(self, customer_auth_client, customer_user):
        Notification.objects.create(
            user=customer_user,
            title='Unread',
            message='Unread notification',
            notification_type='SYSTEM',
            channel='IN_APP',
        )
        read_note = Notification.objects.create(
            user=customer_user,
            title='Read',
            message='Read notification',
            notification_type='SYSTEM',
            channel='IN_APP',
            is_read=True,
        )
        response = customer_auth_client.get(reverse('notification-unread'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == 'Unread'

    def test_mark_notification_read(self, customer_auth_client, customer_user):
        notification = Notification.objects.create(
            user=customer_user,
            title='Unread',
            message='Unread notification',
            notification_type='SYSTEM',
            channel='IN_APP',
        )
        response = customer_auth_client.post(reverse('notification-mark-read', args=[notification.id]))
        assert response.status_code == status.HTTP_200_OK
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_preferences_update(self, customer_auth_client):
        response = customer_auth_client.get(reverse('notification-preferences'))
        assert response.status_code == status.HTTP_200_OK
        response = customer_auth_client.patch(
            reverse('notification-preferences'),
            {'email_enabled': False, 'sms_enabled': False},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email_enabled'] is False
        assert response.data['sms_enabled'] is False
