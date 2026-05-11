from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Service, ServiceAvailability, ServiceCategory, ServicePrice, ServicePromotion, MechanicServiceSpecialty
from .serializers import (
    MechanicServiceSpecialtySerializer,
    ServiceAvailabilitySerializer,
    ServicePriceRequestSerializer,
    ServicePriceSerializer,
    ServicePromotionSerializer,
    ServiceCategorySerializer,
    ServiceSerializer,
)
from .services import calculate_service_price, get_active_services


User = get_user_model()


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-created_at')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        qs = get_active_services()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__name__iexact=category)
        # Only apply city filter for list views, not for detail actions like pricing
        if self.action != 'pricing':
            city = self.request.query_params.get('city')
            if city:
                qs = qs.filter(availability_slots__city__iexact=city, availability_slots__is_available=True).distinct()
        return qs

    @action(detail=True, methods=['get'], url_path='pricing')
    def pricing(self, request, pk=None):
        serializer = ServicePriceRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        city = serializer.validated_data['city']
        booking_datetime = serializer.validated_data.get('booking_datetime')
        promo_code = serializer.validated_data.get('promo_code') or None
        mechanic = None
        mechanic_id = serializer.validated_data.get('mechanic_id')
        if mechanic_id:
            mechanic = User.objects.filter(id=mechanic_id).first()

        service = self.get_object()
        price_profile = ServicePrice.objects.filter(service=service, city__iexact=city).order_by('-valid_from').first()

        return Response(
            {
                'service_id': str(service.id),
                'city': city,
                'pricing_profile': ServicePriceSerializer(price_profile).data if price_profile else None,
                'calculation': calculate_service_price(
                    service=service,
                    city=city,
                    booking_datetime=booking_datetime,
                    mechanic=mechanic,
                    promo_code=promo_code,
                ),
            },
            status=status.HTTP_200_OK,
        )


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all().order_by('name')
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ServicePriceViewSet(viewsets.ModelViewSet):
    queryset = ServicePrice.objects.all().order_by('-valid_from')
    serializer_class = ServicePriceSerializer
    permission_classes = [permissions.IsAuthenticated]


class ServiceAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = ServiceAvailability.objects.all().order_by('city')
    serializer_class = ServiceAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]


class MechanicServiceSpecialtyViewSet(viewsets.ModelViewSet):
    queryset = MechanicServiceSpecialty.objects.select_related('mechanic', 'service').all().order_by('-created_at')
    serializer_class = MechanicServiceSpecialtySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        mechanic_id = self.request.query_params.get('mechanic_id')
        service_id = self.request.query_params.get('service_id')
        if mechanic_id:
            qs = qs.filter(mechanic_id=mechanic_id)
        if service_id:
            qs = qs.filter(service_id=service_id)
        return qs


class ServicePromotionViewSet(viewsets.ModelViewSet):
    queryset = ServicePromotion.objects.select_related('service').all().order_by('-created_at')
    serializer_class = ServicePromotionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        code = self.request.query_params.get('code')
        if code:
            qs = qs.filter(code__iexact=code)
        return qs
