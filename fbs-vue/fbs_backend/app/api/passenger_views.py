from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count
from django.utils import timezone
import csv
from django.http import HttpResponse
from ..models import PassengerInfo, BookingDetail
from ..serializers import PassengerInfoSerializer

class PassengerInfoViewSet(viewsets.ModelViewSet):
    queryset = PassengerInfo.objects.all()
    serializer_class = PassengerInfoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        passenger_type = self.request.query_params.get('type')
        if passenger_type:
            queryset = queryset.filter(passenger_type=passenger_type)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(passport_number__icontains=search)
            )
        return queryset.order_by('id')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = self.get_queryset().count()
        return Response({'total': total})

    @action(detail=False, methods=['get'])
    def export(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="passengers_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Type'])
        for p in self.get_queryset():
            writer.writerow([p.first_name, p.last_name, p.passenger_type])
        return response
