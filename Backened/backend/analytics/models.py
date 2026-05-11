"""Analytics cache and daily dashboard metrics."""
import uuid

from django.db import models


class DashboardMetrics(models.Model):
    """Daily aggregated dashboard metrics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    total_bookings = models.IntegerField(default=0)
    completed_bookings = models.IntegerField(default=0)
    cancelled_bookings = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mechanic_payouts = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_customers = models.IntegerField(default=0)
    new_mechanics = models.IntegerField(default=0)
    active_customers = models.IntegerField(default=0)
    active_mechanics = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    customer_satisfaction_score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_dashboardmetrics'
        ordering = ['-date']

    def __str__(self):
        return f'Dashboard metrics for {self.date}'
