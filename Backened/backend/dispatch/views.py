"""Views for dispatch app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from bookings.models import Booking
from .models import JobOffer, JobOfferStatus, MechanicAssignmentHistory
from .serializers import (
    JobOfferListSerializer,
    JobOfferDetailSerializer,
    JobOfferCreateSerializer,
    JobOfferResponseSerializer,
    MechanicAssignmentHistorySerializer,
)


class JobOfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job offers.
    Supports mechanics accepting/rejecting job offers and admin viewing assignment data.
    """
    permission_classes = [IsAuthenticated]
    queryset = JobOffer.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return JobOfferListSerializer
        elif self.action in ['accept', 'reject']:
            return JobOfferResponseSerializer
        elif self.action == 'create':
            return JobOfferCreateSerializer
        return JobOfferDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        
        # Admin sees all
        if user.is_staff:
            return JobOffer.objects.all()
        
        # Mechanics see their offers
        return JobOffer.objects.filter(mechanic=user)
    
    def list(self, request, *args, **kwargs):
        """List job offers (filtered by user)."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by booking
        booking_id = request.query_params.get('booking_id')
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific job offer."""
        job_offer = self.get_object()
        
        # Permission check
        if not request.user.is_staff and job_offer.mechanic != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(job_offer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        """
        Accept a job offer.
        Mechanic marks their acceptance of the job.
        """
        job_offer = self.get_object()
        
        # Permission check - only mechanic can accept their own offers
        if job_offer.mechanic != request.user:
            return Response(
                {'error': 'Only assigned mechanic can accept this offer'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Status validation
        if job_offer.status != JobOfferStatus.PENDING:
            return Response(
                {'error': f'Cannot accept offer with status {job_offer.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if job_offer.is_expired:
            job_offer.status = JobOfferStatus.EXPIRED
            job_offer.save()
            return Response(
                {'error': 'Job offer has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Accept the offer
        try:
            job_offer.accept()
            
            # Update booking status if this is the first accepted offer
            booking = job_offer.booking
            from bookings.models import BookingStatus, BookingStatusHistory
            
            if booking.status == BookingStatus.CONFIRMED:
                booking.status = BookingStatus.MECHANIC_ASSIGNED
                booking.mechanic = request.user
                booking.save()
                
                # Record status change
                BookingStatusHistory.objects.create(
                    booking=booking,
                    old_status=BookingStatus.CONFIRMED,
                    new_status=BookingStatus.MECHANIC_ASSIGNED,
                    changed_by=request.user,
                    reason='Mechanic accepted job offer'
                )
            
            serializer = self.get_serializer(job_offer)
            return Response(
                {
                    'message': 'Job offer accepted successfully',
                    'offer': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """
        Reject a job offer.
        Mechanic declines the job; next available mechanic will be offered.
        """
        job_offer = self.get_object()
        
        # Permission check
        if job_offer.mechanic != request.user:
            return Response(
                {'error': 'Only assigned mechanic can reject this offer'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Status validation
        if job_offer.status != JobOfferStatus.PENDING:
            return Response(
                {'error': f'Cannot reject offer with status {job_offer.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rejection reason from request
        reason = request.data.get('reason', 'Declined')
        
        try:
            job_offer.reject(reason=reason)
            
            serializer = self.get_serializer(job_offer)
            return Response(
                {
                    'message': 'Job offer rejected. Next mechanic will be notified.',
                    'offer': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending(self, request):
        """Get all pending job offers for current mechanic."""
        queryset = self.get_queryset().filter(status=JobOfferStatus.PENDING)
        
        # Exclude expired offers
        now = timezone.now()
        queryset = queryset.filter(expires_at__gt=now)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobOfferListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobOfferListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def accepted(self, request):
        """Get all accepted job offers for current mechanic."""
        queryset = self.get_queryset().filter(status=JobOfferStatus.ACCEPTED)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobOfferListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobOfferListSerializer(queryset, many=True)
        return Response(serializer.data)


class MechanicAssignmentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for viewing assignment history and audit trails.
    Only admin can view assignment history.
    """
    permission_classes = [IsAuthenticated]
    queryset = MechanicAssignmentHistory.objects.all()
    serializer_class = MechanicAssignmentHistorySerializer
    
    def get_queryset(self):
        """Only admin can view assignment history."""
        if not self.request.user.is_staff:
            return MechanicAssignmentHistory.objects.none()
        
        queryset = MechanicAssignmentHistory.objects.all()
        
        # Filter by booking
        booking_id = self.request.query_params.get('booking_id')
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        
        # Filter by result
        result = self.request.query_params.get('result')
        if result:
            queryset = queryset.filter(assignment_result=result)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List assignment history with filtering."""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
