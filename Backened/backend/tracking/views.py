"""Views for tracking app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from bookings.models import Booking
from .models import MechanicLocation, LocationHistory, LocationAccuracy
from .serializers import (
    MechanicLocationListSerializer,
    MechanicLocationDetailSerializer,
    MechanicLocationUpdateSerializer,
    LocationHistoryListSerializer,
    LocationHistoryDetailSerializer,
    LocationHistoryCreateSerializer,
    LocationAccuracySerializer,
    LocationAccuracyCreateSerializer,
)


class MechanicLocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for real-time mechanic location tracking.
    Follows SRS 4.4 Real-Time Tracking specification.
    """
    permission_classes = [IsAuthenticated]
    queryset = MechanicLocation.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return MechanicLocationListSerializer
        elif self.action in ['update', 'partial_update']:
            return MechanicLocationUpdateSerializer
        return MechanicLocationDetailSerializer
    
    def get_queryset(self):
        """Filter based on user role."""
        user = self.request.user
        
        # Admin sees all
        if user.is_staff:
            return MechanicLocation.objects.all()
        
        # Mechanics see only their own location
        # Customers see mechanic assigned to their booking
        booking_id = self.request.query_params.get('booking_id')
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                # Check access: customer or mechanic on booking, or admin
                if user == booking.customer or user == booking.mechanic:
                    if booking.mechanic:
                        return MechanicLocation.objects.filter(mechanic=booking.mechanic)
            except Booking.DoesNotExist:
                pass
        
        # Mechanic sees their own location
        return MechanicLocation.objects.filter(mechanic=user)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_my_location(self, request):
        """
        Update current mechanic's location.
        Mobile app calls this endpoint every 5 seconds during transit.
        """
        serializer = MechanicLocationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create location record
        mechanic_location, created = MechanicLocation.objects.get_or_create(
            mechanic=request.user,
            defaults={
                'latitude': serializer.validated_data['latitude'],
                'longitude': serializer.validated_data['longitude'],
            }
        )
        
        # Update location
        mechanic_location.update_location(
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            accuracy=serializer.validated_data.get('accuracy', 10),
            speed=serializer.validated_data.get('speed', 0.0)
        )
        
        # Get current booking (active job)
        booking = request.data.get('booking_id')
        if booking:
            try:
                booking_obj = Booking.objects.get(id=booking)
                mechanic_location.booking = booking_obj
                mechanic_location.save()
                
                # Record in history
                LocationHistory.objects.create(
                    mechanic=request.user,
                    booking=booking_obj,
                    latitude=serializer.validated_data['latitude'],
                    longitude=serializer.validated_data['longitude'],
                    accuracy=serializer.validated_data.get('accuracy', 10),
                    speed=serializer.validated_data.get('speed', 0.0),
                    event_type='UPDATE'
                )
            except Booking.DoesNotExist:
                pass
        
        return Response(
            {
                'message': 'Location updated successfully',
                'location': MechanicLocationDetailSerializer(mechanic_location).data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def start_sharing(self, request):
        """
        Start sharing location for a booking.
        Mechanic begins real-time tracking when accepting a job.
        """
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response(
                {'error': 'booking_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            booking = Booking.objects.get(id=booking_id, mechanic=request.user)
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Booking not found or not assigned to you'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        mechanic_location, _ = MechanicLocation.objects.get_or_create(
            mechanic=request.user,
            defaults={
                'latitude': 0.0,
                'longitude': 0.0,
            }
        )
        mechanic_location.booking = booking
        mechanic_location.is_sharing = True
        mechanic_location.save()
        
        # Record event
        if mechanic_location.latitude and mechanic_location.longitude:
            LocationHistory.objects.create(
                mechanic=request.user,
                booking=booking,
                latitude=mechanic_location.latitude,
                longitude=mechanic_location.longitude,
                accuracy=mechanic_location.accuracy,
                event_type='DEPARTURE'
            )
        
        return Response(
            {
                'message': 'Location sharing started',
                'location': MechanicLocationDetailSerializer(mechanic_location).data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def stop_sharing(self, request):
        """
        Stop sharing location.
        Mechanic stops tracking when job is completed or cancelled.
        """
        try:
            mechanic_location = MechanicLocation.objects.get(mechanic=request.user)
            booking = mechanic_location.booking
            
            if booking and mechanic_location.latitude and mechanic_location.longitude:
                LocationHistory.objects.create(
                    mechanic=request.user,
                    booking=booking,
                    latitude=mechanic_location.latitude,
                    longitude=mechanic_location.longitude,
                    accuracy=mechanic_location.accuracy,
                    event_type='ARRIVAL'
                )
            
            mechanic_location.is_sharing = False
            mechanic_location.save()
            
            return Response(
                {'message': 'Location sharing stopped'},
                status=status.HTTP_200_OK
            )
        except MechanicLocation.DoesNotExist:
            return Response(
                {'error': 'No location record found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_mechanic_location(self, request):
        """Get current location for a mechanic (for customer/admin viewing)."""
        mechanic_id = request.query_params.get('mechanic_id')
        if not mechanic_id:
            return Response(
                {'error': 'mechanic_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        if not request.user.is_staff:
            booking_id = request.query_params.get('booking_id')
            if not booking_id:
                return Response(
                    {'error': 'booking_id required for non-admin users'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                booking = Booking.objects.get(id=booking_id)
                if request.user != booking.customer and request.user != booking.mechanic:
                    return Response(
                        {'error': 'Not authorized to view this location'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Booking.DoesNotExist:
                return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            location = MechanicLocation.objects.get(mechanic_id=mechanic_id)
            serializer = MechanicLocationDetailSerializer(location)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MechanicLocation.DoesNotExist:
            return Response(
                {'error': 'Location not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class LocationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for location history and audit trails.
    Used for disputes, analytics, and historical tracking.
    """
    permission_classes = [IsAuthenticated]
    queryset = LocationHistory.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return LocationHistoryListSerializer
        return LocationHistoryDetailSerializer
    
    def get_queryset(self):
        """Filter location history by booking and user permissions."""
        user = self.request.user
        booking_id = self.request.query_params.get('booking_id')
        
        queryset = LocationHistory.objects.all()
        
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
            
            # Check access: must be customer or mechanic on booking, or admin
            if not user.is_staff:
                try:
                    booking = Booking.objects.get(id=booking_id)
                    if user != booking.customer and user != booking.mechanic:
                        return LocationHistory.objects.none()
                except Booking.DoesNotExist:
                    return LocationHistory.objects.none()
        else:
            # Non-admin can only see their own history
            if not user.is_staff:
                queryset = queryset.filter(mechanic=user)
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def booking_track(self, request):
        """Get complete location history for a booking."""
        booking_id = request.query_params.get('booking_id')
        if not booking_id:
            return Response(
                {'error': 'booking_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Permission check
        if not request.user.is_staff:
            if request.user != booking.customer and request.user != booking.mechanic:
                return Response(
                    {'error': 'Not authorized to view this track'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        history = LocationHistory.objects.filter(booking=booking).order_by('-created_at')
        serializer = LocationHistoryDetailSerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LocationAccuracyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing location accuracy metrics.
    Used for debugging GPS issues and monitoring location quality.
    """
    permission_classes = [IsAuthenticated]
    queryset = LocationAccuracy.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return LocationAccuracyCreateSerializer
        return LocationAccuracySerializer
    
    def get_queryset(self):
        """Only admin can view all; mechanics see their own."""
        if self.request.user.is_staff:
            return LocationAccuracy.objects.all()
        return LocationAccuracy.objects.filter(mechanic=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Record location accuracy metrics."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Only allow recording own data
        if serializer.validated_data['mechanic'] != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Can only record own accuracy data'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_accuracy(self, request):
        """Get current mechanic's location accuracy statistics."""
        accuracy_logs = LocationAccuracy.objects.filter(mechanic=request.user).order_by('-recorded_at')[:100]
        
        if not accuracy_logs:
            return Response(
                {'message': 'No accuracy data recorded'},
                status=status.HTTP_200_OK
            )
        
        serializer = LocationAccuracySerializer(accuracy_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
