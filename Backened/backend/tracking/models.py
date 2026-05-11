"""Tracking app models for real-time location and ETA management."""
import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from bookings.models import Booking

User = get_user_model()


class MechanicLocation(models.Model):
    """
    Real-time mechanic location data.
    Updated every 5 seconds while mechanic is in transit.
    Follows SRS 4.4 Real-Time Tracking specification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mechanic = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='current_location'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mechanic_locations'
    )
    
    # Geographic data
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_json = models.JSONField(
        default=dict,
        blank=True,
        help_text='JSON storage for geographic point: {"lat": x, "lng": y}'
    )
    accuracy = models.IntegerField(
        default=10,
        help_text='GPS accuracy in meters'
    )
    speed = models.FloatField(
        default=0.0,
        help_text='Current speed in km/h'
    )
    
    # ETA calculation
    estimated_time_arrival = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Calculated ETA to service location'
    )
    distance_to_destination = models.FloatField(
        default=0.0,
        help_text='Distance to booking location in km'
    )
    
    # Tracking metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Sharing status
    is_sharing = models.BooleanField(default=False, help_text='Whether mechanic is actively sharing location')
    last_pinged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time location was received (for health checks)'
    )
    
    class Meta:
        db_table = 'tracking_mechaniclocation'
        indexes = [
            models.Index(fields=['mechanic', 'booking']),
            models.Index(fields=['-last_updated']),
        ]
    
    def __str__(self):
        return f"{self.mechanic.phone_number} - {self.latitude}, {self.longitude}"
    
    @property
    def is_stale(self):
        """Check if location data is older than 30 seconds."""
        time_diff = timezone.now() - self.last_updated
        return time_diff.total_seconds() > 30
    
    def update_location(self, latitude, longitude, accuracy=10, speed=0.0):
        """Update mechanic location and recalculate ETA."""
        self.latitude = latitude
        self.longitude = longitude
        self.location_json = {'lat': latitude, 'lng': longitude}
        self.accuracy = accuracy
        self.speed = speed
        self.last_pinged_at = timezone.now()
        self.save()


class LocationHistory(models.Model):
    """
    Historical location data for analytics, disputes, and audit trails.
    Stores all location updates with timestamps for track reconstruction.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mechanic = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='location_history'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='location_history'
    )
    
    # Geographic data
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_json = models.JSONField(
        default=dict,
        blank=True,
        help_text='JSON storage for geographic point: {"lat": x, "lng": y}'
    )
    accuracy = models.IntegerField(default=10, help_text='GPS accuracy in meters')
    speed = models.FloatField(default=0.0, help_text='Speed in km/h at this point')
    
    # ETA at this timestamp
    estimated_time_arrival = models.DateTimeField(
        null=True,
        blank=True,
        help_text='ETA calculated at this location update'
    )
    
    # Context
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('DEPARTURE', 'Mechanic Started Travel'),
            ('UPDATE', 'Periodic Location Update'),
            ('ARRIVAL', 'Mechanic Arrived at Location'),
            ('PAUSE', 'Mechanic Paused'),
            ('RESUME', 'Mechanic Resumed Travel'),
        ],
        default='UPDATE'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tracking_locationhistory'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking', '-created_at']),
            models.Index(fields=['mechanic', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.mechanic.phone_number} @ {self.created_at.isoformat()}"


class LocationAccuracy(models.Model):
    """
    Tracks location provider accuracy and quality metrics.
    Used to debug GPS/location issues and monitor data quality.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mechanic = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='location_accuracy_logs'
    )
    
    # Provider info
    provider = models.CharField(
        max_length=50,
        choices=[
            ('GPS', 'GPS'),
            ('NETWORK', 'Network-based'),
            ('FUSED', 'Fused Location Provider'),
        ],
        default='FUSED'
    )
    
    # Accuracy metrics
    horizontal_accuracy = models.FloatField(help_text='Horizontal accuracy in meters')
    vertical_accuracy = models.FloatField(null=True, blank=True, help_text='Vertical accuracy (elevation) in meters')
    bearing_accuracy = models.FloatField(null=True, blank=True, help_text='Bearing accuracy in degrees')
    
    # Quality flags
    is_from_mock_provider = models.BooleanField(default=False, help_text='Flag for mock location detection')
    satellites_used = models.IntegerField(null=True, blank=True, help_text='Number of GPS satellites used')
    
    # Recording
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tracking_locationaccuracy'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['mechanic', '-recorded_at']),
        ]
    
    def __str__(self):
        return f"{self.mechanic.phone_number} - {self.provider} ({self.horizontal_accuracy}m)"
