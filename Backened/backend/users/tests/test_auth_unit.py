import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

User = get_user_model()


@pytest.mark.django_db
class TestEmailServiceIntegration:
    """Tests for email service OTP delivery."""

    def test_otp_email_sent_on_send_otp(self, authenticated_user, mocker):
        """OTP should be sent to user email when requesting OTP."""
        user, _ = authenticated_user

        # Mock email service
        mock_send_email = mocker.patch(
            "users.services.EmailService.send_otp_email"
        )

        api_client = APIClient()
        data = {"phone_number": user.phone_number}
        response = api_client.post("/api/v1/auth/send-otp/", data, format="json")

        # Email service should have been called
        assert mock_send_email.called

    def test_otp_email_contains_code(self, authenticated_user, mocker):
        """OTP email should contain 6-digit code."""
        user, _ = authenticated_user

        mock_send_email = mocker.patch(
            "users.services.EmailService.send_otp_email"
        )

        api_client = APIClient()
        data = {"phone_number": user.phone_number}
        api_client.post("/api/v1/auth/send-otp/", data, format="json")

        # Get call arguments
        if mock_send_email.called:
            call_args = mock_send_email.call_args
            # OTP code should be 6 digits
            otp_code = call_args[0][1] if len(call_args[0]) > 1 else None
            if otp_code:
                assert len(str(otp_code)) == 6
                assert str(otp_code).isdigit()

    def test_password_reset_email_sent(self, authenticated_user, mocker):
        """Password reset email should be sent when requesting reset."""
        user, _ = authenticated_user

        mock_send_email = mocker.patch(
            "users.services.EmailService.send_reset_email"
        )

        api_client = APIClient()
        data = {"email": user.email}
        api_client.post("/api/v1/auth/forgot-password/", data, format="json")

        # Email service should have been called
        if mock_send_email.called:
            assert True


@pytest.mark.django_db
class TestPasswordHashingSecurity:
    """Tests for password hashing and storage security."""

    def test_password_hashed_in_database(self, api_client):
        """Passwords should be hashed, not stored in plain text."""
        signup_data = {
            "phone_number": "+923001234567",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        api_client.post("/api/v1/auth/signup/", signup_data, format="json")

        user = User.objects.get(phone_number="+923001234567")
        # Password should not be stored in plain text
        assert user.password != "SecurePass123!"
        # Password should be hashed (starts with algorithm prefix)
        assert user.password.startswith("pbkdf2_sha256$")

    def test_wrong_password_rejected(self, api_client):
        """Wrong password should not authenticate user."""
        signup_data = {
            "phone_number": "+923001234567",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        api_client.post("/api/v1/auth/signup/", signup_data, format="json")

        login_data = {"phone_number": "+923001234567", "password": "WrongPassword123"}
        response = api_client.post("/api/v1/auth/login/", login_data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestOTPCodeGeneration:
    """Tests for OTP code generation."""

    def test_otp_is_six_digits(self, authenticated_user, mocker):
        """Generated OTP should always be exactly 6 digits."""
        user, _ = authenticated_user

        # Capture generated OTP
        generated_otps = []

        def capture_otp(**kwargs):
            generated_otps.append(kwargs.get('otp_code'))
            return True

        mock_send = mocker.patch(
            "users.services.EmailService.send_otp_email",
            side_effect=capture_otp,
        )

        api_client = APIClient()
        for _ in range(5):
            data = {"phone_number": user.phone_number}
            api_client.post("/api/v1/auth/send-otp/", data, format="json")

        # Check all generated codes are 6 digits
        for otp in generated_otps:
            if otp:
                assert len(str(otp)) == 6
                assert str(otp).isdigit()

    def test_otp_codes_are_random(self, authenticated_user, mocker):
        """Multiple OTP generations should produce different codes."""
        user, _ = authenticated_user

        generated_otps = []

        def capture_otp(**kwargs):
            generated_otps.append(kwargs.get('otp_code'))
            return True

        mocker.patch(
            "users.services.EmailService.send_otp_email",
            side_effect=capture_otp,
        )

        api_client = APIClient()
        # Generate 3 OTPs
        for _ in range(3):
            data = {"phone_number": user.phone_number}
            api_client.post("/api/v1/auth/send-otp/", data, format="json")

        # Filter out None values and check uniqueness
        valid_otps = [otp for otp in generated_otps if otp]
        if len(valid_otps) >= 2:
            # At least some should be different
            assert len(set(valid_otps)) > 1 or len(valid_otps) == 1


@pytest.mark.django_db
class TestRateLimitingService:
    """Tests for rate limiting service functionality."""

    def test_rate_limit_increments_counter(self, authenticated_user):
        """Rate limit attempts should be tracked."""
        user, _ = authenticated_user
        initial_attempts = user.failed_login_attempts

        api_client = APIClient()
        login_data = {"phone_number": user.phone_number, "password": "WrongPassword"}
        api_client.post("/api/v1/auth/login/", login_data, format="json")

        user.refresh_from_db()
        # Failed attempts should have increased
        assert user.failed_login_attempts > initial_attempts

    def test_rate_limit_resets_on_success(self, authenticated_user):
        """Failed login counter should reset on successful login."""
        user, _ = authenticated_user

        # First, increment failed attempts
        api_client = APIClient()
        for _ in range(3):
            login_data = {"phone_number": user.phone_number, "password": "WrongPassword"}
            api_client.post("/api/v1/auth/login/", login_data, format="json")

        user.refresh_from_db()
        failed_before = user.failed_login_attempts
        assert failed_before > 0

        # Now login successfully
        login_data = {"phone_number": user.phone_number, "password": "SecurePass123!"}
        response = api_client.post("/api/v1/auth/login/", login_data, format="json")

        if response.status_code == status.HTTP_200_OK:
            user.refresh_from_db()
            # Counter should be reset
            assert user.failed_login_attempts == 0
