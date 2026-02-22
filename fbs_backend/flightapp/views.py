# flightapp/views.py
from django.http import JsonResponse
import requests
from rest_framework import viewsets, generics, status, filters, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q, F, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import transaction
from decimal import Decimal, ROUND_UP
from django.contrib.auth.models import User
from .services.email_service import EmailService
from .services.pdf_service import BoardingPassPDFService
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .ml.predictor import predictor
from .ml.dynamic_pricing import dynamic_pricing
import hashlib
import json
import random

from app.models import (
    Airport, Route, Flight, Schedule, Seat, Country,
    SeatClass, PassengerInfo, Airline, Booking, BookingDetail,
    MealOption, BaggageOption, AssistanceService, AddOn, AddOnType,
    TaxType, PassengerTypeTaxRate, BookingTax, TravelInsurancePlan, 
    BookingInsuranceRecord, Aircraft, BookingContact, SeatClassFeature
)
from .serializers import *
from .services.paymongo_service import paymongo_service
from .services.grading_service import grade_booking

class AirlineFilterMixin:
    """Mixin to handle common airline filtering logic by ID or Code"""
    def get_queryset(self):
        # Call parent's get_queryset if it exists
        queryset = super().get_queryset() if hasattr(super(), 'get_queryset') else self.queryset
        airline_param = self.request.query_params.get('airline')
        
        if airline_param:
            if airline_param.isdigit():
                # If it's a number, filter by the numeric ID
                return queryset.filter(airline_id=airline_param)
            else:
                # If it's letters (like '5J'), filter by the airline's code field
                return queryset.filter(airline__code=airline_param)
        
        return queryset

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset that provides 'list' and 'retrieve' actions.
    """
    permission_classes = [permissions.AllowAny]
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class AirportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset for Airports.
    """
    permission_classes = [permissions.AllowAny]
    queryset = Airport.objects.all().select_related('country').order_by('code')
    serializer_class = AirportSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city', 'code', 'country__name']

from .ml.predictor import predictor
from decimal import Decimal

from .ml.dynamic_pricing import dynamic_pricing

class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.none()
    pagination_class = None  # Disable pagination for schedules to show all
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Schedule.objects.filter(status='Open').select_related(
            'flight__airline', 
            'flight__route__origin_airport', 
            'flight__route__destination_airport'
        ).prefetch_related(
            'flight__aircraft',
            'seats',
            'seats__seat_class'
        )
        
        origin = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        date = self.request.query_params.get('departure')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if origin:
            queryset = queryset.filter(flight__route__origin_airport__code=origin)
        if destination:
            queryset = queryset.filter(flight__route__destination_airport__code=destination)
            
        # Date range filtering
        if start_date and end_date:
            try:
                queryset = queryset.filter(departure_time__date__range=[start_date, end_date])
            except Exception as e:
                print(f"Date range filter error: {e}")
        elif date:
            try:
                clean_date = date.split('T')[0] if 'T' in date else date
                queryset = queryset.filter(departure_time__date=clean_date)
            except Exception as e:
                print(f"Date filter error: {e}")
                pass

        return queryset.order_by('departure_time')

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
                            # This is a simplification; ideally frontend passes this
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
                                if seat.seat_class_id != class_id:
                                    seat.seat_class = seat_class
                                    seat.save()
                                    updated_count += 1
                                processed_seat_ids.append(seat.id)
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

    @action(detail=True, methods=['get'], url_path='seats-with-info')
    def seats_with_info(self, request, pk=None):
        """Get seats with extra info for a specific schedule"""
        schedule = self.get_object()
        from .serializers import SeatSerializer
        
        seats = Seat.objects.filter(schedule=schedule).select_related(
            'seat_class'
        ).order_by('row', 'column')
        
        serializer = SeatSerializer(seats, many=True)
        
        return Response({
            'success': True,
            'schedule_id': schedule.id,
            'schedule_price': float(schedule.price) if schedule.price else 0.00,
            'aircraft_model': schedule.flight.aircraft.model if schedule.flight and schedule.flight.aircraft else "Airbus A321",
            'aircraft_capacity': schedule.flight.aircraft.capacity if schedule.flight and schedule.flight.aircraft else 220,
            'seats': serializer.data,
            'total_seats': len(serializer.data),
            'available_seats': seats.filter(is_available=True).count()
        })

    @action(detail=True, methods=['get', 'post'], url_path='repair-seats')
    def repair_seats(self, request, pk=None):
        """Temporary endpoint to repair bad seat data for a schedule"""
        try:
            schedule = self.get_object()
            from app.models import Seat, SeatClass
            
            # Delete ALL seats for this schedule
            count = Seat.objects.filter(schedule=schedule).count()
            Seat.objects.filter(schedule=schedule).delete()
            
            # Get seat classes dynamically
            def get_sc(name):
                return SeatClass.objects.filter(name__iexact=name).first()
            
            sc_first = get_sc('First Class') or get_sc('Comfort') or get_sc('Premium Economy')
            sc_business = get_sc('Business') or sc_first
            sc_economy = get_sc('Economy')
            
            if not sc_economy:
                return Response({'success': False, 'error': 'No Economy seat class found'})
            
            aircraft = schedule.flight.aircraft if schedule.flight else None
            model_name = aircraft.model if aircraft else 'Airbus A321'
            created_count = 0
            
            # A321 Layout (approx 180 seats for this flight)
            if 'A321' in model_name or 'Airbus' in model_name:
                # Premium (Rows 1-3)
                for row in range(1, 4):
                    cols = ['A', 'C', 'D', 'F'] if sc_first != sc_economy else ['A', 'B', 'C', 'D', 'E', 'F']
                    for col in cols:
                        Seat.objects.create(
                            schedule=schedule, seat_number=f"{row}{col}",
                            seat_class=sc_first, row=row, column=col,
                            is_available=True, is_window=col in ['A', 'F'], is_aisle=col in ['C', 'D'],
                            price_adjustment=500.00 if row == 1 else 0.00
                        )
                        created_count += 1
                
                # Business/Comfort (Rows 4-8)
                for row in range(4, 9):
                    for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                        Seat.objects.create(
                            schedule=schedule, seat_number=f"{row}{col}",
                            seat_class=sc_business or sc_economy, row=row, column=col,
                            is_available=True, is_window=col in ['A', 'F'], is_aisle=col in ['C', 'D'],
                            price_adjustment=200.00 if row == 4 else 0.00
                        )
                        created_count += 1
                
                # Economy (Rows 9-31) -> to reach ~180 seats
                for row in range(9, 32):
                    for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                        is_exit = row in [12, 24]
                        Seat.objects.create(
                            schedule=schedule, seat_number=f"{row}{col}",
                            seat_class=sc_economy, row=row, column=col,
                            is_available=True, is_window=col in ['A', 'F'], is_aisle=col in ['C', 'D'],
                            is_exit_row=is_exit, has_extra_legroom=is_exit,
                            price_adjustment=150.00 if is_exit else 0.00
                        )
                        created_count += 1
            else:
                # Fallback
                for row in range(1, 31):
                    for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                        Seat.objects.create(
                            schedule=schedule, seat_number=f"{row}{col}",
                            seat_class=sc_economy, row=row, column=col, is_available=True
                        )
                        created_count += 1

            return Response({
                'success': True,
                'message': f'Successfully repaired schedule {schedule.id}. Deleted {count} and created {created_count} seats.',
                'total_seats': Seat.objects.filter(schedule=schedule).count()
            })
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
        return Response({
            'success': True,
            'message': 'No bad seats found for this schedule.',
            'total_seats': Seat.objects.filter(schedule=schedule).count()
        })
    
    def list(self, request, *args, **kwargs):
        """REAL-TIME PRICING - Optimized with Batch Processing"""
        # 1. Pre-fetch context data once
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key
        if not session_id:
            request.session.save()
            session_id = request.session.session_key
        
        # Load pricing config once
        from app.models import PricingConfiguration
        config = PricingConfiguration.load()
        
        # Get base queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        schedules = page if page is not None else queryset
        
        if not schedules:
            return self.get_paginated_response([]) if page is not None else Response([])

        # 2. Pre-calculate common factors
        # User factor is same for all flights in this search
        user_factor = dynamic_pricing.get_user_factor(user, None)
        
        # Bulk fetch occupancy for ALL schedules in the view
        occupancy_data = Seat.objects.filter(schedule__in=schedules).values('schedule_id').annotate(
            available=Count('id', filter=Q(is_available=True)),
            total=Count('id')
        )
        occupancy_map = {item['schedule_id']: (1 - (item['available'] / item['total'])) if item['total'] > 0 else 1.0 
                        for item in occupancy_data}
        
        # 3. Batch ML Price Updates (for stale or missing prices)
        stale_schedules = []
        for s in schedules:
            if (s.ml_base_price is None or 
                s.ml_price_updated_at is None or 
                (timezone.now() - s.ml_price_updated_at).total_seconds() > 3600):
                stale_schedules.append(s)
        
        if stale_schedules:
            flight_data_list = []
            for s in stale_schedules:
                flight_data_list.append({
                    'flight_number': s.flight.flight_number,
                    'airline_code': s.flight.airline.code,
                    'airline_name': s.flight.airline.name,
                    'origin': s.flight.route.origin_airport.code,
                    'destination': s.flight.route.destination_airport.code,
                    'departure_time': s.departure_time.isoformat(),
                    'arrival_time': s.arrival_time.isoformat(),
                    'total_stops': 0,
                    'is_domestic': s.flight.route.is_domestic,
                })
            
            # Use the new batch predictor
            new_prices = predictor.predict_prices_batch(flight_data_list)
            
            # Bulk update in DB (minimal hits)
            now = timezone.now()
            for s, price in zip(stale_schedules, new_prices):
                s.ml_base_price = Decimal(str(price))
                s.ml_price_updated_at = now
            
            Schedule.objects.bulk_update(stale_schedules, ['ml_base_price', 'ml_price_updated_at'])

        # 4. Final Serialization with Dynamic Pricing Context
        serializer = self.get_serializer(schedules, many=True)
        data = serializer.data
        
        for i, (schedule, flight_item) in enumerate(zip(schedules, data)):
            # Create flight data dict for dynamic pricing
            f_data = {
                'schedule_id': schedule.id,
                'flight_number': schedule.flight.flight_number,
                'departure_time': schedule.departure_time.isoformat(),
            }
            
            # Prepare context for "Turbo" pricing (no DB hits inside)
            pricing_context = {
                'config': config,
                'user_factor': user_factor,
                'occupancy_factor': self._get_occ_factor(occupancy_map.get(schedule.id, 1.0), config),
                'base_price': float(schedule.ml_base_price)
            }
            
            pricing_result = dynamic_pricing.get_price_for_user(
                f_data, user, session_id, context=pricing_context
            )
            
            # ============ ROUNDING LOGIC ============
            final_price = dynamic_pricing.round_price(pricing_result['final_price'])
            base_price = dynamic_pricing.round_price(pricing_result['base_price'])
            ml_base = float(schedule.ml_base_price)
            rounded_ml_base = dynamic_pricing.round_price(ml_base)
            
            # Inject dynamic results
            flight_item['price'] = final_price
            flight_item['base_price'] = base_price
            flight_item['ml_base_price'] = rounded_ml_base
            flight_item['ml_predicted'] = True
            flight_item['ml_factors'] = pricing_result['factors_applied']
            flight_item['raw_ml_price'] = ml_base
            
            # Price ID and Timestamp (per search consistency)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
            price_id_input = f"{session_id}_{schedule.id}_{timestamp}_{random.randint(1, 1000)}"
            flight_item['price_id'] = hashlib.md5(price_id_input.encode()).hexdigest()[:8]
            flight_item['price_calculated_at'] = datetime.now().isoformat()
            
            # ============ SEAT CLASS PRICING ============
            if 'seat_classes' in flight_item:
                for seat_class in flight_item['seat_classes']:
                    seat_class_name = seat_class.get('name', 'Economy')
                    raw_seat_price = ml_base * self.get_seat_class_multiplier(seat_class_name)
                    
                    seat_class['base_price'] = rounded_ml_base
                    seat_class['price'] = dynamic_pricing.round_seat_class_price(raw_seat_price)
                    seat_class['raw_price'] = float(raw_seat_price)

        # Track search for demand pricing
        self.track_search_demand(request, schedules)
        
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)

    def _get_occ_factor(self, occupancy_rate, config):
        """Helper to get occupancy factor without DB hits"""
        if config:
            if occupancy_rate > float(config.occupancy_high_threshold):
                return float(config.occupancy_factor_high)
            elif occupancy_rate > float(config.occupancy_medium_threshold):
                return float(config.occupancy_factor_medium)
            elif occupancy_rate < float(config.occupancy_low_threshold):
                return float(config.occupancy_factor_low)
        else:
            if occupancy_rate > 0.8: return 1.20
            elif occupancy_rate > 0.6: return 1.10
            elif occupancy_rate < 0.2: return 0.90
        return 1.0
    # ===================================================================
    
    def get_seat_class_multiplier(self, seat_class_name):
        """Get multiplier for seat class from database"""
        if not seat_class_name:
            return 1.0
            
        normalized = seat_class_name.strip()
        cache_key = f"seat_multiplier_{normalized.lower().replace(' ', '_')}"
        
        # Check cache
        cached_val = cache.get(cache_key)
        if cached_val is not None:
            return float(cached_val)
            
        try:
            # 1. Exact match
            sc = SeatClass.objects.filter(name__iexact=normalized).first()
            if sc:
                val = float(sc.price_multiplier)
                cache.set(cache_key, val, 3600)
                return val
                
            # 2. Try removing "Class" suffix
            if "class" in normalized.lower():
                base_name = normalized.lower().replace("class", "").strip()
                sc = SeatClass.objects.filter(name__iexact=base_name).first()
                if sc:
                    val = float(sc.price_multiplier)
                    cache.set(cache_key, val, 3600)
                    return val
                    
        except Exception as e:
            print(f"Error fetching seat multiplier: {e}")
            
        return 1.0
    
    def track_search_demand(self, request, queryset):
        """Track search queries for demand-based pricing"""
        from django.core.cache import cache
        
        # Track origin-destination pair demand
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        
        if origin and destination:
            route_key = f"route_demand_{origin}_{destination}"
            searches = cache.get(route_key, 0)
            cache.set(route_key, searches + 1, 3600)  # 1 hour expiry
        
        # Track specific flight demand
        for schedule in queryset[:10]:  # Track top 10 only
            try:
                flight_key = f"flight_demand_{schedule.flight.flight_number}"
                searches = cache.get(flight_key, 0)
                cache.set(flight_key, searches + 1, 3600)
            except Exception as e:
                print(f"Error tracking demand: {e}")
                continue
