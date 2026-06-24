import os
import django
from django.utils import timezone
from datetime import date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Schedule, BookingDetail, CheckInDetail, Booking, PassengerInfo, Seat

# ── Target schedule ────────────────────────────────────────────────────────────
SCHEDULE_ID = 11807  # 5J494, 2026-03-01, CEB → DVO
GATE = 'Gate 4'

sched = Schedule.objects.get(id=SCHEDULE_ID)
print(f"✈️  Schedule: {sched.flight.flight_number} | {sched.departure_time} | {sched.flight.route}")

# ── Get any admin user to attach the booking to ───────────────────────────────
admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
print(f"👤 Using user: {admin_user.username}")

# ── Passengers to seed ────────────────────────────────────────────────────────
passengers_data = [
    {'first_name': 'Juan',    'last_name': 'Dela Cruz', 'passenger_type': 'Adult'},
    {'first_name': 'Maria',   'last_name': 'Santos',    'passenger_type': 'Adult'},
    {'first_name': 'Pedro',   'last_name': 'Reyes',     'passenger_type': 'Adult'},
    {'first_name': 'Ana',     'last_name': 'Gonzales',  'passenger_type': 'Adult'},
    {'first_name': 'Michael', 'last_name': 'Torres',    'passenger_type': 'Adult'},
]

# Get available seats for this schedule
seats = list(Seat.objects.filter(schedule=sched, is_available=True)[:5])
print(f"💺 Available seats: {len(seats)}")

created_count = 0

for i, pdata in enumerate(passengers_data):
    # Create passenger
    passenger = PassengerInfo.objects.create(**pdata)
    
    # Create booking
    booking = Booking.objects.create(
        user=admin_user,
        total_amount=Decimal('2899.00'),
        status='confirmed'
    )
    
    # Create booking detail
    seat = seats[i] if i < len(seats) else None
    bd = BookingDetail.objects.create(
        booking=booking,
        passenger=passenger,
        schedule=sched,
        price=sched.price,
        status='confirmed',
        seat=seat
    )
    
    # Mark seat as taken
    if seat:
        seat.is_available = False
        seat.save(update_fields=['is_available'])
    
    # Create check-in
    checkin = CheckInDetail.objects.create(
        booking_detail=bd,
        status='checked-in',
        gate_number=GATE,
        has_declared_safety=True,
    )
    checkin.generate_boarding_pass()
    
    created_count += 1
    print(f"  ✅ {pdata['first_name']} {pdata['last_name']} | Seat {seat.seat_number if seat else 'N/A'} | BP: {checkin.boarding_pass}")

print(f"\n🎉 Created {created_count} passenger check-in(s) for flight {sched.flight.flight_number} on {sched.departure_time.date()}.")
