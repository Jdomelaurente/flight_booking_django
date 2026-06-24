"""
Delete all schedules and create exactly 20 new ones (1 per flight).
Each schedule is set to a future date between Feb 25 - March 31, 2026.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule, Seat
from django.utils import timezone
from datetime import datetime, timedelta

# ============================================
# STEP 1: Delete ALL existing seats and schedules
# ============================================
seat_count = Seat.objects.count()
schedule_count = Schedule.objects.count()

print(f"Deleting {seat_count} seats...")
Seat.objects.all().delete()

print(f"Deleting {schedule_count} schedules...")
Schedule.objects.all().delete()

print(f"✅ Cleaned up! Seats: {Seat.objects.count()}, Schedules: {Schedule.objects.count()}")

# ============================================
# STEP 2: Create 20 new schedules (1 per flight)
# ============================================
flights = Flight.objects.all().select_related('route', 'airline')
print(f"\nCreating 20 schedules for {flights.count()} flights...")

# Spread schedules across Feb 25 - March 20, 2026
# Different departure times for variety
departure_configs = [
    # (month, day, hour, minute, flight_hours)
    (2, 25, 6, 0, 1.5),    # Feb 25, 6:00 AM, 1.5h flight
    (2, 25, 14, 30, 2),     # Feb 25, 2:30 PM, 2h flight
    (2, 26, 8, 0, 1),       # Feb 26, 8:00 AM, 1h flight
    (2, 26, 18, 0, 3),      # Feb 26, 6:00 PM, 3h flight
    (2, 27, 7, 0, 1.5),     # Feb 27, 7:00 AM, 1.5h flight
    (2, 27, 16, 0, 2),      # Feb 27, 4:00 PM, 2h flight
    (2, 28, 9, 0, 1),       # Feb 28, 9:00 AM, 1h flight
    (2, 28, 20, 0, 4),      # Feb 28, 8:00 PM, 4h flight
    (3, 1, 6, 30, 1.5),     # Mar 1, 6:30 AM, 1.5h flight
    (3, 1, 15, 0, 2),       # Mar 1, 3:00 PM, 2h flight
    (3, 3, 10, 0, 1),       # Mar 3, 10:00 AM, 1h flight
    (3, 5, 7, 0, 3),        # Mar 5, 7:00 AM, 3h flight
    (3, 7, 12, 0, 2),       # Mar 7, 12:00 PM, 2h flight
    (3, 10, 5, 30, 1.5),    # Mar 10, 5:30 AM, 1.5h flight
    (3, 12, 19, 0, 2),      # Mar 12, 7:00 PM, 2h flight
    (3, 15, 8, 0, 1),       # Mar 15, 8:00 AM, 1h flight
    (3, 18, 14, 0, 3),      # Mar 18, 2:00 PM, 3h flight
    (3, 20, 6, 0, 2),       # Mar 20, 6:00 AM, 2h flight
    (3, 25, 11, 0, 1.5),    # Mar 25, 11:00 AM, 1.5h flight
    (3, 30, 17, 0, 2),      # Mar 30, 5:00 PM, 2h flight
]

created = 0
for i, flight in enumerate(flights):
    config = departure_configs[i]
    month, day, hour, minute, flight_hours = config
    
    dep_dt = timezone.make_aware(datetime(2026, month, day, hour, minute, 0))
    arr_dt = dep_dt + timedelta(hours=flight_hours)
    
    schedule = Schedule.objects.create(
        flight=flight,
        departure_time=dep_dt,
        arrival_time=arr_dt,
        price=flight.route.base_price,
        status='Open'
    )
    created += 1
    print(f"  ✅ {flight.flight_number} | {dep_dt.strftime('%b %d, %Y %I:%M %p')} -> {arr_dt.strftime('%I:%M %p')} | ₱{flight.route.base_price:,.2f}")

print(f"\n🎉 Done! Created {created} schedules.")
print(f"Total schedules now: {Schedule.objects.count()}")