# ====================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def test_dynamic_pricing(request):
    """
    Test endpoint to see different prices for different sessions/users
    """
    from .ml.dynamic_pricing import dynamic_pricing
    import time
    
    # Test flight data
    test_flight = {
        'schedule_id': 1,
        'flight_number': '5J 123',
        'airline_code': '5J',
        'airline_name': 'Cebu Pacific',
        'origin': 'MNL',
        'destination': 'CEB',
        'departure_time': (datetime.now() + timedelta(days=14)).isoformat(),
        'arrival_time': (datetime.now() + timedelta(days=14, hours=1, minutes=15)).isoformat(),
        'total_stops': 0,
        'is_domestic': True
    }
    
    results = []
    
    # Simulate different users
    for i in range(5):
        # Create mock user
        class MockUser:
            def __init__(self, is_anonymous=True, id=None):
                self.is_anonymous = is_anonymous
                self.id = id
        
        if i == 0:
            user = MockUser(is_anonymous=True)  # Anonymous
        elif i == 1:
            user = MockUser(is_anonymous=False, id=1)  # New user
        elif i == 2:
            user = MockUser(is_anonymous=False, id=2)  # Returning (1 booking)
        elif i == 3:
            user = MockUser(is_anonymous=False, id=3)  # Loyal (5+ bookings)
        else:
            user = MockUser(is_anonymous=False, id=4)  # Premium
        
        # Different session IDs
        session_id = f"session_{i}_{int(time.time())}"
        
        price_data = dynamic_pricing.get_price_for_user(
            test_flight, 
            user=user,
            session_id=session_id
        )
        
        results.append({
            'user_type': ['Anonymous', 'New', 'Returning', 'Loyal', 'Premium'][i],
            'user_id': user.id if not user.is_anonymous else None,
            'session_id': session_id[:10] + '...',
            'price': price_data['final_price'],
            'base_price': price_data['base_price'],
            'factors': price_data['factors_applied']
        })
    
    return Response({
        'success': True,
        'test_flight': test_flight,
        'prices': results,
        'note': 'Different users/sessions see different prices based on dynamic factors'
    })



