"""URL routing for dispatch app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import JobOfferViewSet, MechanicAssignmentHistoryViewSet

router = DefaultRouter()
router.register(r'job-offers', JobOfferViewSet, basename='joboffer')
router.register(r'assignment-history', MechanicAssignmentHistoryViewSet, basename='assignment-history')

urlpatterns = [
    path('', include(router.urls)),
]
