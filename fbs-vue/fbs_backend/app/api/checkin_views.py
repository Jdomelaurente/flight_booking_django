import csv
from django.http import HttpResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from ..models import CheckInDetail, BookingDetail, TrackLog
from ..serializers import CheckInDetailSerializer, CheckInListSerializer

class CheckInDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing check-in details.
    """
    queryset = CheckInDetail.objects.select_related(
        'booking_detail',
        'booking_detail__passenger',
        'booking_detail__schedule',
        'booking_detail__schedule__flight',
    ).all()
    
    serializer_class = CheckInDetailSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'booking_detail__passenger__first_name',
        'booking_detail__passenger__last_name',
        'boarding_pass',
        'booking_detail__schedule__flight__flight_number',
    ]
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        counter = self.request.query_params.get('check_in_counter')
        
        if status:
            queryset = queryset.filter(status=status)
        if counter:
            queryset = queryset.filter(check_in_counter=counter)
            
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CheckInListSerializer
        return CheckInDetailSerializer
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        today_checkins = self.get_queryset().filter(check_in_time__date=today)
        serializer = self.get_serializer(today_checkins, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_checkins = self.get_queryset().count()
        today = timezone.now().date()
        todays_checkins = self.get_queryset().filter(check_in_time__date=today).count()
        
        status_stats = self.get_queryset().values('status').annotate(count=Count('id'))
        
        return Response({
            'total_checkins': total_checkins,
            'todays_checkins': todays_checkins,
            'status_stats': {stat['status']: stat['count'] for stat in status_stats},
        })
    
    @action(detail=True, methods=['post'])
    def print_boarding_pass(self, request, pk=None):
        checkin = self.get_object()
        if not checkin.boarding_pass:
            checkin.boarding_pass = f"BP-{checkin.id}-{timezone.now().strftime('%Y%m%d%H%M')}"
            checkin.save()
        
        # Log the action
        TrackLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=f"Printed boarding pass for {checkin.passenger_name} (Flight: {checkin.flight_number})"
        )
        
        return Response({
            'message': 'Boarding pass ready for printing',
            'boarding_pass': checkin.boarding_pass,
            'passenger_name': checkin.passenger_name,
            'flight_number': checkin.flight_number,
        })
    
    @action(detail=False, methods=['post'])
    def bulk_checkin(self, request):
        booking_detail_ids = request.data.get('booking_detail_ids', [])
        check_in_counter = request.data.get('check_in_counter')
        
        created_checkins = []
        for bd_id in booking_detail_ids:
            try:
                booking_detail = BookingDetail.objects.get(id=bd_id)
                checkin = CheckInDetail.objects.create(
                    booking_detail=booking_detail,
                    check_in_counter=check_in_counter,
                    status='checked-in'
                )
                created_checkins.append(checkin.id)
            except Exception:
                continue
                
        # Log the action
        TrackLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=f"Performed bulk check-in for {len(created_checkins)} passengers."
        )
        
        return Response({'success': len(created_checkins), 'created_checkins': created_checkins})
    
    @action(detail=False, methods=['get'])
    def pending_bookings(self, request):
        pending = BookingDetail.objects.filter(
            status='confirmed',
            checkins__isnull=True
        ).select_related('passenger', 'schedule__flight')
        
        data = [{
            'id': b.id,
            'passenger_name': b.passenger.get_full_name() if b.passenger else 'Guest',
            'flight_number': b.schedule.flight.flight_number if b.schedule and b.schedule.flight else 'N/A',
        } for b in pending]
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        checkin = self.get_object()
        new_status = request.data.get('status')
        if new_status:
            checkin.status = new_status
            checkin.save()
            
            # Log the action
            TrackLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action=f"Updated check-in status for {checkin.passenger_name} to {new_status}."
            )
            
            return Response({'status': 'updated'})
        return Response({'error': 'status required'}, status=400)
    
    @action(detail=False, methods=['post'])
    def lookup(self, request):
        pnr = request.data.get('pnr', '').strip()
        last_name = request.data.get('last_name', '').strip()
        
        print(f"DEBUG: Check-in Lookup Attempt - PNR: |{pnr}|, Last Name: |{last_name}|")
        
        if not pnr or not last_name:
            return Response({'error': 'PNR and last name are required'}, status=400)
            
        # 1. First, check if there is at least one passenger in this PNR with the given Last Name
        # This provides the "authorization" to see the booking party.
        if last_name == 'QR_VERIFIED':
            # QR scan bypass - just verify PNR exists
            auth_exists = BookingDetail.objects.filter(booking__pnr=pnr.upper()).exists()
            if not auth_exists:
                return Response({'error': 'No matching booking found for this scanned QR code'}, status=404)
        else:
            auth_exists = BookingDetail.objects.filter(
                booking__pnr=pnr.upper(),
                passenger__last_name__iexact=last_name
            ).exists()
            
            if not auth_exists:
                return Response({'error': 'No matching booking found for this PNR and Last Name'}, status=404)
            
        # 2. If valid, retrieve ALL passengers in this PNR (the whole party)
        bookings = BookingDetail.objects.filter(
            booking__pnr=pnr.upper()
        ).select_related(
            'passenger', 
            'schedule__flight__route__origin_airport', 
            'schedule__flight__route__destination_airport', 
            'seat'
        ).prefetch_related('addons', 'checkins')
        
        if not bookings.exists():
            return Response({'error': 'No records found for this PNR'}, status=404)
            
        # Serialize the booking details for the passenger to choose
        data = []
        now = timezone.now()
        
        for b in bookings:
            departure = b.schedule.departure_time
            time_until_departure = departure - now
            
            # DCS Logic: Window opens 48 hours before, closes 1 hour before
            window_status = 'open'
            if time_until_departure > timedelta(hours=48):
                window_status = 'early'
            elif time_until_departure < timedelta(hours=1):
                window_status = 'late'
            
            data.append({
                'id': b.id,
                'passenger_name': b.passenger.get_full_name(),
                'flight_number': b.schedule.flight.flight_number,
                'origin': b.schedule.flight.route.origin_airport.city,
                'destination': b.schedule.flight.route.destination_airport.city,
                'departure_time': b.schedule.departure_time,
                'status': b.status,
                'passenger_type': b.passenger_type or (b.passenger.passenger_type if b.passenger else 'Adult'),
                'is_checked_in': b.checkins.exists(),
                'checkin_window_status': window_status,
                'time_until_departure_hours': round(time_until_departure.total_seconds() / 3600, 1),
                'seat': b.seat.id if b.seat else None,
                'seat_number': b.seat.seat_number if b.seat else ('SEAT ON LAP' if b.passenger_type == 'Infant' else 'NOT ASSIGNED'),
                'addons': list(b.addons.values_list('id', flat=True)),
                'addon_details': [a.name for a in b.addons.all()],
                'schedule': b.schedule.id
            })
            
        return Response(data)

    @action(detail=False, methods=['post'])
    def self_checkin(self, request):
        """
        Handles bulk check-in for multiple passengers.
        Expected data: {
            "passengers": [
                {"booking_detail_id": ID, "email": "...", "phone": "..."},
                ...
            ],
            "has_declared_safety": true
        }
        """
        passenger_data = request.data.get('passengers', [])
        has_declared_safety = request.data.get('has_declared_safety', False)
        
        if not passenger_data:
            # Backward compatibility for single passenger if necessary
            single_id = request.data.get('booking_detail_id')
            if single_id:
                passenger_data = [{
                    'booking_detail_id': single_id,
                    'email': request.data.get('email', ''),
                    'phone': request.data.get('phone', '')
                }]
            else:
                return Response({'error': 'Passenger data required'}, status=400)
            
        if not has_declared_safety:
            return Response({'error': 'Safety declaration is required'}, status=400)
            
        results = []
        errors = []
        
        from django.db import transaction
        
        try:
            with transaction.atomic():
                for p in passenger_data:
                    bd_id = p.get('booking_detail_id')
                    try:
                        booking_detail = BookingDetail.objects.get(id=bd_id)
                        
                        # Guard: Check-in window enforcement
                        departure = booking_detail.schedule.departure_time
                        now = timezone.now()
                        time_until_departure = departure - now
                        
                        if time_until_departure > timedelta(hours=48):
                            errors.append({'id': bd_id, 'errors': 'Check-in window not yet open (Opens 48h before departure)'})
                            continue
                        elif time_until_departure < timedelta(hours=1):
                            errors.append({'id': bd_id, 'errors': 'Check-in window closed (Closes 1h before departure)'})
                            continue

                        serializer = self.get_serializer(data={
                            'booking_detail_id': bd_id,
                            'has_declared_safety': True,
                            'status': 'checked-in',
                            'student': request.user.id if request.user.is_authenticated else None,
                            'gate_number': booking_detail.schedule.gate or 'Gate 7'
                        })
                        
                        if serializer.is_valid():
                            checkin = serializer.save()
                            
                            # UPDATE: Persist email/phone to the booking contact so dispatch_email can find it
                            email_provided = p.get('email', '')
                            phone_provided = p.get('phone', '')
                            
                            if email_provided or phone_provided:
                                from ..models import BookingContact
                                booking = booking_detail.booking
                                contact, created = BookingContact.objects.get_or_create(booking=booking)
                                
                                # Update fields if provided
                                if email_provided: contact.email = email_provided
                                if phone_provided: contact.phone = phone_provided
                                contact.save()
                                print(f"DEBUG: Updated booking contact for booking {booking.id} during check-in")

                            booking_detail.status = 'checkin'
                            booking_detail.save(update_fields=['status'])
                            results.append(serializer.data)
                        else:
                            errors.append({'id': bd_id, 'errors': serializer.errors})
                    except BookingDetail.DoesNotExist:
                        errors.append({'id': bd_id, 'errors': 'Booking detail not found'})
                
                # AUTOMATIC EMAIL DISPATCH
                if results and not errors:
                    try:
                        from flightapp.services.email_service import EmailService
                        # Get all checked-in booking details for internal processing
                        # The serializer returns 'booking_detail' as a nested object
                        bd_ids = [r['booking_detail']['id'] for r in results if 'booking_detail' in r]
                        bookings = BookingDetail.objects.filter(id__in=bd_ids)
                        
                        if bookings.exists():
                            if bookings.count() > 1:
                                EmailService.send_group_checkin_confirmation(list(bookings))
                            else:
                                EmailService.send_checkin_confirmation(bookings.first())
                            print(f"DEBUG: Auto-dispatched check-in emails for {bookings.count()} passengers")
                    except Exception as email_err:
                        print(f"ERROR: Auto-email dispatch failed: {email_err}")
                        # Don't fail the whole check-in if email fails
            
            if errors and not results:
                return Response({'errors': errors}, status=400)
                
            return Response({
                'results': results,
                'errors': errors if errors else None
            }, status=201 if not errors else 207)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def dispatch_email(self, request):
        """
        Triggers email dispatch for a list of booking details.
        """
        booking_detail_ids = request.data.get('booking_detail_ids', [])
        
        # Support single ID if provided
        if not booking_detail_ids and request.data.get('booking_detail_id'):
            booking_detail_ids = [request.data.get('booking_detail_id')]
            
        if not booking_detail_ids:
            return Response({'error': 'Booking Detail IDs required'}, status=400)
            
        try:
            from flightapp.services.email_service import EmailService
            bookings = BookingDetail.objects.filter(id__in=booking_detail_ids)
            
            if not bookings.exists():
                return Response({'error': 'No valid bookings found for provided IDs'}, status=404)
            
            if bookings.count() > 1:
                success = EmailService.send_group_checkin_confirmation(list(bookings))
            else:
                success = EmailService.send_checkin_confirmation(bookings.first())
                
            if success:
                return Response({'message': 'Dispatch protocol successful', 'count': bookings.count()})
            
            return Response({'error': 'Dispatch protocol failed. Verify email configuration and recipient details.'}, status=500)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"CRITICAL ERROR in dispatch_email: {e}\n{error_trace}")
            from django.conf import settings
            return Response({
                'error': f"Internal Dispatch Failure: {str(e)}",
                'details': error_trace if settings.DEBUG else "Check server logs"
            }, status=500)

    @action(detail=False, methods=['get'])
    def export(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="checkins.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Passenger', 'Flight', 'Status', 'Gate', 'Time'])
        for c in self.get_queryset():
            writer.writerow([c.id, c.passenger_name, c.flight_number, c.status, c.gate_number, c.check_in_time])
        return response
