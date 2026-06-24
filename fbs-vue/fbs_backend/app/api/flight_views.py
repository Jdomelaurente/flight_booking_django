from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Route, Flight, Schedule, Seat, SeatRequirement, SeatClass
from ..serializers import (
    RouteSerializer, FlightSerializer, ScheduleSerializer, 
    SeatSerializer, SeatRequirementSerializer
)
from ..pagination import OptionalPagination

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    @action(detail=False, methods=['get'])
    def export(self, request):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="routes_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['origin_code', 'destination_code', 'base_price'])
        for r in self.get_queryset():
            writer.writerow([
                r.origin_airport.code if r.origin_airport else '',
                r.destination_airport.code if r.destination_airport else '',
                r.base_price
            ])
        return response

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [AllowAny]
    pagination_class = OptionalPagination

    def get_queryset(self):
        from django.db.models import Q
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        airline = self.request.query_params.get('airline')
        
        if search:
            queryset = queryset.filter(flight_number__icontains=search)
            
        if airline and airline != 'all':
            queryset = queryset.filter(airline_id=airline)
            
        return queryset

    @action(detail=False, methods=['get'])
    def export(self, request):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="flights_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['flight_number', 'airline_code', 'aircraft_id', 'route_id', 'total_stops'])
        for f in self.get_queryset():
            writer.writerow([
                f.flight_number,
                f.airline.code if f.airline else '',
                f.aircraft.id if f.aircraft else '',
                f.route.id if f.route else '',
                f.total_stops
            ])
        return response

class SeatRequirementViewSet(viewsets.ModelViewSet):
    queryset = SeatRequirement.objects.all()
    serializer_class = SeatRequirementSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all().select_related(
        'flight', 'flight__airline', 'flight__aircraft', 
        'flight__route', 'flight__route__origin_airport', 
        'flight__route__destination_airport'
    ).order_by('-departure_time')
    serializer_class = ScheduleSerializer
    permission_classes = [AllowAny]
    pagination_class = OptionalPagination

    def get_queryset(self):
        Schedule.update_all_statuses()
        from django.db.models import Q
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        status_filter = self.request.query_params.get('status')
        stops_filter = self.request.query_params.get('stops')
        
        if search:
            queryset = queryset.filter(
                Q(flight__flight_number__icontains=search) |
                Q(id__icontains=search)
            )
            
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status__iexact=status_filter)
            
        if stops_filter and stops_filter != 'all':
            try:
                stops = int(stops_filter)
                if stops == 3:
                    queryset = queryset.filter(flight__total_stops__gte=3)
                else:
                    queryset = queryset.filter(flight__total_stops=stops)
            except ValueError:
                pass
                
        return queryset

    @action(detail=False, methods=['get'])
    def export(self, request):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="schedules_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['flight_number', 'departure_time', 'arrival_time', 'price', 'status'])
        for s in self.get_queryset():
            writer.writerow([
                s.flight.flight_number if s.flight else '',
                s.departure_time.strftime('%Y-%m-%d %H:%M') if s.departure_time else '',
                s.arrival_time.strftime('%Y-%m-%d %H:%M') if s.arrival_time else '',
                s.price,
                s.status
            ])
        return response

    @action(detail=False, methods=['get'])
    def stats(self, request):
        Schedule.update_all_statuses()
        active = Schedule.objects.filter(status__iexact='On Flight').count()
        open_count = Schedule.objects.filter(status__iexact='Open').count()
        arrived = Schedule.objects.filter(status__iexact='Arrived').count()
        total = Schedule.objects.count()
        
        return Response({
            'total': total,
            'open': open_count,
            'active': active,
            'arrived': arrived
        })

    @action(detail=True, methods=['post'], url_path='generate-seats')
    def generate_seats(self, request, pk=None):
        schedule = self.get_object()
        config_data = request.data.get('layout_config', {})
        seat_classes = config_data.get('seat_classes', [])
        
        if not seat_classes:
            return Response({'error': 'layout_config.seat_classes is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic():
                existing_seats = Seat.objects.filter(schedule=schedule)
                existing_map = {f"{s.row}-{s.column}": s for s in existing_seats}
                processed_seat_ids = []
                
                for sc_config in seat_classes:
                    class_id = sc_config.get('class_id')
                    rows = sc_config.get('rows', 0)
                    columns = sc_config.get('columns', 0)
                    start_row = sc_config.get('start_row', 1)
                    
                    try:
                        seat_class = SeatClass.objects.get(id=class_id)
                    except SeatClass.DoesNotExist:
                        continue
                        
                    for r in range(rows):
                        row_num = start_row + r
                        for c in range(columns):
                            col_label = chr(64 + c + 1)
                            seat_key = f"{row_num}-{col_label}"
                            
                            seat_data = {
                                'schedule': schedule,
                                'seat_class': seat_class,
                                'seat_number': f"{row_num}{col_label}",
                                'row': row_num,
                                'column': col_label,
                                'is_available': True
                            }
                            
                            if seat_key in existing_map:
                                seat = existing_map[seat_key]
                                seat.seat_class = seat_class
                                seat.save()
                                processed_seat_ids.append(seat.id)
                            else:
                                seat = Seat.objects.create(**seat_data)
                                processed_seat_ids.append(seat.id)
                
                Seat.objects.filter(schedule=schedule).exclude(id__in=processed_seat_ids).delete()
                return Response({'success': True, 'message': 'Seats generated successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['schedule', 'seat_class']

    @action(detail=True, methods=['post'], url_path='lock')
    def lock_seat(self, request, pk=None):
        """Temporarily lock a seat for a session to prevent double booking"""
        seat = self.get_object()
        session_id = request.data.get('session_id')
        duration_minutes = int(request.data.get('duration', 10))

        if not session_id:
            return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Refresh and lock the row for update
            seat = Seat.objects.select_for_update().get(id=seat.id)
            
            # 1. Check if permanently booked
            is_permanently_booked = BookingDetail.objects.filter(
                seat=seat,
                status__in=['pending', 'confirmed', 'checkin', 'boarding', 'completed']
            ).exists()
            
            if is_permanently_booked:
                return Response({'error': 'Seat is already booked'}, status=status.HTTP_409_CONFLICT)
            
            # 2. Check if locked by SOMEONE ELSE
            if seat.is_locked and seat.locked_by_session != session_id:
                return Response({'error': 'Seat is currently locked by another user'}, status=status.HTTP_423_LOCKED)
            
            # 3. Apply/Extend the lock
            seat.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
            seat.locked_by_session = session_id
            seat.save()
            
            return Response({
                'success': True, 
                'seat_number': seat.seat_number,
                'locked_until': seat.locked_until
            })

    @action(detail=False, methods=['post'], url_path='bulk-reset')
    def bulk_reset(self, request):
        schedule_id = request.data.get('schedule_id')
        if not schedule_id:
            return Response({"error": "Schedule ID is required"}, status=400)
        updated_count = Seat.objects.filter(schedule_id=schedule_id).update(is_available=True)
        return Response({"message": f"Successfully reset {updated_count} seats.", "count": updated_count})

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        seats_data = request.data.get('seats', [])
        if not isinstance(seats_data, list):
            return Response({"error": "Seats must be a list"}, status=status.HTTP_400_BAD_REQUEST)
        
        created_count = 0
        for seat_data in seats_data:
            serializer = self.get_serializer(data=seat_data)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
        return Response({'success': True, 'created_count': created_count})
