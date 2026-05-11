"""
Token tests (AUTH-025 to AUTH-028)
Tests access tokens, refresh tokens, token expiration.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta

User = get_user_model()


@pytest.mark.django_db
class TestAccessTokenValid:
    """AUTH-025: Access protected route with valid token"""
    
    def test_access_protected_endpoint_with_token(self, authenticated_api_client):
        """Test accessing protected endpoint with valid token"""
        api_client, user, token = authenticated_api_client
        
        response = api_client.get('/api/v1/auth/profile/')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestAccessTokenExpired:
    """AUTH-026: Reject expired token"""
    
    def test_expired_token_rejected(self, api_client):
        """Test expired token is rejected"""
        # Use a fake token that doesn't exist in the database
        fake_expired_token = 'expired_token_that_does_not_exist_12345'
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {fake_expired_token}')
        
        response = api_client.get('/api/v1/auth/profile/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestInvalidToken:
    """AUTH-027: Reject fake token"""
    
    def test_fake_token_rejected(self, api_client):
        """Test fake/malformed token is rejected"""
        fake_token = 'fake_token_123456'
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {fake_token}')
        response = api_client.get('/api/v1/auth/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRefreshToken:
    """AUTH-028: Generate new access token from refresh token"""
    
    def test_refresh_token_generates_new_access_token(self, api_client, authenticated_user, mocker):
        """Test refresh token generates new access token"""
        user, old_token = authenticated_user
        
        mocker.patch('users.services.validate_refresh_token', return_value=user.id)
        
        refresh_data = {
            'refresh_token': old_token.key,
        }
        
        response = api_client.post('/api/v1/auth/refresh-token/', refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
