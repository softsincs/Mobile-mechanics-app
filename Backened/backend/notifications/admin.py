from django.contrib import admin

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id_short', 'user_phone', 'title', 'notification_type', 'channel', 'is_read', 'is_sent', 'created_at']
    list_filter = ['notification_type', 'channel', 'is_read', 'is_sent', 'created_at']
    search_fields = ['user__phone_number', 'title', 'message']
    readonly_fields = ['id', 'created_at', 'updated_at', 'sent_at', 'read_at']

    def id_short(self, obj):
        return str(obj.id)[:8]

    def user_phone(self, obj):
        return obj.user.phone_number


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user_phone', 'email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled']
    search_fields = ['user__phone_number']

    def user_phone(self, obj):
        return obj.user.phone_number