@api_view(['POST'])
@permission_classes([AllowAny])
def predict_flight_price(request):
    """On-demand flight price prediction"""
    try:
        flight_data = request.data
        predicted_price = predictor.predict_price(flight_data)
        
        # Also predict for different seat classes
        seat_class_prices = {}
        for seat_class in ['economy', 'premium_economy', 'business', 'first']:
            seat_class_prices[seat_class] = predictor.predict_seat_class_price(
                predicted_price, seat_class
            )
        
        return Response({
            'success': True,
            'base_price': predicted_price,
            'seat_class_prices': seat_class_prices,
            'currency': 'PHP'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

# In views.py - Update the SeatViewSet class
class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows seats to be viewed based on a schedule.
    """
    serializer_class = SeatSerializer
    queryset = Seat.objects.all()
    permission_classes = [permissions.AllowAny]
    pagination_class = None # Disable pagination for seat map

    def get_queryset(self):
        queryset = Seat.objects.all().select_related(
            'seat_class', 
            'schedule', 
            'schedule__flight',
            'schedule__flight__route'
        )
        schedule_id = self.request.query_params.get('schedule')
        
        if schedule_id:
            queryset = queryset.filter(schedule_id=schedule_id)
        
        return queryset.order_by('row', 'column')

    def list(self, request, *args, **kwargs):
        # Override to add schedule price info
        response = super().list(request, *args, **kwargs)
        
        schedule_id = request.query_params.get('schedule')
        if schedule_id:
            try:
                schedule = Schedule.objects.get(id=schedule_id)
                # Add schedule price to response
                response.data = {
                    'success': True,
                    'schedule_id': int(schedule_id),
                    'schedule_price': float(schedule.price) if schedule.price else 0.00,
                    'seats': response.data,
                    'total_seats': len(response.data),
                    'available_seats': Seat.objects.filter(schedule_id=schedule_id, is_available=True).count()
                }
            except Schedule.DoesNotExist:
                response.data = {
                    'success': False,
                    'error': 'Schedule not found',
                    'seats': [],
                    'schedule_price': 0.00,
                    'total_seats': 0,
                    'available_seats': 0
                }
        else:
            response.data = {
                'success': True,
                'schedule_price': 0.00,
                'seats': response.data,
                'total_seats': len(response.data),
                'available_seats': 0
            }
        
        return response

class MealOptionViewSet(AirlineFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = MealOption.objects.all()
    serializer_class = MealOptionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

class AssistanceServiceViewSet(AirlineFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AssistanceService.objects.all()
    serializer_class = AssistanceServiceSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

class BaggageOptionViewSet(AirlineFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BaggageOption.objects.all()
    serializer_class = BaggageOptionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None



@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment_intent(request):
    """
    Create payment intent with PayMongo for a booking
    """
    try:
        booking_id = request.data.get('booking_id')
        
        if not booking_id:
            return Response({
                'success': False,
                'error': 'Booking ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Booking not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Enforce server-side total amount as the source of truth
        amount = float(booking.total_amount)
        
        # Prepare FLAT metadata (PayMongo does not allow nested objects or Decimals)
        metadata = {
            "booking_id": str(booking.id),
            "booking_ref": booking.pnr,
            "trip_type": str(booking.trip_type)
        }
        
        result = paymongo_service.create_payment_intent(
            amount=amount,
            description=f"Flight Booking {booking_id}",
            metadata=metadata  
        )
        
        if result['success']:
            return Response({
                'success': True,
                'client_key': result['client_key'],
                'intent_id': result['intent_id'],
                'amount': result['amount'],
                'status': result['status'],
                'message': 'Payment intent created successfully'
            })
        else:
            # result['error'] contains the PayMongo error details
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to create payment intent')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment_source(request):
    """
    Create payment source for specific payment methods (GCash, GrabPay, etc.)
    """
    try:
        booking_id = request.data.get('booking_id')
        payment_type = request.data.get('type', 'gcash')
        # amount = request.data.get('amount') # IGNORE frontend amount
        
        if not booking_id:
            return Response({
                'success': False,
                'error': 'Booking ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Get booking to ensure amount is correct
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Booking not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        # Enforce server-side source of truth
        amount = float(booking.total_amount)
        
        # Create payment source
        result = paymongo_service.create_payment_source(
            amount=amount,
            type=payment_type
        )
        
        if result['success']:
            return Response({
                'success': True,
                'source_id': result['source_id'],
                'checkout_url': result['checkout_url'],
                'amount': result['data']['attributes']['amount'],
                'status': result['status'],
                'message': f'{payment_type.capitalize()} payment source created'
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to create payment source')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_and_process_payment(request):
    """
    Verify and process a payment using PayMongo payment intent ID
    """
    try:
        data = request.data
        booking_id = data.get('booking_id')
        payment_intent_id = data.get('payment_intent_id')
        
        print(f"\n=== VERIFY AND PROCESS PAYMENT ===")
        print(f"Booking ID: {booking_id}")
        print(f"Payment Intent ID: {payment_intent_id}")
        
        if not booking_id or not payment_intent_id:
            return Response({
                'success': False,
                'error': 'Booking ID and Payment Intent ID are required'
            }, status=400)
        
        # Get the booking
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Booking {booking_id} not found'
            }, status=404)
        
        # Check if payment already exists for this booking
        existing_payment = Payment.objects.filter(
            booking=booking,
            status='Completed'
        ).first()
        
        if existing_payment:
            print(f"[OK] Payment already exists: {existing_payment.id}")
            return Response({
                'success': True,
                'payment_id': existing_payment.transaction_id,
                'booking_reference': booking.pnr,
                'booking_status': booking.status,
                'message': 'Payment already processed'
            })
        
        # Verify the payment with PayMongo
        from .services.paymongo_service import paymongo_service
        
        print(f"[SEARCH] Verifying payment intent with PayMongo...")
        
        # Get payment intent details
        intent_url = f"{paymongo_service.api_url}/payment_intents/{payment_intent_id}"
        response = requests.get(intent_url, headers=paymongo_service.headers)
        
        if response.status_code != 200:
            print(f"[ERR] Failed to get payment intent: {response.status_code}")
            print(f"Response: {response.text}")
            return Response({
                'success': False,
                'error': f'Failed to verify payment: {response.text}'
            }, status=400)
        
        intent_data = response.json()['data']
        intent_attributes = intent_data['attributes']
        
        print(f"Payment Intent Status: {intent_attributes['status']}")
        print(f"Amount: {intent_attributes['amount'] / 100} PHP")
        
        if intent_attributes['status'] != 'succeeded':
            print(f"[ERR] Payment intent not succeeded. Status: {intent_attributes['status']}")
            return Response({
                'success': False,
                'error': f'Payment is not successful. Status: {intent_attributes["status"]}',
                'payment_status': intent_attributes['status']
            })
        
        # Get the payment ID from the payment intent
        payments = intent_attributes.get('payments', [])
        if not payments:
            print(f"[ERR] No payments found in payment intent")
            return Response({
                'success': False,
                'error': 'No payment found in payment intent'
            })
        
        payment_data = payments[0]
        payment_id = payment_data['id']
        payment_attrs = payment_data['attributes']
        
        print(f"[OK] Found payment: {payment_id}")
        print(f"Payment Status: {payment_attrs['status']}")
        
        # Process the payment
        return process_payment_from_paymongo(payment_id, payment_attrs, booking)
        
    except Exception as e:
        print(f"[ERR] Error in verify_and_process_payment: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)


def process_payment_from_paymongo(payment_id, payment_attrs, booking):
    """Process payment from PayMongo data"""
    from django.db import transaction
    from decimal import Decimal
    
    try:
        with transaction.atomic():
            # Convert amount from centavos to PHP
            amount = Decimal(str(payment_attrs['amount'] / 100))
            
            # Get payment method
            payment_method = "Unknown"
            source = payment_attrs.get('source', {})
            if source.get('type') == 'gcash':
                payment_method = 'GCash'
            elif source.get('type') == 'card':
                payment_method = 'Credit Card'
            elif source.get('type') == 'grab_pay':
                payment_method = 'Grab Pay'
            else:
                payment_method = source.get('type', 'Unknown').capitalize()
            
            print(f"[?] Creating payment record...")
            print(f"   Amount: {amount} PHP")
            print(f"   Method: {payment_method}")
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                method=payment_method,
                transaction_id=payment_id,
                status='Completed',
                payment_date=timezone.now()
            )
            
            print(f"[OK] Payment saved: {payment.id}")
            
            # Update booking status
            booking.status = 'Confirmed'
            booking.save()
            print(f"[OK] Booking status updated to: {booking.status}")
            
            # Update all booking details status
            updated_details = booking.details.all().update(status='confirmed')
            print(f"[OK] Updated {updated_details} booking details")
            
            # Mark seats as unavailable
            seat_count = 0
            for detail in booking.details.all():
                if detail.seat:
                    detail.seat.is_available = False
                    detail.seat.save()
                    seat_count += 1
            print(f"[OK] Marked {seat_count} seats as unavailable")
            
            # [?] AUTO-GRADING
            if booking.activity:
                print(f"[?] Triggering auto-grading for booking {booking.id}")
                try:
                    from .services.grading_service import grade_booking
                    grade_booking(booking, booking.activity.id)
                except Exception as e:
                    print(f"[WARN] Error during auto-grading: {str(e)}")
            
            # [?] SEND BOOKING CONFIRMATION EMAIL
            print(f"[EMAIL] Sending booking confirmation email...")
            email_sent = EmailService.send_booking_confirmation(booking, payment)
            
            if email_sent:
                print(f"[OK] Booking confirmation email sent successfully!")
            else:
                print(f"[WARN] Failed to send booking confirmation email")
            
            print(f"[?] Payment processing COMPLETED!")
            
            return Response({
                'success': True,
                'message': 'Payment processed successfully',
                'payment_id': payment.transaction_id,
                'booking_id': booking.id,
                'booking_reference': booking.pnr,
                'booking_status': 'confirmed',
                'amount': float(amount),
                'method': payment_method,
                'email_sent': email_sent
            })
            
    except Exception as e:
        print(f"[ERR] Error in payment processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_payment(request):
    """
    Verify payment intent status
    """
    try:
        intent_id = request.data.get('intent_id')
        
        if not intent_id:
            return Response({
                'success': False,
                'error': 'Payment intent ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Retrieve payment intent
        result = paymongo_service.retrieve_payment_intent(intent_id)
        
        if result['success']:
            return Response({
                'success': True,
                'status': result['status'],
                'amount': result['amount'],
                'data': result['data'],
                'message': f'Payment status: {result["status"]}'
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to retrieve payment intent')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_checkout_session(request):
    """
    Generate a PayMongo Checkout URL for method selection
    """
    try:
        booking_id = request.data.get('booking_id')
        # amount = request.data.get('amount') # IGNORE frontend amount
        
        if not booking_id:
            return Response({
                'success': False,
                'error': 'Booking ID is required'
            }, status=400)
            
        # Get booking to ensure amount is correct
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Booking not found'
            }, status=404)
            
        # Enforce server-side source of truth
        amount = float(booking.total_amount)

        # Get additional customer info
        customer_email = request.data.get('customer_email')
        customer_name = request.data.get('customer_name')
        customer_phone = request.data.get('customer_phone')
        
        print(f"DEBUG: Creating checkout session for booking {booking_id}, amount {amount} (backend verified)")
        
        result = paymongo_service.create_checkout_session(
            amount=amount,
            booking_id=int(booking_id),
            customer_email=customer_email,
            customer_name=customer_name,
            customer_phone=customer_phone
        )
        
        print(f"DEBUG: PayMongo result: {result}")
        
        if result['success']:
            return Response({
                'success': True,
                'checkout_url': result['checkout_url'],
                'session_id': result.get('session_id')
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to create checkout session')
            }, status=400)
    except Exception as e:
        print(f"ERROR in create_checkout_session: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def attach_payment_method(request):
    """
    Attach payment method to payment intent
    """
    try:
        intent_id = request.data.get('intent_id')
        payment_method_id = request.data.get('payment_method_id')
        
        if not intent_id or not payment_method_id:
            return Response({
                'success': False,
                'error': 'Intent ID and Payment Method ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Attach payment method
        result = paymongo_service.attach_payment_method(intent_id, payment_method_id)
        
        if result['success']:
            return Response({
                'success': True,
                'status': result['status'],
                'data': result['data'],
                'message': 'Payment method attached successfully'
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to attach payment method')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_activity_code(request):
    """
    Validate an activity code for the authenticated student
    
    POST /api/bookings/validate-activity-code/
    Body: {"activity_code": "ABC12345"}
    
    Returns:
        - 200: Activity details if valid
        - 400: Invalid code or student not enrolled
    """
    from fbs_instructor.models import Activity, SectionEnrollment
    from app.models import Students
    
    activity_code = request.data.get('activity_code', '').strip().upper()
    
    if not activity_code:
        return Response({
            'success': False,
            'error': 'Activity code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find activity by code
        activity = Activity.objects.get(
            activity_code=activity_code,
            is_code_active=True
        )
    except Activity.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid or inactive activity code'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get student record
    try:
        student = Students.objects.get(user=request.user)
    except Students.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Student record not found'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if student is enrolled in the section
    is_enrolled = SectionEnrollment.objects.filter(
        student=student,
        section=activity.section,
        is_active=True
    ).exists()
    
    if not is_enrolled:
        return Response({
            'success': False,
            'error': 'You are not enrolled in the section for this activity'
        }, status=status.HTTP_403_FORBIDDEN)

    # NEW: Check if student already has a successful booking for this activity
    from app.models import Booking
    existing_booking = Booking.objects.filter(
        user=request.user,
        activity=activity,
        status='Confirmed',
        is_practice=False
    ).first()

    if existing_booking:
        return Response({
            'success': False,
            'error': f'You have already successfully completed this activity (Booking Ref: {existing_booking.id})',
            'booking_id': existing_booking.id,
            'completed': True
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Return activity details
    return Response({
        'success': True,
        'activity': {
            'id': activity.id,
            'title': activity.title,
            'description': activity.description,
            'activity_code': activity.activity_code,
            'total_points': float(activity.total_points),
            'due_date': activity.due_date.isoformat() if activity.due_date else None,
            'requirements': {
                'trip_type': activity.required_trip_type,
                'origin': activity.required_origin,
                'destination': activity.required_destination,
                'travel_class': activity.required_travel_class,
                'passengers': activity.required_passengers,
            },
            'section': {
                'code': activity.section.section_code,
                'name': activity.section.section_name
            }
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    """
    API endpoint to create a booking with pending status
    """
    try:
        print(f"[SEARCH] DEBUG: Raw request data: {request.data}")
        
        # Validate request data using serializer
        serializer = CreateBookingSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Serializer errors: {serializer.errors}")
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Handle Activity Code Validation and Practice Mode
        activity_code = data.get('activity_code')
        is_practice = data.get('is_practice', False)
        activity_to_link = None
        
        if activity_code and not is_practice:
            # Validate activity code
            from fbs_instructor.models import Activity, SectionEnrollment
            from app.models import Students
            
            try:
                activity_to_link = Activity.objects.get(
                    activity_code=activity_code.strip().upper(),
                    is_code_active=True
                )
                
                # Check if user is a student and enrolled in the section
                try:
                    student = Students.objects.get(user=request.user if request.user.is_authenticated else None)
                    is_enrolled = SectionEnrollment.objects.filter(
                        student=student,
                        section=activity_to_link.section,
                        is_active=True
                    ).exists()
                    
                    if not is_enrolled:
                        return Response({
                            'success': False,
                            'error': 'You are not enrolled in the section for this activity'
                        }, status=status.HTTP_403_FORBIDDEN)
                        
                except Students.DoesNotExist:
                    return Response({
                        'success': False,
                        'error': 'Student record not found'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Activity.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid or inactive activity code'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Start transaction
        with transaction.atomic():
            # 1. Get or create user — prefer the authenticated student's account
            #    This is critical: if a student is logged in (has an activity code),
            #    we MUST use their real Django user so the booking links to their
            #    Student profile and grading can succeed.
            if request.user and request.user.is_authenticated:
                user = request.user
                print(f"[OK] Using authenticated user: {user.id} - {user.username}")
            else:
                user = _get_or_create_user(data)

            
            # 2. Create main booking — total_amount starts at 0, backend will calculate it
            #    SECURITY: We NEVER trust the frontend-supplied total_amount
            trip_type = data.get('trip_type', 'one_way')
            
            print(f"DEBUG: Creating booking (total will be backend-calculated)")
            
            booking = Booking.objects.create(
                user=user,
                trip_type=trip_type,
                status='Pending',
                base_fare_total=Decimal('0.00'),
                insurance_total=Decimal('0.00'),
                tax_total=Decimal('0.00'),
                total_amount=Decimal('0.00'),  # Always start at 0; _update_booking_totals sets the real value
                is_practice=is_practice,
                activity_code_used=activity_code.strip().upper() if activity_code else None,
                activity=activity_to_link
            )
            
            print(f"DEBUG: Booking created with ID: {booking.id} (total pending backend calculation)")
            
            contact_info = data.get('contact_info', {})
            booking_contact = _create_booking_contact(booking, contact_info)
            
            # 3. Create passengers
            passengers = _create_passengers(data.get('passengers', []))
            print(f"DEBUG: Created {len(passengers)} passengers")
            
            # 4. Normalize and create segments
            segments = []
            if trip_type in ['multi_city', 'multi-city']:
                segments = data.get('segments', [])
            else:
                outbound = {
                    'selectedFlight': data.get('selectedOutbound'),
                    'addons': data.get('addons', {})
                }
                segments.append(outbound)
                if trip_type == 'round_trip' and data.get('selectedReturn'):
                    returning = {
                        'selectedFlight': data.get('selectedReturn'),
                        'addons': data.get('return_addons', {})
                    }
                    segments.append(returning)

            # 5. Create booking details for each passenger and segment
            booking_details = []
            for i, passenger in enumerate(passengers):
                print(f"DEBUG: Creating booking details for passenger {i+1}: {passenger.first_name} {passenger.last_name}")
                passenger_data = data.get('passengers', [])[i] if i < len(data.get('passengers', [])) else None
                
                for idx, segment in enumerate(segments):
                    detail = _create_booking_detail(
                        booking, passenger, segment, passenger_data, idx
                    )
                    if detail:
                        booking_details.append(detail)
                        print(f"DEBUG: Segment {idx+1} booking detail created: {detail.id}")
            
            if not booking_details:
                raise Exception("No booking details created")
            
            # 5. Calculate and apply taxes
            print(f"DEBUG: Applying taxes for {len(booking_details)} booking details")
            _apply_taxes(booking, booking_details)
            
            # 5.5. Create insurance records if insurance_plan_id was provided
            insurance_plan_id = data.get('insurance_plan_id')
            if insurance_plan_id:
                print(f"DEBUG: Creating insurance records for plan ID: {insurance_plan_id}")
                _create_insurance_records(booking, booking_details, insurance_plan_id)
            
            # 6. Save booking totals
            print(f"DEBUG: Updating booking totals")
            _update_booking_totals(booking)
            
            # NOTE: Auto-grading happens in process_payment_webhook and process_payment_with_id
            # AFTER the payment is confirmed (status = 'Confirmed'). DO NOT grade here.
            
            print(f"DEBUG: Booking creation successful!")

            
            # Return the correct total amount (backend source of truth)
            return Response({
                'success': True,
                'booking_id': booking.id,
                'booking_reference': booking.pnr,
                'status': 'pending',
                'total_amount': float(booking.total_amount),
                'payment_info': {
                    'needs_payment': True,
                    'amount': float(booking.total_amount),
                    'currency': 'PHP',
                    'description': f'Flight Booking {booking.id}'
                },
                'message': 'Booking created successfully with pending payment status'
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        import traceback
        print("=== ERROR TRACEBACK ===")
        traceback.print_exc()
        print("======================")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'PUT'])
@permission_classes([AllowAny])
def update_booking(request, booking_id):
    """
    API endpoint to update an existing booking
    """
    try:
        print(f"[SEARCH] DEBUG: Updating booking ID: {booking_id}")
        print(f"DEBUG: Request data: {request.data}")
        
        # First, check if booking exists
        try:
            booking = Booking.objects.get(id=booking_id)
            print(f"DEBUG: Found booking {booking_id}, current status: {booking.status}")
        except Booking.DoesNotExist:
            print(f"DEBUG: Booking {booking_id} not found")
            return Response({
                'success': False,
                'error': f'Booking {booking_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Don't update if booking is already confirmed/cancelled
        if booking.status in ['Confirmed', 'Cancelled']:
            print(f"DEBUG: Booking {booking_id} is already {booking.status}, cannot update")
            return Response({
                'success': False,
                'error': f'Cannot update booking with status: {booking.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate the update data
        serializer = CreateBookingSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            print(f"DEBUG: Serializer errors: {serializer.errors}")
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        print(f"DEBUG: Validated data: {data}")
        
        # Start transaction for the update
        with transaction.atomic():
            # Update booking contact info if provided
            if 'contact_info' in data:
                contact_info = data['contact_info']
                print(f"DEBUG: Updating contact info: {contact_info}")
                
                # Create or update booking contact
                try:
                    booking_contact = BookingContact.objects.get(booking=booking)
                    booking_contact.first_name = contact_info.get('firstName', booking_contact.first_name)
                    booking_contact.last_name = contact_info.get('lastName', booking_contact.last_name)
                    booking_contact.email = contact_info.get('email', booking_contact.email)
                    booking_contact.phone = contact_info.get('phone', booking_contact.phone)
                    booking_contact.title = contact_info.get('title', booking_contact.title)
                    booking_contact.middle_name = contact_info.get('middleName', booking_contact.middle_name)
                    booking_contact.save()
                    print(f"DEBUG: Updated booking contact")
                except BookingContact.DoesNotExist:
                    # Create new contact
                    booking_contact = BookingContact.objects.create(
                        booking=booking,
                        first_name=contact_info.get('firstName', ''),
                        last_name=contact_info.get('lastName', ''),
                        email=contact_info.get('email', ''),
                        phone=contact_info.get('phone', ''),
                        title=contact_info.get('title', 'MR'),
                        middle_name=contact_info.get('middleName', '')
                    )
                    print(f"DEBUG: Created new booking contact")
            
            # Update passengers if provided
            if 'passengers' in data:
                passengers_data = data['passengers']
                print(f"DEBUG: Updating {len(passengers_data)} passengers")
                
                # For simplicity, we'll delete existing passengers and create new ones
                # First, delete existing booking details
                deleted_details_count, _ = BookingDetail.objects.filter(booking=booking).delete()
                print(f"DEBUG: Deleted {deleted_details_count} old booking details")
                
                # Delete old taxes to prevent accumulation
                deleted_taxes_count, _ = BookingTax.objects.filter(booking=booking).delete()
                print(f"DEBUG: Deleted {deleted_taxes_count} old taxes")
                
                # Delete existing passengers linked to this booking
                passenger_ids = BookingDetail.objects.filter(booking=booking).values_list('passenger_id', flat=True)
                PassengerInfo.objects.filter(id__in=passenger_ids).delete()
                print(f"DEBUG: Deleted old passengers")
                
                # Create new passengers
                new_passengers = _create_passengers(passengers_data)
                print(f"DEBUG: Created {len(new_passengers)} new passengers")
                
                # Create new booking details
                # Normalize segments
                segments = []
                if booking.trip_type in ['multi_city', 'multi-city']:
                    segments = data.get('segments', [])
                else:
                    outbound = {
                        'selectedFlight': data.get('selectedOutbound'),
                        'addons': data.get('addons', {})
                    }
                    segments.append(outbound)
                    if booking.trip_type == 'round_trip' and data.get('selectedReturn'):
                        returning = {
                            'selectedFlight': data.get('selectedReturn'),
                            'addons': data.get('return_addons', {})
                        }
                        segments.append(returning)

                booking_details = []
                for i, passenger in enumerate(new_passengers):
                    passenger_data = passengers_data[i] if i < len(passengers_data) else {}
                    
                    for idx, segment in enumerate(segments):
                        detail = _create_booking_detail(
                            booking, passenger, segment, passenger_data, idx
                        )
                        if detail:
                            booking_details.append(detail)
                            print(f"DEBUG: Created segment {idx+1} booking detail: {detail.id}")
                
                print(f"DEBUG: Created {len(booking_details)} new booking details")
            
            # Update flight selections if provided
            if 'selectedOutbound' in data:
                # Update would require more complex logic to change schedules
                # For now, we'll log it but not change the actual schedule
                print(f"DEBUG: Update requested for outbound flight: {data['selectedOutbound']}")
                print(f"NOTE: Flight schedule changes not implemented in update")
            
            if 'selectedReturn' in data and booking.trip_type == 'round_trip':
                print(f"DEBUG: Update requested for return flight: {data['selectedReturn']}")
                print(f"NOTE: Flight schedule changes not implemented in update")
            
            # Update add-ons if provided
            if 'addons' in data or 'return_addons' in data:
                print(f"DEBUG: Update requested for add-ons")
                print(f"NOTE: Add-on updates would require more complex logic")
            
            # Update total amount if provided
            if 'total_amount' in data:
                new_total = data['total_amount']
                booking.total_amount = new_total
                print(f"DEBUG: Updated total amount to: {new_total}")
            
            # Save booking
            booking.save()
            
            # Recalculate taxes and insurance
            if booking_details:
                print(f"DEBUG: Recalculating taxes for {len(booking_details)} booking details")
                _apply_taxes(booking, booking_details)
                
                # Create insurance records if insurance_plan_id was provided
                insurance_plan_id = data.get('insurance_plan_id')
                if insurance_plan_id:
                    print(f"DEBUG: Creating insurance records for plan ID: {insurance_plan_id}")
                    _create_insurance_records(booking, booking_details, insurance_plan_id)
                
                _update_booking_totals(booking)
            
            print(f"DEBUG: Booking update successful!")
            
            return Response({
                'success': True,
                'booking_id': booking.id,
                'booking_reference': booking.pnr,
                'status': booking.status,
                'total_amount': float(booking.total_amount),
                'message': 'Booking updated successfully'
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        import traceback
        print("=== ERROR TRACEBACK ===")
        traceback.print_exc()
        print("======================")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

def _create_booking_contact(booking, contact_info):
    """Create contact record for booking"""    
    try:
        contact = BookingContact.objects.create(
            booking=booking,
            first_name=contact_info.get('firstName', ''),
            last_name=contact_info.get('lastName', ''),
            email=contact_info.get('email', ''),
            phone=contact_info.get('phone', ''),
            title=contact_info.get('title', 'MR'),
            middle_name=contact_info.get('middleName', '')
        )
        print(f"[OK] Booking contact created: {contact.id}")
        return contact
    except Exception as e:
        print(f"[ERR] Error creating booking contact: {str(e)}")
        return None

def _get_or_create_user(data):
    """
    Get or create a user for the booking
    """
    contact_info = data.get('contact_info', {})
    email = contact_info.get('email', 'guest@example.com')
    
    if not email:
        print("[ERR] ERROR: No email provided in contact info")
        email = 'guest@example.com'
    
    print(f"DEBUG: Creating user with email: {email}")
    print(f"DEBUG: Contact info for user: {contact_info}")
    
    # Create a unique username based on email and timestamp
    username_base = email.split('@')[0] if '@' in email else 'guest'
    username = f"{username_base}_{int(timezone.now().timestamp())}"
    
    # Clean the username (remove special characters)
    import re
    username = re.sub(r'[^a-zA-Z0-9_]', '', username)
    
    # Get or create the user
    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': contact_info.get('firstName', ''),
                'last_name': contact_info.get('lastName', ''),
                'is_active': True
            }
        )
        
        if created:
            print(f"[OK] Created new user: {user.id} - {user.email}")
            print(f"   First name: {user.first_name}")
            print(f"   Last name: {user.last_name}")
        else:
            print(f"[OK] Found existing user: {user.id} - {user.email}")
            
        return user
        
    except Exception as e:
        print(f"[ERR] Error creating user: {str(e)}")
        # Fallback to a default guest user
        fallback_user, _ = User.objects.get_or_create(
            username=f'guest_{int(timezone.now().timestamp())}',
            defaults={
                'email': 'guest@example.com',
                'first_name': 'Guest',
                'last_name': 'User',
                'is_active': True
            }
        )
        return fallback_user

def _create_booking(data, user):
    """Create main booking record"""
    trip_type = data.get('trip_type', 'one_way')
    is_round_trip = trip_type == 'round_trip'
    
    # Calculate total amount - IGNORE frontend data for security
    # total_amount = Decimal(str(data.get('total_amount', 0))) 
    total_amount = Decimal('0.00') # Start with 0, let backend calculate it
    print(f"DEBUG: Creating booking with initial total amount: {total_amount} (ignoring frontend)")
    
    # Create and save the booking immediately
    booking = Booking.objects.create(
        user=user,
        trip_type=trip_type,
        status='Pending',
        insurance_total=Decimal('0.00'),
        tax_total=Decimal('0.00'),
        total_amount=total_amount,  # Start with 0
        activity_id=data.get('activity_id') # Link to activity if present
    )
    
    print(f"DEBUG: Booking created. ID: {booking.id}, Total: {total_amount}")
    
    return booking

def _create_passengers(passengers_data):
    """Create passenger records"""
    passengers = []
    print(f"DEBUG: Creating {len(passengers_data)} passengers")
    
    for i, pax_data in enumerate(passengers_data):
        try:
            print(f"  Passenger {i+1} full data: {pax_data}")
            
            # Use the validated data from serializer
            # The serializer has already normalized the field names
            first_name = pax_data.get('first_name', '')
            last_name = pax_data.get('last_name', '')
            middle_name = pax_data.get('middle_name', '')
            title = pax_data.get('title', 'MR')
            date_of_birth = pax_data.get('date_of_birth', '')
            nationality = pax_data.get('nationality', 'Philippines')
            passport_number = pax_data.get('passport_number', '')
            passenger_type = pax_data.get('type', 'Adult')
            
            print(f"    First Name: {first_name}")
            print(f"    Last Name: {last_name}")
            print(f"    Middle Name: {middle_name}")
            print(f"    Type: {passenger_type}")
            print(f"    Date of Birth: {date_of_birth}")
            
            # Parse date of birth
            dob_parsed = None
            if date_of_birth:
                try:
                    # Remove timezone if present
                    clean_dob = str(date_of_birth).split('T')[0]
                    dob_parsed = datetime.strptime(clean_dob, '%Y-%m-%d').date()
                    print(f"    Date of birth parsed: {dob_parsed}")
                except Exception as e:
                    print(f"    ERROR parsing date of birth: {e}")
                    # Try alternative format
                    try:
                        dob_parsed = datetime.strptime(str(date_of_birth), '%Y-%m-%d').date()
                        print(f"    Date of birth parsed (alternative): {dob_parsed}")
                    except:
                        print(f"    Could not parse date, using None")
                        dob_parsed = None
            
            print(f"    Creating PassengerInfo...")
            
            # Create passenger with validated data
            passenger = PassengerInfo.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                title=title,
                date_of_birth=dob_parsed,
                nationality=nationality,
                passport_number=passport_number,
                passenger_type=passenger_type
            )
            
            print(f"    Passenger created with ID: {passenger.id}")
            print(f"    Passenger full name: {passenger.get_full_name()}")
            passengers.append(passenger)
            
        except Exception as e:
            print(f"    ERROR creating passenger: {e}")
            import traceback
            traceback.print_exc()
            # Don't continue, raise the error
            raise Exception(f"Failed to create passenger {i+1}: {str(e)}")
    
    print(f"DEBUG: Created {len(passengers)} passengers successfully")
    return passengers

def _create_booking_detail(booking, passenger, segment, passenger_data=None, segment_index=0):
    """Create booking detail for each passenger - UPDATED for multi-city support"""
    try:
        selected_flight = segment.get('selectedFlight', {})
        flight_label = f"Segment {segment_index + 1}"
        
        print(f"  {flight_label} flight data: {selected_flight}")
        
        # Get schedule ID
        schedule_id = selected_flight.get('schedule_id') or selected_flight.get('id')
        
        if not schedule_id:
            print(f"  ERROR: No schedule ID found for {flight_label.lower()}")
            return None
        
        print(f"  {flight_label} Schedule ID: {schedule_id}")
        
        # Get schedule
        try:
            schedule = Schedule.objects.select_related(
                'flight__airline',
                'flight__route',
                'flight__aircraft'
            ).get(id=schedule_id)
            print(f"  {flight_label} schedule found: {schedule.id} - {schedule.flight.flight_number}")
        except Schedule.DoesNotExist:
            print(f"  ERROR: {flight_label} schedule with ID {schedule_id} not found")
            return None
        
        # Get seat if selected
        seat = None
        seat_class = None
        segment_addons = segment.get('addons', {})
        
        # Use the passenger key from passenger_data
        passenger_key = None
        if passenger_data and passenger_data.get('key'):
            passenger_key = passenger_data.get('key')
        else:
            passenger_key = f"{passenger.first_name}_{passenger.last_name}"
        
        print(f"  Passenger key for addons: {passenger_key}")
        
        # Find seat for this passenger
        if passenger_key in segment_addons.get('seats', {}):
            seat_data = segment_addons['seats'][passenger_key]
            print(f"  Seat data for this passenger: {seat_data}")
            
            try:
                if isinstance(seat_data, int):
                    seat = Seat.objects.select_related('seat_class').get(id=seat_data)
                elif isinstance(seat_data, dict) and seat_data.get('id'):
                    seat = Seat.objects.select_related('seat_class').get(id=seat_data['id'])
                
                if seat:
                    seat.is_available = False
                    seat.save()
                    seat_class = seat.seat_class
                    print(f"  Seat assigned: {seat.seat_number}")
                    
            except Seat.DoesNotExist:
                print(f"  WARNING: Seat not found")
        
        # If no seat selected, get default seat class
        if not seat_class:
            fare_type = selected_flight.get('class_type', 'Economy')
            seat_class = SeatClass.objects.filter(
                airline=schedule.flight.airline,
                name__icontains=fare_type
            ).first()
        
        # Calculate base price - DO NOT TRUST FRONTEND
        session_id = getattr(booking, 'session_id', None) or "booking_creation"
        user = booking.user
        
        flight_pricing_data = {
            'schedule_id': schedule.id,
            'flight_number': schedule.flight.flight_number,
            'airline_code': schedule.flight.airline.code,
            'airline_name': schedule.flight.airline.name,
            'origin': schedule.flight.route.origin_airport.code,
            'destination': schedule.flight.route.destination_airport.code,
            'departure_time': schedule.departure_time.isoformat(),
            'arrival_time': schedule.arrival_time.isoformat(),
            'total_stops': 0,
            'is_domestic': schedule.flight.route.is_domestic,
        }
        
        # Recalculate dynamic price
        price_data = dynamic_pricing.get_price_for_user(
            flight_pricing_data, 
            user=user,
            session_id=session_id
        )

        fare_type = selected_flight.get('class_type', 'Economy')

        def get_multiplier(name):
            if not name:
                return 1.0
            normalized = name.strip()
            sc = SeatClass.objects.filter(name__iexact=normalized).first()
            if not sc and "class" in normalized.lower():
                base_name = normalized.lower().replace("class", "").strip()
                sc = SeatClass.objects.filter(name__iexact=base_name).first()
            return float(sc.price_multiplier) if sc else 1.0

        multiplier = get_multiplier(fare_type)

        if multiplier == 1.0:
            frontend_price = selected_flight.get('price')
            if frontend_price is not None:
                base_price = Decimal(str(frontend_price))
            else:
                base_price = Decimal(str(dynamic_pricing.round_price(price_data['final_price'])))
        else:
            ml_base = float(schedule.ml_base_price) if schedule.ml_base_price else float(schedule.price)
            raw_seat_price = Decimal(str(ml_base)) * Decimal(str(multiplier))
            base_price = Decimal(str(dynamic_pricing.round_seat_class_price(raw_seat_price)))
            
        # Apply infant discount
        if passenger.passenger_type and passenger.passenger_type.lower() == 'infant':
            base_price = base_price * Decimal('0.5')
            
        # Add seat adjustment if any
        if seat and hasattr(seat, 'price_adjustment') and seat.price_adjustment:
            base_price += seat.price_adjustment
        
        # Create booking detail
        booking_detail = BookingDetail.objects.create(
            booking=booking,
            passenger=passenger,
            schedule=schedule,
            seat=seat, 
            seat_class=seat_class,
            price=base_price,
            passenger_type=passenger.passenger_type,
            status='pending'
        )
        
        # Add add-ons
        _add_addons_to_booking_detail(booking_detail, segment_addons, passenger_data or {})
        
        return booking_detail
        
    except Exception as e:
        print(f"ERROR in _create_booking_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# In flightapp/views.py, update the _add_addons_to_booking_detail function:
def _add_addons_to_booking_detail(booking_detail, segment_addons, passenger_data):
    """Add selected add-ons to booking detail with segment support"""
    addons_to_link = []
    
    # Get airline from schedule
    airline = booking_detail.schedule.flight.airline if booking_detail.schedule else None
    
    # Get passenger key from passenger data
    passenger_key = passenger_data.get('key', f"{booking_detail.passenger.first_name}_{booking_detail.passenger.last_name}")
    
    print(f"DEBUG: Looking for addons for passenger key: {passenger_key}")
    
    # Baggage add-on
    baggage_data = segment_addons.get('baggage', {}).get(passenger_key)
    if baggage_data:
        if isinstance(baggage_data, dict) and baggage_data.get('id'):
            try:
                baggage_option = BaggageOption.objects.get(id=baggage_data['id'])
                addon, created = AddOn.objects.get_or_create(
                    baggage_option=baggage_option,
                    defaults={
                        'name': f"Extra Baggage {baggage_option.formatted_weight}",
                        'price': baggage_option.price,
                        'airline': airline,
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added baggage addon: {baggage_option.name}")
            except BaggageOption.DoesNotExist:
                print(f"DEBUG: Baggage option with ID {baggage_data['id']} not found")
        elif isinstance(baggage_data, int):
            try:
                baggage_option = BaggageOption.objects.get(id=baggage_data)
                addon, created = AddOn.objects.get_or_create(
                    baggage_option=baggage_option,
                    defaults={
                        'name': f"Extra Baggage {baggage_option.formatted_weight}",
                        'price': baggage_option.price,
                        'airline': airline,
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added baggage addon: {baggage_option.name}")
            except BaggageOption.DoesNotExist:
                print(f"DEBUG: Baggage option with ID {baggage_data} not found")
    
    # Meal add-on
    meal_data = segment_addons.get('meals', {}).get(passenger_key)
    if meal_data:
        if isinstance(meal_data, dict) and meal_data.get('id'):
            try:
                meal_option = MealOption.objects.get(id=meal_data['id'])
                addon, created = AddOn.objects.get_or_create(
                    meal_option=meal_option,
                    defaults={
                        'name': f"Meal: {meal_option.name}",
                        'price': meal_option.price,
                        'airline': airline,
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added meal addon: {meal_option.name}")
            except MealOption.DoesNotExist:
                print(f"DEBUG: Meal option with ID {meal_data['id']} not found")
        elif isinstance(meal_data, int):
            try:
                meal_option = MealOption.objects.get(id=meal_data)
                addon, created = AddOn.objects.get_or_create(
                    meal_option=meal_option,
                    defaults={
                        'name': f"Meal: {meal_option.name}",
                        'price': meal_option.price,
                        'airline': airline,
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added meal addon: {meal_option.name}")
            except MealOption.DoesNotExist:
                print(f"DEBUG: Meal option with ID {meal_data} not found")
    
    # Assistance service
    service_id = segment_addons.get('wheelchair', {}).get(passenger_key)
    if service_id:
        try:
            assistance_service = AssistanceService.objects.get(id=service_id)
            addon, created = AddOn.objects.get_or_create(
                assistance_service=assistance_service,
                defaults={
                    'name': f"Assistance: {assistance_service.name}",
                    'price': assistance_service.price,
                    'airline': airline,
                    'included': assistance_service.is_included,
                }
            )
            addons_to_link.append(addon)
            print(f"DEBUG: Added assistance addon: {assistance_service.name}")
        except AssistanceService.DoesNotExist:
            print(f"DEBUG: Assistance service with ID {service_id} not found")
    
    # Link addons to booking detail
    if addons_to_link:
        booking_detail.addons.add(*addons_to_link)
        print(f"DEBUG: Linked {len(addons_to_link)} addons to booking detail {booking_detail.id}")

def _apply_taxes(booking, booking_details):
    """Calculate and apply taxes to booking"""
    for detail in booking_details:
        if not detail.schedule:
            continue
            
        # Get applicable taxes based on route and passenger type
        route = detail.schedule.flight.route
        passenger_type = detail.passenger_type.lower() if detail.passenger_type else 'adult'
        
        # Find applicable taxes
        applicable_taxes = TaxType.objects.filter(
            is_active=True,
            applies_domestic=route.is_domestic,
            applies_international=route.is_international
        )
        
        applied_any_tax = False
        for tax in applicable_taxes:
            try:
                # Check if passenger type is applicable
                if tax.adult_only and passenger_type != 'adult':
                    continue
                    
                # Check passenger type rate
                try:
                    rate = PassengerTypeTaxRate.objects.get(
                        tax_type=tax,
                        passenger_type=passenger_type
                    )
                    amount = rate.amount
                except PassengerTypeTaxRate.DoesNotExist:
                    amount = tax.base_amount
                
                # Apply per passenger or per booking
                if tax.per_passenger:
                    # Create booking tax record
                    BookingTax.objects.create(
                        booking=booking,
                        tax_type=tax,
                        amount=amount,
                        passenger_type=passenger_type
                    )
                    
                    # Add to booking detail tax amount
                    detail.tax_amount += amount
                    detail.save()
                    applied_any_tax = True
                
            except Exception as e:
                print(f"Error applying tax {tax.name}: {e}")
                continue

        # FALLBACK: If no explicit taxes found in DB, apply 12% VAT estimation
        if not applied_any_tax:
            try:
                print(f"DEBUG: No explicit taxes found in DB for detail {detail.id}. Applying 12% VAT fallback.")
                # We need a TaxType for the record, but if none exist we might be stuck.
                # However, we can at least update the detail.tax_amount.
                # To be compliant with _update_booking_totals (which sums BookingTax objects),
                # we SHOULD ideally have a TaxType.
                
                # Try to find or create a default 'VAT' tax type
                vat_tax, created = TaxType.objects.get_or_create(
                    code='VAT',
                    defaults={
                        'name': 'Value Added Tax',
                        'base_amount': Decimal('0.00'), # We will calculate it dynamically
                        'is_active': True,
                        'per_passenger': True,
                        'applies_domestic': True,
                        'applies_international': True
                    }
                )
                
                # Calculate 12% of detail price
                fallback_amount = Decimal(str(detail.price)) * Decimal('0.12')
                
                BookingTax.objects.create(
                    booking=booking,
                    tax_type=vat_tax,
                    amount=fallback_amount,
                    passenger_type=passenger_type
                )
                
                # Ensure detail.tax_amount is treated as Decimal
                current_tax = Decimal(str(detail.tax_amount)) if detail.tax_amount else Decimal('0.00')
                detail.tax_amount = current_tax + fallback_amount
                detail.save()
            except Exception as e:
                print(f"ERROR in tax fallback: {e}")

def _create_insurance_records(booking, booking_details, insurance_plan_id):
    """Create insurance records for all passengers in the booking."""
    try:
        from app.models import TravelInsurancePlan, BookingInsuranceRecord
        
        # Safety check - ensure we have booking details
        if not booking_details:
            print(f"[WARN] No booking details to attach insurance to")
            return
        
        print(f"DEBUG: Looking up insurance plan {insurance_plan_id}")
        plan = TravelInsurancePlan.objects.get(id=insurance_plan_id, is_active=True)
        print(f"DEBUG: Found insurance plan: {plan.name} - ₱{plan.retail_price}")
        
        # Get the first schedule (depart flight) to identify which details get insurance
        first_schedule = booking_details[0].schedule
        
        created_count = 0
        for detail in booking_details:
            # Only create insurance for the depart flight (not both depart and return)
            # Insurance is per passenger, not per flight segment
            if detail.schedule_id == first_schedule.id:
                insurance_record = BookingInsuranceRecord.objects.create(
                    booking_detail=detail,
                    insurance_plan=plan,
                    insured_amount=plan.retail_price,
                    sale_price=plan.retail_price,
                    status='active'
                )
                created_count += 1
                print(f"DEBUG: Created insurance record {insurance_record.policy_number} for passenger {detail.passenger.get_full_name()}")
        
        print(f"DEBUG: Created {created_count} insurance records")
        
    except TravelInsurancePlan.DoesNotExist:
        print(f"[WARN] Insurance plan {insurance_plan_id} not found or inactive")
    except Exception as e:
        print(f"[ERR] Error creating insurance records: {str(e)}")
        import traceback
        traceback.print_exc()

def _update_booking_totals(booking):
    """Update booking totals after all details are created.
    Backend is the SOLE source of truth — frontend total is ignored.
    """
    try:
        print(f"\n\n=========== DEBUG: _update_booking_totals ===========")
        print(f"DEBUG: In _update_booking_totals for booking {booking.id}")
        
        # Wait a moment to ensure all details are saved
        import time
        time.sleep(0.1)  # Small delay
        
        # Refresh booking from database
        booking.refresh_from_db()
        
        from django.db.models import Sum
        
        # 1. Base fare total (ML-priced per passenger per leg)
        base_fare_total = BookingDetail.objects.filter(
            booking=booking
        ).aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        print(f"  Base fare total: {base_fare_total}")
        
        # 2. Insurance total - calculate from BookingInsuranceRecords
        insurance_total = Decimal('0.00')
        booking_details = BookingDetail.objects.filter(booking=booking)
        for detail in booking_details:
            if hasattr(detail, 'insurance_record') and detail.insurance_record:
                insurance_total += detail.insurance_record.sale_price
        print(f"  Insurance total: {insurance_total}")
        
        # 3. Tax total
        tax_total = BookingTax.objects.filter(
            booking=booking
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        print(f"  Tax total: {tax_total}")
        
        # 4. [OK] Addon total — prices fetched from DB, NOT from frontend
        #    Covers baggage, meals, seat upgrades, and any other paid addons
        addon_total = Decimal('0.00')
        booking_details = BookingDetail.objects.filter(booking=booking).prefetch_related('addons')
        for detail in booking_details:
            for addon in detail.addons.all():
                if addon.price and not addon.included:  # Only count paid (non-included) addons
                    addon_total += Decimal(str(addon.price))
        print(f"  Addon total (baggage, meals, seats): {addon_total}")
        
        # 5. Grand total — backend is the source of truth
        calculated_total = base_fare_total + insurance_total + tax_total + addon_total
        
        # Log any discrepancy with what the frontend claimed
        stored_frontend_total = booking.total_amount
        if stored_frontend_total and abs(calculated_total - stored_frontend_total) > Decimal('1.00'):
            print(f"  [WARN] SECURITY: Total mismatch! Frontend claimed: {stored_frontend_total}, Backend calculated: {calculated_total}")
        
        # Always override with backend-calculated total (rounding up to nearest integer)
        calculated_total = (calculated_total).quantize(Decimal('1.'), rounding=ROUND_UP)
        booking.total_amount = calculated_total
        booking.base_fare_total = base_fare_total
        booking.insurance_total = insurance_total
        booking.tax_total = tax_total
        booking.save()
        
        print(f"  [OK] Booking totals saved: base={base_fare_total}, addons={addon_total}, tax={tax_total}, TOTAL={calculated_total}")
        print(f"=========== END DEBUG: _update_booking_totals ===========\n\n")
        
    except Exception as e:
        print(f"ERROR in _update_booking_totals: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


@api_view(['POST'])
@permission_classes([AllowAny])
def process_payment(request):
    """
    Process payment callback from PayMongo
    """
    try:
        # Get payment intent ID from PayMongo webhook or callback
        intent_id = request.data.get('payment_intent_id') or request.data.get('intent_id')
        booking_id = request.data.get('booking_id')
        
        if not intent_id or not booking_id:
            return Response({
                'success': False,
                'error': 'Payment intent ID and booking ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get booking
        try:
            booking = Booking.objects.select_related('user').get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Booking not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify payment with PayMongo
        payment_result = paymongo_service.retrieve_payment_intent(intent_id)
        
        if not payment_result['success']:
            return Response({
                'success': False,
                'error': f'Payment verification failed: {payment_result.get("error")}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment_data = payment_result['data']
        payment_status = payment_data['attributes']['status']
        
        # Check payment method used
        payment_method = "Unknown"
        if payment_data['attributes'].get('payment_method'):
            pm_type = payment_data['attributes']['payment_method']['attributes']['type']
            if pm_type == 'card':
                payment_method = 'Credit Card'
            elif pm_type == 'gcash':
                payment_method = 'GCash'
            elif pm_type == 'grab_pay':
                payment_method = 'Grab Pay'
            else:
                payment_method = pm_type.capitalize()
        
        # Process payment based on status
        with transaction.atomic():
            if payment_status == 'succeeded':
                # Create payment record
                amount_paid = payment_data['attributes']['amount'] / 100  # Convert from centavos
                
                # SECURITY CHECK: Verify the amount paid against the booking total
                if abs(Decimal(str(amount_paid)) - booking.total_amount) > Decimal('1.00'):
                    print(f"[WARN] SECURITY ALERT: Payment amount mismatch! Paid: {amount_paid}, Booking Total: {booking.total_amount}")
                    # We log it and record the actual amount paid, but maybe we shouldn't confirm the booking automatically?
                    # For now, we'll record it but alert in logs.
                
                payment = Payment.objects.create(
                    booking=booking,
                    amount=Decimal(str(amount_paid)),
                    method=payment_method,
                    transaction_id=intent_id,
                    status='Completed',
                    payment_date=timezone.now()
                )
                
                # Update booking status
                booking.status = 'Confirmed'
                booking.save()
                
                # Update all booking details status
                booking.details.all().update(status='confirmed')
                
                # Mark seats as unavailable
                for detail in booking.details.all():
                    if detail.seat:
                        detail.seat.is_available = False
                        detail.seat.save()

                # [?] AUTO-GRADING
                if booking.activity:
                    print(f"[?] Triggering auto-grading for booking {booking.id}")
                    try:
                        from .services.grading_service import grade_booking
                        grade_booking(booking, booking.activity.id)
                    except Exception as e:
                        print(f"[WARN] Error during auto-grading: {str(e)}")
                
                return Response({
                    'success': True,
                    'payment_id': payment.transaction_id,
                    'booking_status': 'confirmed',
                    'booking_reference': booking.pnr,
                    'message': 'Payment processed successfully'
                }, status=status.HTTP_200_OK)
            
            elif payment_status in ['awaiting_next_action', 'awaiting_payment_method']:
                # Payment is still being processed
                return Response({
                    'success': True,
                    'booking_status': 'pending',
                    'payment_status': payment_status,
                    'message': 'Payment is being processed'
                }, status=status.HTTP_200_OK)
            
            else:
                # Payment failed
                return Response({
                    'success': False,
                    'error': f'Payment failed with status: {payment_status}',
                    'payment_status': payment_status
                }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny])
def get_booking_details(request, booking_id):
    """
    Get booking details by ID
    """
    try:
        booking = Booking.objects.select_related('user').get(id=booking_id)
        
        # Serialize booking data
        from .serializers import BookingSerializer
        
        return Response({
            'success': True,
            'booking': BookingSerializer(booking).data
        })
        
    except Booking.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

# Optional: Add a booking viewset for admin/management
class BookingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view bookings (admin only)
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.none()
    basename = 'booking'
    
    def get_queryset(self):
        user = self.request.user
        
        # If user is staff, show all bookings
        if user.is_staff:
            return Booking.objects.all().select_related('user')
        
        # Otherwise, only show user's own bookings
        return Booking.objects.filter(user=user).select_related('user')
    
# flightapp/views.py
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_session_payment(request):
    """
    Verify payment using session ID
    """
    try:
        session_id = request.data.get('session_id')
        booking_id = request.data.get('booking_id')
        
        if not session_id or not booking_id:
            return Response({
                'success': False,
                'error': 'Session ID and Booking ID are required'
            }, status=400)
        
        # Retrieve checkout session from PayMongo
        from .services.paymongo_service import paymongo_service
        
        session_url = f"{paymongo_service.api_url}/checkout_sessions/{session_id}"
        session_response = requests.get(session_url, headers=paymongo_service.headers)
        
        if session_response.status_code != 200:
            return Response({
                'success': False,
                'error': 'Invalid session ID'
            }, status=400)
        
        session_data = session_response.json()['data']
        session_attributes = session_data['attributes']
        
        # Check if session has successful payments
        payments = session_attributes.get('payments', [])
        
        if payments:
            # Get the first payment
            payment_data = payments[0]
            payment_id = payment_data['id']
            payment_attrs = payment_data['attributes']
            
            if payment_attrs['status'] == 'paid':
                # Process the payment
                return process_payment_from_paymongo(payment_id, payment_attrs, booking_id)
        
        return Response({
            'success': False,
            'session_status': session_attributes.get('status'),
            'message': 'No successful payment found for this session'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

# flightapp/views.py
@api_view(['POST'])
@permission_classes([AllowAny])
def process_payment_callback(request):
    """
    Process payment callback from PayMongo Checkout Session
    """
    try:
        print("\n=== PROCESSING PAYMENT CALLBACK ===")
        print(f"Request data: {request.data}")
        print(f"Request headers: {dict(request.headers)}")
        
        # Check if this is a PayMongo webhook
        if request.data.get('type') == 'checkout_session.payment_succeeded':
            # This is a webhook notification
            session_data = request.data.get('data', {})
            session_id = session_data.get('id')
            attributes = session_data.get('attributes', {})
            
            print(f"Webhook: Checkout session {session_id}")
            
            # Get metadata
            metadata = attributes.get('metadata', {})
            booking_id = metadata.get('booking_id')
            
            if booking_id:
                # Retrieve the checkout session to get payment details
                session_url = f"{paymongo_service.api_url}/checkout_sessions/{session_id}"
                session_response = requests.get(session_url, headers=paymongo_service.headers)
                
                if session_response.status_code == 200:
                    session_details = session_response.json()
                    payments = session_details['data']['attributes'].get('payments', [])
                    
                    if payments:
                        payment_id = payments[0]['id']
                        
                        # Now process the payment with the payment ID
                        return process_payment_with_id(payment_id, booking_id)
        
        # If not a webhook, try to get from query params or body
        booking_id = request.data.get('booking_id') or request.query_params.get('booking_id')
        payment_success = request.data.get('payment_success') or request.query_params.get('payment_success')
        
        print(f"Booking ID: {booking_id}")
        print(f"Payment Success: {payment_success}")
        
        if not booking_id:
            return Response({
                'success': False,
                'error': 'No booking ID provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # If payment was successful but we don't have payment ID yet
        # We need to poll PayMongo for completed payments for this booking
        if payment_success == 'true':
            return handle_successful_payment_without_id(booking_id)
        
        # If payment failed/cancelled
        elif payment_success == 'false':
            return Response({
                'success': False,
                'booking_id': booking_id,
                'status': 'cancelled',
                'message': 'Payment was cancelled by user'
            })
        
        else:
            return Response({
                'success': False,
                'error': 'Invalid payment status'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def paymongo_webhook(request):
    """
    PayMongo webhook for real-time payment processing
    This gets called immediately when payment succeeds
    """
    try:
        print("\n=== PAYMONGO WEBHOOK RECEIVED ===")
        
        # Verify webhook signature (optional but recommended)
        signature = request.headers.get('paymongo-signature')
        print(f"Signature: {signature}")
        
        event_data = request.data
        event_type = event_data.get('type')
        
        print(f"Event Type: {event_type}")
        print(f"Event Data: {json.dumps(event_data, indent=2)}")
        
        if event_type == 'checkout_session.payment_succeeded':
            # Payment succeeded via checkout session
            session_data = event_data.get('data', {})
            session_id = session_data.get('id')
            attributes = session_data.get('attributes', {})
            
            print(f"[OK] Payment succeeded for session: {session_id}")
            
            # Get metadata
            metadata = attributes.get('metadata', {})
            booking_id = metadata.get('booking_id')
            
            if not booking_id:
                # Try to get from payments
                payments = attributes.get('payments', [])
                if payments:
                    payment_attrs = payments[0].get('attributes', {})
                    payment_metadata = payment_attrs.get('metadata', {})
                    booking_id = payment_metadata.get('booking_id')
            
            if booking_id:
                print(f"Processing payment for booking {booking_id}")
                
                # Process the payment
                payments = attributes.get('payments', [])
                if payments:
                    payment_data = payments[0]
                    payment_id = payment_data['id']
                    payment_attrs = payment_data['attributes']
                    
                    # Process this payment
                    return process_payment_webhook(payment_id, payment_attrs, booking_id)
                else:
                    print("[ERR] No payments found in session")
        
        elif event_type == 'payment.paid':
            # Direct payment succeeded
            payment_data = event_data.get('data', {})
            payment_id = payment_data.get('id')
            payment_attrs = payment_data.get('attributes', {})
            
            print(f"[OK] Direct payment succeeded: {payment_id}")
            
            # Get metadata
            metadata = payment_attrs.get('metadata', {})
            booking_id = metadata.get('booking_id')
            
            if booking_id:
                print(f"Processing direct payment for booking {booking_id}")
                return process_payment_webhook(payment_id, payment_attrs, booking_id)
        
        # Return success to PayMongo
        return Response({"success": True}, status=200)
        
    except Exception as e:
        print(f"[ERR] Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=400)

# In flightapp/views.py, update process_payment_webhook:

def process_payment_webhook(payment_id, payment_attrs, booking_id):
    """
    Process payment from webhook and save to database
    """
    from django.db import transaction
    from app.models import Booking, Payment, BookingDetail, Seat
    from decimal import Decimal
    
    try:
        print(f"\n[?] Processing payment for booking {booking_id}")
        print(f"Payment ID: {payment_id}")
        print(f"Payment Status: {payment_attrs.get('status')}")
        
        with transaction.atomic():
            # Get booking (with lock to prevent race conditions)
            try:
                booking = Booking.objects.select_for_update().get(id=booking_id)
                print(f"Found booking: {booking.id}, Status: {booking.status}")
            except Booking.DoesNotExist:
                print(f"[ERR] Booking {booking_id} not found")
                return Response({"error": "Booking not found"}, status=404)
            
            # Check if payment already exists
            existing_payment = Payment.objects.filter(
                transaction_id=payment_id
            ).first()
            
            if existing_payment:
                print(f"[OK] Payment already exists: {existing_payment.id}")
                return Response({
                    "success": True,
                    "message": "Payment already processed",
                    "payment_id": existing_payment.transaction_id,
                    "booking_status": booking.status
                })
            
            # Convert amount from centavos to PHP
            amount = Decimal(str(payment_attrs['amount'] / 100))
            print(f"Amount: {amount} PHP")
            
            # Get payment method
            payment_method = "Unknown"
            source = payment_attrs.get('source', {})
            source_type = source.get('type', '')
            
            if source_type == 'gcash':
                payment_method = 'GCash'
            elif source_type == 'card':
                payment_method = 'Credit Card'
            elif source_type == 'grab_pay':
                payment_method = 'Grab Pay'
            elif source_type == 'paymaya':
                payment_method = 'PayMaya'
            else:
                payment_method = source_type.capitalize() if source_type else 'Unknown'
            
            print(f"Payment Method: {payment_method}")
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                method=payment_method,
                transaction_id=payment_id,
                status='Completed',
                payment_date=timezone.now()
            )
            
            print(f"[OK] Payment saved to database: {payment.id}")
            
            # Update booking status
            booking.status = 'Confirmed'
            booking.save()
            print(f"[OK] Booking status updated to: {booking.status}")
            
            # Update all booking details status
            updated_details = booking.details.all().update(status='confirmed')
            print(f"[OK] Updated {updated_details} booking details")
            
            # Mark seats as unavailable
            seat_count = 0
            for detail in booking.details.all():
                if detail.seat:
                    detail.seat.is_available = False
                    detail.seat.save()
                    seat_count += 1
            print(f"[OK] Marked {seat_count} seats as unavailable")
            
            # [?] AUTO-GRADING
            if booking.activity:
                print(f"[?] Triggering auto-grading for booking {booking.id}")
                try:
                    from .services.grading_service import grade_booking
                    grade_booking(booking, booking.activity.id)
                except Exception as e:
                    print(f"[WARN] Error during auto-grading: {str(e)}")
            
            print(f"[?] Payment processing COMPLETED for booking {booking_id}")
            
            return Response({
                "success": True,
                "message": "Payment processed successfully",
                "payment_id": payment.transaction_id,
                "booking_id": booking_id,
                "booking_status": "confirmed",
                "booking_reference": booking.pnr,
                "amount": float(amount),
                "method": payment_method
            })
            
    except Exception as e:
        print(f"[ERR] Error in payment processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=400)


def send_booking_confirmation_email(booking):
    """
    Send booking confirmation email
    """
    # You can implement email sending here
    # For now, just log it
    print(f"\n[EMAIL] Would send confirmation email for booking {booking.id}")
    print(f"   To: {booking.user.email if booking.user else 'No user email'}")
    print(f"   Reference: {booking.pnr}")
    print(f"   Amount: {booking.total_amount}")

def process_payment_with_id(payment_id, booking_id):
    """Process payment when we have the payment ID"""
    try:
        from .services.paymongo_service import paymongo_service
        
        print(f"Processing payment {payment_id} for booking {booking_id}")
        
        # Get payment details
        payment_url = f"{paymongo_service.api_url}/payments/{payment_id}"
        payment_response = requests.get(payment_url, headers=paymongo_service.headers)
        
        if payment_response.status_code == 200:
            payment_data = payment_response.json()['data']
            payment_attributes = payment_data['attributes']
            
            if payment_attributes['status'] == 'paid':
                # Create payment record
                from django.db import transaction
                from app.models import Booking, Payment
                from decimal import Decimal
                
                with transaction.atomic():
                    booking = Booking.objects.get(id=booking_id)
                    
                    # Convert amount from centavos to PHP
                    amount = Decimal(str(payment_attributes['amount'] / 100))
                    
                    # Get payment method
                    payment_method = "Unknown"
                    source = payment_attributes.get('source', {})
                    if source.get('type') == 'gcash':
                        payment_method = 'GCash'
                    elif source.get('type') == 'card':
                        payment_method = 'Credit Card'
                    elif source.get('type') == 'grab_pay':
                        payment_method = 'Grab Pay'
                    else:
                        payment_method = source.get('type', 'Unknown').capitalize()
                    
                    # Create payment record
                    payment = Payment.objects.create(
                        booking=booking,
                        amount=amount,
                        method=payment_method,
                        transaction_id=payment_id,
                        status='Completed'
                    )
                    
                    # Update booking status
                    booking.status = 'Confirmed'
                    booking.save()
                    
                    # Update booking details
                    booking.details.all().update(status='confirmed')
                    
                    # Mark seats as unavailable
                    for detail in booking.details.all():
                        if detail.seat:
                            detail.seat.is_available = False
                            detail.seat.save()
                    
                    # [?] AUTO-GRADING
                    if booking.activity:
                        print(f"[?] Triggering auto-grading for booking {booking.id}")
                        try:
                            from .services.grading_service import grade_booking
                            grade_booking(booking, booking.activity.id)
                        except Exception as e:
                            print(f"[WARN] Error during auto-grading: {str(e)}")
                    
                    print(f"[OK] Payment processed: {payment.id}")
                    
                    return Response({
                        'success': True,
                        'payment_id': payment.transaction_id,
                        'booking_status': 'confirmed',
                        'booking_reference': booking.pnr,
                        'message': 'Payment processed successfully'
                    })
        
        return Response({
            'success': False,
            'error': 'Payment not found or not completed'
        })
        
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        })


def handle_successful_payment_without_id(booking_id):
    """Handle case where payment succeeded but we don't have payment ID"""
    try:
        from .services.paymongo_service import paymongo_service
        
        print(f"Looking for payments for booking {booking_id}")
        
        # Search for recent payments (last 5 minutes)
        import time
        five_minutes_ago = int(time.time()) - 300
        
        # List checkout sessions with metadata
        sessions_url = f"{paymongo_service.api_url}/checkout_sessions"
        sessions_response = requests.get(sessions_url, headers=paymongo_service.headers)
        
        if sessions_response.status_code == 200:
            sessions = sessions_response.json()['data']
            
            for session in sessions:
                attributes = session['attributes']
                metadata = attributes.get('metadata', {})
                
                if metadata.get('booking_id') == str(booking_id):
                    # Check if session has payments
                    payments = attributes.get('payments', [])
                    
                    for payment in payments:
                        payment_attrs = payment['attributes']
                        
                        if payment_attrs['status'] == 'paid':
                            # Found a successful payment!
                            return process_payment_with_id(payment['id'], booking_id)
        
        # If no payment found, check directly in payments
        payments_url = f"{paymongo_service.api_url}/payments?created[gte]={five_minutes_ago}"
        payments_response = requests.get(payments_url, headers=paymongo_service.headers)
        
        if payments_response.status_code == 200:
            payments = payments_response.json()['data']
            
            for payment in payments:
                attributes = payment['attributes']
                metadata = attributes.get('metadata', {})
                
                if metadata.get('booking_id') == str(booking_id) and attributes['status'] == 'paid':
                    return process_payment_with_id(payment['id'], booking_id)
        
        return Response({
            'success': False,
            'error': 'No completed payment found for this booking',
            'booking_id': booking_id,
            'status': 'pending_verification'
        })
        
    except Exception as e:
        print(f"Error finding payment: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        })

# In flightapp/views.py, update the check_payment_status function:

@api_view(['GET'])
@permission_classes([AllowAny])
def check_payment_status(request, booking_id):
    """
    Check if payment has been processed for a booking
    """
    try:
        print(f"\n=== CHECKING PAYMENT STATUS ===")
        print(f"Booking ID: {booking_id}")
        
        # Get the booking
        try:
            booking = Booking.objects.get(id=booking_id)
            print(f"Booking found: {booking.id}, Status: {booking.status}")
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Booking {booking_id} not found'
            }, status=404)
        
        # Check if booking is already confirmed
        if booking.status == 'Confirmed':
            print(f"[OK] Booking already confirmed in database")
            payment = Payment.objects.filter(booking=booking, status='Completed').first()
            return Response({
                'success': True,
                'paid': True,
                'payment_id': payment.transaction_id if payment else None,
                'booking_id': booking_id,
                'booking_reference': booking.pnr,
                'booking_status': booking.status,
                'amount': float(payment.amount) if payment else 0,
                'method': payment.method if payment else None,
                'message': 'Booking is already confirmed'
            })
        
        # Check database for completed payment
        payment = Payment.objects.filter(booking=booking, status='Completed').first()
        if payment:
            print(f"[OK] Found completed payment in database: {payment.id}")
            return Response({
                'success': True,
                'paid': True,
                'payment_id': payment.transaction_id,
                'booking_id': booking_id,
                'booking_reference': booking.pnr,
                'booking_status': booking.status,
                'amount': float(payment.amount),
                'method': payment.method,
                'message': 'Payment found in database'
            })
        
        # SEARCH PAYMONGO FOR PAYMENTS
        print(f"[SEARCH] Searching PayMongo for payments...")
        
        try:
            # Option 1: Search checkout sessions
            print(f"  1. Searching checkout sessions...")
            sessions_url = f"{paymongo_service.api_url}/checkout_sessions"
            sessions_response = requests.get(sessions_url, headers=paymongo_service.headers, timeout=10)
            
            if sessions_response.status_code == 200:
                sessions_data = sessions_response.json()
                sessions = sessions_data.get('data', [])
                print(f"    Found {len(sessions)} checkout sessions")
                
                for session in sessions:
                    session_id = session['id']
                    attributes = session.get('attributes', {})
                    metadata = attributes.get('metadata', {})
                    
                    if metadata.get('booking_id') == str(booking_id):
                        print(f"    [OK] Found checkout session for booking {booking_id}")
                        print(f"      Session ID: {session_id}")
                        print(f"      Session Status: {attributes.get('status')}")
                        
                        # Check payments in this session
                        payments = attributes.get('payments', [])
                        print(f"      Payments in session: {len(payments)}")
                        
                        for payment_data in payments:
                            payment_attrs = payment_data.get('attributes', {})
                            payment_id = payment_data.get('id')
                            payment_status = payment_attrs.get('status')
                            
                            print(f"      Payment {payment_id}: {payment_status}")
                            
                            if payment_status == 'paid':
                                print(f"      [OK] Found PAID payment!")
                                # Process this payment
                                return process_payment_from_paymongo(
                                    payment_id, payment_attrs, booking
                                )
            
            # Option 2: Search payments directly (if webhook created them)
            print(f"  2. Searching payments directly...")
            payments_url = f"{paymongo_service.api_url}/payments"
            payments_response = requests.get(payments_url, headers=paymongo_service.headers, timeout=10)
            
            if payments_response.status_code == 200:
                payments_data = payments_response.json()
                payments = payments_data.get('data', [])
                print(f"    Found {len(payments)} total payments")
                
                # Filter payments from last 24 hours for this booking
                import time
                one_day_ago = int(time.time()) - (24 * 60 * 60)
                
                for payment_data in payments:
                    payment_attrs = payment_data.get('attributes', {})
                    created_at = payment_attrs.get('created_at', 0)
                    
                    # Check if payment is recent
                    if created_at >= one_day_ago:
                        metadata = payment_attrs.get('metadata', {})
                        
                        if metadata.get('booking_id') == str(booking_id):
                            payment_id = payment_data.get('id')
                            payment_status = payment_attrs.get('status')
                            
                            print(f"    [OK] Found payment for booking {booking_id}: {payment_status}")
                            
                            if payment_status == 'paid':
                                print(f"    [OK] Payment is PAID! Processing...")
                                return process_payment_from_paymongo(
                                    payment_id, payment_attrs, booking
                                )
            
        except Exception as e:
            print(f"[WARN] Error searching PayMongo: {str(e)}")
        
        # No payment found yet
        print(f"[WATCH] No payment found yet for booking {booking_id}")
        return Response({
            'success': True,
            'paid': False,
            'booking_id': booking_id,
            'booking_status': booking.status,
            'message': 'Payment not yet processed. Please complete payment first.'
        })
        
    except Exception as e:
        print(f"[ERR] Error in check_payment_status: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

def process_payment_immediately(payment_id, payment_attrs, booking):
    """Process payment immediately when found in PayMongo"""
    from django.db import transaction
    from decimal import Decimal
    
    try:
        with transaction.atomic():
            # Convert amount from centavos to PHP
            amount = Decimal(str(payment_attrs['amount'] / 100))
            
            # Get payment method
            payment_method = "Unknown"
            source = payment_attrs.get('source', {})
            if source.get('type') == 'gcash':
                payment_method = 'GCash'
            elif source.get('type') == 'card':
                payment_method = 'Credit Card'
            elif source.get('type') == 'grab_pay':
                payment_method = 'Grab Pay'
            else:
                payment_method = source.get('type', 'Unknown').capitalize()
            
            # Check if payment already exists
            existing_payment = Payment.objects.filter(
                transaction_id=payment_id
            ).first()
            
            if existing_payment:
                return Response({
                    'success': True,
                    'paid': True,
                    'payment_id': existing_payment.transaction_id,
                    'booking_reference': booking.pnr,
                    'booking_status': booking.status,
                    'message': 'Payment already processed'
                })
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                method=payment_method,
                transaction_id=payment_id,
                status='Completed'
            )
            
            # Update booking status
            booking.status = 'Confirmed'
            booking.save()
            
            # Update booking details
            booking.details.all().update(status='confirmed')
            
            # Mark seats as unavailable
            for detail in booking.details.all():
                if detail.seat:
                    detail.seat.is_available = False
                    detail.seat.save()
            
            # [?] AUTO-GRADING
            if booking.activity:
                print(f"[?] Triggering auto-grading for booking {booking.id}")
                try:
                    from .services.grading_service import grade_booking
                    grade_booking(booking, booking.activity.id)
                except Exception as e:
                    print(f"[WARN] Error during auto-grading: {str(e)}")
            
            print(f"[OK] IMMEDIATELY processed payment: {payment.id}")
            
            return Response({
                'success': True,
                'paid': True,
                'payment_id': payment.transaction_id,
                'booking_id': booking.id,
                'booking_reference': booking.pnr,
                'booking_status': 'confirmed',
                'amount': float(amount),
                'method': payment_method,
                'message': 'Payment processed successfully!'
            })
            
    except Exception as e:
        print(f"Error processing payment immediately: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def test_paymongo_setup(request):
    """
    Test PayMongo setup and authentication
    """
    import base64
    from .services.paymongo_service import paymongo_service
    
    # Get the raw secret key
    secret_key = paymongo_service.secret_key
    
    # Recreate the auth header manually
    auth_string = f"{secret_key}:"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    # Test headers
    test_headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {encoded_auth}"
    }
    
    # Make a test request to PayMongo
    import requests
    try:
        test_response = requests.get(
            "https://api.paymongo.com/v1/payment_intents",
            headers=test_headers,
            timeout=10
        )
        
        response_info = {
            "status_code": test_response.status_code,
            "success": test_response.status_code == 200,
            "response_body": test_response.text if test_response.content else "No content"
        }
        
    except Exception as e:
        response_info = {
            "error": str(e),
            "success": False
        }
    
    return Response({
        "debug_info": {
            "secret_key_found": bool(secret_key),
            "secret_key_prefix": secret_key[:10] + "..." if secret_key else None,
            "secret_key_length": len(secret_key) if secret_key else 0,
            "auth_string": auth_string,
            "encoded_auth": encoded_auth,
            "headers_created": test_headers,
            "api_url": paymongo_service.api_url
        },
        "paymongo_test": response_info,
        "message": "[OK] Key found in environment" if secret_key else "[ERR] Key not found"
    })    


# Add this to flightapp/views.py

@api_view(['GET'])
@permission_classes([AllowAny])
def check_booking_payment(request, booking_id):
    """
    Check payment status for a booking and process if found
    """
    try:
        print(f"\n=== CHECKING BOOKING PAYMENT ===")
        print(f"Booking ID: {booking_id}")
        
        # Get the booking
        try:
            booking = Booking.objects.get(id=booking_id)
            print(f"Found booking: {booking.id}, Status: {booking.status}")
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Booking {booking_id} not found'
            }, status=404)
        
        # Check if booking is already confirmed
        if booking.status == 'Confirmed':
            print(f"[OK] Booking already confirmed")
            payment = Payment.objects.filter(booking=booking, status='Completed').first()
            return Response({
                'success': True,
                'paid': True,
                'booking_status': 'confirmed',
                'booking_id': booking_id,
                'booking_reference': booking.pnr,
                'payment_id': payment.transaction_id if payment else None,
                'message': 'Booking is already confirmed'
            })
        
        # Search PayMongo for payments for this booking
        print(f"[SEARCH] Searching PayMongo for booking {booking_id}...")
        
        # Look for checkout sessions with this booking ID in metadata
        sessions_url = f"{paymongo_service.api_url}/checkout_sessions"
        response = requests.get(sessions_url, headers=paymongo_service.headers, timeout=10)
        
        if response.status_code == 200:
            sessions = response.json()['data']
            print(f"Found {len(sessions)} sessions")
            
            for session in sessions:
                attributes = session['attributes']
                metadata = attributes.get('metadata', {})
                
                # Check if this session is for our booking
                if metadata.get('booking_id') == str(booking_id):
                    print(f"[OK] Found checkout session for booking {booking_id}")
                    print(f"Session ID: {session['id']}")
                    print(f"Session Status: {attributes.get('status')}")
                    
                    # Check payments in this session
                    payments = attributes.get('payments', [])
                    print(f"Number of payments in session: {len(payments)}")
                    
                    for payment_data in payments:
                        payment_attrs = payment_data['attributes']
                        print(f"Payment Status: {payment_attrs['status']}")
                        
                        if payment_attrs['status'] == 'paid':
                            print(f"[OK] Found PAID payment in session!")
                            payment_id = payment_data['id']
                            
                            # Get payment details
                            payment_url = f"{paymongo_service.api_url}/payments/{payment_id}"
                            payment_response = requests.get(payment_url, headers=paymongo_service.headers)
                            
                            if payment_response.status_code == 200:
                                payment_details = payment_response.json()['data']
                                
                                # Process this payment
                                return process_payment_webhook(
                                    payment_id, 
                                    payment_details['attributes'], 
                                    booking_id
                                )
        
        # Also search payments directly
        print(f"[SEARCH] Searching payments directly...")
        payments_url = f"{paymongo_service.api_url}/payments"
        payments_response = requests.get(payments_url, headers=paymongo_service.headers, timeout=10)
        
        if payments_response.status_code == 200:
            payments = payments_response.json()['data']
            print(f"Found {len(payments)} total payments")
            
            for payment_data in payments:
                payment_attrs = payment_data['attributes']
                metadata = payment_attrs.get('metadata', {})
                
                if metadata.get('booking_id') == str(booking_id) and payment_attrs['status'] == 'paid':
                    print(f"[OK] Found direct PAID payment for booking {booking_id}")
                    return process_payment_webhook(
                        payment_data['id'], 
                        payment_attrs, 
                        booking_id
                    )
        
        # No payment found yet
        print(f"[WATCH] No payment found yet for booking {booking_id}")
        return Response({
            'success': True,
            'paid': False,
            'booking_status': booking.status,
            'booking_id': booking_id,
            'message': 'Payment not yet processed. Please complete payment and refresh.'
        })
        
    except Exception as e:
        print(f"[ERR] Error checking payment: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)
    



# Add this new endpoint for simple status checking
@api_view(['GET'])
@permission_classes([AllowAny])
def check_booking_status(request, booking_id):
    """
    Simple endpoint to check booking status (no PayMongo search)
    For frontend polling after payment
    """
    try:
        print(f"\n=== SIMPLE BOOKING STATUS CHECK ===")
        print(f"Booking ID: {booking_id}")
        
        booking = Booking.objects.get(id=booking_id)
        payment = Payment.objects.filter(booking=booking, status='Completed').first()
        
        return Response({
            'success': True,
            'booking_id': booking_id,
            'booking_reference': booking.pnr,
            'booking_status': booking.status,
            'has_payment': payment is not None,
            'payment_id': payment.transaction_id if payment else None,
            'paid': booking.status == 'Confirmed' or payment is not None,
            'message': 'Booking status checked'
        })
        
    except Booking.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Booking not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)    
    


