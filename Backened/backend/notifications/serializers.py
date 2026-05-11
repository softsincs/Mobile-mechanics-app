"""Serializers for notifications app."""
from rest_framework import serializers

from .models import Notification, NotificationPreference


class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'channel', 'is_read', 'created_at']
        read_only_fields = fields


class NotificationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'channel', 'metadata',
            'related_object_id', 'is_sent', 'sent_at', 'is_read', 'read_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'notification_type', 'channel', 'metadata', 'related_object_id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled']
