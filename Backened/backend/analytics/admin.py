from django.contrib import admin

from .models import DashboardMetrics


@admin.register(DashboardMetrics)
class DashboardMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_bookings', 'completed_bookings', 'cancelled_bookings', 'total_revenue', 'average_rating']
    list_filter = ['date']
    search_fields = ['date']
