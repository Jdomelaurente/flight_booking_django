import os
import sys
import django
import random
from datetime import date, time, timedelta, datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.utils import timezone
from app.models import Airport, Airline, Route, Flight, Schedule, SeatClass, Seat, Aircraft

TARGETS = [
    ('MNL', 'ICN', date(2026, 4, 15)),
    ('ICN', 'DVO', date(2026, 4, 20)),
]

AIRLINE_CODES = ['PR', '5J', 'Z2', 'QR']
DURATION_MINUTES = 240
BASE_PRICE_MIN = 8000
BASE_PRICE_MAX = 25000
SCHEDULES_PER_DAY = 10

def random_departure_time():
    hour   = random.randint(0, 23)
    minute = random.choice([0, 15, 30, 45])
    return hour, minute

def get_or_create_route(origin_code, dest_code):
    try:
        origin = Airport.objects.get(code=origin_code)
        dest   = Airport.objects.get(code=dest_code)
    except Airport.DoesNotExist:
        print(f"Airport {origin_code} or {dest_code} does not exist.")
        return None

    route, created = Route.objects.get_or_create(
        origin_airport=origin,
        destination_airport=dest,
        defaults={
            'base_price': Decimal('12000.00'),
        }
    )
    return route

def get_or_create_flight(route, airline):
    flight = Flight.objects.filter(route=route, airline=airline).first()
    if flight:
        return flight, False
    aircraft = Aircraft.objects.filter(airline=airline).first() or Aircraft.objects.first()
    flight_number = f"{airline.code}{random.randint(100, 999)}"
    while Flight.objects.filter(flight_number=flight_number).exists():
        flight_number = f"{airline.code}{random.randint(100, 999)}"
    flight = Flight.objects.create(
        flight_number=flight_number,
        route=route,
        airline=airline,
        aircraft=aircraft,
        total_stops=0,
    )
    return flight, True

def create_schedule(flight, dep_date, hour, minute):
    dep_dt = timezone.make_aware(
        datetime.combine(dep_date, time(hour, minute))
    )
    arr_dt = dep_dt + timedelta(minutes=DURATION_MINUTES)
    price = Decimal(str(random.randint(BASE_PRICE_MIN, BASE_PRICE_MAX)))
    schedule = Schedule.objects.create(
        flight=flight,
        departure_time=dep_dt,
        arrival_time=arr_dt,
        price=price,
        status='Open',
    )
    airline = flight.airline
    seat_classes = SeatClass.objects.filter(airline=airline)
    if not seat_classes.exists():
        seat_classes = SeatClass.objects.filter(airline__isnull=True)
    for sc in seat_classes:
        num_seats = random.randint(20, 50)
        for i in range(1, num_seats + 1):
            Seat.objects.create(
                schedule=schedule,
                seat_class=sc,
                seat_number=f"{sc.name[:1].upper()}{i:02d}",
                is_available=True,
            )
    return schedule

def main():
    airlines = list(Airline.objects.filter(code__in=AIRLINE_CODES))
    if not airlines:
        print("❌ No matching airlines found.")
        return

    total_created = 0
    for origin_code, dest_code, target_date in TARGETS:
        route = get_or_create_route(origin_code, dest_code)
        if not route:
            continue
        flights = []
        for airline in airlines:
            flight, _ = get_or_create_flight(route, airline)
            flights.append(flight)
        
        existing = Schedule.objects.filter(
            flight__route=route,
            departure_time__date=target_date,
            status='Open',
        ).count()
        
        to_create = max(0, SCHEDULES_PER_DAY - existing)
        for i in range(to_create):
            flight = flights[i % len(flights)]
            hour, minute = random_departure_time()
            create_schedule(flight, target_date, hour, minute)
            total_created += 1
            
        print(f"Created {to_create} schedules for {origin_code} -> {dest_code} on {target_date}")
        
if __name__ == '__main__':
    main()
