"""Django admin for payments app."""
from django.contrib import admin
from django.utils.html import format_html

from .models import Payment, Invoice, PaymentRetry


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for payments."""
    
    list_display = [
        'id',
        'booking',
        'amount_display',
        'payment_method',
        'status_badge',
        'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at', 'updated_at']
    search_fields = ['id', 'booking__id', 'booking__customer__email', 'gateway_transaction_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'gateway_response']
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('id', 'booking', 'amount', 'currency', 'payment_method')
        }),
        ('Status', {
            'fields': ('status', 'completed_at')
        }),
        ('Gateway', {
            'fields': ('gateway_transaction_id', 'gateway_response'),
            'classes': ('collapse',)
        }),
        ('Retry', {
            'fields': ('retry_count', 'max_retries'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def amount_display(self, obj):
        return f"PKR {obj.amount}"
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFA500',
            'PROCESSING': '#0099CC',
            'SUCCESS': '#00AA00',
            'FAILED': '#CC0000',
            'REFUNDED': '#9933CC',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin interface for invoices."""
    
    list_display = [
        'invoice_number',
        'booking',
        'total_amount_display',
        'sent_status',
        'invoice_date'
    ]
    list_filter = ['is_sent', 'invoice_date', 'created_at']
    search_fields = ['invoice_number', 'booking__id', 'payment__booking__customer__email']
    readonly_fields = ['id', 'invoice_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invoice Info', {
            'fields': ('id', 'invoice_number', 'payment', 'booking')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total_amount')
        }),
        ('Distribution', {
            'fields': ('is_sent', 'sent_at', 'pdf_path'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('invoice_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-invoice_date']
    
    def total_amount_display(self, obj):
        return f"PKR {obj.total_amount}"
    total_amount_display.short_description = 'Total'
    
    def sent_status(self, obj):
        color = '#00AA00' if obj.is_sent else '#CC0000'
        status_text = 'Sent' if obj.is_sent else 'Pending'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            status_text
        )
    sent_status.short_description = 'Status'


@admin.register(PaymentRetry)
class PaymentRetryAdmin(admin.ModelAdmin):
    """Admin interface for payment retries."""
    
    list_display = [
        'payment',
        'attempt_number',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['payment__id', 'error_message']
    readonly_fields = ['id', 'created_at', 'payment']
    
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        """Prevent manual creation of retry records."""
        return False
