"""
Business Logic Services for Authentication Module

This module contains services for handling complex business logic operations
including email sending, OTP generation, rate limiting, and password reset.

Services:
- EmailService: Sends OTP and password reset emails
- OTPService: Generates and manages OTP codes
- PasswordResetService: Generates password reset tokens
- RateLimitService: Checks and manages rate limits
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
import secrets
import logging

from .models import User, OTPToken, PasswordResetToken


logger = logging.getLogger(__name__)


# =========================================
# � UTILITY FUNCTIONS
# =========================================

def validate_refresh_token(refresh_token):
    """
    Validate refresh token and return user ID.
    
    Args:
        refresh_token: Token string to validate
        
    Returns:
        user_id if valid, raises ValueError otherwise
    """
    from rest_framework.authtoken.models import Token
    try:
        token = Token.objects.get(key=refresh_token)
        return str(token.user.id)
    except Token.DoesNotExist:
        raise ValueError("Invalid refresh token")


# =========================================
# �📧 EMAIL SERVICE
# =========================================

class EmailService:
    """
    Handles email sending for authentication flows.
    Sends OTP codes and password reset links.
    """

    @staticmethod
    def send_otp_email(user, otp_code):
        """
        Send OTP code to user's email.
        
        Args:
            user: User instance
            otp_code: 6-digit OTP code as string
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = "Your One-Time Password (OTP)"
            message = f"""
Hello {user.first_name or user.email},

Your One-Time Password (OTP) is: {otp_code}

This code will expire in 5 minutes.
Do not share this code with anyone.

If you didn't request this code, please ignore this email.

Best regards,
Mobile Mechanic Team
            """.strip()

            html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
    <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 500px; margin: 0 auto;">
        <h2>Your One-Time Password (OTP)</h2>
        <p>Hello {user.first_name or user.email},</p>
        <p>Your One-Time Password is:</p>
        <div style="background-color: #007bff; color: white; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; border-radius: 8px; letter-spacing: 5px;">
            {otp_code}
        </div>
        <p style="color: #666;">This code will expire in <strong>5 minutes</strong>.</p>
        <p style="color: #d9534f; font-weight: bold;">⚠️ Do not share this code with anyone.</p>
        <p style="color: #666;">If you didn't request this code, please ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
        <p style="color: #999; font-size: 12px;">Mobile Mechanic Team</p>
    </div>
</body>
</html>
            """.strip()

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"OTP email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send OTP email to {user.email}: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(user, reset_token):
        """
        Send password reset link to user's email.
        
        Args:
            user: User instance
            reset_token: Password reset token string
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

            subject = "Reset Your Password"
            message = f"""
Hello {user.first_name or user.email},

Click the link below to reset your password:

{reset_link}

This link will expire in 15 minutes.
If you didn't request this, please ignore this email.

Best regards,
Mobile Mechanic Team
            """.strip()

            html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
    <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 500px; margin: 0 auto;">
        <h2>Reset Your Password</h2>
        <p>Hello {user.first_name or user.email},</p>
        <p>Click the button below to reset your password:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold;">
                Reset Password
            </a>
        </div>
        <p style="color: #666;">Or copy this link: <a href="{reset_link}">{reset_link}</a></p>
        <p style="color: #d9534f; font-weight: bold;">⚠️ This link will expire in 15 minutes.</p>
        <p style="color: #666;">If you didn't request this, please ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
        <p style="color: #999; font-size: 12px;">Mobile Mechanic Team</p>
    </div>
</body>
</html>
            """.strip()

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Password reset email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return False

    @staticmethod
    def send_reset_email(user, reset_token):
        """
        Alias for send_password_reset_email for compatibility.
        
        Args:
            user: User instance
            reset_token: Password reset token string
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        return EmailService.send_password_reset_email(user, reset_token)


# =========================================
# 🔢 OTP SERVICE
# =========================================

