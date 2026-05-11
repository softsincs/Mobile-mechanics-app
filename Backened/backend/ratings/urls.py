"""URL routing for ratings app."""
from django.urls import include, path
from rest_framework import routers

from .views import BookingReviewViewSet

router = routers.DefaultRouter()
router.register(r'reviews', BookingReviewViewSet, basename='booking-review')

urlpatterns = [
    path('', include(router.urls)),
]
