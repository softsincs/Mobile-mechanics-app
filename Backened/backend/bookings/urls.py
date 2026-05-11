"""URL routing for bookings app."""
from django.urls import path, include
from rest_framework import routers
from .views import BookingViewSet, BookingAddOnViewSet

router = routers.DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'add-ons', BookingAddOnViewSet, basename='booking-addon')

urlpatterns = [
    path('', include(router.urls)),
]
