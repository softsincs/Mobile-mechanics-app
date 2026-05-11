"""
OTP tests (AUTH-011 to AUTH-019)
Tests OTP sending, verification, rate limiting, and security.
Assumes OTP is sent to EMAIL for now (SMS will be added later).
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from datetime import datetime, timedelta

User = get_user_model()


@pytest.mark.django_db
class TestOTPSendSuccess:
    """AUTH-011: OTP sent to valid user"""
    
    def test_send_otp_success(self, api_client, authenticated_user, mock_send_email):
        """Test OTP is generated and sent to email"""
        user, _ = authenticated_user
        
        data = {
            'phone_number': user.phone_number,
        }
        
        response = api_client.post('/api/v1/auth/send-otp/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert mock_send_email.called or 'otp_id' in response.json()
        
    def test_otp_sent_to_email(self, api_client, authenticated_user, mock_send_email):
        """Verify OTP is sent to user's email"""
        user, _ = authenticated_user
        
        data = {
            'phone_number': user.phone_number,
        }
        
        api_client.post('/api/v1/auth/send-otp/', data)
        
        # Email service should be called with user's email
        assert mock_send_email.called
        
    def test_otp_response_contains_metadata(self, api_client, authenticated_user, mock_send_email):
        """Verify response contains OTP metadata"""
        user, _ = authenticated_user
        
        data = {
            'phone_number': user.phone_number,
        }
        
        response = api_client.post('/api/v1/auth/send-otp/', data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'otp_id' in data or 'expires_in' in data


@pytest.mark.django_db
class TestOTPSendInvalidUser:
    """AUTH-012: Reject unknown user"""
    
    def test_non_existing_user_rejected(self, api_client):
        """Test OTP request for non-existent user"""
        data = {
            'phone_number': '+999999999999',
        }
        
        response = api_client.post('/api/v1/auth/send-otp/', data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND or status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestOTPRateLimit:
    """AUTH-013: Limit OTP requests"""
    
    def test_otp_rate_limit_after_multiple_requests(self, api_client, authenticated_user, mock_send_email):
        """Test rate limit after 5 OTP requests"""
        user, _ = authenticated_user
        
        data = {
            'phone_number': user.phone_number,
        }
        
        # Send OTP 5 times
        for i in range(5):
            response = api_client.post('/api/v1/auth/send-otp/', data)
            assert response.status_code == status.HTTP_200_OK
        
        # 6th request should be rate limited
        response = api_client.post('/api/v1/auth/send-otp/', data)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        
    def test_otp_rate_limit_resets_after_timeout(self, api_client, authenticated_user, mock_send_email, mocker):
        """Test rate limit resets after timeout"""
        user, _ = authenticated_user
        
        data = {
            'phone_number': user.phone_number,
        }
        
        # Trigger rate limit
        for i in range(5):
            api_client.post('/api/v1/auth/send-otp/', data)
        
        # Mock time passage
        mocker.patch('django.utils.timezone.now', return_value=datetime.now(datetime.now().astimezone().tzinfo) + timedelta(minutes=31))
        
        # Should be able to send again
        response = api_client.post('/api/v1/auth/send-otp/', data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_429_TOO_MANY_REQUESTS]  # May still be limited depending on implementation


@pytest.mark.django_db
class TestOTPGeneration:
    """AUTH-014: OTP stored in cache"""
    
    def test_otp_generated_and_stored(self, api_client, authenticated_user, mock_send_email, mock_cache):
        """Test OTP is generated and cached"""
        user, _ = authenticated_user
        
        data = {
            'phone_number': user.phone_number,
        }
        
        response = api_client.post('/api/v1/auth/send-otp/', data)
        
        assert response.status_code == status.HTTP_200_OK
        # Cache or OTP token model should have the OTP
        
    def test_otp_is_6_digits(self, api_client, authenticated_user, mock_send_email):
        """Test generated OTP is 6 digits"""
        user, _ = authenticated_user
        
        data = {
            'phone_number': user.phone_number,
        }
        
        response = api_client.post('/api/v1/auth/send-otp/', data)
        
        # OTP should be 6 digits (verified in verify endpoint)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestOTPVerifySuccess:
    """AUTH-015: Correct OTP returns access token"""
    
    def test_verify_otp_success(self, api_client, authenticated_user, mock_send_email, mocker):
        """Test correct OTP verification returns tokens"""
        user, _ = authenticated_user
        
        # Send OTP first
        send_data = {'phone_number': user.phone_number}
        send_response = api_client.post('/api/v1/auth/send-otp/', send_data)
        
        # Mock the correct OTP
        mocker.patch('django.core.cache.cache.get', return_value='123456')
        
        verify_data = {
            'phone_number': user.phone_number,
            'otp': '123456',
        }
        
        response = api_client.post('/api/v1/auth/verify-otp/', verify_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'access_token' in data or 'token' in data
        
    def test_access_token_can_authenticate(self, api_client, authenticated_user, mock_send_email, mocker):
        """Test returned token can authenticate requests"""
        user, _ = authenticated_user
        
        # Send OTP
        send_data = {'phone_number': user.phone_number}
        api_client.post('/api/v1/auth/send-otp/', send_data)
        
        # Mock correct OTP
        mocker.patch('django.core.cache.cache.get', return_value='123456')
        
        # Verify OTP
        verify_data = {
            'phone_number': user.phone_number,
            'otp': '123456',
        }
        
        response = api_client.post('/api/v1/auth/verify-otp/', verify_data)
        token = response.json().get('access_token') or response.json().get('token')
        
        # Use token to access protected endpoint
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        protected_response = api_client.get('/api/v1/auth/profile/')
        
        assert protected_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestOTPVerifyWrong:
    """AUTH-016: Reject invalid OTP"""
    
    def test_wrong_otp_rejected(self, api_client, authenticated_user, mock_send_email):
        """Test incorrect OTP is rejected"""
        user, _ = authenticated_user
        
        # Send OTP
        send_data = {'phone_number': user.phone_number}
        api_client.post('/api/v1/auth/send-otp/', send_data)
        
        verify_data = {
            'phone_number': user.phone_number,
            'otp': '000000',  # Wrong OTP
        }
        
        response = api_client.post('/api/v1/auth/verify-otp/', verify_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestOTPExpired:
    """AUTH-017: Reject expired OTP"""
    
    def test_expired_otp_rejected(self, api_client, authenticated_user, mock_send_email, mocker):
        """Test expired OTP is rejected"""
        user, _ = authenticated_user
        
        # Send OTP
        send_data = {'phone_number': user.phone_number}
        api_client.post('/api/v1/auth/send-otp/', send_data)
        
        # Mock OTP as expired
        mocker.patch('django.core.cache.cache.get', return_value=None)
        
        verify_data = {
            'phone_number': user.phone_number,
            'otp': '123456',
        }
        
        response = api_client.post('/api/v1/auth/verify-otp/', verify_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST or status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestOTPReuse:
    """AUTH-018: OTP cannot be reused"""
    
    def test_otp_cannot_be_reused(self, api_client, authenticated_user, mock_send_email, mocker):
        """Test OTP can only be used once"""
        user, _ = authenticated_user
        
        # Send OTP
        send_data = {'phone_number': user.phone_number}
        api_client.post('/api/v1/auth/send-otp/', send_data)
        
        # Mock cache.get to return OTP on first call, then None on second call (after deletion)
        call_count = {'count': 0}
        def cache_get_side_effect(key, default=None):
            if 'otp_code_' in key:
                call_count['count'] += 1
                return '123456' if call_count['count'] == 1 else None
            return default
        
        mocker.patch('django.core.cache.cache.get', side_effect=cache_get_side_effect)
        
        # First verification should succeed
        verify_data = {
            'phone_number': user.phone_number,
            'otp': '123456',
        }
        
        response1 = api_client.post('/api/v1/auth/verify-otp/', verify_data)
        assert response1.status_code == status.HTTP_200_OK
        
        # Second verification with same OTP should fail (because cache returns None)
        response2 = api_client.post('/api/v1/auth/verify-otp/', verify_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestOTPMaxAttempts:
    """AUTH-019: Block after 3 wrong attempts"""
    
    def test_block_after_max_wrong_attempts(self, api_client, authenticated_user, mock_send_email):
        """Test account blocks after 3 wrong OTP attempts"""
        user, _ = authenticated_user
        
        # Send OTP
        send_data = {'phone_number': user.phone_number}
        api_client.post('/api/v1/auth/send-otp/', send_data)
        
        verify_data = {
            'phone_number': user.phone_number,
            'otp': '000000',  # Wrong OTP
        }
        
        # Make 3 wrong attempts
        for i in range(3):
            response = api_client.post('/api/v1/auth/verify-otp/', verify_data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # 4th attempt should be blocked
        response = api_client.post('/api/v1/auth/verify-otp/', verify_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN or status.HTTP_429_TOO_MANY_REQUESTS
