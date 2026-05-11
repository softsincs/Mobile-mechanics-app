from rest_framework import serializers
from .models import (
    MechanicServiceSpecialty,
    Service,
    ServiceAvailability,
    ServiceCategory,
    ServicePrice,
    ServicePromotion,
)


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'icon_url', 'is_active']


class ServicePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePrice
        fields = ['id', 'service', 'city', 'peak_multiplier', 'off_peak_multiplier', 'weekend_multiplier', 'valid_from', 'valid_to']


class ServiceSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all(), source='category', write_only=True)
    prices = ServicePriceSerializer(many=True, read_only=True)
    availability_slots = serializers.SerializerMethodField()
    promotions = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'category', 'category_id', 'name', 'description', 'estimated_duration', 'base_price', 'min_price', 'max_price', 'is_active', 'prices', 'availability_slots', 'promotions', 'created_at', 'updated_at']

    def get_availability_slots(self, obj):
        return ServiceAvailabilitySerializer(obj.availability_slots.all(), many=True).data

    def get_promotions(self, obj):
        return ServicePromotionSerializer(obj.promotions.filter(is_active=True), many=True).data


class ServiceAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAvailability
        fields = ['id', 'service', 'city', 'is_available', 'notes', 'effective_from', 'effective_to']


class MechanicServiceSpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanicServiceSpecialty
        fields = ['id', 'mechanic', 'service', 'proficiency_level', 'years_experience', 'is_active', 'created_at']


class ServicePromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePromotion
        fields = ['id', 'code', 'title', 'description', 'service', 'city', 'discount_type', 'discount_value', 'max_discount_amount', 'min_booking_amount', 'valid_from', 'valid_to', 'is_active', 'created_at']


class ServicePriceRequestSerializer(serializers.Serializer):
    city = serializers.CharField()
    booking_datetime = serializers.DateTimeField(required=False)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    mechanic_id = serializers.UUIDField(required=False)
