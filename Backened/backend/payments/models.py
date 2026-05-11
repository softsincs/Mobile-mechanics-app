"""Models for payments app."""
import uuid
from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from bookings.models import Booking

User = get_user_model()


class PaymentMethod(models.TextChoices):
    """Available payment methods."""
    JAZZCASH = 'JAZZCASH', 'JazzCash'
    EASYPAISA = 'EASYPAISA', 'Easypaisa'
    STRIPE = 'STRIPE', 'Stripe'
    CASH = 'CASH', 'Cash on Completion'
    WALLET = 'WALLET', 'Wallet Balance'


class PaymentStatus(models.TextChoices):
    """Payment status states."""
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'
    REFUNDED = 'REFUNDED', 'Refunded'


class Payment(models.Model):
    """Payment record for booking."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    
    # Amount info
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='PKR')
    
    # Payment method
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Gateway integration
    gateway_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True, default=dict)
    
    # Retry logic
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['gateway_transaction_id']),
        ]
    
    def __str__(self):
        return f"Payment {self.id} - {self.booking.service.name} ({self.status})"
    
    @property
    def is_successful(self):
        """Check if payment was successful."""
        return self.status == PaymentStatus.SUCCESS
    
    @property
    def is_failed(self):
        """Check if payment failed."""
        return self.status == PaymentStatus.FAILED
    
    @property
    def can_retry(self):
        """Check if payment can be retried."""
        return self.is_failed and self.retry_count < self.max_retries
    
    def mark_success(self):
        """Mark payment as successful."""
        self.status = PaymentStatus.SUCCESS
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self):
        """Mark payment as failed."""
        self.status = PaymentStatus.FAILED
        self.save()
    
    def mark_processing(self, gateway_txn_id=None):
        """Mark payment as processing."""
        self.status = PaymentStatus.PROCESSING
        if gateway_txn_id:
            self.gateway_transaction_id = gateway_txn_id
        self.save()


class Invoice(models.Model):
    """Invoice record for completed payment."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='invoice')
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateTimeField(auto_now_add=True)
    
    # Amount breakdown
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # PDF storage
    pdf_path = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    # Status
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Additional notes
    notes = models.TextField(blank=True, default='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['booking']),
            models.Index(fields=['is_sent', '-invoice_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    def generate_invoice_number(self):
        """Generate unique invoice number."""
        from django.utils import timezone
        today = timezone.now().date()
        count = Invoice.objects.filter(invoice_date__date=today).count() + 1
        return f"INV-{today.strftime('%Y%m%d')}-{count:04d}"


class PaymentRetry(models.Model):
    """Track payment retry attempts."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='retries')
    
    attempt_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    error_message = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', '-created_at']),
        ]
    
    def __str__(self):
        return f"Retry #{self.attempt_number} for Payment {self.payment.id}"
