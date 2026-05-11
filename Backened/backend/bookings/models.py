"""Booking app models for MobileMechanic platform."""
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from services.models import Service

User = get_user_model()


class BookingStatus(models.TextChoices):
    """Booking status choices following SRS workflow."""
    PENDING_CONFIRMATION = 'PENDING_CONFIRMATION', 'Pending Confirmation'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    MECHANIC_ASSIGNED = 'MECHANIC_ASSIGNED', 'Mechanic Assigned'
    MECHANIC_ACCEPTED = 'MECHANIC_ACCEPTED', 'Mechanic Accepted'
    MECHANIC_REJECTED = 'MECHANIC_REJECTED', 'Mechanic Rejected'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    NO_SHOW = 'NO_SHOW', 'No Show'
    RATED = 'RATED', 'Rated'
    UNRATED = 'UNRATED', 'Unrated'


class PaymentMethod(models.TextChoices):
    """Payment method choices as per SRS."""
    JAZZCASH = 'JAZZCASH', 'JazzCash'
    EASYPAISA = 'EASYPAISA', 'Easypaisa'
    CARD = 'CARD', 'Credit/Debit Card'
    CASH = 'CASH', 'Cash on Completion'
    WALLET = 'WALLET', 'Wallet Balance'


class CancellationReason(models.TextChoices):
    """Booking cancellation reasons."""
    CUSTOMER_REQUEST = 'CUSTOMER_REQUEST', 'Customer Request'
    MECHANIC_CANCELLED = 'MECHANIC_CANCELLED', 'Mechanic Cancelled'
    SYSTEM_AUTO = 'SYSTEM_AUTO', 'System Auto-cancelled'
    PAYMENT_FAILED = 'PAYMENT_FAILED', 'Payment Failed'
    NO_MECHANIC_AVAILABLE = 'NO_MECHANIC_AVAILABLE', 'No Mechanic Available'
    OTHER = 'OTHER', 'Other Reason'


class CancelledBy(models.TextChoices):
    """Who cancelled the booking."""
    CUSTOMER = 'CUSTOMER', 'Customer'
    MECHANIC = 'MECHANIC', 'Mechanic'
    SYSTEM = 'SYSTEM', 'System'
    ADMIN = 'ADMIN', 'Admin'


class Booking(models.Model):
    """Main booking model encompassing the complete booking lifecycle."""
    
    # Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_as_customer')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='bookings')
    mechanic = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='bookings_as_mechanic',
        help_text='Assigned mechanic, can be null initially'
    )
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=BookingStatus.choices, 
        default=BookingStatus.PENDING_CONFIRMATION
    )
    
    # Location Information
    service_location = models.CharField(max_length=255, help_text='Address for service')
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Timing
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    estimated_duration = models.IntegerField(help_text='Duration in minutes')
    start_time = models.DateTimeField(null=True, blank=True, help_text='Actual start time')
    end_time = models.DateTimeField(null=True, blank=True, help_text='Actual end time')
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    surge_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('1.0'))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices, 
        default=PaymentMethod.CASH
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Cancellation
    cancellation_reason = models.CharField(
        max_length=50, 
        choices=CancellationReason.choices, 
        null=True, 
        blank=True
    )
    cancelled_by = models.CharField(
        max_length=20, 
        choices=CancelledBy.choices, 
        null=True, 
        blank=True
    )
    cancellation_date = models.DateTimeField(null=True, blank=True)
    cancellation_notes = models.TextField(blank=True, help_text='Reason details for cancellation')
    
    # Additional Information
    customer_notes = models.TextField(blank=True, help_text='Customer instructions/notes for the service')
    mechanic_notes = models.TextField(blank=True, help_text='Mechanic notes on completion')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['mechanic', 'status']),
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['city', 'scheduled_date']),
        ]
    
    def __str__(self):
        return f"Booking {self.id} - {self.service} by {self.customer} ({self.status})"
    
    def calculate_total_amount(self):
        """Calculate total booking amount including taxes and discounts."""
        subtotal = self.base_price * self.surge_multiplier
        subtotal_after_discount = subtotal - self.discount_amount
        total = subtotal_after_discount + self.tax_amount
        return total
    
    @property
    def is_cancellable(self):
        """Check if booking can still be cancelled."""
        non_cancellable_statuses = [
            BookingStatus.COMPLETED,
            BookingStatus.CANCELLED,
            BookingStatus.NO_SHOW,
        ]
        return self.status not in non_cancellable_statuses
    
    @property
    def can_be_confirmed(self):
        """Check if booking can be confirmed."""
        return self.status == BookingStatus.PENDING_CONFIRMATION


class BookingStatusHistory(models.Model):
    """Track status changes for audit and analytics."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_history')
    
    old_status = models.CharField(max_length=20, choices=BookingStatus.choices)
    new_status = models.CharField(max_length=20, choices=BookingStatus.choices)
    
    changed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        help_text='User who made the status change'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, help_text='Reason for status change')
    
    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['booking', 'changed_at']),
        ]
    
    def __str__(self):
        return f"{self.booking.id}: {self.old_status} → {self.new_status}"


class BookingAddOn(models.Model):
    """Optional add-ons for bookings (e.g., inspection, fluid replacement)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Service categories this add-on applies to
    applicable_services = models.ManyToManyField(Service, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BookingAddOnAssignment(models.Model):
    """Link between bookings and add-ons."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='add_ons')
    add_on = models.ForeignKey(BookingAddOn, on_delete=models.PROTECT, related_name='bookings')
    
    # Store price at time of booking (in case add-on price changes)
    price_at_booking = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_completed = models.BooleanField(default=False, help_text='Whether this add-on was performed')
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('booking', 'add_on')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.booking.id} + {self.add_on.name}"
