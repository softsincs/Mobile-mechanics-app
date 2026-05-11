import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestFullLoginFlow:
    """Tests for complete login flow: login -> OTP -> verify -> authenticated."""

    def test_signup_login_otp_verify_flow(self, api_client):
        """Complete flow: signup -> login -> send OTP -> verify OTP -> access token."""
        # Step 1: Signup
        signup_data = {
            "phone_number": "+923001234567",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = api_client.post("/api/v1/auth/signup/", signup_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Step 2: Login
        login_data = {"phone_number": "+923001234567", "password": "SecurePass123!"}
        response = api_client.post("/api/v1/auth/login/", login_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        temp_token = response.json().get("temp_token")
        assert temp_token is not None

        # Step 3: Send OTP
        otp_data = {"phone_number": "+923001234567"}
        response = api_client.post("/api/v1/auth/send-otp/", otp_data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Step 4: Verify OTP (use mock OTP or retrieve from cache)
        user = User.objects.get(phone_number="+923001234567")
        from django.core.cache import cache

        otp_code = cache.get(f"otp_{user.id}")
        if otp_code is None:
            otp_code = "123456"  # Default test OTP

        verify_data = {"phone_number": "+923001234567", "otp": otp_code}
        response = api_client.post(
            "/api/v1/auth/verify-otp/", verify_data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    def test_login_without_otp_verification_fails(self, api_client):
        """Cannot access protected routes without OTP verification."""
        signup_data = {
            "phone_number": "+923001234567",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        api_client.post("/api/v1/auth/signup/", signup_data, format="json")

        login_data = {"phone_number": "+923001234567", "password": "SecurePass123!"}
        response = api_client.post("/api/v1/auth/login/", login_data, format="json")

        # Temp token should not grant access to protected routes
        temp_token = response.json().get("temp_token")
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {temp_token}")
        response = api_client.get("/api/v1/auth/profile/")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, 403]


@pytest.mark.django_db
class TestSignupLoginFlow:
    """Tests for signup followed by login."""

    def test_new_user_can_login_after_signup(self, api_client):
        """User should be able to login immediately after signup."""
        # Signup
        signup_data = {
            "phone_number": "+923001234567",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = api_client.post("/api/v1/auth/signup/", signup_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Login
        login_data = {"phone_number": "+923001234567", "password": "SecurePass123!"}
        response = api_client.post("/api/v1/auth/login/", login_data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_signup_with_duplicate_phone_prevents_login(self, api_client):
        """Cannot signup twice with same phone, so login would fail."""
        signup_data = {
            "phone_number": "+923001234567",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        api_client.post("/api/v1/auth/signup/", signup_data, format="json")

        # Try duplicate signup
        duplicate_data = {
            "phone_number": "+923001234567",
            "email": "test2@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = api_client.post(
            "/api/v1/auth/signup/", duplicate_data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordResetFlow:
    """Tests for password reset flow."""

    def test_forgot_password_reset_login_flow(self, api_client, authenticated_user):
        """Complete password reset: request -> reset -> login with new password."""
        user, _ = authenticated_user
        old_password = "SecurePass123!"
        new_password = "NewSecurePass123!"

        # Step 1: Request password reset
        data = {"email": user.email}
        response = api_client.post("/api/v1/auth/forgot-password/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Step 2: Reset with token
        from users.models import PasswordResetToken

        token = PasswordResetToken.objects.create(user=user)
        reset_data = {
            "reset_token": str(token.token),
            "new_password": new_password,
            "new_password_confirm": new_password,
        }
        response = api_client.post("/api/v1/auth/reset-password/", reset_data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Step 3: Login with new password should work
        login_data = {"phone_number": user.phone_number, "password": new_password}
        response = api_client.post("/api/v1/auth/login/", login_data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_old_password_fails_after_reset(self, api_client, authenticated_user):
        """Old password should not work after reset."""
        user, _ = authenticated_user
        old_password = "SecurePass123!"
        new_password = "NewSecurePass123!"

        # Reset password
        from users.models import PasswordResetToken

        token = PasswordResetToken.objects.create(user=user)
        reset_data = {
            "reset_token": str(token.token),
            "new_password": new_password,
            "new_password_confirm": new_password,
        }
        api_client.post("/api/v1/auth/reset-password/", reset_data, format="json")

        # Try login with old password
        login_data = {"phone_number": user.phone_number, "password": old_password}
        response = api_client.post("/api/v1/auth/login/", login_data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
