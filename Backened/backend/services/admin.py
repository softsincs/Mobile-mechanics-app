from django.contrib import admin
from .models import (
    MechanicServiceSpecialty,
    Service,
    ServiceAvailability,
    ServiceCategory,
    ServicePrice,
    ServicePromotion,
)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at')
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'base_price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)


@admin.register(ServicePrice)
class ServicePriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'city', 'peak_multiplier', 'valid_from')
    list_filter = ('city',)


@admin.register(ServiceAvailability)
class ServiceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'city', 'is_available')
    list_filter = ('city', 'is_available')


@admin.register(MechanicServiceSpecialty)
class MechanicServiceSpecialtyAdmin(admin.ModelAdmin):
    list_display = ('id', 'mechanic', 'service', 'proficiency_level', 'years_experience', 'is_active')
    list_filter = ('proficiency_level', 'is_active')


@admin.register(ServicePromotion)
class ServicePromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'title', 'discount_type', 'discount_value', 'is_active')
    list_filter = ('discount_type', 'is_active')
