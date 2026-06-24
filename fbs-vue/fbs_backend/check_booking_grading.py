import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Booking, BookingDetail

# Find a booking that actually has details
bookings = Booking.objects.annotate(detail_count=django.db.models.Count('details')).filter(detail_count__gt=0).order_by('-created_at')

if not bookings.exists():
    print("No bookings with details found.")
else:
    booking = bookings.first()
    print(f"Booking ID: {booking.id}")
    print(f"Trip Type: {booking.trip_type}")
    print(f"Total Details: {booking.details.count()}")
    print("Details:")
    for d in booking.details.all():
        print(f"  - Segment: {getattr(d.schedule.flight, 'flight_number', 'N/A')}")
        print(f"    - Schedule Origin: '{d.schedule.origin}'")
        print(f"    - Schedule Destination: '{d.schedule.destination}'")
        print(f"    - Origin Airport Code: '{d.schedule.flight.route.origin_airport.code}'")
        print(f"    - Destination Airport Code: '{d.schedule.flight.route.destination_airport.code}'")
        print(f"    - Departure Time: {d.schedule.departure_time}")
        print(f"    - Date (Split): {str(d.schedule.departure_time).split(' ')[0]}")
