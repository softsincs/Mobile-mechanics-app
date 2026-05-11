"""Django admin configuration for bookings app."""
from django.contrib import admin
from .models import Booking, BookingStatusHistory, BookingAddOn, BookingAddOnAssignment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'service', 'mechanic', 'status', 'scheduled_date', 'total_amount', 'payment_method']
    list_filter = ['status', 'payment_method', 'city', 'scheduled_date', 'created_at']
    search_fields = ['id', 'customer__email', 'customer__phone_number', 'service__name', 'mechanic__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Booking ID', {
            'fields': ('id',)
        }),
        ('Participants', {
            'fields': ('customer', 'service', 'mechanic')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Location', {
            'fields': ('service_location', 'city', 'latitude', 'longitude')
        }),
        ('Timing', {
            'fields': ('scheduled_date', 'scheduled_time', 'estimated_duration', 'start_time', 'end_time')
        }),
        ('Pricing', {
            'fields': ('base_price', 'surge_multiplier', 'discount_percentage', 'discount_amount', 'tax_amount', 'total_amount', 'paid_amount', 'payment_method')
        }),
        ('Cancellation', {
            'fields': ('cancellation_reason', 'cancelled_by', 'cancellation_date', 'cancellation_notes'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'mechanic_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-created_at']


@admin.register(BookingStatusHistory)
class BookingStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['new_status', 'changed_at']
    search_fields = ['booking__id', 'changed_by__email']
    readonly_fields = ['id', 'booking', 'changed_at']
    
    def has_add_permission(self, request):
        """Don't allow manual addition of status history."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow deletion of status history."""
        return False


@admin.register(BookingAddOn)
class BookingAddOnAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['applicable_services']


@admin.register(BookingAddOnAssignment)
class BookingAddOnAssignmentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'add_on', 'price_at_booking', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at']
    search_fields = ['booking__id', 'add_on__name']
    readonly_fields = ['id', 'created_at', 'completed_at']
