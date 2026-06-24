import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Booking, BookingDetail, PassengerInfo, Schedule, Seat

def seed_flight123():
    pnr = "FLT123"
    last_name = "SIMULATOR"
    
    # 1. Get or create a demo user
    user, _ = User.objects.get_or_create(username='demo_user', defaults={'email': 'demo@example.com'})
    
    # 2. Get or create the passenger
    passenger, created = PassengerInfo.objects.get_or_create(
        last_name=last_name,
        first_name="FLIGHT",
        defaults={'passenger_type': 'Adult'}
    )
    
    # 3. Find a schedule in the check-in window (48h - 1h)
    now = timezone.now()
    window_start = now + timedelta(hours=2)
    window_end = now + timedelta(hours=47)
    
    schedule = Schedule.objects.filter(
        departure_time__gte=window_start,
        departure_time__lte=window_end,
        status='Open'
    ).first()
    
    if not schedule:
        print("No suitable schedule found. Creating one...")
        from app.models import Flight
        flight = Flight.objects.first()
        if not flight:
            print("No flights found in DB. Seed data first.")
            return
            
        schedule = Schedule.objects.create(
            flight=flight,
            departure_time=now + timedelta(hours=24),
            arrival_time=now + timedelta(hours=26),
            price=5000,
            status='Open'
        )

    # 4. Find an available seat
    seat = Seat.objects.filter(schedule=schedule, is_available=True).first()
    if not seat:
        print("No available seats. Generating seats...")
        schedule.generate_seats()
        seat = Seat.objects.filter(schedule=schedule, is_available=True).first()

    # 5. Create or update the booking
    booking, b_created = Booking.objects.get_or_create(
        pnr=pnr,
        defaults={
            'user': user,
            'trip_type': 'one_way',
            'status': 'Confirmed',
            'total_amount': 5000
        }
    )
    
    # Ensure status is Confirmed if it existed
    if not b_created:
        booking.status = 'Confirmed'
        booking.save()

    # 6. Create booking detail
    detail, d_created = BookingDetail.objects.get_or_create(
        booking=booking,
        passenger=passenger,
        schedule=schedule,
        defaults={
            'seat': seat,
            'seat_class': seat.seat_class if seat else None,
            'status': 'confirmed',
            'price': 5000
        }
    )
    
    if not d_created:
        detail.schedule = schedule
        detail.status = 'confirmed'
        detail.save()

    print(f"Successfully seeded booking:")
    print(f"PNR: {pnr}")
    print(f"Last Name: {last_name}")
    print(f"Flight: {schedule.flight.flight_number}")
    print(f"Departure: {schedule.departure_time}")
    print(f"Window: {schedule.automatic_status}")

if __name__ == "__main__":
    seed_flight123()
