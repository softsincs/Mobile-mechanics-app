"""URL routing for notifications app."""
from django.urls import include, path
from rest_framework import routers

from .views import NotificationViewSet

router = routers.DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
