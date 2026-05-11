"""Notification models for in-app delivery and preferences."""
import uuid
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class NotificationChannel(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    PUSH = 'PUSH', 'Push'
    IN_APP = 'IN_APP', 'In App'


class NotificationType(models.TextChoices):
    SYSTEM = 'SYSTEM', 'System'
    BOOKING = 'BOOKING', 'Booking'
    DISPATCH = 'DISPATCH', 'Dispatch'
    PAYMENT = 'PAYMENT', 'Payment'
    REVIEW = 'REVIEW', 'Review'


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices, default=NotificationChannel.IN_APP)
    metadata = models.JSONField(default=dict, blank=True)
    related_object_id = models.CharField(max_length=64, blank=True, default='')
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
            models.Index(fields=['channel', '-created_at']),
        ]

    def __str__(self):
        return f'{self.title} -> {self.user.phone_number}'

    def mark_read(self):
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])

    def mark_sent(self):
        if not self.is_sent:
            from django.utils import timezone
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=['is_sent', 'sent_at', 'updated_at'])


class NotificationPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications_preference'

    def __str__(self):
        return f'Preferences for {self.user.phone_number}'