class OTPService:
    """
    Handles OTP generation and management.
    """

    @staticmethod
    def generate_otp(length=6):
        """
        Generate a random OTP code.
        
        Args:
            length: Length of OTP code (default 6 digits)
            
        Returns:
            str: OTP code as string
        """
        return f"{secrets.randbelow(10**length):0{length}d}"

    @staticmethod
    def create_otp_token(user, purpose="email_verification", expiry_minutes=5):
        """
        Create an OTP token for the user.
        
        Args:
            user: User instance
            purpose: OTP purpose (email_verification, phone_verification, login)
            expiry_minutes: Token expiry time in minutes
            
        Returns:
            tuple: (OTPToken instance, otp_code)
        """
        otp_code = OTPService.generate_otp()

        otp = OTPToken.objects.create(
            user=user,
            code=otp_code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
        )

        return otp, otp_code

    @staticmethod
    def verify_otp(user, otp_code):
        """
        Verify OTP code for user.
        
        Args:
            user: User instance
            otp_code: OTP code to verify
            
        Returns:
            tuple: (is_valid, otp_instance, error_message)
        """
        otp = (
            OTPToken.objects.filter(user=user, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return False, None, "No OTP found. Please request a new one."

        is_valid, error_msg = otp.verify(otp_code)
        if is_valid:
            return True, otp, None
        else:
            return False, otp, error_msg


# =========================================
# 🔐 PASSWORD RESET SERVICE
# =========================================

class PasswordResetService:
    """
    Handles password reset token generation and validation.
    """

    @staticmethod
    def generate_reset_token(user, expiry_minutes=15):
        """
        Generate a password reset token for the user.
        
        Args:
            user: User instance
            expiry_minutes: Token expiry time in minutes
            
        Returns:
            tuple: (PasswordResetToken instance, token_string)
        """
        token = secrets.token_urlsafe(32)

        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
        )

        return reset_token, token

    @staticmethod
    def validate_reset_token(token_string):
        """
        Validate a password reset token.
        
        Args:
            token_string: Token string to validate
            
        Returns:
            tuple: (is_valid, reset_token_instance, error_message)
        """
        try:
            reset_token = PasswordResetToken.objects.get(token=token_string)
        except PasswordResetToken.DoesNotExist:
            return False, None, "Invalid reset token"

        if not reset_token.is_valid():
            return False, reset_token, "Token has expired or already used"

        return True, reset_token, None


# =========================================
# 🚫 RATE LIMIT SERVICE
# =========================================

def validate_refresh_token(refresh_token):
    """
    Validate refresh token and return user ID.
    
    Args:
        refresh_token: Token string to validate
        
    Returns:
        user_id if valid, raises ValidationError otherwise
    """
    try:
        from rest_framework.authtoken.models import Token
        token = Token.objects.get(key=refresh_token)
        return token.user.id
    except Token.DoesNotExist:
        raise ValueError("Invalid refresh token")



class RateLimitService:
    """
    Handles rate limiting using cache.
    """

    @staticmethod
    def check_rate_limit(key, max_attempts, window_seconds):
        """
        Check if action is within rate limit.
        
        Args:
            key: Unique key for rate limiting (e.g., "login_user_123")
            max_attempts: Maximum attempts allowed in time window
            window_seconds: Time window in seconds
            
        Returns:
            tuple: (is_allowed, remaining_attempts, retry_after_seconds)
        """
        attempts = cache.get(key, 0)

        if attempts >= max_attempts:
            ttl = cache.ttl(key)
            return False, 0, ttl or window_seconds

        return True, max_attempts - attempts - 1, None

    @staticmethod
    def increment_rate_limit(key, window_seconds):
        """
        Increment rate limit counter.
        
        Args:
            key: Unique key for rate limiting
            window_seconds: Time window in seconds
        """
        attempts = cache.get(key, 0)
        cache.set(key, attempts + 1, window_seconds)

    @staticmethod
    def reset_rate_limit(key):
        """
        Reset rate limit counter.
        
        Args:
            key: Unique key for rate limiting
        """
        cache.delete(key)

    @staticmethod
    def check_otp_rate_limit(user):
        """
        Check OTP request rate limit for user.
        
        Args:
            user: User instance
            
        Returns:
            tuple: (is_allowed, seconds_until_retry)
        """
        cache_key = f"otp_request_{user.id}"
        is_allowed, _, retry_after = RateLimitService.check_rate_limit(
            cache_key, max_attempts=1, window_seconds=60
        )
        return is_allowed, retry_after

    @staticmethod
    def check_password_reset_rate_limit(user):
        """
        Check password reset request rate limit for user.
        
        Args:
            user: User instance
            
        Returns:
            tuple: (is_allowed, seconds_until_retry)
        """
        cache_key = f"password_reset_{user.id}"
        is_allowed, _, retry_after = RateLimitService.check_rate_limit(
            cache_key, max_attempts=1, window_seconds=300
        )
        return is_allowed, retry_after

    @staticmethod
    def check_login_rate_limit(identifier):
        """
        Check login attempt rate limit for phone/email.
        
        Args:
            identifier: Phone or email address
            
        Returns:
            tuple: (is_allowed, retry_after_seconds)
        """
        cache_key = f"login_attempts_{identifier}"
        is_allowed, _, retry_after = RateLimitService.check_rate_limit(
            cache_key, max_attempts=5, window_seconds=900  # 15 minutes
        )
        return is_allowed, retry_after
