import os
import django
from datetime import datetime, time
from django.utils import timezone
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule, Seat, SeatClass, Airline, Aircraft

def get_or_create_route(origin_code, dest_code):
    origin = Airport.objects.get(code=origin_code)
    dest = Airport.objects.get(code=dest_code)
    route, created = Route.objects.get_or_create(
        origin_airport=origin,
        destination_airport=dest,
        defaults={'base_price': 5000.00}
    )
    if created:
        print(f"Created Route: {origin_code} -> {dest_code}")
    return route

def create_flight_and_schedule(route, flight_num, date_str):
    airline = Airline.objects.first()
    aircraft = Aircraft.objects.first()
    
    flight, created = Flight.objects.get_or_create(
        flight_number=flight_num,
        defaults={
            'airline': airline,
            'aircraft': aircraft,
            'route': route
        }
    )
    if created:
        print(f"Created Flight: {flight_num}")
        
    # Create Schedule
    departure_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    departure_time = timezone.make_aware(datetime.combine(departure_date, time(10, 0)))
    arrival_time = timezone.make_aware(datetime.combine(departure_date, time(14, 0)))
    
    schedule, s_created = Schedule.objects.get_or_create(
        flight=flight,
        departure_time=departure_time,
        defaults={
            'arrival_time': arrival_time,
            'price': 8000.00,
            'status': 'Open'
        }
    )
    
    if s_created:
        print(f"Created Schedule for {flight_num} on {date_str}")
        # Generate Seats
        generate_seats_for_schedule(schedule)
    else:
        print(f"Schedule already exists for {flight_num} on {date_str}")
    return schedule

def generate_seats_for_schedule(schedule):
    seat_classes = SeatClass.objects.all()
    if not seat_classes.exists():
        print("No SeatClasses found!")
        return

    seats_to_create = []
    # Standardizing to match the user's previous data (Numeric labels)
    for sc in seat_classes:
        start_range = 1
        if "Economy" in sc.name: start_range = 1
        elif "Premium" in sc.name: start_range = 100
        elif "Business" in sc.name: start_range = 200
        elif "First" in sc.name: start_range = 300
        
        for i in range(start_range, start_range + 50):
            seat_num = f"{i:03d}"
            seats_to_create.append(Seat(
                schedule=schedule,
                seat_class=sc,
                seat_number=seat_num,
                is_available=True
            ))
            
    Seat.objects.bulk_create(seats_to_create, ignore_conflicts=True)
    print(f"Generated {len(seats_to_create)} seats for schedule {schedule.id}")

# Run the task
try:
    # 1. CRK -> ICN (April 10)
    r1 = get_or_create_route('CRK', 'ICN')
    create_flight_and_schedule(r1, 'PRO-101', '2026-04-10')
    
    # 2. ICN -> DVO (April 15)
    r2 = get_or_create_route('ICN', 'DVO')
    create_flight_and_schedule(r2, 'PRO-102', '2026-04-15')
    
    # 3. DVO -> SYD (April 17)
    r3 = get_or_create_route('DVO', 'SYD')
    create_flight_and_schedule(r3, 'PRO-103', '2026-04-17')
    
    print("\nSUCCESS: All flight data added for the itinerary segments.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"\nERROR: {str(e)}")
