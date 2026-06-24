import os
import django
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Booking, BookingDetail

def find_valid_pnr():
    now = timezone.now()
    window_start = now + timedelta(hours=1)
    window_end = now + timedelta(hours=48)
    
    print(f"Current local time: {now}")
    print(f"Looking for flights departing between: {window_start} and {window_end}")
    
    # Find active bookings with schedules in the window
    valid_details = BookingDetail.objects.filter(
        schedule__departure_time__gte=window_start,
        schedule__departure_time__lte=window_end,
        status__in=['confirmed', 'checkin', 'pending'] # Assuming pending can also check in or at least see the manifest
    ).select_related('booking', 'passenger', 'schedule')
    
    if not valid_details.exists():
        print("No valid bookings found in the check-in window.")
        # Let's see some nearby bookings to help the user
        all_details = BookingDetail.objects.all().order_by('schedule__departure_time')[:10]
        if all_details.exists():
            print("\nNearby bookings:")
            for d in all_details:
                print(f"PNR: {d.booking.pnr}, Name: {d.passenger.last_name}, Departure: {d.schedule.departure_time}, Status: {d.status}")
        return

    print("\nValid bookings for online check-in today:")
    for detail in valid_details:
        print(f"PNR: {detail.booking.pnr}")
        print(f"Last Name: {detail.passenger.last_name}")
        print(f"Flight: {detail.schedule.flight.flight_number}")
        print(f"Departure: {detail.schedule.departure_time}")
        print("-" * 20)

if __name__ == "__main__":
    find_valid_pnr()
