"""
Login tests (AUTH-006 to AUTH-010)
Tests login with temporary token, rate limiting, error cases.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from datetime import datetime, timedelta

User = get_user_model()


@pytest.mark.django_db
class TestLoginSuccess:
    """AUTH-006: Valid login returns temporary token"""
    
    def test_login_with_valid_credentials(self, api_client, authenticated_user):
        """Test successful login returns temporary token"""
        user, _ = authenticated_user
        
        login_data = {
            'phone_number': user.phone_number,
            'password': 'SecurePass123!',
        }
        
        response = api_client.post('/api/v1/auth/login/', login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'temp_token' in data or 'token' in data
        assert 'otp_required' in data or 'expires_at' in data
        
    def test_login_response_structure(self, api_client, authenticated_user):
        """Verify login response contains expected fields"""
        user, _ = authenticated_user
        
        login_data = {
            'phone_number': user.phone_number,
            'password': 'SecurePass123!',
        }
        
        response = api_client.post('/api/v1/auth/login/', login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Response should indicate OTP is required
        assert 'otp_required' in data or 'status' in data
        
    def test_temp_token_expires(self, api_client, authenticated_user):
        """Verify temporary token has expiration"""
        user, _ = authenticated_user
        
        login_data = {
            'phone_number': user.phone_number,
            'password': 'SecurePass123!',
        }
        
        response = api_client.post('/api/v1/auth/login/', login_data)
        data = response.json()
        
        assert 'expires_at' in data or 'expires_in' in data


@pytest.mark.django_db
class TestLoginWrongPassword:
    """AUTH-007: Reject incorrect password"""
    
    def test_wrong_password_rejected(self, api_client, authenticated_user):
        """Test login with wrong password returns 401"""
        user, _ = authenticated_user
        
        login_data = {
            'phone_number': user.phone_number,
            'password': 'WrongPassword123!',
        }
        
        response = api_client.post('/api/v1/auth/login/', login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_failed_login_increments_counter(self, api_client, authenticated_user):
        """Verify failed login attempts are tracked"""
        user, _ = authenticated_user
        user.refresh_from_db()
        initial_attempts = user.failed_login_attempts
        
        login_data = {
            'phone_number': user.phone_number,
            'password': 'WrongPassword123!',
        }
        
        api_client.post('/api/v1/auth/login/', login_data)
        
        user.refresh_from_db()
        assert user.failed_login_attempts > initial_attempts


@pytest.mark.django_db
class TestLoginUserNotFound:
    """AUTH-008: Reject non-existing user"""
    
    def test_non_existing_user_rejected(self, api_client):
        """Test login with non-existent phone number"""
        login_data = {
            'phone_number': '+999999999999',
            'password': 'SomePass123!',
        }
        
        response = api_client.post('/api/v1/auth/login/', login_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND or response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLoginEmptyCredentials:
    """AUTH-009: Reject empty login"""
    
    def test_empty_request_rejected(self, api_client):
        """Test empty POST data"""
        response = api_client.post('/api/v1/auth/login/', {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_missing_phone_rejected(self, api_client):
        """Test missing phone number"""
        data = {'password': 'SomePass123!'}
        
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_missing_password_rejected(self, api_client):
        """Test missing password"""
        data = {'phone_number': '+923001234567'}
        
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginRateLimit:
    """AUTH-010: Block after multiple attempts"""
    
    def test_rate_limit_after_multiple_failed_attempts(self, api_client, authenticated_user):
        """Test account gets locked after max failed attempts"""
        user, _ = authenticated_user
        
        login_data = {
            'phone_number': user.phone_number,
            'password': 'WrongPassword123!',
        }
        
        # Make 5 failed login attempts
        for i in range(5):
            response = api_client.post('/api/v1/auth/login/', login_data)
            assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_429_TOO_MANY_REQUESTS]
        
        # 6th attempt should be rate limited
        response = api_client.post('/api/v1/auth/login/', login_data)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        
    def test_account_locked_until_time_set(self, api_client, authenticated_user):
        """Verify account_locked_until is set after rate limit"""
        user, _ = authenticated_user
        
        login_data = {
            'phone_number': user.phone_number,
            'password': 'WrongPassword123!',
        }
        
        # Make multiple failed attempts
        for i in range(5):
            api_client.post('/api/v1/auth/login/', login_data)
        
        user.refresh_from_db()
        assert user.account_locked_until is not None
        assert user.account_locked_until > datetime.now(user.account_locked_until.tzinfo)
        
    def test_correct_password_fails_when_rate_limited(self, api_client, authenticated_user):
        """Test that correct password also fails when rate limited"""
        user, _ = authenticated_user
        
        # First, trigger rate limit with wrong password
        wrong_login = {
            'phone_number': user.phone_number,
            'password': 'WrongPassword123!',
        }
        
        for i in range(5):
            api_client.post('/api/v1/auth/login/', wrong_login)
        
        # Now try with correct password
        correct_login = {
            'phone_number': user.phone_number,
            'password': 'SecurePass123!',
        }
        
        response = api_client.post('/api/v1/auth/login/', correct_login)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        
    def test_rate_limit_lifted_after_timeout(self, api_client, authenticated_user, mocker):
        """Test that rate limit is lifted after timeout"""
        user, _ = authenticated_user
        
        # Trigger rate limit
        wrong_login = {
            'phone_number': user.phone_number,
            'password': 'WrongPassword123!',
        }
        
        for i in range(5):
            api_client.post('/api/v1/auth/login/', wrong_login)
        
        # Mock time passage (15 minutes = 900 seconds) - set lock time in the past
        from django.utils import timezone
        user.account_locked_until = timezone.now() - timedelta(seconds=1)
        user.failed_login_attempts = 0
        user.save()
        
        # Try login again
        correct_login = {
            'phone_number': user.phone_number,
            'password': 'SecurePass123!',
        }
        
        response = api_client.post('/api/v1/auth/login/', correct_login)
        assert response.status_code == status.HTTP_200_OK
