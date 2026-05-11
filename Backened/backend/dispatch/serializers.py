"""Serializers for dispatch app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import JobOffer, JobOfferStatus, MechanicAssignmentHistory

User = get_user_model()


class JobOfferListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for job offer listings."""
    mechanic_phone = serializers.CharField(source='mechanic.phone_number', read_only=True)
    booking_id = serializers.UUIDField(source='booking.id', read_only=True)
    service_name = serializers.CharField(source='booking.service.name', read_only=True)
    
    class Meta:
        model = JobOffer
        fields = [
            'id',
            'booking_id',
            'mechanic_phone',
            'service_name',
            'status',
            'matching_score',
            'offered_at',
            'expires_at',
            'response_time'
        ]
        read_only_fields = fields


class JobOfferDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for job offers with score breakdown."""
    mechanic_data = serializers.SerializerMethodField(read_only=True)
    booking_data = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = JobOffer
        fields = [
            'id',
            'booking_id',
            'mechanic_data',
            'booking_data',
            'status',
            'offered_at',
            'expires_at',
            'response_time',
            'rejection_reason',
            'is_expired',
            'is_accepted',
            'matching_score',
            'proximity_score',
            'availability_score',
            'specialization_score',
            'rating_score',
            'performance_score',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields
    
    def get_mechanic_data(self, obj):
        return {
            'id': str(obj.mechanic.id),
            'phone': obj.mechanic.phone_number,
            'email': obj.mechanic.email,
            'first_name': obj.mechanic.first_name,
            'last_name': obj.mechanic.last_name,
        }
    
    def get_booking_data(self, obj):
        return {
            'id': str(obj.booking.id),
            'service': obj.booking.service.name,
            'location': obj.booking.service_location,
            'city': obj.booking.city,
            'scheduled_date': obj.booking.scheduled_date,
            'scheduled_time': obj.booking.scheduled_time,
        }


class JobOfferCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating job offers (internal API)."""
    class Meta:
        model = JobOffer
        fields = [
            'booking',
            'mechanic',
            'expires_at',
            'matching_score',
            'proximity_score',
            'availability_score',
            'specialization_score',
            'rating_score',
            'performance_score',
        ]


class JobOfferResponseSerializer(serializers.ModelSerializer):
    """Serializer for mechanic responses (accept/reject)."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = JobOffer
        fields = [
            'id',
            'status',
            'status_display',
            'response_time',
            'rejection_reason',
            'updated_at'
        ]
        read_only_fields = ['id', 'status_display', 'response_time', 'updated_at']


class MechanicAssignmentHistorySerializer(serializers.ModelSerializer):
    """Serializer for assignment history audit trail."""
    assigned_mechanic_phone = serializers.CharField(
        source='assigned_mechanic.phone_number',
        read_only=True
    )
    booking_id = serializers.UUIDField(source='booking.id', read_only=True)
    result_display = serializers.CharField(source='get_assignment_result_display', read_only=True)
    
    class Meta:
        model = MechanicAssignmentHistory
        fields = [
            'id',
            'booking_id',
            'assignment_round',
            'available_mechanics_count',
            'top_mechanics_considered',
            'assigned_mechanic_phone',
            'algorithm_version',
            'assignment_result',
            'result_display',
            'algorithm_params',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields
