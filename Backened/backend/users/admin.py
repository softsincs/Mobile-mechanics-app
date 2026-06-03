from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html

from .models import (
	User,
	OTPToken,
	PasswordResetToken,
	UserSession,
	ExtendedToken,
	SecurityLog,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	model = User
	list_display = ('phone_number', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'phone_verified', 'email_verified', 'wallet_balance', 'created_at')
	list_filter = ('is_active', 'is_staff', 'phone_verified', 'email_verified')
	search_fields = ('phone_number', 'email', 'first_name', 'last_name')
	ordering = ('-created_at',)
	readonly_fields = ('id', 'created_at', 'updated_at', 'last_login')

	fieldsets = (
		(None, {'fields': ('phone_number', 'email', 'password')}),
		('Personal info', {'fields': ('first_name', 'last_name')}),
		('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('Verification', {'fields': ('phone_verified', 'email_verified')}),
		('Important dates', {'fields': ('last_login', 'created_at')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('phone_number', 'email', 'password1', 'password2'),
		}),
	)


@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
	list_display = ('code', 'user_phone', 'purpose', 'is_used', 'attempts', 'created_at', 'expires_at')
	list_filter = ('purpose', 'is_used', 'created_at')
	search_fields = ('code', 'user__phone_number', 'user__email')
	readonly_fields = ('id', 'created_at')

	def user_phone(self, obj):
		return obj.user.phone_number
	user_phone.short_description = 'User'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
	list_display = ('user_phone', 'token_short', 'is_used', 'created_at', 'expires_at')
	list_filter = ('is_used', 'created_at')
	search_fields = ('token', 'user__phone_number', 'user__email')
	readonly_fields = ('id', 'created_at', 'used_at')

	def user_phone(self, obj):
		return obj.user.phone_number

	def token_short(self, obj):
		return str(obj.token)[:12]
	token_short.short_description = 'Token'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
	list_display = ('user_phone', 'session_key_short', 'ip_address', 'login_at', 'logout_at', 'last_activity')
	list_filter = ('login_at', 'logout_at')
	search_fields = ('session_key', 'user__phone_number', 'ip_address')
	readonly_fields = ('id', 'login_at', 'logout_at', 'last_activity')

	def user_phone(self, obj):
		return obj.user.phone_number

	def session_key_short(self, obj):
		return str(obj.session_key)[:12]
	session_key_short.short_description = 'Session Key'


@admin.register(ExtendedToken)
class ExtendedTokenAdmin(admin.ModelAdmin):
	list_display = ('user_phone', 'key_short', 'created', 'expires_at')
	list_filter = ('created', 'expires_at')
	search_fields = ('key', 'user__phone_number', 'user__email')
	readonly_fields = ('id', 'created')

	def user_phone(self, obj):
		return obj.user.phone_number

	def key_short(self, obj):
		return str(obj.key)[:12]
	key_short.short_description = 'Key'


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
	list_display = ('event_type', 'user_repr', 'ip_address', 'created_at')
	list_filter = ('event_type', 'created_at')
	search_fields = ('user__phone_number', 'details')
	readonly_fields = ('id', 'created_at')

	def user_repr(self, obj):
		return obj.user.phone_number if obj.user else 'Anonymous'
	user_repr.short_description = 'User'

