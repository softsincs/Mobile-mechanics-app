from django.contrib import admin

from .models import BookingReview


@admin.register(BookingReview)
class BookingReviewAdmin(admin.ModelAdmin):
    list_display = ['id_short', 'booking_short', 'customer_email', 'mechanic_phone', 'service_rating', 'mechanic_rating', 'is_verified', 'reviewed_at']
    list_filter = ['is_verified', 'service_rating', 'mechanic_rating', 'reviewed_at']
    search_fields = ['booking__id', 'customer__email', 'mechanic__phone_number', 'comment']
    readonly_fields = ['id', 'reviewed_at', 'updated_at', 'overall_rating_display']
    fieldsets = (
        ('Review', {'fields': ('id', 'booking', 'customer', 'mechanic', 'service_rating', 'mechanic_rating', 'comment')}),
        ('Status', {'fields': ('is_verified', 'overall_rating_display', 'reviewed_at', 'updated_at')}),
    )

    def id_short(self, obj):
        return str(obj.id)[:8]

    def booking_short(self, obj):
        return str(obj.booking.id)[:8]

    def customer_email(self, obj):
        return obj.customer.email

    def mechanic_phone(self, obj):
        return obj.mechanic.phone_number

    def overall_rating_display(self, obj):
        return obj.overall_rating
    overall_rating_display.short_description = 'Overall Rating'
