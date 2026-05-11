"""Admin interface for dispatch app."""
from django.contrib import admin
from django.utils.html import format_html
from .models import JobOffer, MechanicAssignmentHistory


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    """Admin interface for job offers."""
    list_display = [
        'id_short',
        'booking_id_short',
        'mechanic_phone',
        'status_badge',
        'offered_at',
        'response_time_display',
        'matching_score_display'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'booking__id', 'mechanic__phone_number']
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'offered_at',
        'response_time',
        'score_breakdown'
    ]
    
    fieldsets = (
        ('Offer Details', {
            'fields': ('id', 'booking', 'mechanic')
        }),
        ('Timeline', {
            'fields': ('offered_at', 'expires_at', 'response_time', 'created_at', 'updated_at')
        }),
        ('Status', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Matching Scores', {
            'fields': ('matching_score', 'score_breakdown'),
            'classes': ('collapse',),
            'description': 'Algorithm component breakdown'
        }),
    )
    
    ordering = ['-created_at']
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'Offer ID'
    
    def booking_id_short(self, obj):
        return str(obj.booking.id)[:8]
    booking_id_short.short_description = 'Booking'
    
    def mechanic_phone(self, obj):
        return obj.mechanic.phone_number
    mechanic_phone.short_description = 'Mechanic'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFA500',
            'ACCEPTED': '#28a745',
            'REJECTED': '#dc3545',
            'EXPIRED': '#6c757d',
            'CANCELLED': '#666',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def response_time_display(self, obj):
        if obj.response_time:
            return f"{obj.response_time:.1f}s"
        return '—'
    response_time_display.short_description = 'Response Time'
    
    def matching_score_display(self, obj):
        return f"{obj.matching_score:.1f}"
    matching_score_display.short_description = 'Score'
    
    def score_breakdown(self, obj):
        return f"""
        Proximity: {obj.proximity_score:.1f} (40%)
        Availability: {obj.availability_score:.1f} (25%)
        Specialization: {obj.specialization_score:.1f} (20%)
        Rating: {obj.rating_score:.1f} (10%)
        Performance: {obj.performance_score:.1f} (5%)
        Total: {obj.matching_score:.1f}
        """
    score_breakdown.short_description = 'Score Breakdown'


@admin.register(MechanicAssignmentHistory)
class MechanicAssignmentHistoryAdmin(admin.ModelAdmin):
    """Admin interface for assignment history and audit trail."""
    list_display = [
        'id_short',
        'booking_id_short',
        'assignment_round',
        'assigned_mechanic_phone',
        'result_badge',
        'available_mechanics',
        'created_at'
    ]
    list_filter = ['assignment_result', 'assignment_round', 'created_at']
    search_fields = ['id', 'booking__id', 'assigned_mechanic__phone_number']
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'algorithm_params_display'
    ]
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('id', 'booking', 'assignment_round')
        }),
        ('Mechanic Information', {
            'fields': ('assigned_mechanic', 'available_mechanics_count', 'top_mechanics_considered')
        }),
        ('Algorithm', {
            'fields': ('algorithm_version', 'algorithm_params_display'),
            'classes': ('collapse',)
        }),
        ('Result', {
            'fields': ('assignment_result',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'Assignment ID'
    
    def booking_id_short(self, obj):
        return str(obj.booking.id)[:8]
    booking_id_short.short_description = 'Booking'
    
    def assigned_mechanic_phone(self, obj):
        return obj.assigned_mechanic.phone_number if obj.assigned_mechanic else '—'
    assigned_mechanic_phone.short_description = 'Mechanic'
    
    def result_badge(self, obj):
        colors = {
            'SUCCESS': '#28a745',
            'ACCEPTANCE_PENDING': '#FFA500',
            'REJECTION': '#dc3545',
            'EXPIRY': '#6c757d',
            'NO_AVAILABLE_MECHANICS': '#e83e8c',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.assignment_result, '#000'),
            obj.get_assignment_result_display()
        )
    result_badge.short_description = 'Result'
    
    def available_mechanics(self, obj):
        return obj.available_mechanics_count
    available_mechanics.short_description = 'Available'
    
    def algorithm_params_display(self, obj):
        params = obj.algorithm_params or {}
        lines = [f"{k}: {v}" for k, v in params.items()]
        return '\n'.join(lines) if lines else 'No parameters'
    algorithm_params_display.short_description = 'Algorithm Parameters'
