# flightapp/views.py
import logging
from django.http import JsonResponse
import requests

logger = logging.getLogger(__name__)
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
    BookingInsuranceRecord, Aircraft, BookingContact, SeatClassFeature,
    TrackLog
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

def get_shared_seat_class_multiplier(airline, seat_class_name):
    """Unified logic to fetch seat class multiplier across search and booking."""
    if not seat_class_name:
        return 1.0
    
    # Normalize name: "Economy Class" -> "Economy"
    name = seat_class_name.strip()
    if "class" in name.lower():
        name = name.lower().replace("class", "").strip().capitalize()

    # Map dynamic frontend bundle names (e.g. "Economy Saver", "Business Flex") to core class names
    name_lower = name.lower()
    base_name = name
    if "premium economy" in name_lower:
        base_name = "Premium Economy"
    elif "economy" in name_lower:
        base_name = "Economy"
    elif "business" in name_lower:
        base_name = "Business"
    elif "first" in name_lower:
        base_name = "First Class"

    try:
        from app.models import SeatClass
        from django.core.cache import cache
        
        # Cache key includes airline if provided
        airline_id = airline.id if hasattr(airline, 'id') else airline if isinstance(airline, (int, str)) else 'gen'
        cache_key = f"sc_mult_{airline_id}_{base_name.replace(' ', '_')}"
        multiplier = cache.get(cache_key)
        
        if multiplier is None:
            # 1. Try airline-specific
            sc = None
            if airline:
                if hasattr(airline, 'id'):
                    sc = SeatClass.objects.filter(airline=airline, name__iexact=base_name).first()
                else:
                    sc = SeatClass.objects.filter(airline_id=airline, name__iexact=base_name).first()
            
            if not sc:
                sc = SeatClass.objects.filter(name__iexact=base_name).first()
                
            multiplier = float(sc.price_multiplier) if sc else 1.0
            cache.set(cache_key, multiplier, 3600)
            
        return multiplier
    except Exception:
        return 1.0

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
        Schedule.update_all_statuses()
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
            success = schedule.generate_seats(config_data=request.data.get('layout_config', {}))
            
            if success:
                return Response({
                    'success': True,
                    'message': 'Seats updated/generated successfully based on provided config',
                    'total_seats': schedule.seats.count(),
                    'available_seats': schedule.seats.filter(is_available=True).count()
                })
            else:
                return Response(
                    {'error': 'Failed to generate seats. Ensure aircraft layout is configured.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
                
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
        
        serializer = SeatSerializer(seats, many=True, context={'session_id': request.query_params.get('session_id')})
        
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

    @action(detail=False, methods=['get'], url_path='price-calendar')
    def price_calendar(self, request):
        """Get the lowest price for each day in a date range for a specific route"""
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not origin or not destination or not start_date_str or not end_date_str:
            return Response({
                'error': 'origin, destination, start_date, and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Pre-fetch context data for pricing
        user = request.user if request.user.is_authenticated else None
        session_id = request.query_params.get('session_id') or request.session.session_key
        if not session_id:
            request.session.save()
            session_id = request.session.session_key

        from app.models import PricingConfiguration
        config = PricingConfiguration.load()
        user_factor = dynamic_pricing.get_user_factor(user, None)

        # Get all schedules for the route and date range
        schedules = Schedule.objects.filter(
            flight__route__origin_airport__code=origin,
            flight__route__destination_airport__code=destination,
            departure_time__date__range=[start_date, end_date],
            status='Open'
        ).select_related(
            'flight__airline',
            'flight__route__origin_airport',
            'flight__route__destination_airport'
        )

        # Group schedules by date
        from collections import defaultdict
        schedules_by_date = defaultdict(list)
        for s in schedules:
            schedules_by_date[s.departure_time.date()].append(s)

        # Calculate occupancy for these schedules
        occupancy_data = Seat.objects.filter(schedule__in=schedules).values('schedule_id').annotate(
            available=Count('id', filter=Q(is_available=True)),
            total=Count('id')
        )
        occupancy_map = {item['schedule_id']: (1 - (item['available'] / item['total'])) if item['total'] > 0 else 1.0 
                        for item in occupancy_data}

        # Prepare calendar data
        calendar_data = []
        current_date = start_date
        while current_date <= end_date:
            daily_schedules = schedules_by_date.get(current_date, [])
            
            if daily_schedules:
                min_price = float('inf')
                for s in daily_schedules:
                    # Pricing context
                    fallback_price = float(s.flight.route.base_price) if s.flight.route.base_price else 5000.0
                    base_price = float(s.ml_base_price) if s.ml_base_price else fallback_price
                    
                    pricing_context = {
                        'config': config,
                        'user_factor': user_factor,
                        'occupancy_factor': self._get_occ_factor(occupancy_map.get(s.id, 1.0), config),
                        'base_price': base_price
                    }
                    
                    # Mock flight data for pricing
                    f_data = {
                        'schedule_id': s.id,
                        'flight_number': s.flight.flight_number,
                        'departure_time': s.departure_time.isoformat(),
                        'origin': origin,
                        'destination': destination,
                    }
                    
                    price_result = dynamic_pricing.get_price_for_user(
                        f_data, user, session_id, context=pricing_context
                    )
                    
                    price = dynamic_pricing.round_price(price_result['final_price'])
                    if price < min_price:
                        min_price = price
                
                calendar_data.append({
                    'date': current_date.isoformat(),
                    'price': min_price,
                    'available': True
                })
            else:
                calendar_data.append({
                    'date': current_date.isoformat(),
                    'price': None,
                    'available': False
                })
                
            current_date += timedelta(days=1)

        return Response({
            'success': True,
            'origin': origin,
            'destination': destination,
            'calendar': calendar_data
        })

    @action(detail=True, methods=['get', 'post'], url_path='repair-seats')
    def repair_seats(self, request, pk=None):
        """Temporary endpoint to repair bad seat data for a schedule"""
        try:
            schedule = self.get_object()
            from app.models import Seat, SeatClass
            
            # Try to generate seats using model logic first
            success = schedule.generate_seats()
            
            if success:
                return Response({
                    'success': True,
                    'message': f'Successfully repaired schedule {schedule.id} using aircraft template.',
                    'total_seats': Seat.objects.filter(schedule=schedule).count()
                })

            # If that fails (e.g. no aircraft template), use hardcoded repair logic as last resort
            from app.models import Seat, SeatClass
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
        return Response({
            'success': True,
            'message': 'No bad seats found for this schedule.',
            'total_seats': Seat.objects.filter(schedule=schedule).count()
        })
    
    def list(self, request, *args, **kwargs):
        """REAL-TIME PRICING - Optimized with Batch Processing"""
        # 0. Track search for demand pricing immediately (affects pricing factors for this request)
        # Get base queryset early to pass to demand tracker
        queryset = self.filter_queryset(self.get_queryset())
        self.track_search_demand(request, queryset)

        # 1. Pre-fetch context data once
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key
        if not session_id:
            request.session.save()
            session_id = request.session.session_key
        
        # Load pricing config once
        from app.models import PricingConfiguration
        config = PricingConfiguration.load()
        
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
                (timezone.now() - s.ml_price_updated_at).total_seconds() > 300): # 5 min refresh
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
                    'total_stops': s.flight.total_stops,
                    'is_domestic': s.flight.route.is_domestic,
                })
            
            # Use the new batch predictor
            new_prices = predictor.predict_prices_batch(flight_data_list)
            
            # Bulk update in DB (minimal hits)
            now = timezone.now()
            for s, price in zip(stale_schedules, new_prices):
                # If ML prediction returns 0, use fallback
                if price <= 0:
                    print(f"[WARN] ML returned 0 for {s.flight.flight_number}, using fallback")
                    price = float(s.flight.route.base_price) if s.flight.route.base_price else 5000.0
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
                'origin': schedule.flight.route.origin_airport.code,
                'destination': schedule.flight.route.destination_airport.code,
            }
            
            # Get base price - use ml_base_price or fallback
            fallback_price = float(schedule.flight.route.base_price) if schedule.flight and schedule.flight.route and schedule.flight.route.base_price else 5000.0
            base_price = float(schedule.ml_base_price) if schedule.ml_base_price else fallback_price
            
            # Prepare context for "Turbo" pricing (no DB hits inside)
            pricing_context = {
                'config': config,
                'user_factor': user_factor,
                'occupancy_factor': self._get_occ_factor(occupancy_map.get(schedule.id, 1.0), config),
                'base_price': base_price
            }
            
            pricing_result = dynamic_pricing.get_price_for_user(
                f_data, user, session_id, context=pricing_context
            )
            
            # ============ ROUNDING LOGIC ============
            final_price = dynamic_pricing.round_price(pricing_result['final_price'])
            base_price = dynamic_pricing.round_price(pricing_result['base_price'])
            
            fallback_price = float(schedule.flight.route.base_price) if schedule.flight and schedule.flight.route and schedule.flight.route.base_price else 5000.0
            ml_base = float(schedule.ml_base_price) if schedule.ml_base_price else fallback_price
            rounded_ml_base = dynamic_pricing.round_price(ml_base)
            
            # Inject dynamic results
            flight_item['price'] = final_price
            flight_item['base_price'] = base_price
            flight_item['ml_base_price'] = rounded_ml_base
            flight_item['ml_predicted'] = True
            flight_item['ml_factors'] = pricing_result['factors_applied']
            flight_item['raw_ml_price'] = ml_base
            
            # Price ID and Timestamp (per search consistency)
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
            price_id_input = f"{session_id}_{schedule.id}_{timestamp}_{random.randint(1, 1000)}"
            flight_item['price_id'] = hashlib.md5(price_id_input.encode()).hexdigest()[:8]
            flight_item['price_calculated_at'] = timezone.now().isoformat()
            
            # ============ SEAT CLASS PRICING ============
            if 'seat_classes' in flight_item:
                for seat_class in flight_item['seat_classes']:
                    seat_class_name = seat_class.get('name', 'Economy')
                    # APPLY DYNAMIC PRICE (pricing_result['final_price']) TO SEAT CLASS
                    # This ensures discounts/surges are reflected in the search results
                    multiplier = get_shared_seat_class_multiplier(schedule.flight.airline, seat_class_name)
                    raw_seat_price = pricing_result['final_price'] * multiplier
                    
                    seat_class['base_price'] = base_price
                    seat_class['price'] = dynamic_pricing.round_seat_class_price(raw_seat_price)
                    seat_class['raw_price'] = float(raw_seat_price)
        
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
            if occupancy_rate > 0.8: return 1.30
            elif occupancy_rate > 0.6: return 1.15
            elif occupancy_rate < 0.2: return 0.85
        return 1.0
    # ===================================================================
    
    def get_seat_class_multiplier(self, seat_class_name):
        return get_shared_seat_class_multiplier(None, seat_class_name)
    
    def track_search_demand(self, request, queryset):
        """Track search queries for demand-based pricing"""
        from django.core.cache import cache
        
        # Track origin-destination pair demand
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        
        if origin and destination:
            route_key = f"route_demand_{origin}_{destination}"
            try:
                cache.incr(route_key)
            except ValueError:
                cache.set(route_key, 1, 3600)
        
        # Track specific flight demand
        for schedule in queryset[:10]:  # Track top 10 only
            try:
                flight_key = f"flight_demand_{schedule.flight.flight_number}"
                try:
                    cache.incr(flight_key)
                except ValueError:
                    cache.set(flight_key, 1, 3600)
            except Exception as e:
                logger.warning(f"Error tracking demand: {e}")
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
        print(f"[API] Received flight data: {flight_data}")
        
        predicted_price = predictor.predict_price(flight_data)
        print(f"[API] Predicted price: {predicted_price}")
        
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
        print(f"[API ERROR] {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

# In views.py - Update the SeatViewSet class
class SeatViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows seats to be viewed, locked and unlocked.
    """
    serializer_class = SeatSerializer
    queryset = Seat.objects.all()
    permission_classes = [permissions.AllowAny]
    pagination_class = None # Disable pagination for seat map
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Handle session_id from either query params or request body
        context['session_id'] = self.request.query_params.get('session_id') or self.request.data.get('session_id')
        return context

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

    @action(detail=True, methods=['post'], url_path='lock')
    def lock(self, request, pk=None):
        """Lock a seat for selection"""
        try:
            seat = self.get_object()
            session_id = request.data.get('session_id')
            duration = int(request.data.get('duration', 15))
            
            if not session_id:
                session_id = request.session.session_key
                if not session_id:
                    request.session.save()
                    session_id = request.session.session_key
            
            # Use atomic transaction with select_for_update to prevent race conditions
            with transaction.atomic():
                # Re-fetch seat with row-level lock
                seat = Seat.objects.select_for_update().get(id=seat.id)
                
                # 1. Check if permanently booked
                is_permanently_booked = BookingDetail.objects.filter(
                    seat=seat,
                    status__in=['pending', 'confirmed', 'checkin', 'boarding', 'completed']
                ).exists()
                
                if is_permanently_booked:
                    return Response({
                        'success': False,
                        'error': 'This seat is already fully booked'
                    }, status=status.HTTP_409_CONFLICT)
                
                # 2. Check if already locked by someone else
                if seat.is_locked and seat.locked_by_session != session_id:
                    return Response({
                        'success': False, 
                        'error': 'Seat is temporarily reserved by another passenger'
                    }, status=status.HTTP_423_LOCKED)
                    
                # Lock the seat
                now = timezone.now()
                seat.locked_at = now
                seat.locked_until = now + timedelta(minutes=duration)
                seat.locked_by_session = session_id
                seat.save()
            
            # Re-read to ensure fresh state
            serializer = self.get_serializer(seat)
            
            return Response({
                'success': True, 
                'message': f'Seat {seat.seat_number} reserved for {duration} minutes',
                'locked_until': seat.locked_until,
                'is_locked_by_me': True,
                'seat': serializer.data
            })
        except Exception as e:
            logger.error(f"Error locking seat {pk}: {str(e)}")
            return Response({'success': False, 'error': str(e)}, status=500)

    @action(detail=True, methods=['post'], url_path='unlock')
    def unlock(self, request, pk=None):
        """Unlock a seat manually"""
        try:
            seat = self.get_object()
            session_id = request.data.get('session_id')
            
            if not session_id:
                session_id = request.session.session_key
            
            # Only allow unlocking if locked by the same session or if it's already expired
            if seat.locked_by_session == session_id or not seat.is_locked:
                seat.locked_at = None
                seat.locked_until = None
                seat.locked_by_session = None
                seat.save()
                return Response({
                    'success': True,
                    'message': f'Seat {seat.seat_number} is now available'
                })
            else:
                return Response({
                    'success': False,
                    'error': 'You do not have permission to release this reservation'
                }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)

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

            booking.submitted_at = timezone.now()
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
                'seat_class': activity.required_seat_class if hasattr(activity, 'required_seat_class') else "",
                'passengers': activity.required_passengers,
            },
            'activity_addons': [
                {
                    "id": aa.id,
                    "addon_id": aa.addon_id if hasattr(aa, 'addon_id') else aa.addon.id,
                    "addon_name": aa.addon.name,
                    "passenger": {
                        "id": aa.passenger_id if hasattr(aa, 'passenger_id') else aa.passenger.id,
                        "first_name": aa.passenger.first_name,
                        "last_name": aa.passenger.last_name
                    }
                }
                for aa in activity.activity_addons.all()
            ],
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
        serializer = CreateBookingSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            with open('backend_debug.log', 'w') as f:
                f.write(f"SER ERROR: {serializer.errors}\n")
            print(f"DEBUG: [Create Booking] Serializer errors: {serializer.errors}")
            logger.error(f"Booking Creation Error: {serializer.errors}. Payload: {request.data}")
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Handle Activity Code Validation and Practice Mode
        activity_code = data.get('activity_code')
        activity_id = data.get('activity_id')
        is_practice = data.get('is_practice', False)
        activity_to_link = None
        
        if (activity_code or activity_id) and not is_practice:
            # Validate activity code or ID
            from fbs_instructor.models import Activity, SectionEnrollment
            from app.models import Students
            
            try:
                if activity_id:
                    activity_to_link = Activity.objects.get(id=activity_id, status='published')
                else:
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
                activity=activity_to_link,
                booking_session_id=data.get('booking_session_id')
            )
            
            # Log the action
            TrackLog.objects.create(
                user=user,
                action=f"Student Operation: Created new booking {booking.id} (Status: {booking.status})"
            )
            
            print(f"DEBUG: Booking created with ID: {booking.id}")
            
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
            
            # NEW: Auto-grading trigger for direct instructor display
            if booking.activity:
                print(f"DEBUG: Triggering early auto-grading for activity-linked booking {booking.id}")
                try:
                    from fbs_instructor.views import calculate_submission_score
                    from fbs_instructor.models import ActivityStudentBinding
                    
                    # Force calculation using the professional rubric logic
                    score_data = calculate_submission_score(booking.activity, booking)
                    
                    # Update or create binding with the score
                    binding, created = ActivityStudentBinding.objects.get_or_create(
                        activity=booking.activity,
                        student__user=booking.user
                    )
                    
                    binding.grade = score_data['total']
                    binding.rubric_breakdown = score_data['rubric_breakdown']
                    binding.status = 'submitted'
                    binding.submitted_at = timezone.now()
                    binding.save()
                    
                    print(f"DEBUG: Early grading SUCCESS for booking {booking.id}. [Score: {score_data['total']}]")
                except Exception as e:
                    print(f"DEBUG: Early grading FAILED: {str(e)}")
                    import traceback
                    traceback.print_exc()

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
        with open('backend_debug.log', 'w') as f:
            f.write(f"EXC ERROR: {str(e)}\n")
            f.write(traceback.format_exc())
            
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
                
                # Normalize segments
                segments = []
                fare_families = data.get('fare_families', {})
                if booking.trip_type in ['multi_city', 'multi-city']:
                    segments = data.get('segments', [])
                else:
                    outbound_ff = fare_families.get('depart') or request.data.get('fare_families', {}).get('depart')
                    outbound = {
                        'selectedFlight': data.get('selectedOutbound'),
                        'addons': data.get('addons', {}),
                        'fare_family': outbound_ff
                    }
                    if outbound['selectedFlight'] and outbound_ff:
                        outbound['selectedFlight']['fare_family'] = outbound_ff
                    segments.append(outbound)
                    
                    if booking.trip_type == 'round_trip' and data.get('selectedReturn'):
                        return_ff = fare_families.get('return') or request.data.get('fare_families', {}).get('return')
                        returning = {
                            'selectedFlight': data.get('selectedReturn'),
                            'addons': data.get('return_addons', {}),
                            'fare_family': return_ff
                        }
                        if returning['selectedFlight'] and return_ff:
                            returning['selectedFlight']['fare_family'] = return_ff
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
            passport_expiry = pax_data.get('passport_expiry', '')
            passenger_type = pax_data.get('type', 'Adult')
            ph_discount_type = pax_data.get('ph_discount_type', 'none')
            
            print(f"    First Name: {first_name}")
            print(f"    Last Name: {last_name}")
            print(f"    Middle Name: {middle_name}")
            print(f"    Type: {passenger_type}")
            print(f"    Date of Birth: {date_of_birth}")
            print(f"    Discount Type: {ph_discount_type}")
            
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

            # Parse passport expiry
            expiry_parsed = None
            if passport_expiry:
                try:
                    clean_expiry = str(passport_expiry).split('T')[0]
                    expiry_parsed = datetime.strptime(clean_expiry, '%Y-%m-%d').date()
                    print(f"    Passport expiry parsed: {expiry_parsed}")
                except Exception as e:
                    print(f"    ERROR parsing passport expiry: {e}")
                    try:
                        expiry_parsed = datetime.strptime(str(passport_expiry), '%Y-%m-%d').date()
                    except:
                        expiry_parsed = None
            
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
                passport_expiry=expiry_parsed,
                passenger_type=passenger_type,
                ph_discount_type=ph_discount_type
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
                # 1. Fetch seat with row-level lock
                if isinstance(seat_data, int):
                    seat = Seat.objects.select_for_update().get(id=seat_data)
                elif isinstance(seat_data, dict) and seat_data.get('id'):
                    seat = Seat.objects.select_for_update().get(id=seat_data['id'])
                
                if seat:
                    # 2. Check if seat is PERMANENTLY booked already (by someone else)
                    is_permanently_booked = BookingDetail.objects.filter(
                        seat=seat,
                        status__in=['pending', 'confirmed', 'checkin', 'boarding', 'completed']
                    ).exclude(booking=booking).exists()
                    
                    if is_permanently_booked:
                        raise Exception(f"Seat {seat.seat_number} has already been booked by another passenger.")
                        
                    # 3. Check if seat is TEMPORARILY locked (by someone else)
                    # If it's locked, it MUST be locked by THIS session
                    if seat.is_locked and seat.locked_by_session != booking.booking_session_id:
                        raise Exception(f"Seat {seat.seat_number} is currently reserved by another passenger.")
                    
                    print(f"  Seat {seat.seat_number} claimed for session {booking.booking_session_id}")
                    
                    # 4. Success - The seat is now permanently linked to this booking
                    # We can clear the soft lock fields as the BookingDetail now serves as the permanent lock
                    seat.locked_until = None
                    seat.locked_by_session = None
                    seat.is_available = False # Model still uses this for legacy checks
                    seat.save()
                    
                    seat_class = seat.seat_class
            except Seat.DoesNotExist:
                print(f"  ERROR: Seat with ID {seat_data} not found")
                seat = None
        
        # If no seat selected (or seat had no seat_class), resolve seat class from flight data.
        # The frontend sends: class_type = "Premium Economy", seat_class = "Premium Economy",
        # fare_family_name = "Premium Saver" (the bundle — different from the class).
        if not seat_class:
            # Try the different keys the frontend may send for the class name
            fare_type_name = (
                selected_flight.get('class_type') or
                selected_flight.get('seat_class') or
                'Economy'
            ).strip()
            # 1. Try airline-specific lookup first
            seat_class = SeatClass.objects.filter(
                airline=schedule.flight.airline,
                name__iexact=fare_type_name
            ).first()
            # 2. Try case-insensitive contains match with airline
            if not seat_class:
                seat_class = SeatClass.objects.filter(
                    airline=schedule.flight.airline,
                    name__icontains=fare_type_name
                ).first()
            # 3. Airline-agnostic fallback (any airline with matching name)
            if not seat_class:
                seat_class = SeatClass.objects.filter(name__iexact=fare_type_name).first()
            if not seat_class:
                seat_class = SeatClass.objects.filter(name__icontains=fare_type_name).first()
            print(f"  [SEAT CLASS LOOKUP] fare_type='{fare_type_name}' -> seat_class={seat_class}")
        
        # Calculate base price - DO NOT TRUST FRONTEND
        session_id = booking.booking_session_id or "booking_creation"
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
            'total_stops': schedule.flight.total_stops,
            'is_domestic': schedule.flight.route.is_domestic,
        }
        
        # Use frontend-selected price as the authoritative quote to match search results exactly
        frontend_price = selected_flight.get('price', 0)
        fare_family = selected_flight.get('fare_family', 'basic')
        
        if frontend_price and float(frontend_price) > 0:
            base_price = Decimal(str(float(frontend_price)))
            print(f"    [CREATE DETAIL] Using frontend quoted base price: PHP {base_price}")
        else:
            # ONLY fallback if missing
            fare_type = selected_flight.get('seat_class') or selected_flight.get('class_type', 'Economy')
            multiplier = get_shared_seat_class_multiplier(schedule.flight.airline, fare_type)

            price_data = dynamic_pricing.get_price_for_user(
                flight_pricing_data, 
                user=user,
                session_id=session_id
            )
            ml_base = float(price_data.get('final_price', schedule.ml_base_price or schedule.price))
            raw_seat_price = Decimal(str(ml_base)) * Decimal(str(multiplier))
            base_price = Decimal(str(dynamic_pricing.round_seat_class_price(raw_seat_price)))
                
            markup = Decimal('0.00')
            if fare_family == 'standard':
                markup = Decimal('1200.00')
            elif fare_family in ['premium', 'flex']:
                markup = Decimal('2500.00')
                
            base_price += markup

        # Apply discounts
        if passenger.passenger_type and passenger.passenger_type.lower() == 'infant':
            # 50% discount for Infants
            print(f"    Applying 50% Infant discount for {passenger.get_full_name()}")
            base_price = base_price * Decimal('0.5')
        elif passenger.ph_discount_type in ['senior', 'pwd']:
            # 20% discount for Senior Citizens and PWDs
            print(f"    Applying 20% {passenger.ph_discount_type.upper()} discount for {passenger.get_full_name()}")
            base_price = base_price * Decimal('0.8')
            
        # Add seat adjustment if any
        if seat:
            # Check for the correct property name from models.py
            adjustment = seat.total_price_adjustment if hasattr(seat, 'total_price_adjustment') else Decimal('0.00')
            if adjustment > 0:
                # Check for explicit is_included flag (same logic as other addons)
                is_included = False
                if isinstance(seat_data, dict):
                    is_included = seat_data.get('is_included', fare_family == 'premium')
                else:
                    is_included = (fare_family == 'premium')

                if not is_included:
                    base_price += adjustment
                    print(f"    Added seat adjustment to base price: PHP {adjustment}")
                else:
                    print(f"    Skipping seat adjustment because it is marked as INCLUDED")
        
        # Create booking detail
        booking_detail = BookingDetail.objects.create(
            booking=booking,
            passenger=passenger,
            schedule=schedule,
            seat=seat, 
            seat_class=seat_class,
            price=base_price,
            fare_family_name=selected_flight.get('fare_family_name') or selected_flight.get('class_type') or selected_flight.get('seat_class'),
            passenger_type=passenger.passenger_type,
            status='pending'
        )
        
        # Add add-ons
        fare_family = selected_flight.get('fare_family', 'basic')
        _add_addons_to_booking_detail(booking_detail, segment_addons, passenger_data or {}, fare_family=fare_family)
        
        return booking_detail
        
    except Exception as e:
        print(f"ERROR in _create_booking_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# In flightapp/views.py, update the _add_addons_to_booking_detail function:
def _add_addons_to_booking_detail(booking_detail, segment_addons, passenger_data, fare_family='basic'):
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
                
                # Check for explicit is_included flag from frontend, fallback to premium rule
                is_premium = fare_family == 'premium'
                is_included = baggage_data.get('is_included', is_premium)
                
                # Check for explicit price from frontend, fallback to 0.00 or DB price
                if 'price' in baggage_data and baggage_data['price'] is not None:
                    try:
                        addon_price = Decimal(str(baggage_data['price']))
                    except Exception:
                        addon_price = Decimal('0.00')
                else:
                    addon_price = Decimal('0.00') if is_included else baggage_option.price
                
                # COLLISION FIX: Include price and included in lookup
                addon, created = AddOn.objects.get_or_create(
                    baggage_option=baggage_option,
                    price=addon_price,
                    included=is_included,
                    defaults={
                        'name': f"Extra Baggage {baggage_option.formatted_weight}",
                        'airline': airline,
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added baggage addon: {baggage_option.name} (Price: {addon_price})")
            except BaggageOption.DoesNotExist:
                print(f"DEBUG: Baggage option with ID {baggage_data['id']} not found")
        elif isinstance(baggage_data, int):
            try:
                baggage_option = BaggageOption.objects.get(id=baggage_data)
                
                # Is this baggage included in the fare family?
                is_premium = fare_family == 'premium'
                addon_price = Decimal('0.00') if is_premium else baggage_option.price
                
                # COLLISION FIX: Include price and included in lookup
                addon, created = AddOn.objects.get_or_create(
                    baggage_option=baggage_option,
                    price=addon_price,
                    included=is_premium,
                    defaults={
                        'name': f"Extra Baggage {baggage_option.formatted_weight}",
                        'airline': airline,
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added baggage addon: {baggage_option.name} (Price: {addon_price})")
            except BaggageOption.DoesNotExist:
                print(f"DEBUG: Baggage option with ID {baggage_data} not found")
    
    # Meal add-on - UPDATED for multiple meals
    meals_data = segment_addons.get('meals', {}).get(passenger_key)
    if meals_data:
        # Convert to list if it's a single item for uniform processing
        if not isinstance(meals_data, list):
            meals_data = [meals_data]
            
        for meal_item in meals_data:
            meal_id = None
            if isinstance(meal_item, dict) and meal_item.get('id'):
                meal_id = meal_item['id']
            elif isinstance(meal_item, (int, str)):
                meal_id = meal_item
                
            if meal_id:
                try:
                    meal_option = MealOption.objects.get(id=meal_id)
                    
                    is_premium = fare_family == 'premium'
                    if isinstance(meal_item, dict):
                        is_included = meal_item.get('is_included', is_premium)
                        if 'price' in meal_item and meal_item['price'] is not None:
                            try:
                                addon_price = Decimal(str(meal_item['price']))
                            except Exception:
                                addon_price = Decimal('0.00')
                        else:
                            addon_price = Decimal('0.00') if is_included else meal_option.price
                    else:
                        is_included = is_premium
                        addon_price = Decimal('0.00') if is_included else meal_option.price

                    # COLLISION FIX: Include price in lookup
                    addon, created = AddOn.objects.get_or_create(
                        meal_option=meal_option,
                        price=addon_price,
                        included=is_included,
                        defaults={
                            'name': f"Meal: {meal_option.name}",
                            'airline': airline,
                        }
                    )
                    addons_to_link.append(addon)
                    print(f"DEBUG: Added meal addon: {meal_option.name}")
                except MealOption.DoesNotExist:
                    print(f"DEBUG: Meal option with ID {meal_id} not found")
    
    # Assistance service
    assistance_data = segment_addons.get('wheelchair', {}).get(passenger_key)
    if assistance_data:
        service_id = None
        if isinstance(assistance_data, dict) and assistance_data.get('id'):
            service_id = assistance_data['id']
        elif isinstance(assistance_data, (int, str)):
            service_id = assistance_data
            
        if service_id:
            try:
                assistance_service = AssistanceService.objects.get(id=service_id)
                
                if isinstance(assistance_data, dict):
                    is_included = assistance_data.get('is_included', assistance_service.is_included)
                    if 'price' in assistance_data and assistance_data['price'] is not None:
                        try:
                            addon_price = Decimal(str(assistance_data['price']))
                        except Exception:
                            addon_price = Decimal('0.00')
                    else:
                        addon_price = Decimal('0.00') if is_included else assistance_service.price
                else:
                    is_included = assistance_service.is_included
                    addon_price = Decimal('0.00') if is_included else assistance_service.price

                # COLLISION FIX: Include price and included in lookup
                addon, created = AddOn.objects.get_or_create(
                    assistance_service=assistance_service,
                    price=addon_price,
                    included=is_included,
                    defaults={
                        'name': f"Assistance: {assistance_service.name}",
                        'airline': airline,
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
        has_vat_applied = False
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
                    
                    if tax.code == 'VAT':
                        has_vat_applied = True
                        
                    # Add to booking detail tax amount (Ensuring Decimal)
                    current_tax = Decimal(str(detail.tax_amount or 0.0))
                    detail.tax_amount = current_tax + Decimal(str(amount))
                    detail.save()
                    applied_any_tax = True
                
            except Exception as e:
                print(f"Error applying tax {tax.name}: {e}")
                continue


        # Fallbacks for missing VAT and DPSC independently
        try:
            has_dpsc_applied = any(tax.code == 'DPSC' for tax in applicable_taxes)
            
            # VAT
            if not has_vat_applied and detail.passenger.ph_discount_type not in ['senior', 'pwd']:
                vat_tax, _ = TaxType.objects.get_or_create(code='VAT', defaults={'name': 'Value Added Tax', 'base_amount': Decimal('0.00'), 'is_active': True, 'per_passenger': True, 'applies_domestic': True, 'applies_international': True})
                fallback_vat = Decimal(str(detail.price)) * Decimal('0.12')
                if fallback_vat > 0:
                    BookingTax.objects.create(booking=booking, tax_type=vat_tax, amount=fallback_vat, passenger_type=passenger_type)
                    current_tax = Decimal(str(detail.tax_amount or 0.0))
                    detail.tax_amount = current_tax + fallback_vat
                    detail.save()
                    print(f"DEBUG: Applied fallback VAT for detail {detail.id}")

            # Terminal Fee
            if not has_dpsc_applied and passenger_type != 'infant':
                dpsc_tax, _ = TaxType.objects.get_or_create(code='DPSC', defaults={'name': 'Domestic Passenger Service Charge', 'base_amount': Decimal('200.00'), 'is_active': True, 'per_passenger': True, 'applies_domestic': True, 'applies_international': False})
                terminal_fee = Decimal('200.00')
                BookingTax.objects.create(booking=booking, tax_type=dpsc_tax, amount=terminal_fee, passenger_type=passenger_type)
                current_tax = Decimal(str(detail.tax_amount or 0.0))
                detail.tax_amount = current_tax + terminal_fee
                detail.save()
                print(f"DEBUG: Applied fallback Terminal Fee for detail {detail.id}")
                
        except Exception as e:
            print(f"ERR Fallback Taxes: {e}")

        # ADDON VAT: Always apply 12% VAT to paid addons
        try:
            addons_vat = Decimal('0.00')
            for addon in detail.addons.all():
                if addon.price and not addon.included:
                    addons_vat += Decimal(str(addon.price)) * Decimal('0.12')
            
            if addons_vat > 0:
                print(f"DEBUG: Applying {addons_vat} VAT to addons for detail {detail.id}")
                # Create a VAT record for addons
                vat_tax, _ = TaxType.objects.get_or_create(code='VAT', defaults={'name': 'Value Added Tax'})
                BookingTax.objects.create(
                    booking=booking,
                    tax_type=vat_tax,
                    amount=addons_vat,
                    passenger_type=passenger_type
                )
                # Update detail tax amount
                current_tax = Decimal(str(detail.tax_amount)) if detail.tax_amount else Decimal('0.00')
                detail.tax_amount = current_tax + addons_vat
                detail.save()
        except Exception as e:
            print(f"ERROR in addon VAT: {e}")

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
            # IMPORTANT: Skip infants for insurance
            is_infant = detail.passenger_type and detail.passenger_type.lower() == 'infant'
            
            if detail.schedule_id == first_schedule.id and not is_infant:
                insurance_record = BookingInsuranceRecord.objects.create(
                    booking_detail=detail,
                    insurance_plan=plan,
                    insured_amount=plan.retail_price,
                    sale_price=plan.retail_price,
                    status='active'
                )
                created_count += 1
                print(f"DEBUG: Created insurance record {insurance_record.policy_number} for passenger {detail.passenger.get_full_name()}")
            elif is_infant:
                print(f"DEBUG: Skipping insurance for infant {detail.passenger.get_full_name()}")
        
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
        
        # No delay needed in transaction context
        # Refresh booking from database
        booking.refresh_from_db()
        
        from django.db.models import Sum
        
        # 1. Base fare total
        base_fare_total = BookingDetail.objects.filter(
            booking=booking
        ).aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        print(f"  Base fare total: {base_fare_total}")
        
        # 2. Insurance total
        insurance_total = Decimal('0.00')
        booking_details = BookingDetail.objects.filter(booking=booking)
        for detail in booking_details:
            if hasattr(detail, 'insurance_record') and detail.insurance_record:
                insurance_total += detail.insurance_record.sale_price
        print(f"  Insurance total: {insurance_total}")
        
        # 3. Tax total (includes base fare tax AND addon VAT)
        tax_total = BookingTax.objects.filter(
            booking=booking
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        print(f"  Tax total: {tax_total}")
        
        # 4. Addon total (sum of base prices)
        addon_total = Decimal('0.00')
        booking_details = BookingDetail.objects.filter(booking=booking).prefetch_related('addons')
        for detail in booking_details:
            for addon in detail.addons.all():
                if addon.price and not addon.included:
                    addon_total += Decimal(str(addon.price))
        print(f"  Addon total base: {addon_total}")
        
        # 5. Grand total
        calculated_total = base_fare_total + insurance_total + tax_total + addon_total
        
        # Log any discrepancy
        stored_frontend_total = booking.total_amount
        if stored_frontend_total and abs(calculated_total - stored_frontend_total) > Decimal('1.00'):
            print(f"  [WARN] SECURITY: Total mismatch! Frontend claimed: {stored_frontend_total}, Backend calculated: {calculated_total}")
        
        # Rounding up to nearest integer
        final_total = (calculated_total).quantize(Decimal('1.'), rounding=ROUND_UP)
        
        # Save totals to booking
        booking.base_fare_total = base_fare_total
        booking.insurance_total = insurance_total
        booking.tax_total = tax_total
        booking.total_amount = final_total # Update with authoritative volume
        booking.save()
        
        print(f"  [OK] Final Grand Total: {final_total}")
        print(f"=========== END DEBUG: _update_booking_totals ===========\n\n")
        
    except Exception as e:
        print(f"[ERR] Error in _update_booking_totals: {str(e)}")
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
                    print(f"[SECURITY ALERT] Payment mismatch! Paid: {amount_paid}, Required: {booking.total_amount}")
                    return Response({
                        'success': False,
                        'error': f'Payment discrepancy detected. Expected {booking.total_amount}, but received {amount_paid}. This transaction has been flagged for review.',
                        'booking_reference': booking.pnr
                    }, status=status.HTTP_400_BAD_REQUEST)
                
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

                booking.submitted_at = timezone.now()
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

        from app.models import Booking
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Booking not found'
            }, status=404)

        # Handle Mock Session Fallback
        if str(session_id).startswith('mock_session_'):
            print(f"[FALLBACK] Verifying mock session for booking {booking_id}")
            # Manually trigger processing for mock session
            mock_attrs = {
                'amount': int(float(booking.total_amount) * 100),
                'source': {'type': 'mock_fallback'}
            }
            return process_payment_from_paymongo(f"mock_tr_{booking_id}", mock_attrs, booking)

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

            booking.submitted_at = timezone.now()
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

                    booking.submitted_at = timezone.now()
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

            booking.submitted_at = timezone.now()
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
    API endpoint to get seat class features and fare bundles from database
    """
    try:
        from app.models import SeatClass, SeatClassFeature, FareBundle
        from app.serializers import FareBundleSerializer
        # Get all seat classes
        seat_classes = SeatClass.objects.all()
        
        features_data = {}
        bundles_data = {}
        for seat_class in seat_classes:
            # 1. Get basic features
            class_features = SeatClassFeature.objects.filter(
                seat_class=seat_class, is_active=True
            ).order_by('display_order').values_list('feature', flat=True)
            
            class_key = seat_class.name.lower().replace(' ', '_')
            if class_features.exists():
                features_data[class_key] = list(class_features)

            # 2. Get Fare Bundles for this class
            bundles = FareBundle.objects.filter(
                seat_class=seat_class, is_active=True
            ).prefetch_related('bundle_features').order_by('display_order')
            
            if bundles.exists():
                bundles_data[class_key] = FareBundleSerializer(bundles, many=True).data
        
        return Response({
            'success': True,
            'data': features_data,
            'bundles': bundles_data
        })
        
    except Exception as e:
        print(f"Error loading seat class features: {str(e)}")
        # Return empty data instead of error
        return Response({
            'success': False,
            'data': {},
            'bundles': {}
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

            booking.submitted_at = timezone.now()
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
        passengers = data.get('passengers', [])
        
        if not passengers:
            # Fallback to counts if No passengers array (unlikely with new frontend)
            passenger_counts = data.get('passengerCount', {})
            adult_count = int(passenger_counts.get('adult', 1))
            child_count = int(passenger_counts.get('children', 0))
            infant_count = int(passenger_counts.get('infant', 0))
            
            # Reconstruct passengers array for consistency
            passengers = []
            for _ in range(adult_count): passengers.append({'type': 'adult', 'ph_discount_type': 'none'})
            for _ in range(child_count): passengers.append({'type': 'child', 'ph_discount_type': 'none'})
            for _ in range(infant_count): passengers.append({'type': 'infant', 'ph_discount_type': 'none'})
        else:
            # Calculate counts from passengers list
            adult_count = len([p for p in passengers if p.get('type', 'adult').lower() == 'adult'])
            child_count = len([p for p in passengers if p.get('type', '').lower() == 'child'])
            infant_count = len([p for p in passengers if p.get('type', '').lower() == 'infant'])

        # Normalize segments
        segments = []
        if trip_type in ['multi_city', 'multi-city']:
            segments = data.get('segments', [])
        else:
            # Normalize round-trip identifiers (frontend may use dash or underscore)
            is_round_trip = trip_type in ['round_trip', 'round-trip']
            if data.get('selectedOutbound'):
                segments.append({
                    'selectedFlight': data.get('selectedOutbound'),
                    'addons': data.get('addons', {}),
                    'type': 'depart'
                })
            if is_round_trip and data.get('selectedReturn'):
                segments.append({
                    'selectedFlight': data.get('selectedReturn'),
                    'addons': data.get('return_addons', {}),
                    'type': 'return'
                })
        
        # 2. Extract IDs helper
        def extract_ids(source, segment_key=None):
            ids = []
            if not source: return ids
            for category in ['baggage', 'meals', 'wheelchair', 'seats']:
                cat_data = source.get(category, {})
                
                # The frontend store structure is addons[category][segmentKey][passengerKey]
                # If segment_key is provided, we only look into that segment.
                # If not, we iterate all segments (fallback for old format).
                
                target_data = cat_data
                if segment_key and segment_key in cat_data:
                    target_data = cat_data[segment_key]
                
                def _process_item(item_val, pax_key):
                    if item_val is None:
                        return
                        
                    # Handle multiple items (e.g., list of meal IDs)
                    if isinstance(item_val, list):
                        for sub_item in item_val:
                            _process_item(sub_item, pax_key)
                        return

                    if isinstance(item_val, (int, str)):
                        ids.append({'type': category, 'id': item_val, 'passenger_key': pax_key})
                    elif isinstance(item_val, dict):
                        # Some addons are objects with an 'id'
                        if item_val.get('id'):
                            ids.append({
                                'type': category, 
                                'id': item_val['id'], 
                                'passenger_key': pax_key,
                                'is_included': item_val.get('is_included', False),
                                'price': item_val.get('price')
                            })
                        # Or maybe it's the seat object which has 'seat_id' or just 'id'
                        elif item_val.get('seat_id'):
                            ids.append({
                                'type': category, 
                                'id': item_val['seat_id'], 
                                'passenger_key': pax_key,
                                'is_included': item_val.get('is_included', False),
                                'price': item_val.get('price')
                            })
                
                if not isinstance(target_data, dict):
                    print(f"[WARN] target_data for {category} is not a dict: {type(target_data)}")
                    continue

                for k, v in target_data.items():
                    # If v is another dict and doesn't look like an addon object (no ID/price), 
                    # it might be another level of nesting (segment or passenger)
                    if isinstance(v, dict) and not (v.get('id') or v.get('price') or v.get('seat_id')):
                        for sub_k, sub_v in v.items():
                            _process_item(sub_v, sub_k)
                    else:
                        _process_item(v, k)
            return ids

        # 3. Estimate Taxes helper
        def estimate_taxes_for_segment(schedule_data, passengers, segment_addons_data=None, segment_key=None, tax_breakdown=None, fare_family='basic', base_price_override=None):
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
            
            # Initialize breakdown if needed
            if tax_breakdown is None:
                tax_breakdown = {}

            total_taxes = Decimal('0.00')
            applied_any_tax = False
            
            segment_price = base_price_override if base_price_override is not None else Decimal(str(schedule_data.get('price', 0)))
            
            for pax in passengers:
                pax_type = pax.get('type', 'adult').lower()
                ph_discount = pax.get('ph_discount_type', 'none')

                has_vat_applied = False
                has_dpsc_applied = False
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
                            continue

                        total_taxes += amount
                        applied_any_tax = True
                        if tax.code == 'VAT':
                            has_vat_applied = True
                        if tax.code == 'DPSC':
                            has_dpsc_applied = True
                        
                        # Granular breakdown
                        label = tax.name or tax.code
                        tax_breakdown[label] = tax_breakdown.get(label, Decimal('0.00')) + amount
                    except Exception as e:
                        print(f"Error estimating tax {tax.name}: {e}")
                        continue

                # Add Fallback 12% VAT if not found in DB tax rules
                if not has_vat_applied and ph_discount not in ['senior', 'pwd']:
                    pax_base = segment_price
                    if pax_type == 'infant':
                        pax_base = segment_price * Decimal('0.5')
                    fallback_vat = (pax_base * Decimal('0.12')).quantize(Decimal('0.01'))
                    total_taxes += fallback_vat
                    applied_any_tax = True
                    
                    label = "Value Added Tax (VAT)"
                    tax_breakdown[label] = tax_breakdown.get(label, Decimal('0.00')) + fallback_vat
                    print(f"DEBUG: Applied fallback 12% VAT ({fallback_vat}) for {pax_type} on segment {schedule_id}")
                
                # Add Fallback Terminal Fee
                if not has_dpsc_applied and pax_type != 'infant':
                    fee = Decimal('200.00')
                    total_taxes += fee
                    applied_any_tax = True
                    label = "Domestic Passenger Service Charge"
                    tax_breakdown[label] = tax_breakdown.get(label, Decimal('0.00')) + fee
                    print(f"DEBUG: Applied fallback Terminal Fee ({fee}) for {pax_type} on segment {schedule_id}")
            
            # ADDON VAT: Always apply 12% VAT to paid addons (matches frontend totalTaxes)
            if segment_addons_data:
                all_segment_addons = extract_ids(segment_addons_data, segment_key)
                for item in all_segment_addons:
                    try:
                        price = Decimal('0.00')
                        is_included = item.get('is_included', fare_family == 'premium')
                        
                        if item.get('price') is not None:
                            price = Decimal(str(item.get('price')))
                        else:
                            if item['type'] == 'baggage':
                                obj = BaggageOption.objects.get(id=item['id'])
                                price = obj.price
                            elif item['type'] == 'meals':
                                obj = MealOption.objects.get(id=item['id'])
                                price = obj.price
                            elif item['type'] == 'seats':
                                if isinstance(item['id'], (int, str)) and str(item['id']).isdigit():
                                    obj = Seat.objects.get(id=item['id'])
                                    price = obj.total_price_adjustment or Decimal('0.00')
                                else:
                                    price = Decimal(str(item.get('price', 0)))
                                    
                            if is_included:
                                price = Decimal('0.00')
                            
                            # DEBUG: Track addon prices for discrepancy audit
                            print(f"DEBUG: Addon estimate for segment {segment_key}: {item['type']} ID {item['id']} - price={price}, is_included={is_included}")
                        
                        if price > 0:
                            addon_vat = (price * Decimal('0.12')).quantize(Decimal('0.01'))
                            total_taxes += addon_vat
                            label = "Value Added Tax (VAT)"
                            tax_breakdown[label] = tax_breakdown.get(label, Decimal('0.00')) + addon_vat
                            
                    except Exception as e:
                        print(f"[WARN] Addon base price error in tax estimate: {e}")

            return total_taxes

        # 4. Iterate over segments
        overall_tax_breakdown = {}
        total_adult_base = Decimal('0.00')
        total_child_base = Decimal('0.00')
        total_infant_base = Decimal('0.00')
        
        # Categorized addon tracking
        breakdown['seats'] = Decimal('0.00')
        breakdown['baggage'] = Decimal('0.00')
        breakdown['meals'] = Decimal('0.00')
        breakdown['assistance'] = Decimal('0.00')
        
        for idx, segment in enumerate(segments):
            selected_flight = segment.get('selectedFlight')
            if not selected_flight:
                continue
            
            # Determine segment key (depart/return/index)
            segment_key = segment.get('type')
            if not segment_key:
                if idx == 0: segment_key = 'depart'
                elif idx == 1 and trip_type == 'round_trip': segment_key = 'return'
                else: segment_key = str(idx)

            # Base Fare calculation per passenger
            frontend_price = selected_flight.get('price', 0)
            fare_family = selected_flight.get('fare_family', 'basic')
            schedule_id = selected_flight.get('schedule_id') or selected_flight.get('id')
            
            try:
                schedule_obj = Schedule.objects.get(id=schedule_id)
                
                if frontend_price and float(frontend_price) > 0:
                    outbound_price = Decimal(str(float(frontend_price)))
                else:
                    fare_type = selected_flight.get('seat_class') or selected_flight.get('class_type', 'Economy')
                    multiplier = get_shared_seat_class_multiplier(schedule_obj.flight.airline, fare_type)
                    
                    flight_pricing_data = {
                        'schedule_id': schedule_obj.id,
                        'flight_number': schedule_obj.flight.flight_number,
                        'airline_code': schedule_obj.flight.airline.code,
                        'airline_name': schedule_obj.flight.airline.name,
                        'origin': schedule_obj.flight.route.origin_airport.code,
                        'destination': schedule_obj.flight.route.destination_airport.code,
                        'departure_time': schedule_obj.departure_time.isoformat(),
                        'arrival_time': schedule_obj.arrival_time.isoformat(),
                        'total_stops': schedule_obj.flight.total_stops,
                        'is_domestic': schedule_obj.flight.route.is_domestic,
                    }
                    session_id = data.get('booking_session_id', "booking_creation")
                    user = request.user if request.user.is_authenticated else None
                    price_data = dynamic_pricing.get_price_for_user(flight_pricing_data, user=user, session_id=session_id)
                    ml_base = float(price_data.get('final_price', schedule_obj.ml_base_price or schedule_obj.price))
                    raw_seat_price = Decimal(str(ml_base)) * Decimal(str(multiplier))
                    outbound_price = Decimal(str(dynamic_pricing.round_seat_class_price(raw_seat_price)))
                    
                    markup = Decimal('0.00')
                    if fare_family == 'standard':
                        markup = Decimal('1200.00')
                    elif fare_family in ['premium', 'flex']:
                        markup = Decimal('2500.00')
                    outbound_price += markup
            except Schedule.DoesNotExist:
                outbound_price = Decimal(str(frontend_price or 0))

            segment_base_fare = Decimal('0.00')
            for pax in passengers:
                pax_type = pax.get('type', 'adult').lower()
                ph_discount = pax.get('ph_discount_type', 'none')
                
                pax_price = outbound_price
                if pax_type == 'infant':
                    pax_price = outbound_price * Decimal('0.5')
                    total_infant_base += pax_price
                elif ph_discount in ['senior', 'pwd']:
                    pax_price = outbound_price * Decimal('0.8')
                    total_adult_base += pax_price
                elif pax_type == 'child':
                    total_child_base += pax_price
                else:
                    total_adult_base += pax_price
                segment_base_fare += pax_price
                
            breakdown['base_fare'] += segment_base_fare
            
            # Taxes
            breakdown['taxes'] += estimate_taxes_for_segment(
                selected_flight, 
                passengers, 
                segment.get('addons', {}), 
                segment_key, 
                overall_tax_breakdown, 
                fare_family=fare_family,
                base_price_override=outbound_price
            )
            
            # Addons with categorized tracking
            segment_addons_data = segment.get('addons', {})
            all_segment_addons = extract_ids(segment_addons_data, segment_key)
            for item in all_segment_addons:
                try:
                    price = Decimal('0.00')
                    is_included = item.get('is_included', fare_family == 'premium')
                    
                    if item.get('price') is not None:
                        price = Decimal(str(item.get('price')))
                    else:
                        if item['type'] == 'baggage':
                            obj = BaggageOption.objects.get(id=item['id'])
                            price = obj.price
                        elif item['type'] == 'meals':
                            obj = MealOption.objects.get(id=item['id'])
                            price = obj.price
                        elif item['type'] == 'seats':
                            try:
                                if isinstance(item['id'], (int, str)) and str(item['id']).isdigit():
                                    obj = Seat.objects.get(id=item['id'])
                                    price = obj.total_price_adjustment if hasattr(obj, 'total_price_adjustment') else Decimal('0.00')
                                else:
                                    price = Decimal(str(item.get('price', 0)))
                            except Seat.DoesNotExist:
                                price = Decimal(str(item.get('price', 0)))
                        
                        if is_included:
                            price = Decimal('0.00')
                            
                    breakdown['addons'] += price
                    
                    # Store in category
                    if item['type'] == 'seats': breakdown['seats'] += price
                    elif item['type'] == 'baggage': breakdown['baggage'] += price
                    elif item['type'] == 'meals': breakdown['meals'] += price
                    elif item['type'] == 'wheelchair': breakdown['assistance'] += price
                    
                except Exception as e:
                    print(f"[WARN] Price calculation error for addon {item}: {e}")

        # Finalize passenger-type breakdowns
        breakdown['adult_base'] = total_adult_base
        breakdown['child_base'] = total_child_base
        breakdown['infant_base'] = total_infant_base

        # 5. Calculate Insurance
        insurance_plan_id = data.get('insurance_plan_id')
        if insurance_plan_id:
            try:
                plan = TravelInsurancePlan.objects.get(id=insurance_plan_id, is_active=True)
                total_insurable = adult_count + child_count
                breakdown['insurance'] = plan.retail_price * total_insurable
            except TravelInsurancePlan.DoesNotExist:
                print(f"[WARN] Insurance plan {insurance_plan_id} not found")

        # 5. Final Total (rounding up)
        total_price = breakdown['base_fare'] + breakdown['taxes'] + breakdown['addons'] + breakdown['insurance']
        total_price = total_price.quantize(Decimal('1.'), rounding=ROUND_UP)
        breakdown['grand_total'] = total_price
        
        return Response({
            'success': True,
            'total_amount': float(total_price),
            'currency': 'PHP',
            'breakdown': {k: float(v) for k, v in breakdown.items()},
            'tax_details': {k: float(v) for k, v in overall_tax_breakdown.items()}
        })

    except Exception as e:
        print(f"[ERR] Error calculating price: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def price_trend_report(request):
    """
    Debug endpoint to visualize price fluctuations over 60 days.
    """
    flight_number = request.query_params.get('flight_number', 'AP-TREND-101')
    
    # Get schedules for the next 60 days
    schedules = Schedule.objects.filter(
        flight__flight_number=flight_number,
        departure_time__gte=timezone.now()
    ).select_related(
        'flight__airline', 
        'flight__route__origin_airport', 
        'flight__route__destination_airport'
    ).order_by('departure_time')[:60]
    
    if not schedules:
        return Response({
            "error": "No schedules found for this flight. Run 'python manage.py generate_price_trend_data' first.",
            "flight_number": flight_number
        }, status=404)
    
    report_data = []
    
    # Pre-calculate common context
    session_id = "trend_analysis_session"
    user = None # Anonymous
    
    # Bulk fetch occupancy for ALL schedules
    occupancy_data = Seat.objects.filter(schedule__in=schedules).values('schedule_id').annotate(
        available=Count('id', filter=Q(is_available=True)),
        total=Count('id')
    )
    occupancy_map = {item['schedule_id']: (1 - (item['available'] / item['total'])) if item['total'] > 0 else 0.0 
                    for item in occupancy_data}

    # Load config
    from app.models import PricingConfiguration
    config = PricingConfiguration.load()

    for s in schedules:
        f_data = {
            'schedule_id': s.id,
            'flight_number': s.flight.flight_number,
            'departure_time': s.departure_time.isoformat(),
            'origin': s.flight.route.origin_airport.code,
            'destination': s.flight.route.destination_airport.code,
        }
        
        occ_rate = occupancy_map.get(s.id, 0.0)
        
        # Prepare context
        pricing_context = {
            'config': config,
            'user_factor': 1.0,
            'occupancy_factor': None, # Service will calculate from rate
            'base_price': float(s.ml_base_price) if s.ml_base_price else 2500.0,
            'occupancy_rate': occ_rate # Inject rate for factor calculation
        }
        
        pricing_result = dynamic_pricing.get_price_for_user(
            f_data, user, session_id, context=pricing_context
        )
        
        report_data.append({
            'date': s.departure_time.date().isoformat(),
            'day_of_week': s.departure_time.strftime('%A'),
            'final_price': dynamic_pricing.round_price(pricing_result['final_price']),
            'base_price': dynamic_pricing.round_price(pricing_result['base_price']),
            'load_factor': f"{occ_rate:.1%}",
            'is_weekend': s.departure_time.weekday() >= 5,
            'factors': pricing_result['factors_applied']
        })
        
    return Response({
        'flight_number': flight_number,
        'route': f"{schedules[0].flight.route}",
        'data': report_data
    })
