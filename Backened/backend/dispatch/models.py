"""Dispatch app models for job assignment and mechanic matching."""
import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from bookings.models import Booking

User = get_user_model()


class JobOfferStatus(models.TextChoices):
    """Job offer status choices following SRS dispatch workflow."""
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'
    EXPIRED = 'EXPIRED', 'Expired'
    CANCELLED = 'CANCELLED', 'Cancelled'


class JobOffer(models.Model):
    """
    Represents a job offer sent to a mechanic for a booking.
    Follows SRS 4.3 Dispatch & Assignment System specification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='job_offers')
    mechanic = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_offers_received')
    
    # Offer tracking
    offered_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    response_time = models.FloatField(null=True, blank=True, help_text='Response time in seconds')
    
    # Status management
    status = models.CharField(
        max_length=20,
        choices=JobOfferStatus.choices,
        default=JobOfferStatus.PENDING,
        db_index=True
    )
    rejection_reason = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Reason for rejection if status is REJECTED'
    )
    
    # Scoring & matching
    matching_score = models.FloatField(
        default=0.0,
        help_text='Algorithm score used for ranking (0-100)'
    )
    proximity_score = models.FloatField(default=0.0, help_text='Proximity component (40% weight)')
    availability_score = models.FloatField(default=0.0, help_text='Availability component (25% weight)')
    specialization_score = models.FloatField(default=0.0, help_text='Specialization component (20% weight)')
    rating_score = models.FloatField(default=0.0, help_text='Rating component (10% weight)')
    performance_score = models.FloatField(default=0.0, help_text='Performance component (5% weight)')
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dispatch_joboffer'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['mechanic', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Job {self.booking.id} -> {self.mechanic.phone_number} ({self.status})"
    
    @property
    def is_expired(self):
        """Check if job offer has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_accepted(self):
        """Check if offer was accepted."""
        return self.status == JobOfferStatus.ACCEPTED
    
    def accept(self):
        """Accept the job offer and record response time."""
        if self.status != JobOfferStatus.PENDING:
            raise ValueError(f"Cannot accept offer with status {self.status}")
        
        self.response_time = (timezone.now() - self.offered_at).total_seconds()
        self.status = JobOfferStatus.ACCEPTED
        self.save(update_fields=['status', 'response_time', 'updated_at'])
    
    def reject(self, reason=''):
        """Reject the job offer."""
        if self.status != JobOfferStatus.PENDING:
            raise ValueError(f"Cannot reject offer with status {self.status}")
        
        self.response_time = (timezone.now() - self.offered_at).total_seconds()
        self.status = JobOfferStatus.REJECTED
        self.rejection_reason = reason
        self.save(update_fields=['status', 'response_time', 'rejection_reason', 'updated_at'])


class MechanicAssignmentHistory(models.Model):
    """
    Audit trail for mechanic assignment attempts per booking.
    Tracks the assignment algorithm results and fallback chain.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='assignment_history')
    
    # Round information
    assignment_round = models.IntegerField(default=1, help_text='Attempt number (1st, 2nd, 3rd choice, etc.)')
    
    # Ranking data
    available_mechanics_count = models.IntegerField(default=0, help_text='Total mechanics available in city')
    top_mechanics_considered = models.IntegerField(default=3, help_text='Number of top candidates evaluated')
    
    # Algorithm details
    algorithm_version = models.CharField(max_length=20, default='v1.0')
    algorithm_params = models.JSONField(default=dict, help_text='Algorithm weights and parameters used')
    
    # Result
    assigned_mechanic = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignment_history_received'
    )
    assignment_result = models.CharField(
        max_length=50,
        choices=[
            ('SUCCESS', 'Mechanic Assigned Successfully'),
            ('ACCEPTANCE_PENDING', 'Awaiting Mechanic Response'),
            ('REJECTION', 'Mechanic Rejected'),
            ('EXPIRY', 'Offer Expired'),
            ('NO_AVAILABLE_MECHANICS', 'No Available Mechanics'),
        ],
        default='ACCEPTANCE_PENDING'
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dispatch_mechanicassignmenthistory'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking', 'assignment_round']),
            models.Index(fields=['assigned_mechanic', '-created_at']),
        ]
    
    def __str__(self):
        return f"Assignment #{self.assignment_round} for Booking {self.booking.id}"
