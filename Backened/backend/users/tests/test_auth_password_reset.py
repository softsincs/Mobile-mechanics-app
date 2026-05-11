import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestPasswordResetRequest:
    """Tests for requesting password reset token via email."""

    def test_request_reset_success(self, api_client, authenticated_user):
        """User should receive password reset email when requesting reset."""
        user, _ = authenticated_user
        data = {"email": user.email}
        response = api_client.post("/api/v1/auth/forgot-password/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    def test_invalid_email_rejected(self, api_client):
        """Non-existent email should be rejected gracefully."""
        data = {"email": "nonexistent@example.com"}
        response = api_client.post("/api/v1/auth/forgot-password/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_email_rejected(self, api_client):
        """Empty email should be rejected."""
        data = {"email": ""}
        response = api_client.post("/api/v1/auth/forgot-password/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordReset:
    """Tests for resetting password with valid token."""

    def test_reset_with_valid_token(self, api_client, authenticated_user):
        """User should be able to reset password with valid reset token."""
        user, _ = authenticated_user
        # In real implementation, this would generate a token from forgot-password
        from users.models import PasswordResetToken
        token = PasswordResetToken.objects.create(user=user)

        data = {
            "reset_token": str(token.token),
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!",
        }
        response = api_client.post("/api/v1/auth/reset-password/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_token_rejected(self, api_client):
        """Invalid reset token should be rejected."""
        data = {
            "reset_token": "invalid_token_12345",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!",
        }
        response = api_client.post("/api/v1/auth/reset-password/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_expired_token_rejected(self, api_client, authenticated_user):
        """Expired reset token should be rejected."""
        user, _ = authenticated_user
        from users.models import PasswordResetToken
        from datetime import datetime, timedelta, timezone

        token = PasswordResetToken.objects.create(
            user=user, expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )

        data = {
            "reset_token": str(token.token),
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!",
        }
        response = api_client.post("/api/v1/auth/reset-password/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_password_rejected(self, api_client, authenticated_user):
        """Weak passwords should be rejected during reset."""
        user, _ = authenticated_user
        from users.models import PasswordResetToken

        token = PasswordResetToken.objects.create(user=user)

        weak_passwords = [
            ("123", "123"),
            ("abc", "abc"),
            ("password", "password"),
            ("Pass1", "Pass1"),
        ]

        for weak_pass, weak_confirm in weak_passwords:
            data = {
                "reset_token": str(token.token),
                "new_password": weak_pass,
                "new_password_confirm": weak_confirm,
            }
            response = api_client.post("/api/v1/auth/reset-password/", data, format="json")
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_mismatch_rejected(self, api_client, authenticated_user):
        """Mismatched password confirmation should be rejected."""
        user, _ = authenticated_user
        from users.models import PasswordResetToken

        token = PasswordResetToken.objects.create(user=user)

        data = {
            "reset_token": str(token.token),
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "DifferentPass123!",
        }
        response = api_client.post("/api/v1/auth/reset-password/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_can_login_after_reset(self, api_client, authenticated_user):
        """User should be able to login with new password after reset."""
        user, _ = authenticated_user
        from users.models import PasswordResetToken

        new_password = "NewSecurePass123!"
        token = PasswordResetToken.objects.create(user=user)

        # Reset password
        data = {
            "reset_token": str(token.token),
            "new_password": new_password,
            "new_password_confirm": new_password,
        }
        response = api_client.post("/api/v1/auth/reset-password/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Try login with new password
        login_data = {"phone_number": user.phone_number, "password": new_password}
        response = api_client.post("/api/v1/auth/login/", login_data, format="json")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
