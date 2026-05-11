"""Serializers for bookings app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Booking, BookingStatusHistory, BookingAddOn, BookingAddOnAssignment
from services.models import Service

User = get_user_model()


class BookingAddOnSerializer(serializers.ModelSerializer):
    """Serializer for add-ons available for bookings."""
    
    class Meta:
        model = BookingAddOn
        fields = ['id', 'name', 'description', 'price', 'is_active']


class BookingAddOnAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for add-ons assigned to a booking."""
    
    add_on_name = serializers.CharField(source='add_on.name', read_only=True)
    
    class Meta:
        model = BookingAddOnAssignment
        fields = ['id', 'add_on', 'add_on_name', 'price_at_booking', 'is_completed', 'created_at']


class BookingStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for booking status history."""
    
    changed_by_email = serializers.CharField(source='changed_by.email', read_only=True)
    
    class Meta:
        model = BookingStatusHistory
        fields = ['id', 'old_status', 'new_status', 'changed_by', 'changed_by_email', 'changed_at', 'reason']


class BookingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for booking list view."""
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    mechanic_name = serializers.CharField(source='mechanic.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'customer_name', 'customer_email', 'service', 'service_name', 
            'mechanic', 'mechanic_name', 'status', 'scheduled_date', 'scheduled_time', 
            'total_amount', 'payment_method', 'city', 'created_at'
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    """Full serializer for booking detail view."""
    
    # Nested read-only fields
    customer = serializers.StringRelatedField(read_only=True)
    service = serializers.StringRelatedField(read_only=True)
    mechanic = serializers.StringRelatedField(read_only=True, allow_null=True)
    
    # Related data
    status_history = BookingStatusHistorySerializer(many=True, read_only=True)
    add_ons = BookingAddOnAssignmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'service', 'mechanic', 'status',
            'service_location', 'city', 'latitude', 'longitude',
            'scheduled_date', 'scheduled_time', 'estimated_duration',
            'start_time', 'end_time',
            'base_price', 'surge_multiplier', 'discount_percentage', 'discount_amount',
            'tax_amount', 'total_amount', 'paid_amount', 'payment_method',
            'created_at', 'updated_at', 'confirmed_at', 'started_at', 'completed_at',
            'cancellation_reason', 'cancelled_by', 'cancellation_date', 'cancellation_notes',
            'customer_notes', 'mechanic_notes',
            'status_history', 'add_ons'
        ]
        read_only_fields = [
            'id', 'customer', 'service', 'mechanic', 'status',
            'created_at', 'updated_at', 'confirmed_at', 'started_at', 'completed_at',
            'status_history', 'add_ons'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new bookings."""
    
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source='service', write_only=True)
    add_on_ids = serializers.PrimaryKeyRelatedField(
        queryset=BookingAddOn.objects.filter(is_active=True),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Booking
        fields = [
            'service_id',
            'service_location', 'city', 'latitude', 'longitude',
            'scheduled_date', 'scheduled_time', 'estimated_duration',
            'base_price', 'discount_amount', 'tax_amount', 'total_amount',
            'payment_method', 'customer_notes', 'add_on_ids'
        ]
    
    def create(self, validated_data):
        """Create booking and assign add-ons."""
        add_on_ids = validated_data.pop('add_on_ids', [])
        booking = Booking.objects.create(**validated_data)
        
        # Assign add-ons
        for add_on in add_on_ids:
            BookingAddOnAssignment.objects.create(
                booking=booking,
                add_on=add_on,
                price_at_booking=add_on.price
            )
        
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating bookings."""
    
    class Meta:
        model = Booking
        fields = [
            'service_location', 'scheduled_date', 'scheduled_time',
            'payment_method', 'customer_notes', 'mechanic_notes'
        ]


class BookingConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a booking."""
    
    payment_method = serializers.ChoiceField(
        choices=['JAZZCASH', 'EASYPAISA', 'CARD', 'CASH', 'WALLET']
    )
    promo_code = serializers.CharField(required=False, allow_blank=True)


class BookingCancelSerializer(serializers.Serializer):
    """Serializer for cancelling a booking."""
    
    reason = serializers.ChoiceField(
        choices=['CUSTOMER_REQUEST', 'PAYMENT_FAILED', 'OTHER'],
        default='CUSTOMER_REQUEST'
    )
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
