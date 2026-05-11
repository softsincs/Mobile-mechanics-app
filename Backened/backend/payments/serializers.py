"""Serializers for payments app."""
from rest_framework import serializers
from decimal import Decimal

from .models import Payment, Invoice, PaymentRetry, PaymentStatus


class PaymentRetrySerializer(serializers.ModelSerializer):
    """Serializer for payment retry records."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PaymentRetry
        fields = ['id', 'attempt_number', 'status', 'status_display', 'error_message', 'created_at']
        read_only_fields = ['id', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices."""
    
    booking_service = serializers.CharField(source='booking.service.name', read_only=True)
    customer_name = serializers.CharField(source='booking.customer.get_full_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'booking', 'booking_service',
            'customer_name', 'subtotal', 'discount_amount', 'tax_amount', 'total_amount',
            'is_sent', 'sent_at', 'notes', 'invoice_date', 'created_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'invoice_date', 'created_at']


class PaymentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for payment list view."""
    
    booking_service = serializers.CharField(source='booking.service.name', read_only=True)
    customer_email = serializers.CharField(source='booking.customer.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'booking_service', 'customer_email', 'amount',
            'payment_method', 'payment_method_display', 'status', 'status_display',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Full serializer for payment detail view."""
    
    # Nested read-only fields
    booking = serializers.StringRelatedField(read_only=True)
    invoice = InvoiceSerializer(read_only=True, allow_null=True)
    retries = PaymentRetrySerializer(many=True, read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'amount', 'currency', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'gateway_transaction_id', 'gateway_response',
            'retry_count', 'max_retries', 'created_at', 'updated_at', 'completed_at',
            'invoice', 'retries'
        ]
        read_only_fields = [
            'id', 'booking', 'gateway_response', 'created_at', 'updated_at',
            'invoice', 'retries'
        ]


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating payment."""
    
    payment_method = serializers.ChoiceField(
        choices=['JAZZCASH', 'EASYPAISA', 'STRIPE', 'CASH', 'WALLET']
    )
    gateway_transaction_id = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class PaymentWebhookSerializer(serializers.Serializer):
    """Serializer for payment gateway webhook."""
    
    gateway_name = serializers.CharField()
    transaction_id = serializers.CharField()
    transaction_status = serializers.ChoiceField(
        choices=['SUCCESS', 'FAILED', 'PENDING']
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    error_code = serializers.CharField(required=False, allow_blank=True)
    error_message = serializers.CharField(required=False, allow_blank=True)
