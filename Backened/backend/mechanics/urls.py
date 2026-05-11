from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MechanicJobViewSet, MechanicProfileViewSet

router = DefaultRouter()
router.register(r'mechanics', MechanicProfileViewSet, basename='mechanics')
router.register(r'mechanics/me/jobs', MechanicJobViewSet, basename='mechanic-jobs')

urlpatterns = [
    path('', include(router.urls)),
]
