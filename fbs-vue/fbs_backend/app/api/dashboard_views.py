from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from ..models import (
    Booking, BookingDetail, PassengerInfo, Schedule, Airline, SeatClass, CheckInDetail
)

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
                'active_flights_map',
                'airports_map',
                'flight_operations_stats',
                'aircraft_utilization',
                'revenue_by_route'
            ]
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        try:
            Schedule.update_all_statuses()
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
            revenue_query = Q(status__iexact='Completed') | Q(status__iexact='confirmed') | Q(status__iexact='Paid')
            
            total_revenue = Booking.objects.filter(
                revenue_query
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            last_month_revenue = Booking.objects.filter(
                revenue_query,
                created_at__gte=last_month
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            previous_month_start = last_month - timedelta(days=30)
            previous_month_revenue = Booking.objects.filter(
                revenue_query,
                created_at__gte=previous_month_start,
                created_at__lt=last_month
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            revenue_growth = 0
            if previous_month_revenue and previous_month_revenue > 0:
                revenue_growth = round(((last_month_revenue - previous_month_revenue) / previous_month_revenue) * 100, 1)
            
            total_bookings = Booking.objects.count()
            pending_bookings = Booking.objects.filter(Q(status__iexact='Pending') | Q(status='pending')).count()
            
            now = timezone.now()
            active_flights = Schedule.objects.filter(
                status__iexact='On Flight'
            ).count()
            
            scheduled_flights = Schedule.objects.filter(
                departure_time__date=today
            ).count()

            open_for_booking = Schedule.objects.filter(
                status__iexact='Open'
            ).count()

            total_checkins = CheckInDetail.objects.count()
            
            return Response({
                'passengersToday': passengers_today,
                'passengerGrowth': passenger_growth,
                'totalRevenue': float(total_revenue) if total_revenue else 0.0,
                'revenueGrowth': revenue_growth,
                'totalBookings': total_bookings,
                'pendingBookings': pending_bookings,
                'activeFlights': active_flights,
                'scheduledFlights': scheduled_flights,
                'openForBooking': open_for_booking,
                'totalCheckins': total_checkins
            })
        except Exception as e:
            return Response({'error': str(e)}, status=200)
    
    @action(detail=False, methods=['get'])
    def revenue_breakdown(self, request):
        revenue_query = Q(status__iexact='Completed') | Q(status__iexact='confirmed') | Q(status__iexact='Paid')
        completed_bookings = Booking.objects.filter(revenue_query)
        
        total = completed_bookings.aggregate(sum=Sum('total_amount'))['sum'] or 0
        tickets = completed_bookings.aggregate(sum=Sum('base_fare_total'))['sum'] or 0
        addons = completed_bookings.aggregate(sum=Sum('insurance_total'))['sum'] or 0
        taxes = completed_bookings.aggregate(sum=Sum('tax_total'))['sum'] or 0
        
        return Response({
            'total': float(total),
            'breakdown': {
                'tickets': float(tickets),
                'addons': float(addons),
                'taxes': float(taxes)
            }
        })
    
    @action(detail=False, methods=['get'])
    def ticket_sales(self, request):
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
            labels.append(date.strftime('%a')) if days <= 7 else labels.append(date.strftime('%d %b'))
            
        return Response({'labels': labels, 'data': sales_data})
    
    @action(detail=False, methods=['get'])
    def recent_bookings(self, request):
        limit = int(request.query_params.get('limit', 5))
        bookings = Booking.objects.select_related('user').order_by('-created_at')[:limit]
        
        data = []
        for b in bookings:
            detail = b.details.first()
            flight = detail.schedule.flight if detail and detail.schedule else None
            data.append({
                'id': b.id,
                'passenger': b.user.get_full_name() if b.user else 'Guest',
                'flight': flight.flight_number if flight else 'N/A',
                'date': b.created_at,
                'amount': float(b.total_amount),
                'status': b.status
            })
        return Response(data)

    @action(detail=False, methods=['get'])
    def active_flights_map(self, request):
        Schedule.update_all_statuses()
        now = timezone.now()
        
        # Unify definition: Only show flights that are technically in the air
        active_schedules = Schedule.objects.filter(
            status__iexact='On Flight'
        ).select_related(
            'flight__route__origin_airport',
            'flight__route__destination_airport',
            'flight__airline'
        ).distinct()
        
        data = []
        for s in active_schedules:
            origin = s.flight.route.origin_airport
            dest = s.flight.route.destination_airport
            
            # Enrich layovers with coordinates
            layovers = s.flight.layovers_data or []
            if isinstance(layovers, str):
                import json
                try:
                    layovers = json.loads(layovers)
                except Exception:
                    layovers = []

            enriched_layovers = []
            for stop in layovers:
                if isinstance(stop, str):
                    stop = {'airport': stop}
                elif not isinstance(stop, dict):
                    continue
                from ..models import Airport
                ap = Airport.objects.filter(code=stop.get('airport')).first()
                if ap and ap.latitude and ap.longitude:
                    enriched_layovers.append({
                        **stop,
                        'lat': float(ap.latitude),
                        'lng': float(ap.longitude)
                    })
                else:
                    enriched_layovers.append(stop)

            if origin.latitude and origin.longitude and dest.latitude and dest.longitude:
                data.append({
                    'id': s.id,
                    'flight_number': s.flight.flight_number,
                    'airline': s.flight.airline.name,
                    'origin': {'lat': float(origin.latitude), 'lng': float(origin.longitude), 'city': origin.city, 'code': origin.code},
                    'destination': {'lat': float(dest.latitude), 'lng': float(dest.longitude), 'city': dest.city, 'code': dest.code},
                    'layovers': enriched_layovers,
                    'departure_time': s.departure_time,
                    'arrival_time': s.arrival_time,
                    'status': s.automatic_status
                })
        return Response(data)

    @action(detail=False, methods=['get'])
    def airports_map(self, request):
        """Return all airports that have valid coordinates for map display."""
        from ..models import Airport
        airports = Airport.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).select_related('country').order_by('code')

        data = []
        for ap in airports:
            data.append({
                'code': ap.code,
                'name': ap.name,
                'city': ap.city or '',
                'country': ap.country.name if ap.country else '',
                'lat': float(ap.latitude),
                'lng': float(ap.longitude),
                'type': ap.airport_type,
            })
        return Response(data)


    @action(detail=False, methods=['get'])
    def seat_class_distribution(self, request):
        distribution = BookingDetail.objects.filter(
            Q(booking__status__iexact='confirmed') | Q(booking__status__iexact='Completed') | Q(booking__status__iexact='Paid')
        ).values('seat_class__name', 'seat_class__color').annotate(
            count=Count('id'),
            revenue=Sum('price')
        ).order_by('-count')
        
        total = sum(item['count'] for item in distribution)
        
        classes = []
        for item in distribution:
            percentage = round((item['count'] / total * 100), 1) if total > 0 else 0
            classes.append({
                'label': item['seat_class__name'] or 'Unknown',
                'count': item['count'],
                'revenue': float(item['revenue']) if item['revenue'] else 0.0,
                'color': item['seat_class__color'] or '#CBD5E1', # Default gray if no color
                'percentage': percentage
            })
            
        return Response({
            'total': total,
            'classes': classes
        })
    
    @action(detail=False, methods=['get'])
    def passenger_composition(self, request):
        composition = PassengerInfo.objects.all().values('passenger_type').annotate(
            count=Count('id')
        )
        return Response({
            'labels': [c['passenger_type'] for c in composition],
            'data': [c['count'] for c in composition]
        })

    @action(detail=False, methods=['get'])
    def popular_routes(self, request):
        period = request.query_params.get('period', 'all')
        now = timezone.now()
        
        queryset = BookingDetail.objects.all()
        if period == 'weekly':
            queryset = queryset.filter(booking__created_at__gte=now - timedelta(days=7))
        elif period == 'monthly':
            queryset = queryset.filter(booking__created_at__gte=now - timedelta(days=30))
        elif period == 'yearly':
            queryset = queryset.filter(booking__created_at__gte=now - timedelta(days=365))

        routes = queryset.values(
            'schedule__flight__route__origin_airport__city',
            'schedule__flight__route__destination_airport__city'
        ).annotate(count=Count('id')).order_by('-count')[:5]
        
        data = []
        for r in routes:
            label = f"{r['schedule__flight__route__origin_airport__city']} to {r['schedule__flight__route__destination_airport__city']}"
            data.append({'label': label, 'count': r['count']})
        return Response({
            'labels': [d['label'] for d in data],
            'data': [d['count'] for d in data]
        })

    @action(detail=False, methods=['get'])
    def flight_operations_stats(self, request):
        Schedule.update_all_statuses()
        # Precise operational mapping to ensure radar chart accuracy
        target_statuses = ['On Flight', 'Arrived', 'Open', 'Closed']
        schedules = Schedule.objects.all()
        
        counts = []
        for status_name in target_statuses:
            count = schedules.filter(status__iexact=status_name).count()
            counts.append(count)
            
        return Response({
            'labels': target_statuses,
            'data': counts
        })

    @action(detail=False, methods=['get'])
    def aircraft_utilization(self, request):
        # Implementation depends on fleet logic, but here is a sample
        return Response([])

    @action(detail=False, methods=['get'])
    def revenue_by_route(self, request):
        rev = BookingDetail.objects.all().values(
            'schedule__flight__route__origin_airport__city',
            'schedule__flight__route__destination_airport__city'
        ).annotate(revenue=Sum('price')).order_by('-revenue')[:5]
        
        return Response({
            'labels': [f"{r['schedule__flight__route__origin_airport__city']} to {r['schedule__flight__route__destination_airport__city']}" for r in rev],
            'data': [float(r['revenue']) for r in rev]
        })
    
    @action(detail=False, methods=['get'])
    def network_peak_hours(self, request):
        from django.db.models.functions import ExtractHour
        
        # Get distribution of flights across 24 hours
        distribution = Schedule.objects.annotate(
            hour=ExtractHour('departure_time')
        ).values('hour').annotate(count=Count('id')).order_by('hour')
        
        # Create full 24-hour array (defaulting to 0)
        hourly_data = [0] * 24
        for d in distribution:
            if d['hour'] is not None:
                hourly_data[d['hour']] = d['count']
                
        return Response({
            'labels': [f"{h:02d}:00" for h in range(24)],
            'data': hourly_data
        })
    
    @action(detail=False, methods=['post'])
    def sync_active_flights(self, request):
        """
        Simulation Utility: Adjusts departure/arrival times of all 'On Flight' 
        schedules so they are currently somewhere in the middle of their duration.
        """
        Schedule.update_all_statuses()
        now = timezone.now()
        active_schedules = Schedule.objects.filter(status__iexact='On Flight')
        count = active_schedules.count()
        
        for s in active_schedules:
            duration = s.arrival_time - s.departure_time
            if duration <= timedelta(0):
                duration = timedelta(hours=2)
            
            # Scatter them based on ID
            percent = (20 + (s.id * 17) % 60) / 100.0 
            elapsed = duration.total_seconds() * percent
            
            s.departure_time = now - timedelta(seconds=elapsed)
            s.arrival_time = s.departure_time + duration
            s.save(update_fields=['departure_time', 'arrival_time'])
            
        return Response({'message': f'Synchronized {count} flights.', 'count': count})

    @action(detail=False, methods=['get'])
    def alerts(self, request):
        return Response([])
