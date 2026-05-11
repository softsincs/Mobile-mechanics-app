"""Serializers for the mechanics app."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from bookings.models import Booking, BookingStatus
from services.models import MechanicServiceSpecialty, Service

from .models import MechanicAvailability, MechanicDocument, MechanicJobPhoto, MechanicProfile, MechanicVacation

User = get_user_model()


class MechanicServiceSpecialtySerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = MechanicServiceSpecialty
        fields = ['id', 'service', 'service_name', 'proficiency_level', 'years_experience', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class MechanicAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanicAvailability
        fields = ['id', 'mechanic', 'day_of_week', 'start_time', 'end_time', 'is_available', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'mechanic', 'created_at', 'updated_at']


class MechanicVacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanicVacation
        fields = ['id', 'mechanic', 'start_date', 'end_date', 'reason', 'is_active', 'created_at']
        read_only_fields = ['id', 'mechanic', 'created_at']


class MechanicDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanicDocument
        fields = ['id', 'mechanic', 'document_type', 'document_file', 'document_name', 'is_verified', 'verified_at', 'expiry_date', 'created_at']
        read_only_fields = ['id', 'mechanic', 'is_verified', 'verified_at', 'created_at']


class MechanicJobPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanicJobPhoto
        fields = ['id', 'booking', 'mechanic', 'photo_type', 'image_url', 'caption', 'created_at']
        read_only_fields = ['id', 'booking', 'mechanic', 'created_at']


class MechanicProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    specialties = MechanicServiceSpecialtySerializer(source='user.service_specialties', many=True, read_only=True)
    availability_slots = MechanicAvailabilitySerializer(many=True, read_only=True)
    can_accept_more_jobs = serializers.SerializerMethodField()

    class Meta:
        model = MechanicProfile
        fields = [
            'id', 'user_id', 'phone_number', 'email', 'full_name', 'years_experience', 'emergency_contact',
            'bio', 'service_area_city', 'service_radius_km', 'max_concurrent_jobs', 'current_active_jobs',
            'current_rating', 'acceptance_rate', 'cancellation_rate', 'is_approved', 'is_active', 'is_available',
            'can_accept_more_jobs', 'specialties', 'availability_slots', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user_id', 'phone_number', 'email', 'full_name', 'current_active_jobs', 'current_rating', 'acceptance_rate', 'cancellation_rate', 'is_approved', 'is_active', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.phone_number

    def get_can_accept_more_jobs(self, obj):
        return obj.can_accept_more_jobs()


class MechanicRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=8)
    years_experience = serializers.IntegerField(min_value=0, default=0)
    emergency_contact = serializers.CharField(max_length=20, required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    service_area_city = serializers.CharField(max_length=150, required=False, allow_blank=True)
    service_radius_km = serializers.IntegerField(min_value=1, default=25)
    max_concurrent_jobs = serializers.IntegerField(min_value=1, default=3)

    def create(self, validated_data):
        password = validated_data.pop('password')
        years_experience = validated_data.pop('years_experience', 0)
        emergency_contact = validated_data.pop('emergency_contact', '')
        bio = validated_data.pop('bio', '')
        service_area_city = validated_data.pop('service_area_city', '')
        service_radius_km = validated_data.pop('service_radius_km', 25)
        max_concurrent_jobs = validated_data.pop('max_concurrent_jobs', 3)

        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', ''),
        )
        profile = MechanicProfile.objects.create(
            user=user,
            years_experience=years_experience,
            emergency_contact=emergency_contact,
            bio=bio,
            service_area_city=service_area_city,
            service_radius_km=service_radius_km,
            max_concurrent_jobs=max_concurrent_jobs,
            is_approved=False,
            is_active=False,
            is_available=False,
        )
        return profile


class MechanicJobSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    photos = MechanicJobPhotoSerializer(source='job_photos', many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'customer_name', 'service', 'service_name', 'mechanic', 'status',
            'city', 'service_location', 'scheduled_date', 'scheduled_time', 'estimated_duration',
            'mechanic_notes', 'customer_notes', 'start_time', 'end_time', 'completed_at', 'photos',
        ]
        read_only_fields = fields


class MechanicJobActionSerializer(serializers.Serializer):
    mechanic_notes = serializers.CharField(required=False, allow_blank=True)
    issues_found = serializers.CharField(required=False, allow_blank=True)
    additional_charges = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    photo_type = serializers.ChoiceField(choices=[('BEFORE', 'Before'), ('AFTER', 'After')], required=False, default='BEFORE')
    caption = serializers.CharField(required=False, allow_blank=True)
    photo_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=list,
        allow_empty=True,
    )
    service_completed = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        if not attrs.get('mechanic_notes') and not attrs.get('issues_found') and not attrs.get('photo_urls'):
            return attrs
        return attrs
