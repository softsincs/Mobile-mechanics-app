from django.conf import settings
from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    icon_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    estimated_duration = models.PositiveIntegerField(help_text='Estimated duration in minutes')
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ServicePrice(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='prices')
    city = models.CharField(max_length=150)
    peak_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    off_peak_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    weekend_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (('service', 'city', 'valid_from'),)

    def __str__(self):
        return f"{self.service.name} - {self.city}"


class ServiceAvailability(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='availability_slots')
    city = models.CharField(max_length=150)
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    effective_from = models.DateTimeField(null=True, blank=True)
    effective_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (('service', 'city'),)

    def __str__(self):
        return f"{self.service.name} in {self.city}"


class MechanicServiceSpecialty(models.Model):
    PROFICIENCY_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('EXPERT', 'Expert'),
    ]

    mechanic = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_specialties')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='mechanic_specialties')
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES)
    years_experience = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('mechanic', 'service'),)

    def __str__(self):
        return f"{self.mechanic} - {self.service.name} ({self.proficiency_level})"


class ServicePromotion(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='promotions', null=True, blank=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_booking_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def calculate_discount(self, amount):
        from decimal import Decimal

        amount = Decimal(str(amount))
        if self.discount_type == 'PERCENTAGE':
            discount = amount * (self.discount_value / Decimal('100'))
        else:
            discount = self.discount_value

        if self.max_discount_amount is not None:
            discount = min(discount, self.max_discount_amount)

        return max(Decimal('0'), discount)