# In flightapp/views.py, update the get_seat_class_features function:

@api_view(['GET'])
@permission_classes([AllowAny])
def get_seat_class_features(request):
    """
    API endpoint to get seat class features from database
    """
    try:
        # Get all seat classes
        seat_classes = SeatClass.objects.all()
        
        features_data = {}
        for seat_class in seat_classes:
            # Get features for this seat class
            class_features = SeatClassFeature.objects.filter(
                seat_class=seat_class
            ).order_by('display_order').values_list('feature', flat=True)
            
            if class_features.exists():
                features_data[seat_class.name.lower().replace(' ', '_')] = list(class_features)
            # Don't add empty arrays - only add if features exist
        
        return Response({
            'success': True,
            'data': features_data
        })
        
    except Exception as e:
        print(f"Error loading seat class features: {str(e)}")
        # Return empty data instead of error
        return Response({
            'success': True,
            'data': {}
        })
    


# Django views.py
@api_view(['GET'])
@permission_classes([AllowAny])
def get_booking_by_reference(request, reference):
    """Get booking by reference number (CSUCC00000071 or PNR)"""
    try:
        if reference.startswith('CSUCC'):
            # Extract ID from legacy reference
            booking_id = int(reference.replace('CSUCC', ''))
            booking = Booking.objects.get(id=booking_id)
        else:
            # Search by PNR (GDS style)
            booking = Booking.objects.get(pnr=reference)
            
        serializer = BookingSerializer(booking)
        return Response({
            'success': True,
            'booking': serializer.data
        })
    except (ValueError, Booking.DoesNotExist):
        return Response({
            'success': False,
            'error': 'Booking not found'
        }, status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.status = 'cancelled'
        booking.save()
        return Response({
            'success': True,
            'message': 'Booking cancelled successfully'
        })
    except Booking.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Booking not found'
        }, status=404)    
    


    # Add this function in views.py (anywhere after the imports)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_seats_with_schedule_info(request, schedule_id):
    """
    Get seats with schedule price information
    """
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        seats = Seat.objects.filter(schedule=schedule).select_related(
            'seat_class', 
            'schedule', 
            'schedule__flight',
            'schedule__flight__route'
        ).order_by('row', 'column')
        
        seat_data = []
        for seat in seats:
            # Calculate final price
            try:
                final_price = seat.final_price
            except:
                # Fallback calculation
                base_price = schedule.price if schedule.price else Decimal('0.00')
                multiplier = seat.seat_class.price_multiplier if seat.seat_class else Decimal('1.00')
                adjustment = seat.price_adjustment if seat.price_adjustment else Decimal('0.00')
                final_price = (base_price * multiplier) + adjustment
            
            seat_info = {
                'id': seat.id,
                'seat_code': f"{seat.row}{seat.column}" if seat.row and seat.column else seat.seat_number,
                'seat_number': seat.seat_number,
                'row': seat.row,
                'column': seat.column,
                'is_available': seat.is_available,
                'final_price': float(final_price),
                'price_adjustment': float(seat.price_adjustment) if seat.price_adjustment else 0.0,
                'has_extra_legroom': seat.has_extra_legroom,
                'is_exit_row': seat.is_exit_row,
                'is_bulkhead': seat.is_bulkhead,
                'is_window': seat.is_window,
                'is_aisle': seat.is_aisle,
                'features': [],
            }
            
            # Add features
            if seat.has_extra_legroom:
                seat_info['features'].append("Extra Legroom")
            if seat.is_exit_row:
                seat_info['features'].append("Exit Row")
            if seat.is_bulkhead:
                seat_info['features'].append("Bulkhead")
            if seat.is_window:
                seat_info['features'].append("Window")
            if seat.is_aisle:
                seat_info['features'].append("Aisle")
            
            if seat.seat_class:
                seat_info['seat_class'] = {
                    'id': seat.seat_class.id,
                    'name': seat.seat_class.name,
                    'price_multiplier': float(seat.seat_class.price_multiplier)
                }
            
            seat_data.append(seat_info)
        
        return JsonResponse({
            'success': True,
            'schedule_id': schedule_id,
            'schedule_price': float(schedule.price) if schedule.price else 0.00,
            'flight_number': schedule.flight.flight_number if schedule.flight else '',
            'airline': schedule.flight.airline.code if schedule.flight and schedule.flight.airline else '',
            'seats': seat_data,
            'total_seats': len(seat_data),
            'available_seats': seats.filter(is_available=True).count()
        })
        
    except Schedule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Schedule not found'
        }, status=404)
    except Exception as e:
        print(f"Error in get_seats_with_schedule_info: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    


@api_view(['GET'])
@permission_classes([AllowAny])
def test_seat_data(request, schedule_id):
    """Test endpoint to see what seat data looks like"""
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        seats = Seat.objects.filter(schedule=schedule)[:3]
        
        data = {
            'schedule': {
                'id': schedule.id,
                'price': float(schedule.price) if schedule.price else 0,
                'flight_number': schedule.flight.flight_number if schedule.flight else None
            },
            'seat_count': Seat.objects.filter(schedule=schedule).count(),
            'sample_seats': []
        }
        
        for seat in seats:
            seat_data = {
                'id': seat.id,
                'seat_code': f"{seat.row}{seat.column}" if seat.row and seat.column else seat.seat_number,
                'row': seat.row,
                'column': seat.column,
                'seat_number': seat.seat_number,
                'is_available': seat.is_available,
                'price_adjustment': float(seat.price_adjustment) if seat.price_adjustment else 0,
                'has_extra_legroom': seat.has_extra_legroom,
                'is_exit_row': seat.is_exit_row,
                'is_bulkhead': seat.is_bulkhead,
                'is_window': seat.is_window,
                'is_aisle': seat.is_aisle,
            }
            
            if seat.seat_class:
                seat_data['seat_class'] = {
                    'id': seat.seat_class.id,
                    'name': seat.seat_class.name,
                    'price_multiplier': float(seat.seat_class.price_multiplier)
                }
            
            # Calculate price
            base_price = schedule.price if schedule.price else Decimal('0.00')
            multiplier = seat.seat_class.price_multiplier if seat.seat_class else Decimal('1.00')
            adjustment = seat.price_adjustment if seat.price_adjustment else Decimal('0.00')
            calculated_price = (base_price * multiplier) + adjustment
            
            seat_data['calculated_price'] = float(calculated_price)
            
            # Try to get from property
            try:
                seat_data['final_price_property'] = float(seat.final_price)
            except:
                seat_data['final_price_property'] = 'Error accessing property'
            
            data['sample_seats'].append(seat_data)
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  


def process_payment_webhook(payment_id, payment_attrs, booking_id):
    """
    Process payment from webhook and save to database + send confirmation email
    """
    from django.db import transaction
    from app.models import Booking, Payment, BookingDetail, Seat
    from decimal import Decimal
    
    try:
        print(f"\n[?] Processing payment for booking {booking_id}")
        print(f"Payment ID: {payment_id}")
        print(f"Payment Status: {payment_attrs.get('status')}")
        
        with transaction.atomic():
            # Get booking (with lock to prevent race conditions)
            try:
                booking = Booking.objects.select_for_update().get(id=booking_id)
                print(f"Found booking: {booking.id}, Status: {booking.status}")
            except Booking.DoesNotExist:
                print(f"[ERR] Booking {booking_id} not found")
                return Response({"error": "Booking not found"}, status=404)
            
            # Check if payment already exists
            existing_payment = Payment.objects.filter(
                transaction_id=payment_id
            ).first()
            
            if existing_payment:
                print(f"[OK] Payment already exists: {existing_payment.id}")
                
                # Still send email if booking is confirmed but email wasn't sent
                if booking.status == 'Confirmed':
                    EmailService.send_booking_confirmation(booking, existing_payment)
                
                return Response({
                    "success": True,
                    "message": "Payment already processed",
                    "payment_id": existing_payment.transaction_id,
                    "booking_status": booking.status
                })
            
            # Convert amount from centavos to PHP
            amount = Decimal(str(payment_attrs['amount'] / 100))
            print(f"Amount: {amount} PHP")
            
            # Get payment method
            payment_method = "Unknown"
            source = payment_attrs.get('source', {})
            source_type = source.get('type', '')
            
            if source_type == 'gcash':
                payment_method = 'GCash'
            elif source_type == 'card':
                payment_method = 'Credit Card'
            elif source_type == 'grab_pay':
                payment_method = 'Grab Pay'
            elif source_type == 'paymaya':
                payment_method = 'PayMaya'
            else:
                payment_method = source_type.capitalize() if source_type else 'Unknown'
            
            print(f"Payment Method: {payment_method}")
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                method=payment_method,
                transaction_id=payment_id,
                status='Completed',
                payment_date=timezone.now()
            )
            
            print(f"[OK] Payment saved to database: {payment.id}")
            
            # Update booking status
            booking.status = 'Confirmed'
            booking.save()
            print(f"[OK] Booking status updated to: {booking.status}")
            
            # Update all booking details status
            updated_details = booking.details.all().update(status='confirmed')
            print(f"[OK] Updated {updated_details} booking details")
            
            # Mark seats as unavailable
            seat_count = 0
            for detail in booking.details.all():
                if detail.seat:
                    detail.seat.is_available = False
                    detail.seat.save()
                    seat_count += 1
            print(f"[OK] Marked {seat_count} seats as unavailable")
            
            # [?] SEND BOOKING CONFIRMATION EMAIL
            print(f"[EMAIL] Sending booking confirmation email...")
            email_sent = EmailService.send_booking_confirmation(booking, payment)
            
            if email_sent:
                print(f"[OK] Booking confirmation email sent successfully!")
            else:
                print(f"[WARN] Failed to send booking confirmation email - will retry via admin")
                # Optionally: Queue for retry or notify admin
            
            print(f"[?] Payment processing COMPLETED for booking {booking_id}")
            
            return Response({
                "success": True,
                "message": "Payment processed successfully",
                "payment_id": payment.transaction_id,
                "booking_id": booking_id,
                "booking_status": "confirmed",
                "booking_reference": booking.pnr,
                "amount": float(amount),
                "method": payment_method,
                "email_sent": email_sent
            })
            
    except Exception as e:
        print(f"[ERR] Error in payment processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_seats_with_schedule_info(request, schedule_id):
    """
    Get seats with schedule and aircraft information
    """
    try:
        schedule = Schedule.objects.select_related(
            'flight__aircraft',
            'flight__airline'
        ).get(id=schedule_id)
        
        seats = Seat.objects.filter(schedule=schedule).select_related(
            'seat_class', 
            'schedule', 
            'schedule__flight',
            'schedule__flight__route'
        ).order_by('row', 'column')
        
        # Get aircraft model
        aircraft_model = schedule.flight.aircraft.model if schedule.flight.aircraft else "Airbus A321"
        
        seat_data = []
        for seat in seats:
            # Calculate final price
            try:
                final_price = seat.final_price
            except:
                # Fallback calculation
                base_price = schedule.price if schedule.price else Decimal('0.00')
                multiplier = seat.seat_class.price_multiplier if seat.seat_class else Decimal('1.00')
                adjustment = seat.price_adjustment if seat.price_adjustment else Decimal('0.00')
                final_price = (base_price * multiplier) + adjustment
            
            seat_info = {
                'id': seat.id,
                'seat_code': f"{seat.row}{seat.column}" if seat.row and seat.column else seat.seat_number,
                'seat_number': seat.seat_number,
                'row': seat.row,
                'column': seat.column,
                'is_available': seat.is_available,
                'final_price': float(final_price),
                'price_adjustment': float(seat.price_adjustment) if seat.price_adjustment else 0.0,
                'has_extra_legroom': seat.has_extra_legroom,
                'is_exit_row': seat.is_exit_row,
                'is_bulkhead': seat.is_bulkhead,
                'is_window': seat.is_window,
                'is_aisle': seat.is_aisle,
                'features': [],
            }
            
            # Add features
            if seat.has_extra_legroom:
                seat_info['features'].append("Extra Legroom")
            if seat.is_exit_row:
                seat_info['features'].append("Exit Row")
            if seat.is_bulkhead:
                seat_info['features'].append("Bulkhead")
            if seat.is_window:
                seat_info['features'].append("Window")
            if seat.is_aisle:
                seat_info['features'].append("Aisle")
            
            if seat.seat_class:
                seat_info['seat_class'] = {
                    'id': seat.seat_class.id,
                    'name': seat.seat_class.name,
                    'price_multiplier': float(seat.seat_class.price_multiplier)
                }
            
            seat_data.append(seat_info)
        
        return JsonResponse({
            'success': True,
            'schedule_id': schedule_id,
            'schedule_price': float(schedule.price) if schedule.price else 0.00,
            'aircraft_model': aircraft_model,  # Add aircraft model
            'aircraft_capacity': schedule.flight.aircraft.capacity if schedule.flight.aircraft else 220,
            'flight_number': schedule.flight.flight_number if schedule.flight else '',
            'airline': schedule.flight.airline.code if schedule.flight and schedule.flight.airline else '',
            'airline_name': schedule.flight.airline.name if schedule.flight and schedule.flight.airline else '',
            'seats': seat_data,
            'total_seats': len(seat_data),
            'available_seats': seats.filter(is_available=True).count()
        })
        
    except Schedule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Schedule not found'
        }, status=404)
    except Exception as e:
        print(f"Error in get_seats_with_schedule_info: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    


@api_view(['GET'])
@permission_classes([AllowAny])
def download_boarding_pass(request, booking_detail_id):
    """
    Download boarding pass PDF for a specific booking detail
    """
    try:
        response = BoardingPassPDFService.download_boarding_pass(booking_detail_id)
        if response:
            return response
        else:
            return Response({
                'success': False,
                'error': 'Booking detail not found'
            }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def download_itinerary(request, booking_id):
    """
    Download full itinerary PDF for a booking
    """
    try:
        response = BoardingPassPDFService.download_itinerary(booking_id)
        if response:
            return response
        else:
            return Response({
                'success': False,
                'error': 'Booking not found'
            }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_booking_price(request):
    """
    Calculate the total price for a potential booking without creating it.
    Used by the Review Booking page to show the authoritative backend price.
    """
    try:
        print(f"\n\n=========== DEBUG: calculate_booking_price ===========")
        data = request.data
        print(f"DEBUG: Calculating price for request: {data}")
        
        total_price = Decimal('0.00')
        breakdown = {
            'base_fare': Decimal('0.00'),
            'taxes': Decimal('0.00'),
            'addons': Decimal('0.00'),
            'insurance': Decimal('0.00'),
            'grand_total': Decimal('0.00')
        }
        
        # 1. Calculate Base Fare, Taxes, and Addons
        trip_type = data.get('trip_type', 'one_way')
        passenger_counts = data.get('passengerCount', {})
        adult_count = int(passenger_counts.get('adult', 1))
        child_count = int(passenger_counts.get('children', 0))
        infant_count = int(passenger_counts.get('infant', 0))
        
        pax_type_counts = {
            'adult': adult_count,
            'child': child_count,
            'infant': infant_count,
        }

        # Normalize segments
        segments = []
        if trip_type in ['multi_city', 'multi-city']:
            segments = data.get('segments', [])
        else:
            if data.get('selectedOutbound'):
                segments.append({
                    'selectedFlight': data.get('selectedOutbound'),
                    'addons': data.get('addons', {})
                })
            if trip_type == 'round_trip' and data.get('selectedReturn'):
                segments.append({
                    'selectedFlight': data.get('selectedReturn'),
                    'addons': data.get('return_addons', {})
                })
        
        # 2. Extract IDs helper
        def extract_ids(source):
            ids = []
            if not source: return ids
            for category in ['baggage', 'meals', 'wheelchair', 'seats']:
                cat_data = source.get(category, {})
                for key, val in cat_data.items():
                    if isinstance(val, int):
                        ids.append({'type': category, 'id': val})
                    elif isinstance(val, dict) and val.get('id'):
                        ids.append({'type': category, 'id': val['id']})
            return ids

        # 3. Estimate Taxes helper
        def estimate_taxes_for_segment(schedule_data, pax_type_counts):
            if not schedule_data:
                return Decimal('0.00')

            schedule_id = schedule_data.get('schedule_id') or schedule_data.get('id')
            if not schedule_id:
                return Decimal('0.00')

            try:
                schedule = Schedule.objects.select_related('flight__route').get(id=schedule_id)
            except Schedule.DoesNotExist:
                return Decimal('0.00')

            route = schedule.flight.route
            applicable_taxes = TaxType.objects.filter(
                is_active=True,
                applies_domestic=route.is_domestic,
                applies_international=route.is_international,
            )

            total_taxes = Decimal('0.00')
            applied_any_tax = False
            
            for pax_type, count in pax_type_counts.items():
                if count <= 0:
                    continue

                for tax in applicable_taxes:
                    try:
                        if tax.adult_only and pax_type != 'adult':
                            continue

                        try:
                            rate = PassengerTypeTaxRate.objects.get(
                                tax_type=tax,
                                passenger_type=pax_type,
                            )
                            amount = rate.amount
                        except PassengerTypeTaxRate.DoesNotExist:
                            amount = tax.base_amount

                        if not tax.per_passenger:
                            if pax_type == 'adult':
                                total_taxes += amount
                                applied_any_tax = True
                            continue

                        total_taxes += amount * count
                        applied_any_tax = True
                    except Exception as e:
                        print(f"Error estimating tax {tax.name}: {e}")
                        continue

            # FALLBACK: If no explicit taxes found in DB, use 12% VAT estimation (matches frontend)
            if not applied_any_tax:
                print(f"DEBUG: No explicit taxes found in DB. Applying 12% VAT estimation fallback.")
                outbound_price = Decimal(str(schedule_data.get('price', 0)))
                # Calculate base for this segment
                seg_base = outbound_price * (pax_type_counts.get('adult', 0) + pax_type_counts.get('child', 0))
                seg_base += (outbound_price * Decimal('0.5')) * pax_type_counts.get('infant', 0)
                total_taxes = seg_base * Decimal('0.12')

            return total_taxes

        # 4. Iterate over segments
        for segment in segments:
            selected_flight = segment.get('selectedFlight')
            if not selected_flight:
                continue
            
            # Base Fare
            outbound_price = Decimal(str(selected_flight.get('price', 0)))
            total_base = outbound_price * (adult_count + child_count)
            total_base += (outbound_price * Decimal('0.5')) * infant_count
            breakdown['base_fare'] += total_base
            
            # Taxes
            breakdown['taxes'] += estimate_taxes_for_segment(selected_flight, pax_type_counts)
            
            # Addons
            segment_addons = segment.get('addons', {})
            all_segment_addons = extract_ids(segment_addons)
            for item in all_segment_addons:
                try:
                    price = Decimal('0.00')
                    if item['type'] == 'baggage':
                        obj = BaggageOption.objects.get(id=item['id'])
                        price = obj.price
                    elif item['type'] == 'meals':
                        obj = MealOption.objects.get(id=item['id'])
                        price = obj.price
                    elif item['type'] == 'seats':
                        obj = Seat.objects.get(id=item['id'])
                        price = obj.price_adjustment
                    
                    breakdown['addons'] += price
                except Exception as e:
                    print(f"[WARN] Price calculation error for addon {item}: {e}")

        # 5. Calculate Insurance (per passenger, once)
        insurance_plan_id = data.get('insurance_plan_id')
        if insurance_plan_id:
            try:
                plan = TravelInsurancePlan.objects.get(id=insurance_plan_id, is_active=True)
                # Insurance is per passenger (Adult + Child)
                breakdown['insurance'] = plan.retail_price * (adult_count + child_count)
            except TravelInsurancePlan.DoesNotExist:
                print(f"[WARN] Insurance plan {insurance_plan_id} not found")

        # 5. Final Total (rounding up to nearest integer)
        total_price = breakdown['base_fare'] + breakdown['taxes'] + breakdown['addons'] + breakdown['insurance']
        total_price = total_price.quantize(Decimal('1.'), rounding=ROUND_UP)
        breakdown['grand_total'] = total_price
        
        print(f"[OK] Calculated price: {total_price}")
        print(f"=========== END DEBUG: calculate_booking_price ===========\n\n")
        
        return Response({
            'success': True,
            'total_amount': float(total_price),
            'currency': 'PHP',
            'breakdown': {k: float(v) for k, v in breakdown.items()}
        })

    except Exception as e:
        print(f"[ERR] Error calculating price: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
