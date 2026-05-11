"""Views for notifications app."""
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification, NotificationPreference
from .serializers import (
    NotificationListSerializer,
    NotificationDetailSerializer,
    NotificationCreateSerializer,
    NotificationPreferenceSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all().select_related('user')

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Notification.objects.all().select_related('user')
        return Notification.objects.filter(user=user).select_related('user')

    @action(detail=False, methods=['get'])
    def unread(self, request):
        notifications = self.get_queryset().filter(is_read=False)
        serializer = NotificationListSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if notification.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        notification.mark_read()
        return Response(NotificationDetailSerializer(notification).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return Response({'detail': 'All notifications marked as read'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def preferences(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            return Response(NotificationPreferenceSerializer(prefs).data, status=status.HTTP_200_OK)
        serializer = NotificationPreferenceSerializer(prefs, data=request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
