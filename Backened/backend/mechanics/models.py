"""Mechanic onboarding, availability, and job support models."""
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from bookings.models import Booking, BookingStatus, BookingStatusHistory

User = get_user_model()


class MechanicProfile(models.Model):
    """Profile and workload data for a mechanic user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mechanic_profile')
    years_experience = models.PositiveIntegerField(default=0)
    emergency_contact = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    service_area_city = models.CharField(max_length=150, blank=True)
    service_radius_km = models.PositiveIntegerField(default=25)
    max_concurrent_jobs = models.PositiveIntegerField(default=3)
    current_active_jobs = models.PositiveIntegerField(default=0)
    current_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    cancellation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mechanics_profile'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone_number} mechanic profile'

    def can_accept_more_jobs(self):
        return self.is_active and self.current_active_jobs < self.max_concurrent_jobs


class MechanicAvailability(models.Model):
    """Weekly availability window for a mechanic."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mechanic = models.ForeignKey(MechanicProfile, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mechanics_availability'
        ordering = ['day_of_week', 'start_time']
        unique_together = ('mechanic', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f'{self.mechanic.user.phone_number} - {self.day_of_week} {self.start_time}'


class MechanicVacation(models.Model):
    """Temporary unavailability window."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mechanic = models.ForeignKey(MechanicProfile, on_delete=models.CASCADE, related_name='vacations')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mechanics_vacation'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.mechanic.user.phone_number} vacation {self.start_date} - {self.end_date}'


class MechanicDocument(models.Model):
    """Document verification record for a mechanic."""

    DOCUMENT_TYPES = [
        ('CNIC', 'CNIC'),
        ('LICENSE', 'License'),
        ('CERTIFICATION', 'Certification'),
        ('INSURANCE', 'Insurance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mechanic = models.ForeignKey(MechanicProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='mechanic_docs/', blank=True, null=True)
    document_name = models.CharField(max_length=150, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mechanics_document'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.mechanic.user.phone_number} {self.document_type}'


class MechanicJobPhoto(models.Model):
    """Before/after photos uploaded for a mechanic job."""

    PHOTO_TYPES = [
        ('BEFORE', 'Before'),
        ('AFTER', 'After'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='job_photos')
    mechanic = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_photos_uploaded')
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPES, default='BEFORE')
    image_url = models.URLField(blank=True)
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mechanics_jobphoto'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking', 'photo_type']),
            models.Index(fields=['mechanic', '-created_at']),
        ]

    def __str__(self):
        return f'{self.booking_id} {self.photo_type}'
