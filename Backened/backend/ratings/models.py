"""Ratings and reviews for completed bookings."""
import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from bookings.models import Booking, BookingStatus

User = get_user_model()


class BookingReview(models.Model):
    """Verified review submitted after a completed booking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_reviews')
    mechanic = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')

    service_rating = models.PositiveSmallIntegerField()
    mechanic_rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, default='')
    is_verified = models.BooleanField(default=False)

    reviewed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ratings_bookingreview'
        ordering = ['-reviewed_at']
        indexes = [
            models.Index(fields=['booking']),
            models.Index(fields=['customer', '-reviewed_at']),
            models.Index(fields=['mechanic', '-reviewed_at']),
            models.Index(fields=['is_verified', '-reviewed_at']),
        ]

    def __str__(self):
        return f'Review for booking {self.booking_id}'

    @property
    def overall_rating(self):
        return round((self.service_rating + self.mechanic_rating) / 2, 2)

    def mark_verified(self):
        self.is_verified = True
        self.save(update_fields=['is_verified', 'updated_at'])

    def save(self, *args, **kwargs):
        if self.booking_id and self.booking.status == BookingStatus.COMPLETED:
            self.is_verified = True
        super().save(*args, **kwargs)
