from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Sum
from django.utils import timezone
from ..models import Booking, BookingDetail, BookingTax, Payment
from ..serializers import (
    BookingSerializer, BookingDetailSerializer, 
    BookingTaxSerializer, PaymentSerializer
)

class BookingViewSet(viewsets.ModelViewSet):
    """
    Unified Booking ViewSet for managing flight bookings.
    """
    queryset = Booking.objects.select_related('user').prefetch_related('details').all()
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Booking.objects.count()
        pending = Booking.objects.filter(status='Pending').count()
        confirmed = Booking.objects.filter(status='Confirmed').count()
        return Response({'total': total, 'pending': pending, 'confirmed': confirmed})
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        total = Booking.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        breakdown = {
            'tickets': Booking.objects.aggregate(sum=Sum('base_fare_total'))['sum'] or 0,
            'addons': Booking.objects.aggregate(sum=Sum('insurance_total'))['sum'] or 0,
            'taxes': Booking.objects.aggregate(sum=Sum('tax_total'))['sum'] or 0
        }
        return Response({'total': float(total), 'breakdown': breakdown})

class BookingDetailViewSet(viewsets.ModelViewSet):
    queryset = BookingDetail.objects.all()
    serializer_class = BookingDetailSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class BookingTaxViewSet(viewsets.ModelViewSet):
    queryset = BookingTax.objects.select_related('booking', 'tax_type').all()
    serializer_class = BookingTaxSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by('-payment_date')
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]
    pagination_class = None
