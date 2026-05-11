"""Views for payments app."""
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from django.conf import settings
import stripe

from .models import Payment, Invoice, PaymentRetry, PaymentStatus
from .serializers import (
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentInitiateSerializer,
    InvoiceSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments."""
    
    queryset = Payment.objects.all().select_related('booking', 'invoice')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id', 'gateway_transaction_id', 'booking__customer__email']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action in ['retrieve', 'webhook']:
            return PaymentDetailSerializer
        elif self.action == 'initiate':
            return PaymentInitiateSerializer
        return PaymentDetailSerializer
    
    def get_queryset(self):
        """Filter payments based on user role."""
        user = self.request.user
        
        # Customers see their own payments, admin sees all
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(booking__customer=user)
    
    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """Initiate payment for a booking."""
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get booking from request data
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response(
                {'detail': 'booking_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from bookings.models import Booking
        try:
            booking = Booking.objects.get(id=booking_id, customer=request.user)
        except Booking.DoesNotExist:
            return Response(
                {'detail': 'Booking not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        payment_method = serializer.validated_data['payment_method']
        
        # Create or get payment
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': booking.total_amount,
                'payment_method': payment_method,
                'status': PaymentStatus.PENDING,
            }
        )
        
        # Handle different payment methods
        if payment_method == 'CASH':
            payment.status = PaymentStatus.PENDING
            payment.save()
        elif payment_method == 'WALLET':
            # Check wallet balance
            if request.user.wallet_balance >= booking.total_amount:
                request.user.wallet_balance -= booking.total_amount
                request.user.save()
                payment.mark_success()
            else:
                payment.mark_failed()
                return Response(
                    {'detail': 'Insufficient wallet balance'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif payment_method == 'STRIPE':
            if not settings.STRIPE_SECRET_KEY:
                return Response(
                    {'detail': 'Stripe is not configured. Set STRIPE_SECRET_KEY in environment.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                amount_cents = int(booking.total_amount * 100)
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': settings.STRIPE_CURRENCY.lower(),
                            'product_data': {
                                'name': f'MobileMechanic Booking {booking.id}',
                                'description': getattr(booking.service, 'description', booking.service.name),
                            },
                            'unit_amount': amount_cents,
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f"{settings.STRIPE_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=f"{settings.STRIPE_CANCEL_URL}?session_id={{CHECKOUT_SESSION_ID}}",
                    metadata={
                        'payment_id': str(payment.id),
                        'booking_id': str(booking.id),
                    }
                )
            except Exception as exc:
                payment.mark_failed()
                return Response(
                    {'detail': 'Stripe checkout session creation failed', 'error': str(exc)},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            payment.gateway_transaction_id = session.id
            payment.gateway_response = {
                'checkout_session_id': session.id,
                'status': session.status,
                'url': session.url,
            }
            payment.mark_processing(gateway_txn_id=session.id)
            return Response({
                'id': payment.id,
                'status': payment.status,
                'redirect_url': session.url,
                'message': 'Redirecting to Stripe Checkout...'
            }, status=status.HTTP_200_OK)
        elif payment_method in ['JAZZCASH', 'EASYPAISA']:
            payment.mark_processing()
            return Response({
                'id': payment.id,
                'status': payment.status,
                'redirect_url': f'/payments/gateway/{payment_method}/?payment_id={payment.id}',
                'message': f'Redirecting to {payment_method}...'
            }, status=status.HTTP_200_OK)

        return Response(
            PaymentDetailSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def webhook(self, request):
        """Handle payment gateway webhook callback."""
        try:
            data = request.data
            
            gateway_name = data.get('gateway')
            transaction_id = data.get('transaction_id')
            transaction_status = data.get('status')
            
            if not all([gateway_name, transaction_id, transaction_status]):
                return Response(
                    {'detail': 'Missing required webhook fields'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find payment by gateway transaction ID
            try:
                payment = Payment.objects.get(gateway_transaction_id=transaction_id)
            except Payment.DoesNotExist:
                return Response(
                    {'detail': 'Payment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Store gateway response
            payment.gateway_response = dict(data)
            
            # Update payment status
            if transaction_status == 'SUCCESS':
                payment.mark_success()
                
                # Create invoice if not exists
                if not hasattr(payment, 'invoice'):
                    from django.utils.text import slugify
                    invoice = Invoice.objects.create(
                        payment=payment,
                        booking=payment.booking,
                        invoice_number=self._generate_invoice_number(),
                        subtotal=payment.booking.base_price,
                        discount_amount=payment.booking.discount_amount,
                        tax_amount=payment.booking.tax_amount,
                        total_amount=payment.amount
                    )
            
            elif transaction_status == 'FAILED':
                payment.mark_failed()
                payment.retry_count += 1
                
                # Log retry attempt
                PaymentRetry.objects.create(
                    payment=payment,
                    attempt_number=payment.retry_count,
                    status=PaymentStatus.FAILED,
                    error_message=data.get('error_message', '')
                )
            
            payment.save()
            return Response({'status': 'WEBHOOK_PROCESSED'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed payment."""
        payment = self.get_object()
        
        if not payment.can_retry:
            return Response(
                {'detail': 'Payment cannot be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.retry_count += 1
        payment.status = PaymentStatus.PROCESSING
        payment.save()
        
        return Response(
            PaymentDetailSerializer(payment).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        """Get invoice for a payment."""
        payment = self.get_object()
        
        if not hasattr(payment, 'invoice'):
            return Response(
                {'detail': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            InvoiceSerializer(payment.invoice).data,
            status=status.HTTP_200_OK
        )
    
    def _generate_invoice_number(self):
        """Generate unique invoice number."""
        today = timezone.now().date()
        count = Invoice.objects.filter(invoice_date__date=today).count() + 1
        return f"INV-{today.strftime('%Y%m%d')}-{count:04d}"
