from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..models import (
    Airline, Airport, Aircraft, SeatClass, AddOnType, 
    TaxType, AirportFee, AirlineTax, PassengerTypeTaxRate
)
from ..serializers import (
    AirlineSerializer, AirportSerializer, AircraftSerializer, 
    SeatClassSerializer, AddOnTypeSerializer, TaxTypeSerializer,
    AirportFeeSerializer, AirlineTaxSerializer, PassengerTypeTaxRateSerializer
)

class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    @action(detail=False, methods=['get'])
    def export(self, request):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="airlines_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['code', 'name', 'country', 'is_active'])
        for a in self.get_queryset():
            writer.writerow([a.code, a.name, a.country, a.is_active])
        return response

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    @action(detail=False, methods=['get'])
    def export(self, request):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="airports_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['code', 'name', 'city', 'country', 'airport_type'])
        for a in self.get_queryset():
            writer.writerow([a.code, a.name, a.city, a.country, a.airport_type])
        return response

class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    @action(detail=True, methods=['post'], url_path='save-layout')
    def save_layout(self, request, pk=None):
        aircraft = self.get_object()
        config_data = request.data.get('layout_config', {})
        seat_classes = config_data.get('seat_classes', [])
        
        if not seat_classes:
            return Response({'error': 'layout_config.seat_classes is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        total_seats = sum(c.get('class_capacity', c.get('rows', 0) * c.get('columns', 0)) for c in seat_classes)
        if total_seats > aircraft.capacity:
            return Response({'error': f'Layout has {total_seats} units but capacity is {aircraft.capacity}'}, status=status.HTTP_400_BAD_REQUEST)
        
        aircraft.save_layout({'seat_classes': seat_classes, 'total_seats': total_seats})
        return Response({'success': True, 'message': f'Layout saved to {aircraft.model}'})

    @action(detail=True, methods=['get'], url_path='layout')
    def get_layout(self, request, pk=None):
        aircraft = self.get_object()
        return Response({
            'aircraft_id': aircraft.id,
            'model': aircraft.model,
            'capacity': aircraft.capacity,
            'layout': aircraft.get_layout_config()
        })

class SeatClassViewSet(viewsets.ModelViewSet):
    queryset = SeatClass.objects.all()
    serializer_class = SeatClassSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class AddOnTypeViewSet(viewsets.ModelViewSet):
    queryset = AddOnType.objects.all()
    serializer_class = AddOnTypeSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class TaxTypeViewSet(viewsets.ModelViewSet):
    queryset = TaxType.objects.all()
    serializer_class = TaxTypeSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class AirportFeeViewSet(viewsets.ModelViewSet):
    queryset = AirportFee.objects.select_related('airport', 'tax_type').all()
    serializer_class = AirportFeeSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class AirlineTaxViewSet(viewsets.ModelViewSet):
    queryset = AirlineTax.objects.select_related('airline', 'tax_type').all()
    serializer_class = AirlineTaxSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class PassengerTypeTaxRateViewSet(viewsets.ModelViewSet):
    queryset = PassengerTypeTaxRate.objects.select_related('tax_type').all()
    serializer_class = PassengerTypeTaxRateSerializer
    permission_classes = [AllowAny]
    pagination_class = None
