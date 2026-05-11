"""Views for bookings app."""
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Booking, BookingStatusHistory, BookingAddOn, BookingAddOnAssignment, BookingStatus, CancelledBy
from .serializers import (
    BookingListSerializer,
    BookingDetailSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
    BookingConfirmSerializer,
    BookingCancelSerializer,
    BookingAddOnSerializer,
)


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing bookings."""
    
    queryset = Booking.objects.all().select_related('customer', 'service', 'mechanic')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id', 'service__name', 'city']
    ordering_fields = ['created_at', 'scheduled_date', 'total_amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return BookingListSerializer
        elif self.action == 'retrieve':
            return BookingDetailSerializer
        elif self.action == 'create':
            return BookingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        return BookingDetailSerializer
    
    def get_queryset(self):
        """Filter bookings based on user role."""
        user = self.request.user
        
        # Show customer's own bookings or mechanic's assigned bookings
        return Booking.objects.filter(
            Q(customer=user) | Q(mechanic=user)
        ).select_related('customer', 'service', 'mechanic')
    
    def perform_create(self, serializer):
        """Create booking with customer set to current user."""
        serializer.save(customer=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        """Confirm a booking (transitions from PENDING_CONFIRMATION to CONFIRMED)."""
        booking = self.get_object()
        serializer = BookingConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not booking.can_be_confirmed:
            return Response(
                {'detail': f'Booking cannot be confirmed from {booking.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update booking
        booking.status = BookingStatus.CONFIRMED
        booking.payment_method = serializer.validated_data['payment_method']
        booking.confirmed_at = timezone.now()
        booking.save()
        
        # Record status change
        BookingStatusHistory.objects.create(
            booking=booking,
            old_status=BookingStatus.PENDING_CONFIRMATION,
            new_status=BookingStatus.CONFIRMED,
            changed_by=request.user,
            reason=f'Booking confirmed via {booking.payment_method}'
        )
        
        return Response(BookingDetailSerializer(booking).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        serializer = BookingCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not booking.is_cancellable:
            return Response(
                {'detail': f'Booking cannot be cancelled from {booking.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permission: only customer, mechanic, or admin can cancel
        if booking.customer != request.user and booking.mechanic != request.user:
            if not request.user.is_staff:
                return Response(
                    {'detail': 'You do not have permission to cancel this booking'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Update booking
        booking.status = BookingStatus.CANCELLED
        booking.cancellation_reason = serializer.validated_data['reason']
        booking.cancelled_by = CancelledBy.CUSTOMER if booking.customer == request.user else CancelledBy.MECHANIC
        booking.cancellation_date = timezone.now()
        booking.cancellation_notes = serializer.validated_data.get('notes', '')
        booking.save()
        
        # Record status change
        BookingStatusHistory.objects.create(
            booking=booking,
            old_status=booking.status,
            new_status=BookingStatus.CANCELLED,
            changed_by=request.user,
            reason=f'Cancelled by {booking.cancelled_by}: {booking.cancellation_reason}'
        )
        
        return Response(BookingDetailSerializer(booking).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        """Start a booking (mechanic marks job as in progress)."""
        booking = self.get_object()
        
        # Only assigned mechanic can start
        if booking.mechanic != request.user:
            return Response(
                {'detail': 'Only assigned mechanic can start the booking'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != BookingStatus.MECHANIC_ACCEPTED:
            return Response(
                {'detail': f'Booking must be in MECHANIC_ACCEPTED status, currently {booking.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update booking
        old_status = booking.status
        booking.status = BookingStatus.IN_PROGRESS
        booking.started_at = timezone.now()
        booking.save()
        
        # Record status change
        BookingStatusHistory.objects.create(
            booking=booking,
            old_status=old_status,
            new_status=BookingStatus.IN_PROGRESS,
            changed_by=request.user,
            reason='Mechanic started the job'
        )
        
        return Response(BookingDetailSerializer(booking).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """Complete a booking (mechanic marks job as done)."""
        booking = self.get_object()
        
        # Only assigned mechanic can complete
        if booking.mechanic != request.user:
            return Response(
                {'detail': 'Only assigned mechanic can complete the booking'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != BookingStatus.IN_PROGRESS:
            return Response(
                {'detail': f'Booking must be IN_PROGRESS to complete, currently {booking.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update booking
        old_status = booking.status
        booking.status = BookingStatus.COMPLETED
        booking.completed_at = timezone.now()
        booking.end_time = timezone.now()
        
        # Capture mechanic notes if provided
        if 'mechanic_notes' in request.data:
            booking.mechanic_notes = request.data['mechanic_notes']
        
        booking.save()
        
        # Record status change
        BookingStatusHistory.objects.create(
            booking=booking,
            old_status=old_status,
            new_status=BookingStatus.COMPLETED,
            changed_by=request.user,
            reason='Mechanic completed the job'
        )
        
        return Response(BookingDetailSerializer(booking).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='my-bookings')
    def my_bookings(self, request):
        """Get current user's bookings (as customer or mechanic)."""
        bookings = Booking.objects.filter(
            Q(customer=request.user) | Q(mechanic=request.user)
        ).select_related('customer', 'service', 'mechanic')
        
        # Apply filters
        status_param = request.query_params.get('status')
        if status_param:
            bookings = bookings.filter(status=status_param)
        
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingAddOnViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for browsing available add-ons."""
    
    queryset = BookingAddOn.objects.filter(is_active=True)
    serializer_class = BookingAddOnSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    ordering = ['name']
