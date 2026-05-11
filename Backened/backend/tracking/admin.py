"""Admin interface for tracking app."""
from django.contrib import admin
from django.utils.html import format_html
from .models import MechanicLocation, LocationHistory, LocationAccuracy


@admin.register(MechanicLocation)
class MechanicLocationAdmin(admin.ModelAdmin):
    """Admin interface for current mechanic locations."""
    list_display = [
        'mechanic_phone',
        'booking_id_short',
        'coordinates_display',
        'accuracy_display',
        'speed_display',
        'eta_display',
        'sharing_status_badge',
        'last_updated'
    ]
    list_filter = ['is_sharing', 'last_updated']
    search_fields = ['mechanic__phone_number', 'booking__id']
    readonly_fields = [
        'id',
        'created_at',
        'last_updated',
        'location_json_display'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'mechanic', 'booking')
        }),
        ('Current Location', {
            'fields': (
                'latitude',
                'longitude',
                'location_json_display',
                'accuracy',
                'speed'
            )
        }),
        ('ETA Information', {
            'fields': (
                'estimated_time_arrival',
                'distance_to_destination'
            ),
            'classes': ('collapse',)
        }),
        ('Tracking Status', {
            'fields': ('is_sharing', 'last_pinged_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-last_updated']
    
    def mechanic_phone(self, obj):
        return obj.mechanic.phone_number
    mechanic_phone.short_description = 'Mechanic'
    
    def booking_id_short(self, obj):
        if obj.booking:
            return str(obj.booking.id)[:8]
        return '—'
    booking_id_short.short_description = 'Booking'
    
    def coordinates_display(self, obj):
        return f"{obj.latitude:.4f}, {obj.longitude:.4f}"
    coordinates_display.short_description = 'Coordinates'
    
    def accuracy_display(self, obj):
        return f"{obj.accuracy}m"
    accuracy_display.short_description = 'Accuracy'
    
    def speed_display(self, obj):
        return f"{obj.speed:.1f} km/h"
    speed_display.short_description = 'Speed'
    
    def eta_display(self, obj):
        if obj.estimated_time_arrival:
            return obj.estimated_time_arrival.strftime('%H:%M:%S')
        return '—'
    eta_display.short_description = 'ETA'
    
    def sharing_status_badge(self, obj):
        color = '#28a745' if obj.is_sharing else '#6c757d'
        text = 'Sharing' if obj.is_sharing else 'Not Sharing'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            text
        )
    sharing_status_badge.short_description = 'Status'
    
    def location_json_display(self, obj):
        if obj.latitude and obj.longitude:
            return f"({obj.latitude:.4f}, {obj.longitude:.4f})"
        return '—'
    location_json_display.short_description = 'Coordinates'


@admin.register(LocationHistory)
class LocationHistoryAdmin(admin.ModelAdmin):
    """Admin interface for historical location data."""
    list_display = [
        'mechanic_phone',
        'booking_id_short',
        'event_type_badge',
        'coordinates_display',
        'speed_display',
        'accuracy_display',
        'created_at'
    ]
    list_filter = ['event_type', 'created_at', 'mechanic']
    search_fields = ['mechanic__phone_number', 'booking__id']
    readonly_fields = [
        'id',
        'created_at',
        'location_json_display'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'mechanic', 'booking')
        }),
        ('Location Data', {
            'fields': (
                'latitude',
                'longitude',
                'location_json_display',
                'accuracy',
                'speed'
            )
        }),
        ('Event Information', {
            'fields': ('event_type', 'estimated_time_arrival')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    ordering = ['-created_at']
    
    def mechanic_phone(self, obj):
        return obj.mechanic.phone_number
    mechanic_phone.short_description = 'Mechanic'
    
    def booking_id_short(self, obj):
        return str(obj.booking.id)[:8]
    booking_id_short.short_description = 'Booking'
    
    def event_type_badge(self, obj):
        colors = {
            'DEPARTURE': '#0275d8',
            'UPDATE': '#6c757d',
            'ARRIVAL': '#28a745',
            'PAUSE': '#ffc107',
            'RESUME': '#17a2b8',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.event_type, '#000'),
            obj.get_event_type_display()
        )
    event_type_badge.short_description = 'Event'
    
    def coordinates_display(self, obj):
        return f"{obj.latitude:.4f}, {obj.longitude:.4f}"
    coordinates_display.short_description = 'Coordinates'
    
    def speed_display(self, obj):
        return f"{obj.speed:.1f} km/h"
    speed_display.short_description = 'Speed'
    
    def accuracy_display(self, obj):
        return f"{obj.accuracy}m"
    accuracy_display.short_description = 'Accuracy'
    
    def location_json_display(self, obj):
        return f"({obj.latitude:.4f}, {obj.longitude:.4f})"
    location_json_display.short_description = 'Coordinates'


@admin.register(LocationAccuracy)
class LocationAccuracyAdmin(admin.ModelAdmin):
    """Admin interface for location accuracy metrics."""
    list_display = [
        'mechanic_phone',
        'provider_badge',
        'horizontal_accuracy_display',
        'vertical_accuracy_display',
        'satellites_display',
        'mock_provider_badge',
        'recorded_at'
    ]
    list_filter = ['provider', 'is_from_mock_provider', 'recorded_at']
    search_fields = ['mechanic__phone_number']
    readonly_fields = ['id', 'recorded_at']
    
    fieldsets = (
        ('Mechanic', {
            'fields': ('id', 'mechanic')
        }),
        ('Provider Information', {
            'fields': ('provider', 'is_from_mock_provider')
        }),
        ('Accuracy Metrics', {
            'fields': (
                'horizontal_accuracy',
                'vertical_accuracy',
                'bearing_accuracy',
                'satellites_used'
            )
        }),
        ('Timestamps', {
            'fields': ('recorded_at',)
        }),
    )
    
    ordering = ['-recorded_at']
    
    def mechanic_phone(self, obj):
        return obj.mechanic.phone_number
    mechanic_phone.short_description = 'Mechanic'
    
    def provider_badge(self, obj):
        colors = {
            'GPS': '#0275d8',
            'NETWORK': '#6c757d',
            'FUSED': '#28a745',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.provider, '#000'),
            obj.get_provider_display()
        )
    provider_badge.short_description = 'Provider'
    
    def horizontal_accuracy_display(self, obj):
        return f"{obj.horizontal_accuracy:.1f}m"
    horizontal_accuracy_display.short_description = 'Horizontal'
    
    def vertical_accuracy_display(self, obj):
        if obj.vertical_accuracy:
            return f"{obj.vertical_accuracy:.1f}m"
        return '—'
    vertical_accuracy_display.short_description = 'Vertical'
    
    def satellites_display(self, obj):
        if obj.satellites_used:
            return f"{obj.satellites_used} satellites"
        return '—'
    satellites_display.short_description = 'Satellites'
    
    def mock_provider_badge(self, obj):
        if obj.is_from_mock_provider:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">MOCK</span>'
            )
        return '✓'
    mock_provider_badge.short_description = 'Authentic'
