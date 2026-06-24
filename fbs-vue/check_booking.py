import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Booking, BookingDetail
try:
    booking = Booking.objects.get(pnr='5TP6F7')
    print(f"PNR: {booking.pnr}")
    print(f"Booking Date: {booking.booking_date}")
    for detail in booking.details.all():
        print(f"  Passenger: {detail.passenger.first_name} {detail.passenger.last_name}")
        print(f"  Schedule ID: {detail.schedule.id}")
        print(f"  Departure: {detail.schedule.departure_time}")
except Exception as e:
    print(f"Error: {e}")
