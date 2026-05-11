"""Views for ratings app."""
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from bookings.models import BookingStatus
from .models import BookingReview
from .serializers import (
    BookingReviewListSerializer,
    BookingReviewDetailSerializer,
    BookingReviewCreateSerializer,
)


class BookingReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = BookingReview.objects.all().select_related('booking', 'customer', 'mechanic')

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingReviewListSerializer
        if self.action == 'create':
            return BookingReviewCreateSerializer
        return BookingReviewDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return BookingReview.objects.all().select_related('booking', 'customer', 'mechanic')
        return BookingReview.objects.filter(Q(customer=user) | Q(mechanic=user)).select_related('booking', 'customer', 'mechanic')

    def perform_create(self, serializer):
        review = serializer.save()
        booking = review.booking
        if booking.status == BookingStatus.COMPLETED:
            booking.status = BookingStatus.RATED
            booking.save(update_fields=['status', 'updated_at'])

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        reviews = self.get_queryset().filter(Q(customer=request.user) | Q(mechanic=request.user))
        serializer = BookingReviewListSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
