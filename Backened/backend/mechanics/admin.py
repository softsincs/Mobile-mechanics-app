from django.contrib import admin

from .models import MechanicAvailability, MechanicDocument, MechanicJobPhoto, MechanicProfile, MechanicVacation


@admin.register(MechanicProfile)
class MechanicProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'years_experience', 'service_area_city', 'current_active_jobs', 'max_concurrent_jobs', 'is_approved', 'is_active', 'is_available']
    list_filter = ['is_approved', 'is_active', 'is_available', 'service_area_city']
    search_fields = ['user__phone_number', 'user__email', 'service_area_city', 'emergency_contact']


@admin.register(MechanicAvailability)
class MechanicAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['mechanic', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']


@admin.register(MechanicVacation)
class MechanicVacationAdmin(admin.ModelAdmin):
    list_display = ['mechanic', 'start_date', 'end_date', 'reason', 'is_active']
    list_filter = ['is_active', 'start_date', 'end_date']


@admin.register(MechanicDocument)
class MechanicDocumentAdmin(admin.ModelAdmin):
    list_display = ['mechanic', 'document_type', 'document_name', 'is_verified', 'expiry_date']
    list_filter = ['document_type', 'is_verified']
    search_fields = ['mechanic__user__phone_number', 'document_name']


@admin.register(MechanicJobPhoto)
class MechanicJobPhotoAdmin(admin.ModelAdmin):
    list_display = ['booking', 'mechanic', 'photo_type', 'created_at']
    list_filter = ['photo_type', 'created_at']
