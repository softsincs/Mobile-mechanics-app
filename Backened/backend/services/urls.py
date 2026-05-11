from django.urls import path, include
from rest_framework import routers
from .views import (
    MechanicServiceSpecialtyViewSet,
    ServiceAvailabilityViewSet,
    ServiceCategoryViewSet,
    ServicePriceViewSet,
    ServicePromotionViewSet,
    ServiceViewSet,
)

router = routers.DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'categories', ServiceCategoryViewSet, basename='servicecategory')
router.register(r'pricing', ServicePriceViewSet, basename='serviceprice')
router.register(r'availability', ServiceAvailabilityViewSet, basename='serviceavailability')
router.register(r'specialties', MechanicServiceSpecialtyViewSet, basename='mechanicservicespecialty')
router.register(r'promotions', ServicePromotionViewSet, basename='servicepromotion')

urlpatterns = [
    path('', include(router.urls)),
]
