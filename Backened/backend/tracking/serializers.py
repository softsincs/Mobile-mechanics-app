"""Serializers for tracking app."""
from rest_framework import serializers

from .models import MechanicLocation, LocationHistory, LocationAccuracy


class MechanicLocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for mechanic locations."""
    mechanic_phone = serializers.CharField(source='mechanic.phone_number', read_only=True)
    booking_id = serializers.UUIDField(source='booking.id', read_only=True)
    
    class Meta:
        model = MechanicLocation
        fields = [
            'id',
            'mechanic_phone',
            'booking_id',
            'latitude',
            'longitude',
            'accuracy',
            'speed',
            'is_sharing',
            'last_updated'
        ]
        read_only_fields = fields


class MechanicLocationDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for mechanic location with ETA."""
    mechanic_data = serializers.SerializerMethodField(read_only=True)
    booking_data = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = MechanicLocation
        fields = [
            'id',
            'mechanic_data',
            'booking_data',
            'latitude',
            'longitude',
            'accuracy',
            'speed',
            'estimated_time_arrival',
            'distance_to_destination',
            'is_sharing',
            'is_stale',
            'last_updated',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_mechanic_data(self, obj):
        return {
            'id': str(obj.mechanic.id),
            'phone': obj.mechanic.phone_number,
            'first_name': obj.mechanic.first_name,
        }
    
    def get_booking_data(self, obj):
        if obj.booking:
            return {
                'id': str(obj.booking.id),
                'service': obj.booking.service.name,
                'destination': obj.booking.service_location,
            }
        return None


class MechanicLocationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for receiving location updates from mechanic app."""
    class Meta:
        model = MechanicLocation
        fields = [
            'latitude',
            'longitude',
            'accuracy',
            'speed'
        ]


class LocationHistoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for location history listing."""
    mechanic_phone = serializers.CharField(source='mechanic.phone_number', read_only=True)
    booking_id = serializers.UUIDField(source='booking.id', read_only=True)
    event_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = LocationHistory
        fields = [
            'id',
            'mechanic_phone',
            'booking_id',
            'latitude',
            'longitude',
            'accuracy',
            'speed',
            'event_type',
            'event_display',
            'created_at'
        ]
        read_only_fields = fields


class LocationHistoryDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for location history with coordinates."""
    mechanic_phone = serializers.CharField(source='mechanic.phone_number', read_only=True)
    
    class Meta:
        model = LocationHistory
        fields = [
            'id',
            'mechanic_phone',
            'booking_id',
            'latitude',
            'longitude',
            'accuracy',
            'speed',
            'estimated_time_arrival',
            'event_type',
            'created_at'
        ]
        read_only_fields = fields


class LocationHistoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for recording location history events."""
    class Meta:
        model = LocationHistory
        fields = [
            'mechanic',
            'booking',
            'latitude',
            'longitude',
            'accuracy',
            'speed',
            'estimated_time_arrival',
            'event_type'
        ]


class LocationAccuracySerializer(serializers.ModelSerializer):
    """Serializer for location accuracy metrics."""
    mechanic_phone = serializers.CharField(source='mechanic.phone_number', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = LocationAccuracy
        fields = [
            'id',
            'mechanic_phone',
            'provider',
            'provider_display',
            'horizontal_accuracy',
            'vertical_accuracy',
            'bearing_accuracy',
            'is_from_mock_provider',
            'satellites_used',
            'recorded_at'
        ]
        read_only_fields = fields


class LocationAccuracyCreateSerializer(serializers.ModelSerializer):
    """Serializer for recording location accuracy data."""
    class Meta:
        model = LocationAccuracy
        fields = [
            'mechanic',
            'provider',
            'horizontal_accuracy',
            'vertical_accuracy',
            'bearing_accuracy',
            'is_from_mock_provider',
            'satellites_used'
        ]
