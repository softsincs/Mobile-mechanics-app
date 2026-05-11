"""Serializers for ratings app."""
from rest_framework import serializers

from bookings.models import Booking, BookingStatus
from .models import BookingReview


class BookingReviewListSerializer(serializers.ModelSerializer):
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    mechanic_phone = serializers.CharField(source='mechanic.phone_number', read_only=True)
    booking_city = serializers.CharField(source='booking.city', read_only=True)
    overall_rating = serializers.SerializerMethodField()

    class Meta:
        model = BookingReview
        fields = [
            'id', 'booking', 'customer_email', 'mechanic_phone', 'booking_city',
            'service_rating', 'mechanic_rating', 'overall_rating', 'is_verified', 'reviewed_at'
        ]
        read_only_fields = fields

    def get_overall_rating(self, obj):
        return obj.overall_rating


class BookingReviewDetailSerializer(serializers.ModelSerializer):
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    mechanic_phone = serializers.CharField(source='mechanic.phone_number', read_only=True)
    booking_service = serializers.CharField(source='booking.service.name', read_only=True)
    booking_status = serializers.CharField(source='booking.status', read_only=True)
    overall_rating = serializers.SerializerMethodField()

    class Meta:
        model = BookingReview
        fields = [
            'id', 'booking', 'booking_service', 'booking_status', 'customer', 'customer_email',
            'mechanic', 'mechanic_phone', 'service_rating', 'mechanic_rating', 'overall_rating',
            'comment', 'is_verified', 'reviewed_at', 'updated_at'
        ]
        read_only_fields = fields

    def get_overall_rating(self, obj):
        return obj.overall_rating


class BookingReviewCreateSerializer(serializers.ModelSerializer):
    booking_id = serializers.PrimaryKeyRelatedField(source='booking', queryset=Booking.objects.all(), write_only=True)

    class Meta:
        model = BookingReview
        fields = ['booking_id', 'service_rating', 'mechanic_rating', 'comment']

    def validate(self, attrs):
        booking = attrs['booking']
        request = self.context['request']

        if booking.customer != request.user:
            raise serializers.ValidationError('You can only review your own booking.')
        if booking.status != BookingStatus.COMPLETED:
            raise serializers.ValidationError('Booking must be completed before it can be reviewed.')
        if hasattr(booking, 'review'):
            raise serializers.ValidationError('This booking has already been reviewed.')
        if booking.mechanic is None:
            raise serializers.ValidationError('Completed booking must have an assigned mechanic.')
        return attrs

    def create(self, validated_data):
        booking = validated_data.pop('booking')
        return BookingReview.objects.create(
            booking=booking,
            customer=self.context['request'].user,
            mechanic=booking.mechanic,
            **validated_data,
        )
