import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestBruteForceProtection:
    """Tests for brute force attack protection."""

    def test_rate_limit_after_failed_attempts(self, api_client, authenticated_user):
        """Login attempts should be rate limited after failures."""
        user, _ = authenticated_user
        login_url = "/api/v1/auth/login/"

        # Make 5 failed login attempts
        for i in range(5):
            data = {"phone_number": user.phone_number, "password": "WrongPassword123"}
            response = api_client.post(login_url, data, format="json")

        # 6th attempt should be rate limited or blocked
        data = {"phone_number": user.phone_number, "password": "WrongPassword123"}
        response = api_client.post(login_url, data, format="json")
        assert response.status_code in [
            status.HTTP_429_TOO_MANY_REQUESTS,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_brute_force_locks_account(self, api_client, authenticated_user):
        """Account should be locked after multiple failed attempts."""
        user, _ = authenticated_user
        login_url = "/api/v1/auth/login/"

        # Make 5 failed attempts
        for i in range(5):
            data = {"phone_number": user.phone_number, "password": "WrongPassword123"}
            api_client.post(login_url, data, format="json")

        # Check account is locked
        user.refresh_from_db()
        assert user.is_account_locked()

    def test_correct_password_fails_when_rate_limited(
        self, api_client, authenticated_user
    ):
        """Even correct password should fail during rate limit."""
        user, _ = authenticated_user
        login_url = "/api/v1/auth/login/"

        # Make 5 failed attempts
        for i in range(5):
            data = {"phone_number": user.phone_number, "password": "WrongPassword123"}
            api_client.post(login_url, data, format="json")

        # Try correct password while rate limited
        data = {"phone_number": user.phone_number, "password": "SecurePass123!"}
        response = api_client.post(login_url, data, format="json")
        assert response.status_code in [
            status.HTTP_429_TOO_MANY_REQUESTS,
            status.HTTP_400_BAD_REQUEST,
        ]


@pytest.mark.django_db
class TestSQLInjectionProtection:
    """Tests for SQL injection vulnerability prevention."""

    def test_sql_injection_in_phone_rejected(self, api_client):
        """SQL injection payloads in phone should be safely rejected."""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "1; DELETE FROM users WHERE 1=1; --",
            "admin' --",
        ]

        for payload in sql_payloads:
            data = {"phone_number": payload, "password": "TestPassword123"}
            response = api_client.post("/api/v1/auth/login/", data, format="json")
            # Should be rejected, not cause database error
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
            ]

    def test_sql_injection_in_email_rejected(self, api_client):
        """SQL injection payloads in email should be safely rejected."""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "test@example.com' --",
        ]

        for payload in sql_payloads:
            data = {
                "email": payload,
            }
            response = api_client.post(
                "/api/v1/auth/forgot-password/", data, format="json"
            )
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
            ]


@pytest.mark.django_db
class TestXSSProtection:
    """Tests for XSS (Cross-Site Scripting) prevention."""

    def test_xss_in_password_sanitized(self, api_client):
        """XSS payloads in password should be sanitized/rejected."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror='alert(1)'>",
            "<svg onload=alert('XSS')>",
        ]

        for payload in xss_payloads:
            data = {"phone_number": "+923001234567", "password": payload}
            response = api_client.post("/api/v1/auth/login/", data, format="json")
            # Should reject XSS payloads
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
            ]

    def test_xss_in_email_sanitized(self, api_client):
        """XSS payloads in email should be sanitized."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror='alert(1)'>",
        ]

        for payload in xss_payloads:
            data = {"email": payload}
            response = api_client.post(
                "/api/v1/auth/forgot-password/", data, format="json"
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
