import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()
from django.utils import timezone
import pytz
manila_tz = pytz.timezone('Asia/Manila')

from app.models import Airline, Airport, Aircraft, SeatClass, Route, Flight, Schedule, Seat, Booking, BookingDetail

print("Cleaning existing non-real world and old flight data...")
# We delete Bookings to avoid protected foreign key errors
BookingDetail.objects.all().delete()
Booking.objects.all().delete()
Schedule.objects.all().delete()
Flight.objects.all().delete()

print("Starting high-frequency real-world flight simulation...")
hubs = Airport.objects.filter(code__in=['MNL', 'CEB'])
top_spoke_codes = ['DVO', 'ILO', 'KLO', 'MPH', 'PPS', 'BCD', 'ZAM', 'CGY', 'TAC', 'BOH']
spokes = list(Airport.objects.filter(code__in=top_spoke_codes))

airlines = Airline.objects.filter(code__in=['PR', '5J', 'Z2'])
if not airlines.exists():
    airlines = list(Airline.objects.all())[:3]

start_date = timezone.now().date()
days_to_simulate = 14

departure_slots = [
    (4, 30), (5, 45), (6, 15), (7, 30), (8, 45), (10, 0), 
    (11, 20), (13, 10), (14, 45), (16, 20), (17, 50), 
    (19, 15), (20, 30), (22, 10), (23, 40)
]

# Hub-to-Hub (MNL <-> CEB)
hub_pairs = [('MNL', 'CEB'), ('CEB', 'MNL')]
# Hub-to-Spoke and Spoke-to-Hub
all_route_pairs = hub_pairs.copy()
for hub in hubs:
    for spoke in spokes:
        all_route_pairs.append((hub.code, spoke.code))
        all_route_pairs.append((spoke.code, hub.code))

daily_flights = []

print("Setting up daily flight templates...")
for origin_code, dest_code in all_route_pairs:
    try:
        origin_air = Airport.objects.get(code=origin_code)
        dest_air = Airport.objects.get(code=dest_code)
        
        route, _ = Route.objects.get_or_create(
            origin_airport=origin_air, destination_airport=dest_air,
            defaults={'base_price': Decimal(random.randint(1800, 3500)), 'is_domestic': True}
        )
        
        # Each airline does 3 to 4 flights per day on this route.
        for airline in airlines:
            aircraft = Aircraft.objects.filter(airline=airline).order_by('?').first() or Aircraft.objects.all().order_by('?').first()
            if not aircraft:
                continue
                
            num_trips = random.randint(3, 4)
            slots = random.sample(departure_slots, num_trips)
            slots.sort()
            
            for hour, minute in slots:
                f_num = f"{airline.code}{random.randint(100, 999)}"
                # Make sure unique flight numbers
                while Flight.objects.filter(flight_number=f_num).exists():
                    f_num = f"{airline.code}{random.randint(100, 999)}"
                f = Flight.objects.create(flight_number=f_num, airline=airline, aircraft=aircraft, route=route)
                daily_flights.append((f, hour, minute))
                
    except Airport.DoesNotExist:
        continue

print(f"Prepared {len(daily_flights)} daily flights. Generating schedules...")

total_schedules = 0
for day_offset in range(days_to_simulate):
    current_day = start_date + timedelta(days=day_offset)
    print(f"Generating for {current_day}...")
    
    for f, hour, minute in daily_flights:
        dep_time = manila_tz.localize(datetime.combine(current_day, datetime.min.time().replace(hour=hour, minute=minute)))
        arr_time = dep_time + timedelta(minutes=random.randint(70, 110))
        Schedule.objects.create(flight=f, departure_time=dep_time, arrival_time=arr_time, price=f.route.base_price, status='Open')
        total_schedules += 1
        
    print(f"  Day complete. Total schedules so far: {total_schedules}")

print(f"DONE! Created {total_schedules} real-world schedules with seats.")
