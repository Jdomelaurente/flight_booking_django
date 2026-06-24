# simulate_real_world_flights.py
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
try:
    django.setup()
except Exception:
    pass

from app.models import (
    Airline, Airport, Aircraft, SeatClass, Route, Flight, Schedule, Seat
)

def generate_seats(schedule):
    """Generate seats based on aircraft layout or default for the schedule."""
    aircraft = schedule.flight.aircraft
    layout = aircraft.get_layout_config()
    seat_classes_config = layout.get('seat_classes', [])
    
    if not seat_classes_config:
        # Fallback to basic generation if no layout config
        seat_classes = SeatClass.objects.filter(airline=aircraft.airline)
        if not seat_classes.exists():
            seat_classes = SeatClass.objects.filter(airline__isnull=True)
        
        sc = seat_classes.first()
        if not sc: return
        
        # Simple 3x3 or 2x2 depending on capacity
        cols = ['A', 'B', 'C', 'D', 'E', 'F'] if aircraft.capacity > 50 else ['A', 'B', 'C', 'D']
        rows = (aircraft.capacity // len(cols)) + 1
        
        for r in range(1, rows + 1):
            for c in cols:
                Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=f"{r}{c}",
                    defaults={'seat_class': sc, 'row': r, 'column': c, 'is_available': True}
                )
        return
        
    for sc_config in seat_classes_config:
        class_id = sc_config.get('class_id')
        rows = sc_config.get('rows', 0)
        columns = sc_config.get('columns', 0)
        start_row = sc_config.get('start_row', 1)
        
        try:
            seat_class = SeatClass.objects.get(id=class_id)
        except SeatClass.DoesNotExist:
            continue
            
        for r in range(rows):
            row_num = start_row + r
            for c in range(columns):
                col_label = chr(65 + c)
                Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=f"{row_num}{col_label}",
                    defaults={'seat_class': seat_class, 'row': row_num, 'column': col_label, 'is_available': True}
                )

def create_real_world_simulation():
    print("🚀 Starting Real-World Flight Simulation Data Generation...")
    
    # 1. Define Hubs and Spokes
    hubs = Airport.objects.filter(code__in=['MNL', 'CEB'])
    spokes = Airport.objects.exclude(code__in=['MNL', 'CEB'])
    
    if not hubs.exists() or not spokes.exists():
        print("❌ Required airports (MNL, CEB) or spokes not found. Please run seed_philippines.py first.")
        return

    # 2. Get active Airlines
    airlines = Airline.objects.filter(code__in=['PR', '5J', 'Z2'])
    if not airlines.exists():
        airlines = Airline.objects.all()[:3]
        
    # 3. Simulation Parameters
    start_date = timezone.now().date()
    days_to_simulate = 14
    
    # Typical flight times (morning, mid-day, evening, night)
    departure_slots = [
        (6, 0), (8, 30), (10, 15), (13, 0), (15, 45), (18, 20), (21, 0)
    ]

    total_schedules = 0

    for day_offset in range(days_to_simulate):
        current_day = start_date + timedelta(days=day_offset)
        print(f"📅 Simulating for {current_day}...")
        
        for airline in airlines:
            # Each airline serves specific hub-spoke routes daily
            # Pick a subset of spokes for this airline to keep it realistic
            airline_spokes = random.sample(list(spokes), min(len(spokes), 5))
            
            for hub in hubs:
                for spoke in airline_spokes:
                    # Create/Get Routes
                    route_out, _ = Route.objects.get_or_create(
                        origin_airport=hub,
                        destination_airport=spoke,
                        defaults={'base_price': Decimal(random.randint(1800, 3500))}
                    )
                    route_back, _ = Route.objects.get_or_create(
                        origin_airport=spoke,
                        destination_airport=hub,
                        defaults={'base_price': route_out.base_price}
                    )
                    
                    # Create/Get Flights
                    flight_num_out = f"{airline.code}{random.randint(100, 999)}"
                    flight_num_back = f"{airline.code}{random.randint(100, 999)}"
                    
                    # Try to find a suitable aircraft for the airline
                    aircraft = Aircraft.objects.filter(airline=airline).order_by('?').first()
                    if not aircraft:
                        aircraft = Aircraft.objects.all().order_by('?').first()
                    
                    flight_out, _ = Flight.objects.get_or_create(
                        flight_number=flight_num_out,
                        defaults={'airline': airline, 'aircraft': aircraft, 'route': route_out}
                    )
                    flight_back, _ = Flight.objects.get_or_create(
                        flight_number=flight_num_back,
                        defaults={'airline': airline, 'aircraft': aircraft, 'route': route_back}
                    )
                    
                    # Schedule 1-2 round trips per day for this route
                    num_trips = random.randint(1, 2)
                    slots = random.sample(departure_slots, num_trips)
                    
                    for hour, minute in slots:
                        # Departure Outbound
                        dep_time = timezone.make_aware(datetime.combine(current_day, datetime.min.time().replace(hour=hour, minute=minute)))
                        arr_time = dep_time + timedelta(minutes=random.randint(60, 90))
                        
                        # Check if schedule already exists to avoid duplicates
                        if not Schedule.objects.filter(flight=flight_out, departure_time=dep_time).exists():
                            s_out = Schedule.objects.create(
                                flight=flight_out,
                                departure_time=dep_time,
                                arrival_time=arr_time,
                                price=route_out.base_price,
                                status='Open'
                            )
                            generate_seats(s_out)
                            total_schedules += 1
                        
                        # Return Flight (approx 1 hour after arrival)
                        ret_dep_time = arr_time + timedelta(minutes=random.randint(45, 75))
                        ret_arr_time = ret_dep_time + timedelta(minutes=(arr_time - dep_time).seconds // 60)
                        
                        if not Schedule.objects.filter(flight=flight_back, departure_time=ret_dep_time).exists():
                            s_back = Schedule.objects.create(
                                flight=flight_back,
                                departure_time=ret_dep_time,
                                arrival_time=ret_arr_time,
                                price=route_back.base_price,
                                status='Open'
                            )
                            generate_seats(s_back)
                            total_schedules += 1

    print(f"✅ Simulation Complete! Created {total_schedules} new schedules with associated seats.")

if __name__ == "__main__":
    create_real_world_simulation()
