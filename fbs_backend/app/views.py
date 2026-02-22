from django.contrib.auth import authenticate
from django.db import transaction, models
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
import random

from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status, filters
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    AirlineTax, Booking, BookingDetail, BookingTax, CheckInDetail, 
    PassengerTypeTaxRate, Route, TrackLog, AirportFee, TaxType,
    Airline, Airport, Aircraft, SeatClass, AddOnType, Flight, Schedule, 
    Seat, PassengerInfo, SeatRequirement, Students, Payment
)
from fbs_instructor.models import Instructor
from .serializers import (
    AirlineSerializer, AirlineTaxSerializer, AirportSerializer, 
    AircraftSerializer, BookingDetailSerializer, BookingTaxSerializer,
    CheckInDetailSerializer, CheckInListSerializer, SeatClassSerializer, 
    AddOnTypeSerializer, RouteSerializer, FlightSerializer, ScheduleSerializer,
    SeatSerializer, PassengerInfoSerializer, TrackLogSerializer,
    AirportFeeSerializer, TaxTypeSerializer, PassengerTypeTaxRateSerializer,
    BookingSerializer, SeatRequirementSerializer, StudentsSerializer, InstructorsSerializer,
    PaymentSerializer
)


# ==========================================
# AUTHENTICATION VIEW
# ==========================================
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user and user.is_staff:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'success': True,
                'token': token.key,
                'user': {
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
            
        return Response({
            'success': False, 
            'message': 'Invalid admin credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


# ==========================================
# MANAGE FLIGHT
# ==========================================
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [AllowAny]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [AllowAny]


class SeatRequirementViewSet(viewsets.ModelViewSet):
    queryset = SeatRequirement.objects.all()
    serializer_class = SeatRequirementSerializer
    permission_classes = [AllowAny]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by('-payment_date')
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        now = timezone.now()
        today = now.date()
        
        active = Schedule.objects.filter(
            departure_time__lte=now,
            arrival_time__gte=now
        ).count()
        
        scheduled_today = Schedule.objects.filter(
            departure_time__date=today
        ).count()
        
        upcoming = Schedule.objects.filter(
            departure_time__gte=now,
            departure_time__date=today
        ).count()
        
        return Response({
            'active': active,
            'scheduled': scheduled_today,
            'upcoming': upcoming
        })

    @action(detail=True, methods=['post'], url_path='generate-seats')
    def generate_seats(self, request, pk=None):
        """Generate seats for this schedule based on layout config"""
        schedule = self.get_object()
        
        config_data = request.data.get('layout_config', {})
        seat_classes = config_data.get('seat_classes', [])
        
        if not seat_classes:
            return Response(
                {'error': 'layout_config.seat_classes is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            with transaction.atomic():
                # Get existing seats to avoid duplicates or identify updates
                existing_seats = Seat.objects.filter(schedule=schedule)
                existing_map = {f"{s.row}-{s.column}": s for s in existing_seats}
                
                created_count = 0
                updated_count = 0
                
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
                            col_num = c + 1
                            col_label = chr(64 + col_num) # 1=A, 2=B, etc.
                            
                            seat_key = f"{row_num}-{col_label}"
                            
                            # Determine basic features based on position
                            is_window = (col_num == 1 or col_num == columns)
                            is_aisle = False
                            
                            # Simple aisle logic (assuming 2 aisles for wide body, 1 for narrow)
                            if columns == 6: # 3-3 => Aisle between 3 and 4
                                is_aisle = (col_num == 3 or col_num == 4)
                            elif columns == 4: # 2-2 => Aisle between 2 and 3
                                is_aisle = (col_num == 2 or col_num == 3)
                                
                            seat_data = {
                                'schedule': schedule,
                                'seat_class': seat_class,
                                'seat_number': f"{row_num}{col_label}",
                                'row': row_num,
                                'column': col_label,
                                'is_window': is_window,
                                'is_aisle': is_aisle,
                                'is_available': True
                            }
                            
                            if seat_key in existing_map:
                                # Update existing seat class if changed
                                seat = existing_map[seat_key]
                                processed_seat_ids.append(seat.id)
                                if seat.seat_class_id != class_id:
                                    seat.seat_class = seat_class
                                    seat.save()
                                    updated_count += 1
                            else:
                                # Create new seat
                                seat = Seat.objects.create(**seat_data)
                                created_count += 1
                                processed_seat_ids.append(seat.id)

                
                # Delete seats that are no longer in the layout
                seats_to_delete = Seat.objects.filter(schedule=schedule).exclude(id__in=processed_seat_ids)
                deleted_count = seats_to_delete.count()
                seats_to_delete.delete()

                return Response({
                    'success': True,
                    'message': f'Generated {created_count} new seats, updated {updated_count} seats, deleted {deleted_count} obsolete seats',
                    'created': created_count,
                    'updated': updated_count,
                    'deleted': deleted_count
                })
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['schedule', 'seat_class']

    @action(detail=False, methods=['post'], url_path='bulk-reset')
    def bulk_reset(self, request):
        schedule_id = request.data.get('schedule_id')
        if not schedule_id:
            return Response({"error": "Schedule ID is required"}, status=400)
        
        updated_count = Seat.objects.filter(schedule_id=schedule_id).update(is_available=True)
        
        return Response({
            "message": f"Successfully reset {updated_count} seats to available.",
            "count": updated_count
        })

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """
        Bulk create seats for a schedule.
        Expects: { "seats": [ { seat data }, ... ] }
        """
        seats_data = request.data.get('seats', [])
        
        if not seats_data:
            return Response(
                {"error": "No seats provided. Expected format: {'seats': [...]}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(seats_data, list):
            return Response(
                {"error": "Seats must be a list"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_seats = []
        errors = []
        
        for index, seat_data in enumerate(seats_data):
            try:
                # Validate required fields
                required_fields = ['schedule', 'seat_class', 'seat_number', 'row', 'column']
                missing_fields = [f for f in required_fields if f not in seat_data]
                
                if missing_fields:
                    errors.append({
                        'index': index,
                        'error': f"Missing required fields: {missing_fields}",
                        'data': seat_data
                    })
                    continue
                
                # Check if seat already exists for this schedule
                existing = Seat.objects.filter(
                    schedule_id=seat_data.get('schedule'),
                    seat_number=seat_data.get('seat_number')
                ).first()
                
                if existing:
                    errors.append({
                        'index': index,
                        'error': f"Seat {seat_data.get('seat_number')} already exists",
                        'seat_number': seat_data.get('seat_number')
                    })
                    continue
                
                # Create seat
                serializer = self.get_serializer(data=seat_data)
                if serializer.is_valid():
                    seat = serializer.save()
                    created_seats.append(serializer.data)
                else:
                    errors.append({
                        'index': index,
                        'error': serializer.errors,
                        'data': seat_data
                    })
                    
            except Exception as e:
                errors.append({
                    'index': index,
                    'error': str(e),
                    'data': seat_data
                })
        
        # Return appropriate response
        if created_seats:
            return Response({
                'success': True,
                'created_count': len(created_seats),
                'errors': errors,
                'seats': created_seats
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': 'No seats were created',
                'details': errors
            }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# ASSET VIEWSETS 
# ==========================================
class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [AllowAny]


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [AllowAny]


# views.py

class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'], url_path='save-layout')
    def save_layout(self, request, pk=None):
        """Save seat layout template to this aircraft"""
        aircraft = self.get_object()
        
        config_data = request.data.get('layout_config', {})
        seat_classes = config_data.get('seat_classes', [])
        
        if not seat_classes:
            return Response(
                {'error': 'layout_config.seat_classes is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate total seats don't exceed capacity
        total_seats = sum(c.get('rows', 0) * c.get('columns', 0) for c in seat_classes)
        if total_seats > aircraft.capacity:
            return Response(
                {'error': f'Layout has {total_seats} seats but aircraft capacity is {aircraft.capacity}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save to aircraft
        aircraft.save_layout({
            'seat_classes': seat_classes,
            'total_seats': total_seats
        })
        
        return Response({
            'success': True,
            'message': f'Layout saved to {aircraft.model}',
            'aircraft_id': aircraft.id,
            'total_seats': total_seats,
            'layout_config': aircraft.layout_config
        })

    @action(detail=True, methods=['get'], url_path='layout')
    def get_layout(self, request, pk=None):
        """Get layout configuration for this aircraft"""
        aircraft = self.get_object()
        config = aircraft.get_layout_config()
        
        return Response({
            'aircraft_id': aircraft.id,
            'model': aircraft.model,
            'capacity': aircraft.capacity,
            'has_custom_layout': bool(aircraft.layout_config),
            'layout': config
        })

class SeatClassViewSet(viewsets.ModelViewSet):
    queryset = SeatClass.objects.all()
    serializer_class = SeatClassSerializer
    permission_classes = [AllowAny]


class AddOnTypeViewSet(viewsets.ModelViewSet):
    queryset = AddOnType.objects.all()
    serializer_class = AddOnTypeSerializer
    permission_classes = [AllowAny]


# ==========================================
# BOOKING DETAIL VIEWSET (for check-ins)
# ==========================================
class BookingDetailViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing booking details (for check-ins).
    """
    queryset = BookingDetail.objects.all()
    serializer_class = BookingDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'passenger', 
            'schedule', 
            'schedule__flight',
            'schedule__flight__route',
            'seat'
        )
        
        flight_number = self.request.query_params.get('flight')
        if flight_number:
            queryset = queryset.filter(schedule__flight__flight_number=flight_number)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        date_filter = self.request.query_params.get('date')
        if date_filter:
            queryset = queryset.filter(schedule__departure_time__date=date_filter)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(passenger__first_name__icontains=search) |
                Q(passenger__last_name__icontains=search) |
                Q(schedule__flight__flight_number__icontains=search)
            )
        
        return queryset.order_by('id')

    @action(detail=False, methods=['get'])
    def today_checkins(self, request):
        today = timezone.now().date()
        checkins = self.get_queryset().filter(
            schedule__departure_time__date=today,
            status__in=['checkin', 'boarding']
        )
        
        serializer = self.get_serializer(checkins, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        booking_detail = self.get_object()
        
        if booking_detail.status in ['checkin', 'boarding', 'completed']:
            return Response(
                {'error': 'Passenger already checked in or boarded.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking_detail.status = 'checkin'
        booking_detail.save()
        
        boarding_pass = f"{booking_detail.schedule.flight.flight_number}-{booking_detail.id}-{random.randint(1000, 9999)}"
        
        return Response({
            'success': True,
            'message': 'Passenger checked in successfully.',
            'boarding_pass': boarding_pass,
            'seat': booking_detail.seat.seat_number if booking_detail.seat else None
        })

    @action(detail=True, methods=['post'])
    def update_baggage(self, request, pk=None):
        booking_detail = self.get_object()
        
        baggage_count = request.data.get('baggage_count', 0)
        baggage_weight = request.data.get('baggage_weight', 0.0)
        
        return Response({
            'success': True,
            'message': 'Baggage information updated.',
            'baggage_count': baggage_count,
            'baggage_weight': baggage_weight
        })


# ==========================================
# PASSENGERS VIEWSETS 
# ==========================================
class PassengerInfoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing passenger information.
    """
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
        
        has_booking = self.request.query_params.get('has_booking')
        if has_booking == 'yes':
            passenger_ids = BookingDetail.objects.values_list('passenger_id', flat=True).distinct()
            queryset = queryset.filter(id__in=passenger_ids)
        elif has_booking == 'no':
            passenger_ids = BookingDetail.objects.values_list('passenger_id', flat=True).distinct()
            queryset = queryset.exclude(id__in=passenger_ids)
        
        return queryset.select_related('linked_adult').order_by('id')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get passenger statistics (combined stats).
        """
        total = self.get_queryset().count()
        adults = self.get_queryset().filter(passenger_type='Adult').count()
        children = self.get_queryset().filter(passenger_type='Child').count()
        infants = self.get_queryset().filter(passenger_type='Infant').count()
        
        passengers_with_bookings = self.get_queryset().filter(
            id__in=BookingDetail.objects.values_list('passenger_id', flat=True).distinct()
        ).count()
        
        today = timezone.now().date()
        today_count = self.get_queryset().filter(
            bookingdetail__booking_date__date=today
        ).distinct().count()
        
        return Response({
            'total': total,
            'adults': adults,
            'children': children,
            'infants': infants,
            'with_bookings': passengers_with_bookings,
            'without_bookings': total - passengers_with_bookings,
            'today': today_count
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="passengers_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Type', 'Date of Birth', 'Passport', 'Nationality', 'Bookings Count'])
        
        passengers = self.get_queryset()
        for passenger in passengers:
            booking_count = BookingDetail.objects.filter(passenger=passenger).count()
            writer.writerow([
                passenger.first_name,
                passenger.last_name,
                passenger.passenger_type,
                passenger.date_of_birth,
                passenger.passport_number or '',
                passenger.nationality or '',
                booking_count
            ])
        
        return response


# ==========================================
# STUDENTS VIEWSET
# ==========================================
class StudentsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student information.
    """
    queryset = Students.objects.all().order_by('id')
    serializer_class = StudentsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        gender = self.request.query_params.get('gender')
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(student_number__icontains=search) |
                Q(email__icontains=search)
            )
            
        if gender:
            queryset = queryset.filter(gender=gender)
            
        return queryset



# ==========================================
# INSTRUCTORS VIEWSET
# ==========================================
class InstructorsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing instructor information.
    """
    queryset = Instructor.objects.all().order_by('id')
    serializer_class = InstructorsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(instructor_id__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset


# ==========================================
# CHECK-IN VIEWS
# ==========================================
class CheckInDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing check-in details
    """
    queryset = CheckInDetail.objects.select_related(
        'booking_detail',
        'booking_detail__passenger',
        'booking_detail__schedule',
        'booking_detail__schedule__flight',
        'booking_detail__schedule__flight__route',
        'booking_detail__schedule__flight__route__origin_airport',
        'booking_detail__schedule__flight__route__destination_airport',
    ).all()
    
    serializer_class = CheckInDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'flight_number', 'check_in_counter']
    search_fields = [
        'booking_detail__passenger__first_name',
        'booking_detail__passenger__last_name',
        'boarding_pass',
        'booking_detail__schedule__flight__flight_number',
    ]
    ordering_fields = ['check_in_time', 'departure_time', 'created_at']
    ordering = ['-check_in_time']
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CheckInListSerializer
        return CheckInDetailSerializer
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        today_checkins = self.get_queryset().filter(
            check_in_time__date__gte=today,
            check_in_time__date__lt=tomorrow
        )
        
        page = self.paginate_queryset(today_checkins)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(today_checkins, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_checkins = self.get_queryset().count()
        
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        todays_checkins = self.get_queryset().filter(
            check_in_time__date__gte=today,
            check_in_time__date__lt=tomorrow
        ).count()
        
        status_stats = self.get_queryset().values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        baggage_stats = self.get_queryset().aggregate(
            total_baggage=Sum('baggage_count'),
            avg_baggage_weight=Avg('baggage_weight')
        )
        
        pending_bookings = BookingDetail.objects.filter(
            status='confirmed',
            checkins__isnull=True
        ).count()
        
        return Response({
            'total_checkins': total_checkins,
            'todays_checkins': todays_checkins,
            'status_stats': {stat['status']: stat['count'] for stat in status_stats},
            'baggage_stats': baggage_stats,
            'pending_checkins': pending_bookings,
        })
    
    @action(detail=True, methods=['post'])
    def print_boarding_pass(self, request, pk=None):
        checkin = self.get_object()
        
        if not checkin.boarding_pass:
            checkin.boarding_pass = checkin.generate_boarding_pass()
            checkin.save()
        
        return Response({
            'message': 'Boarding pass ready for printing',
            'boarding_pass': checkin.boarding_pass,
            'passenger_name': checkin.passenger_name,
            'flight_number': checkin.flight_number,
            'seat_number': checkin.seat_number,
            'departure_time': checkin.departure_time,
            'gate_number': checkin.gate_number or 'TBD',
        })
    
    @action(detail=False, methods=['post'])
    def bulk_checkin(self, request):
        booking_detail_ids = request.data.get('booking_detail_ids', [])
        check_in_counter = request.data.get('check_in_counter')
        agent_id = request.data.get('agent_id')
        
        if not booking_detail_ids:
            return Response(
                {'error': 'No booking detail IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_checkins = []
        errors = []
        
        for booking_detail_id in booking_detail_ids:
            try:
                booking_detail = BookingDetail.objects.get(id=booking_detail_id, status='confirmed')
                
                if CheckInDetail.objects.filter(
                    booking_detail=booking_detail,
                    status__in=['checked-in', 'boarding']
                ).exists():
                    errors.append(f"Booking {booking_detail_id} already checked in")
                    continue
                
                checkin = CheckInDetail.objects.create(
                    booking_detail=booking_detail,
                    check_in_counter=check_in_counter,
                    agent_id=agent_id,
                    status='checked-in',
                    seat_assignment=booking_detail.seat.seat_number if booking_detail.seat else None
                )
                
                created_checkins.append(checkin.id)
                
            except BookingDetail.DoesNotExist:
                errors.append(f"Booking {booking_detail_id} not found or not confirmed")
            except Exception as e:
                errors.append(f"Error checking in booking {booking_detail_id}: {str(e)}")
        
        return Response({
            'success': len(created_checkins),
            'failed': len(errors),
            'created_checkins': created_checkins,
            'errors': errors
        })
    
    @action(detail=False, methods=['get'])
    def pending_bookings(self, request):
        pending_bookings = BookingDetail.objects.filter(
            status='confirmed',
            checkins__isnull=True,
            schedule__departure_time__gt=timezone.now()
        ).select_related(
            'passenger',
            'schedule',
            'schedule__flight',
            'schedule__flight__route'
        )
        
        search_query = request.query_params.get('search', None)
        if search_query:
            pending_bookings = pending_bookings.filter(
                Q(passenger__first_name__icontains=search_query) |
                Q(passenger__last_name__icontains=search_query) |
                Q(schedule__flight__flight_number__icontains=search_query) |
                Q(passenger__passport_number__icontains=search_query)
            )
        
        flight_number = request.query_params.get('flight', None)
        if flight_number:
            pending_bookings = pending_bookings.filter(
                schedule__flight__flight_number=flight_number
            )
        
        data = []
        for booking in pending_bookings:
            data.append({
                'id': booking.id,
                'passenger_name': booking.passenger.get_full_name(),
                'passport_number': booking.passenger.passport_number,
                'flight_number': booking.schedule.flight.flight_number,
                'route': str(booking.schedule.flight.route),
                'departure_time': booking.schedule.departure_time,
                'seat_class': booking.seat_class.name if booking.seat_class else None,
                'seat_number': booking.seat.seat_number if booking.seat else None,
            })
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        checkin = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_transitions = {
            'pending': ['checked-in', 'cancelled', 'no_show'],
            'checked-in': ['boarding', 'completed', 'cancelled'],
            'boarding': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': [],
            'no_show': [],
        }
        
        if new_status not in valid_transitions.get(checkin.status, []):
            return Response(
                {'error': f'Cannot transition from {checkin.status} to {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        checkin.status = new_status
        checkin.save()
        
        serializer = self.get_serializer(checkin)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="checkins_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Check-in ID', 'Passenger Name', 'Flight Number', 'Route',
            'Departure Time', 'Check-in Time', 'Seat Number', 'Baggage Count',
            'Baggage Weight', 'Boarding Pass', 'Status', 'Check-in Counter', 'Gate Number'
        ])
        
        for checkin in queryset:
            writer.writerow([
                checkin.id, checkin.passenger_name, checkin.flight_number,
                checkin.route, checkin.departure_time, checkin.check_in_time,
                checkin.seat_number, checkin.baggage_count, checkin.baggage_weight,
                checkin.boarding_pass, checkin.get_status_display(),
                checkin.check_in_counter, checkin.gate_number
            ])
        
        return response


class CheckInDashboardView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        today_checkins = CheckInDetail.objects.filter(
            check_in_time__date__gte=today,
            check_in_time__date__lt=tomorrow
        )
        
        stats = {
            'total_today': today_checkins.count(),
            'checked_in': today_checkins.filter(status='checked-in').count(),
            'boarding': today_checkins.filter(status='boarding').count(),
            'completed': today_checkins.filter(status='completed').count(),
            'pending': BookingDetail.objects.filter(
                status='confirmed',
                checkins__isnull=True,
                schedule__departure_time__date=today
            ).count(),
        }
        
        flights_today = today_checkins.values(
            'booking_detail__schedule__flight__flight_number'
        ).annotate(
            passenger_count=Count('id'),
            checked_in=Count('id', filter=Q(status='checked-in')),
            boarding=Count('id', filter=Q(status='boarding'))
        ).order_by('booking_detail__schedule__flight__flight_number')
        
        recent_checkins = today_checkins.order_by('-check_in_time')[:10]
        recent_data = CheckInListSerializer(recent_checkins, many=True).data
        
        return Response({
            'stats': stats,
            'flights_today': flights_today,
            'recent_checkins': recent_data,
            'date': today,
        })


# ==========================================
# TRACK LOG VIEWSET
# ==========================================
class TrackLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing activity logs.
    Read-only for regular users, full access for admins.
    """
    queryset = TrackLog.objects.select_related('user').all()
    serializer_class = TrackLogSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        count = TrackLog.objects.count()
        TrackLog.objects.all().delete()
        return Response({
            'message': f'Successfully deleted {count} log entries',
            'deleted_count': count
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        
        total = TrackLog.objects.count()
        today_count = TrackLog.objects.filter(timestamp__gte=today).count()
        week_count = TrackLog.objects.filter(timestamp__gte=week_ago).count()
        unique_users = TrackLog.objects.values('user').distinct().count()
        
        top_users = TrackLog.objects.values(
            'user__id', 'user__username'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return Response({
            'total': total,
            'today': today_count,
            'this_week': week_count,
            'unique_users': unique_users,
            'top_users': list(top_users)
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="track_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'User', 'Action', 'Timestamp'])
        
        for log in self.get_queryset():
            writer.writerow([
                log.id,
                log.user.username if log.user else 'Anonymous',
                log.action,
                log.timestamp
            ])
        
        return response


# ==========================================
# TAX AND FEE MANAGEMENT
# ==========================================
class TaxTypeViewSet(viewsets.ModelViewSet):
    queryset = TaxType.objects.all()
    serializer_class = TaxTypeSerializer
    permission_classes = [AllowAny]


class AirportFeeViewSet(viewsets.ModelViewSet):
    queryset = AirportFee.objects.select_related('airport', 'tax_type').all()
    serializer_class = AirportFeeSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        airport_id = self.request.query_params.get('airport')
        tax_type_id = self.request.query_params.get('tax_type')
        
        if airport_id:
            queryset = queryset.filter(airport_id=airport_id)
        if tax_type_id:
            queryset = queryset.filter(tax_type_id=tax_type_id)
        
        return queryset


class AirlineTaxViewSet(viewsets.ModelViewSet):
    queryset = AirlineTax.objects.select_related('airline', 'tax_type').all()
    serializer_class = AirlineTaxSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class PassengerTypeTaxRateViewSet(viewsets.ModelViewSet):
    queryset = PassengerTypeTaxRate.objects.select_related('tax_type').all()
    serializer_class = PassengerTypeTaxRateSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        tax_type_id = self.request.query_params.get('tax_type')
        passenger_type = self.request.query_params.get('passenger_type')
        
        if tax_type_id:
            queryset = queryset.filter(tax_type_id=tax_type_id)
        if passenger_type:
            queryset = queryset.filter(passenger_type=passenger_type)
        
        return queryset


class BookingTaxViewSet(viewsets.ModelViewSet):
    queryset = BookingTax.objects.select_related('booking', 'tax_type').all()
    serializer_class = BookingTaxSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        booking_id = self.request.query_params.get('booking')
        tax_type_id = self.request.query_params.get('tax_type')
        passenger_type = self.request.query_params.get('passenger_type')
        
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        if tax_type_id:
            queryset = queryset.filter(tax_type_id=tax_type_id)
        if passenger_type:
            queryset = queryset.filter(passenger_type=passenger_type)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="booking_taxes.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Booking ID', 'Tax Type', 'Passenger Type', 'Amount', 'Date'])
        
        for tax in queryset:
            writer.writerow([
                tax.id,
                tax.booking.id if tax.booking else '',
                tax.tax_type.name if tax.tax_type else '',
                tax.passenger_type,
                tax.amount,
                tax.created_at
            ])
        
        return response


# ==========================================
# BOOKING VIEWSET (MERGED - SINGLE DEFINITION)
# ==========================================
class BookingViewSet(viewsets.ModelViewSet):
    """
    Unified Booking ViewSet with all actions.
    Previously had duplicate class definition causing second to overwrite first.
    """
    queryset = Booking.objects.select_related('user').prefetch_related('details')
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Booking.objects.select_related('user').prefetch_related('details')
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        today = timezone.now().date()
        
        total = Booking.objects.count()
        pending = Booking.objects.filter(status='Pending').count()
        confirmed = Booking.objects.filter(status='Confirmed').count()
        completed = Booking.objects.filter(status='Completed').count()
        
        return Response({
            'total': total,
            'pending': pending,
            'confirmed': confirmed,
            'completed': completed
        })
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        total = Booking.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        breakdown = {
            'tickets': Booking.objects.aggregate(
                sum=Sum('base_fare_total')
            )['sum'] or 0,
            'addons': Booking.objects.aggregate(
                sum=Sum('insurance_total')
            )['sum'] or 0,
            'taxes': Booking.objects.aggregate(
                sum=Sum('tax_total')
            )['sum'] or 0
        }
        
        return Response({
            'total': total,
            'breakdown': breakdown
        })

# ==========================================
# DASHBOARD STATS
# ==========================================
class DashboardViewSet(viewsets.ViewSet):
    """
    API endpoint for dashboard statistics
    """
    permission_classes = [AllowAny]
    
    def list(self, request):
        """Default list action - returns available dashboard endpoints"""
        return Response({
            'endpoints': [
                'stats',
                'revenue_breakdown',
                'ticket_sales',
                'recent_bookings',
                'alerts',
                'passenger_composition',
                'popular_routes',
                'active_flights_map'
            ]
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        try:
            today = timezone.now().date()
            yesterday = today - timedelta(days=1)
            last_month = today - timedelta(days=30)
            
            # Passengers today
            passengers_today = PassengerInfo.objects.filter(
                bookingdetail__booking_date__date=today
            ).distinct().count()
            
            passengers_yesterday = PassengerInfo.objects.filter(
                bookingdetail__booking_date__date=yesterday
            ).distinct().count()
            
            passenger_growth = 0
            if passengers_yesterday > 0:
                passenger_growth = round(((passengers_today - passengers_yesterday) / passengers_yesterday) * 100, 1)
            
            # Revenue
            total_revenue = Booking.objects.filter(
                status='Completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            last_month_revenue = Booking.objects.filter(
                status='Completed',
                created_at__gte=last_month
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            previous_month_start = last_month - timedelta(days=30)
            previous_month_revenue = Booking.objects.filter(
                status='Completed',
                created_at__gte=previous_month_start,
                created_at__lt=last_month
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            revenue_growth = 0
            if previous_month_revenue and previous_month_revenue > 0:
                revenue_growth = round(((last_month_revenue - previous_month_revenue) / previous_month_revenue) * 100, 1)
            
            total_bookings = Booking.objects.count()
            pending_bookings = Booking.objects.filter(status='Pending').count()
            
            now = timezone.now()
            active_flights = Schedule.objects.filter(
                departure_time__lte=now,
                arrival_time__gte=now
            ).count()
            
            scheduled_flights = Schedule.objects.filter(
                departure_time__date=today
            ).count()
            
            return Response({
                'passengersToday': passengers_today,
                'passengerGrowth': passenger_growth,
                'totalRevenue': float(total_revenue) if total_revenue else 0.0,
                'revenueGrowth': revenue_growth,
                'totalBookings': total_bookings,
                'pendingBookings': pending_bookings,
                'activeFlights': active_flights,
                'scheduledFlights': scheduled_flights
            })
        except Exception as e:
            print(f"Dashboard stats error: {str(e)}")
            return Response({
                'passengersToday': 0,
                'passengerGrowth': 0,
                'totalRevenue': 0.0,
                'revenueGrowth': 0,
                'totalBookings': 0,
                'pendingBookings': 0,
                'activeFlights': 0,
                'scheduledFlights': 0,
                'error': str(e)
            }, status=200)
    
    @action(detail=False, methods=['get'])
    def revenue_breakdown(self, request):
        try:
            completed_bookings = Booking.objects.filter(status='Completed')
            
            total = completed_bookings.aggregate(sum=Sum('total_amount'))['sum'] or 0
            tickets = completed_bookings.aggregate(sum=Sum('base_fare_total'))['sum'] or 0
            addons = completed_bookings.aggregate(sum=Sum('insurance_total'))['sum'] or 0
            taxes = completed_bookings.aggregate(sum=Sum('tax_total'))['sum'] or 0
            
            # Fallback: If sub-totals are zero but total is not (e.g. legacy or partially migrated data)
            # Try to aggregate from BookingDetail and BookingTax
            if total > 0 and tickets == 0 and taxes == 0:
                from .models import BookingDetail
                # Standard tax is roughly 12% in PH, but we can aggregate actual fields
                details = BookingDetail.objects.filter(booking__in=completed_bookings)
                tickets = details.aggregate(sum=Sum('price'))['sum'] or 0
                taxes = details.aggregate(sum=Sum('tax_amount'))['sum'] or 0
                # Insurance/Addons are usually separate but for now we aggregate what we have
                
            return Response({
                'total': float(total),
                'breakdown': {
                    'tickets': float(tickets),
                    'addons': float(addons),
                    'taxes': float(taxes)
                }
            })
        except Exception as e:
            print(f"Revenue breakdown error: {str(e)}")
            return Response({
                'total': 0.0,
                'breakdown': {'tickets': 0.0, 'addons': 0.0, 'taxes': 0.0}
            }, status=200)
    
    @action(detail=False, methods=['get'])
    def ticket_sales(self, request):
        try:
            days = int(request.query_params.get('days', 7))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            sales_data = []
            labels = []
            
            for i in range(days):
                date = start_date + timedelta(days=i)
                count = BookingDetail.objects.filter(
                    booking_date__date=date
                ).count()
                
                sales_data.append(count)
                
                # Dynamic labeling based on period
                if days <= 1:
                    labels.append(date.strftime('%d %b'))
                elif days <= 7:
                    labels.append(date.strftime('%a'))
                elif days <= 31:
                    labels.append(date.strftime('%d %b'))
                else: 
                    # For long periods, only label the first of each month
                    if date.day == 1 or i == 0:
                        labels.append(date.strftime('%b %y'))
                    else:
                        labels.append('')
            
            return Response({
                'labels': labels,
                'data': sales_data
            })
        except Exception as e:
            print(f"Ticket sales error: {str(e)}")
            return Response({
                'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'data': [0, 0, 0, 0, 0, 0, 0]
            }, status=200)
    
    @action(detail=False, methods=['get'])
    def recent_bookings(self, request):
        try:
            limit = int(request.query_params.get('limit', 5))
            
            bookings = Booking.objects.select_related(
                'user'
            ).prefetch_related(
                'details__schedule__flight'
            ).order_by('-created_at')[:limit]
            
            data = []
            for booking in bookings:
                detail = booking.details.first()
                flight = None
                if detail and detail.schedule:
                    flight = detail.schedule.flight
                
                # Safe user name extraction
                passenger_name = 'Guest'
                if booking.user:
                    try:
                        passenger_name = booking.user.get_full_name() or booking.user.username or 'Guest'
                    except:
                        passenger_name = booking.user.username or 'Guest'
                
                data.append({
                    'id': booking.id,
                    'passenger': passenger_name,
                    'flight': flight.flight_number if flight else 'N/A',
                    'date': booking.created_at.isoformat() if booking.created_at else None,
                    'amount': float(booking.total_amount) if booking.total_amount else 0.0,
                    'status': booking.status or 'Unknown'
                })
            
            return Response(data)
        except Exception as e:
            print(f"Recent bookings error: {str(e)}")
            return Response([], status=200)

    @action(detail=False, methods=['get'])
    def active_flights_map(self, request):
        """Returns active flights with coordinates for the map"""
        try:
            from django.utils import timezone as tz
            now = tz.now()
            
            # Get flights that are 'On Flight' or 'Closed' (boarding)
            # AND whose arrival time is still in the future (not yet landed)
            active_schedules = Schedule.objects.filter(
                status__in=['On Flight', 'Closed'],
                arrival_time__gt=now
            ).select_related(
                'flight__route__origin_airport',
                'flight__route__destination_airport',
                'flight__airline'
            )
            
            data = []
            for s in active_schedules:
                origin = s.flight.route.origin_airport
                dest = s.flight.route.destination_airport
                
                # Only include if coordinates are available
                if origin.latitude and origin.longitude and dest.latitude and dest.longitude:
                    data.append({
                        'id': s.id,
                        'flight_number': s.flight.flight_number,
                        'airline': s.flight.airline.name,
                        'status': s.status,
                        'origin': {
                            'code': origin.code,
                            'city': origin.city,
                            'lat': float(origin.latitude),
                            'lng': float(origin.longitude)
                        },
                        'destination': {
                            'code': dest.code,
                            'city': dest.city,
                            'lat': float(dest.latitude),
                            'lng': float(dest.longitude)
                        },
                        'departure_time': s.departure_time,
                        'arrival_time': s.arrival_time
                    })
            
            return Response(data)
        except Exception as e:
            print(f"Active flights map error: {str(e)}")
            return Response([], status=200)

    @action(detail=False, methods=['get'])
    def seat_class_distribution(self, request):
        """Returns booking counts and revenue grouped by seat class"""
        try:
            from app.models import BookingDetail, SeatClass
            from django.db.models import Count, Sum

            # Aggregate by seat class
            distribution = (
                BookingDetail.objects
                .filter(seat_class__isnull=False)
                .values('seat_class__name', 'seat_class__color')
                .annotate(
                    count=Count('id'),
                    revenue=Sum('price')
                )
                .order_by('-count')
            )

            total = sum(item['count'] for item in distribution)

            data = []
            palette = ['#fe3787', '#002D1E', '#6366f1', '#f59e0b', '#22c55e', '#0ea5e9', '#ec4899', '#84cc16']
            for i, item in enumerate(distribution):
                count = item['count']
                color = item['seat_class__color'] or palette[i % len(palette)]
                data.append({
                    'label': item['seat_class__name'],
                    'count': count,
                    'revenue': float(item['revenue'] or 0),
                    'percentage': round((count / total * 100), 1) if total else 0,
                    'color': color,
                })

            return Response({
                'total': total,
                'classes': data
            })
        except Exception as e:
            print(f"Seat class distribution error: {str(e)}")
            return Response({'total': 0, 'classes': []}, status=200)

    @action(detail=False, methods=['get'])
    def alerts(self, request):
        try:
            alerts = []
            
            # Check for low seats
            low_seats = Schedule.objects.filter(
                departure_time__gte=timezone.now(),
                seats__is_available=True
            ).annotate(
                available_seats=Count('seats', filter=Q(seats__is_available=True))
            ).filter(available_seats__lt=10)
            
            for schedule in low_seats[:3]:
                alerts.append({
                    'id': f'low_seats_{schedule.id}',
                    'type': 'warning',
                    'message': f'Low seats on flight {schedule.flight.flight_number} ({schedule.available_seats} remaining)',
                    'time': timezone.now().isoformat()
                })
            
            # Check for pending bookings
            pending_count = Booking.objects.filter(status='Pending').count()
            if pending_count > 0:
                alerts.append({
                    'id': 'pending_bookings',
                    'type': 'info',
                    'message': f'{pending_count} booking(s) pending confirmation',
                    'time': timezone.now().isoformat()
                })
            
            return Response(alerts)
        except Exception as e:
            print(f"Alerts error: {str(e)}")
            return Response([], status=200)

    @action(detail=False, methods=['get'])
    def passenger_composition(self, request):
        """Returns the split of passenger types (Adult, Child, Infant)"""
        try:
            stats = PassengerInfo.objects.values('passenger_type').annotate(
                count=Count('id')
            )
            # Map type codes to readable labels if necessary
            type_map = dict(PassengerInfo.TYPE_CHOICES)
            
            labels = [type_map.get(s['passenger_type'], s['passenger_type']) for s in stats]
            data = [s['count'] for s in stats]
            
            return Response({
                'labels': labels,
                'data': data
            })
        except Exception as e:
            print(f"Passenger composition error: {str(e)}")
            return Response({'labels': [], 'data': []}, status=200)

    @action(detail=False, methods=['get'])
    def popular_routes(self, request):
        """Returns top 5 most booked flight routes"""
        try:
            # Group by route and count bookings
            routes = Schedule.objects.values(
                'flight__route__origin_airport__code',
                'flight__route__destination_airport__code'
            ).annotate(
                bookings_count=Count('bookingdetail', filter=Q(bookingdetail__status__in=['confirmed', 'checkin', 'boarding', 'completed']))
            ).order_by('-bookings_count')[:5]
            
            labels = [f"{r['flight__route__origin_airport__code']} → {r['flight__route__destination_airport__code']}" for r in routes]
            data = [r['bookings_count'] for r in routes]
            
            return Response({
                'labels': labels,
                'data': data
            })
        except Exception as e:
            print(f"Popular routes error: {str(e)}")
            return Response({'labels': [], 'data': []}, status=200)
        
