"""URL routing for tracking app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MechanicLocationViewSet, LocationHistoryViewSet, LocationAccuracyViewSet

router = DefaultRouter()
router.register(r'mechanic-locations', MechanicLocationViewSet, basename='mechanic-location')
router.register(r'location-history', LocationHistoryViewSet, basename='location-history')
router.register(r'location-accuracy', LocationAccuracyViewSet, basename='location-accuracy')

urlpatterns = [
    path('', include(router.urls)),
]
