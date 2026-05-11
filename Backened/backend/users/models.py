import uuid
import secrets
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator
from datetime import timedelta


def default_password_reset_expiry():
    return timezone.now() + timedelta(minutes=15)


def default_extended_token_expiry():
    return timezone.now() + timedelta(days=7)


def default_password_reset_token():
    return secrets.token_urlsafe(32)


class UserManager(BaseUserManager):
    """Custom user manager for User model."""
    
    def create_user(self, phone_number, email, password=None, **extra_fields):
        """Create a regular user."""
        if not phone_number:
            raise ValueError('Phone number is required')
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        """Create a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone_number, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with phone number as primary identifier."""
    
    # Phone regex: international format +XXXXXXXXXXX (10-15 digits)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Phone number must be in international format (+923001234567) with 10-15 digits.',
        code='invalid_phone'
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[phone_regex],
        help_text='International format: +923001234567'
    )
    email = models.EmailField(unique=True)
    
    # Verification status
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Rate limiting fields
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Profile fields
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone_number} ({self.email})"

    def get_full_name(self):
        """Return the user's full name, falling back to phone number."""
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full_name if full_name else self.phone_number

    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name or self.phone_number

    def is_account_locked(self):
        """Check if account is currently locked."""
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        return False
    
    def unlock_account(self):
        """Unlock the account and reset failed attempts."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save()
    
    def increment_failed_login(self):
        """Increment failed login counter and lock if needed."""
        from django.conf import settings
        
        self.failed_login_attempts += 1
        
        # Lock account if max attempts exceeded
        if self.failed_login_attempts >= settings.RATE_LIMIT_LOGIN_ATTEMPTS:
            self.account_locked_until = timezone.now() + timedelta(
                seconds=settings.RATE_LIMIT_BLOCK_DURATION
            )
        
        self.save()
    
    def reset_failed_login(self):
        """Reset failed login counter."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()


class OTPToken(models.Model):
    """OTP token for email/phone verification."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_tokens')
    code = models.CharField(max_length=6)  # 6-digit OTP
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('email_verification', 'Email Verification'),
            ('phone_verification', 'Phone Verification'),
            ('login', 'Login OTP'),
        ],
        default='login'
    )
    
    # Attempt tracking
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'users_otp_token'
        verbose_name = 'OTP Token'
        verbose_name_plural = 'OTP Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP {self.code} for {self.user.phone_number}"
    
    def is_expired(self):
        """Check if OTP has expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid (not expired and not used)."""
        return not self.is_expired() and not self.is_used
    
    def verify(self, code):
        """Verify OTP code."""
        from django.conf import settings
        
        if self.is_used:
            return False, 'OTP already used'
        
        if self.is_expired():
            return False, 'OTP expired'
        
        self.attempts += 1
        
        if self.attempts > settings.MAX_OTP_ATTEMPTS:
            return False, 'Maximum attempts exceeded'
        
        if self.code != code:
            self.save()
            return False, 'Invalid OTP'
        
        self.is_used = True
        self.save()
        return True, 'OTP verified'


class PasswordResetToken(models.Model):
    """Password reset token."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True, default=default_password_reset_token)
    is_used = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_password_reset_expiry)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users_password_reset_token'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reset token for {self.user.phone_number}"
    
    def is_valid(self):
        """Check if token is valid."""
        return not self.is_used and timezone.now() < self.expires_at


class UserSession(models.Model):
    """User session tracking."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_user_session'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-login_at']
    
    def __str__(self):
        return f"Session for {self.user.phone_number} from {self.ip_address}"


class ExtendedToken(models.Model):
    """Extended token model with expiry support."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extended_token')
    key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_extended_token_expiry)
    
    class Meta:
        db_table = 'users_extended_token'
        verbose_name = 'Extended Token'
        verbose_name_plural = 'Extended Tokens'
    
    def __str__(self):
        return f"Token for {self.user.phone_number}"
    
    def is_expired(self):
        """Check if token has expired."""
        return timezone.now() > self.expires_at


class SecurityLog(models.Model):
    """Security event logging."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_logs', null=True, blank=True)
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('login_success', 'Login Success'),
            ('login_failed', 'Login Failed'),
            ('password_changed', 'Password Changed'),
            ('otp_sent', 'OTP Sent'),
            ('otp_verified', 'OTP Verified'),
            ('account_locked', 'Account Locked'),
            ('account_unlocked', 'Account Unlocked'),
            ('suspicious_activity', 'Suspicious Activity'),
        ]
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    details = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_security_log'
        verbose_name = 'Security Log'
        verbose_name_plural = 'Security Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.user or 'Anonymous'} at {self.created_at}"
