"""
Pytest configuration and fixtures for users app tests.
Provides factories, fixtures, and utilities for authentication tests.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from unittest.mock import patch

User = get_user_model()

# Patch email services at import time to prevent real email sends
patch('users.services.EmailService.send_otp_email', return_value=True).start()
patch('users.services.EmailService.send_password_reset_email', return_value=True).start()
patch('users.services.EmailService.send_reset_email', return_value=True).start()


@pytest.fixture
def api_client():
    """Provide REST API client for tests."""
    return APIClient()


@pytest.fixture
def authenticated_user(db):
    """Create an authenticated user for tests."""
    user = User.objects.create_user(
        phone_number='+923001234567',
        email='test@example.com',
        password='SecurePass123!',
        phone_verified=True,
        email_verified=True,
    )
    token = Token.objects.create(user=user)
    return user, token


@pytest.fixture
def authenticated_api_client(authenticated_user, api_client):
    """Provide authenticated API client."""
    user, token = authenticated_user
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client, user, token


@pytest.fixture
def valid_signup_data():
    """Valid signup data for testing."""
    return {
        'phone_number': '+923001234567',
        'email': 'newuser@example.com',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!',
    }


@pytest.fixture
def valid_login_data():
    """Valid login credentials."""
    return {
        'phone_number': '+923001234567',
        'password': 'SecurePass123!',
    }




@pytest.fixture
def mock_send_email(mocker):
    """Mock email sending - primarily for send_otp_email which most tests check."""
    return mocker.patch('users.services.EmailService.send_otp_email', return_value=True)


@pytest.fixture
def mock_cache(mocker):
    """Mock Django cache for OTP storage."""
    return mocker.patch('django.core.cache.cache')


@pytest.mark.django_db
class TestSetup:
    """Test database setup."""
    
    def test_user_model_exists(self):
        """Test that User model is properly configured."""
        assert User is not None
        
    def test_create_user(self, db):
        """Test basic user creation."""
        user = User.objects.create_user(
            phone_number='+923001234567',
            email='test@example.com',
            password='TestPass123'
        )
        assert user.phone_number == '+923001234567'
        assert user.email == 'test@example.com'
