"""Views for mechanic registration, profile, availability, and jobs."""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from bookings.models import Booking, BookingStatus, BookingStatusHistory
from dispatch.models import JobOffer, JobOfferStatus

from .models import MechanicAvailability, MechanicJobPhoto, MechanicProfile
from .serializers import (
    MechanicAvailabilitySerializer,
    MechanicJobActionSerializer,
    MechanicJobPhotoSerializer,
    MechanicJobSerializer,
    MechanicProfileSerializer,
    MechanicRegisterSerializer,
)


class MechanicProfileViewSet(viewsets.GenericViewSet):
    queryset = MechanicProfile.objects.select_related('user').prefetch_related('availability_slots', 'user__service_specialties')
    serializer_class = MechanicProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # List all approved mechanics for customers
        qs = MechanicProfile.objects.select_related('user').prefetch_related('availability_slots', 'user__service_specialties').filter(is_approved=True)
        
        # Staff can see all mechanics
        if self.request.user.is_staff:
            qs = MechanicProfile.objects.select_related('user').prefetch_related('availability_slots', 'user__service_specialties')
        
        return qs

    def get_object(self):
        return get_object_or_404(MechanicProfile.objects.select_related('user').prefetch_related('availability_slots', 'user__service_specialties'), user=self.request.user)

    def _ensure_approved(self, user):
        profile = getattr(user, 'mechanic_profile', None)
        if not profile or not profile.is_approved:
            raise PermissionDenied('Mechanic account is pending admin approval.')

    def get_serializer_class(self):
        if self.action == 'register':
            return MechanicRegisterSerializer
        if self.action == 'availability':
            return MechanicAvailabilitySerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'register':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """List all available mechanics."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Get a specific mechanic profile."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = MechanicRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(MechanicProfileSerializer(profile, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        try:
            profile = self.get_object()
        except Exception:
            return Response({'detail': 'Mechanic profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            return Response(MechanicProfileSerializer(profile, context={'request': request}).data)

        serializer = MechanicProfileSerializer(profile, data=request.data, partial=request.method == 'PATCH', context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'post'])
    def availability(self, request):
        profile = self.get_object()
        if request.method == 'GET':
            serializer = MechanicAvailabilitySerializer(profile.availability_slots.all(), many=True)
            return Response(serializer.data)

        self._ensure_approved(request.user)
        serializer = MechanicAvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(mechanic=profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MechanicJobViewSet(viewsets.GenericViewSet):
    queryset = Booking.objects.select_related('customer', 'service', 'mechanic').prefetch_related('job_photos')
    serializer_class = MechanicJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(mechanic=self.request.user)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])

    def _record_status_history(self, booking, old_status, new_status, reason):
        BookingStatusHistory.objects.create(
            booking=booking,
            old_status=old_status,
            new_status=new_status,
            changed_by=self.request.user,
            reason=reason,
        )

    def _bump_active_jobs(self, mechanic_user, delta):
        profile = getattr(mechanic_user, 'mechanic_profile', None)
        if not profile:
            return
        profile.current_active_jobs = max(0, profile.current_active_jobs + delta)
        profile.is_available = profile.can_accept_more_jobs()
        profile.save(update_fields=['current_active_jobs', 'is_available', 'updated_at'])

    def _ensure_approved(self, user):
        profile = getattr(user, 'mechanic_profile', None)
        if not profile or not profile.is_approved:
            raise PermissionDenied('Mechanic account is pending admin approval.')

    @action(detail=False, methods=['get'])
    def jobs(self, request):
        self._ensure_approved(request.user)
        queryset = self.get_queryset().filter(status__in=[BookingStatus.MECHANIC_ASSIGNED, BookingStatus.MECHANIC_ACCEPTED, BookingStatus.IN_PROGRESS, BookingStatus.COMPLETED])
        serializer = MechanicJobSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def accept(self, request, pk=None):
        self._ensure_approved(request.user)
        booking = self.get_object()
        if booking.mechanic != request.user and not request.user.is_staff:
            return Response({'detail': 'Only assigned mechanic can accept this job.'}, status=status.HTTP_403_FORBIDDEN)
        if booking.status not in [BookingStatus.MECHANIC_ASSIGNED, BookingStatus.MECHANIC_REJECTED]:
            return Response({'detail': 'Booking is not waiting for mechanic acceptance.'}, status=status.HTTP_400_BAD_REQUEST)

        old_status = booking.status
        booking.status = BookingStatus.MECHANIC_ACCEPTED
        booking.save(update_fields=['status', 'updated_at'])
        self._record_status_history(booking, old_status, BookingStatus.MECHANIC_ACCEPTED, 'Mechanic accepted job in mechanics app')
        self._bump_active_jobs(request.user, 1)
        return Response(MechanicJobSerializer(booking, context={'request': request}).data)

    @action(detail=True, methods=['put'])
    def start(self, request, pk=None):
        self._ensure_approved(request.user)
        booking = self.get_object()
        if booking.mechanic != request.user and not request.user.is_staff:
            return Response({'detail': 'Only assigned mechanic can start this job.'}, status=status.HTTP_403_FORBIDDEN)
        if booking.status != BookingStatus.MECHANIC_ACCEPTED:
            return Response({'detail': 'Booking must be accepted before it can be started.'}, status=status.HTTP_400_BAD_REQUEST)

        old_status = booking.status
        booking.status = BookingStatus.IN_PROGRESS
        if not booking.start_time:
            booking.start_time = timezone.now()
        booking.save(update_fields=['status', 'start_time', 'updated_at'])
        self._record_status_history(booking, old_status, BookingStatus.IN_PROGRESS, 'Mechanic started job')
        return Response(MechanicJobSerializer(booking, context={'request': request}).data)

    @action(detail=True, methods=['put'])
    def complete(self, request, pk=None):
        self._ensure_approved(request.user)
        booking = self.get_object()
        if booking.mechanic != request.user and not request.user.is_staff:
            return Response({'detail': 'Only assigned mechanic can complete this job.'}, status=status.HTTP_403_FORBIDDEN)
        if booking.status != BookingStatus.IN_PROGRESS:
            return Response({'detail': 'Booking must be in progress before completion.'}, status=status.HTTP_400_BAD_REQUEST)

        payload = MechanicJobActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data

        old_status = booking.status
        booking.status = BookingStatus.COMPLETED
        booking.end_time = timezone.now()
        booking.completed_at = timezone.now()
        if data.get('mechanic_notes'):
            booking.mechanic_notes = data['mechanic_notes']
        if data.get('issues_found'):
            booking.mechanic_notes = (booking.mechanic_notes + '\n\nIssues found: ' + data['issues_found']).strip()
        booking.save(update_fields=['status', 'end_time', 'completed_at', 'mechanic_notes', 'updated_at'])
        self._record_status_history(booking, old_status, BookingStatus.COMPLETED, 'Mechanic completed job')
        self._bump_active_jobs(request.user, -1)
        return Response(MechanicJobSerializer(booking, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def upload_photos(self, request, pk=None):
        self._ensure_approved(request.user)
        booking = self.get_object()
        if booking.mechanic != request.user and not request.user.is_staff:
            return Response({'detail': 'Only assigned mechanic can upload job photos.'}, status=status.HTTP_403_FORBIDDEN)

        payload = MechanicJobActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data
        photo_urls = data.get('photo_urls', [])
        if not photo_urls:
            return Response({'detail': 'photo_urls is required.'}, status=status.HTTP_400_BAD_REQUEST)

        created_photos = []
        for url in photo_urls:
            created_photos.append(MechanicJobPhoto.objects.create(
                booking=booking,
                mechanic=request.user,
                photo_type=data.get('photo_type', 'BEFORE'),
                image_url=url,
                caption=data.get('caption', ''),
            ))

        serializer = MechanicJobPhotoSerializer(created_photos, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
