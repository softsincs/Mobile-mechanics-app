from django.urls import path

from .views import AnalyticsDashboardView, BookingAnalyticsView, CustomerAnalyticsView, MechanicAnalyticsView, RevenueAnalyticsView

urlpatterns = [
    path('admin/analytics/', AnalyticsDashboardView.as_view(), name='analytics-dashboard'),
    path('admin/analytics/bookings/', BookingAnalyticsView.as_view(), name='analytics-bookings'),
    path('admin/analytics/revenue/', RevenueAnalyticsView.as_view(), name='analytics-revenue'),
    path('admin/analytics/mechanics/', MechanicAnalyticsView.as_view(), name='analytics-mechanics'),
    path('admin/analytics/customers/', CustomerAnalyticsView.as_view(), name='analytics-customers'),
]
