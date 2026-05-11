import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestAccessToken:
    """Tests for access token usage and validation."""

    def test_protected_route_with_valid_token(self, authenticated_api_client):
        """Protected endpoint should accept valid access token."""
        api_client, user, token = authenticated_api_client
        response = api_client.get("/api/v1/auth/profile/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["phone_number"] == user.phone_number

    def test_protected_route_without_token(self, api_client):
        """Protected endpoint should reject requests without token."""
        response = api_client.get("/api/v1/auth/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_route_with_invalid_token(self, api_client):
        """Protected endpoint should reject invalid/fake tokens."""
        api_client.credentials(HTTP_AUTHORIZATION="Token invalid_fake_token_12345")
        response = api_client.get("/api/v1/auth/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenExpiration:
    """Tests for token expiration behavior."""

    def test_expired_token_rejected(self, api_client, authenticated_user):
        """Expired token should be rejected."""
        user, token = authenticated_user
        # Simulate token expiration by marking it as used/invalid
        from rest_framework.authtoken.models import Token

        Token.objects.filter(key=token.key).update(key="expired_token_key")
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = api_client.get("/api/v1/auth/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRefreshToken:
    """Tests for refresh token functionality."""

    def test_refresh_token_generates_new_access(self, api_client, authenticated_user):
        """Refresh token should generate new access token."""
        user, old_token = authenticated_user
        data = {"refresh_token": str(old_token.key)}
        response = api_client.post(
            "/api/v1/auth/refresh-token/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        # New token should be different
        assert response.json()["access_token"] != old_token.key

    def test_invalid_refresh_token_rejected(self, api_client):
        """Invalid refresh token should be rejected."""
        data = {"refresh_token": "invalid_refresh_token_12345"}
        response = api_client.post(
            "/api/v1/auth/refresh-token/", data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_old_token_works_after_refresh(self, api_client, authenticated_user):
        """New token should work after refresh (old token is invalidated)."""
        user, old_token = authenticated_user
        old_token_key = old_token.key
        
        # Refresh to get new token
        data = {"refresh_token": str(old_token.key)}
        response = api_client.post(
            "/api/v1/auth/refresh-token/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        new_token_key = response.json()["access_token"]
        
        # New token should work
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {new_token_key}")
        response = api_client.get("/api/v1/auth/profile/")
        assert response.status_code == status.HTTP_200_OK
        
        # Old token should NOT work (invalidated after refresh)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {old_token_key}")
        response = api_client.get("/api/v1/auth/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
