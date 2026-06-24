import os
import sys
import django
import random
from datetime import date, time, timedelta, datetime
from decimal import Decimal

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.utils import timezone
from app.models import (
    Airport, Airline, Route, Flight, Schedule, SeatClass, Seat, Aircraft
)

# -- Config --
TARGET_ROUTE_PAIRS = [
    ('CRK', 'ILO'),
    ('ILO', 'CRK'),
]
SCHEDULES_PER_DAY = 10

# March 2026 date range
START_DATE = date(2026, 3, 1)
END_DATE   = date(2026, 3, 31)

# Airlines that fly domestic PH routes
AIRLINE_CODES = ['5J', 'PR', 'Z2', '2P']

# CRK <-> ILO flight duration ~1.5 hours
DURATION_MINUTES = 90

# Base price range (PHP) domestic
BASE_PRICE_MIN = 1500
BASE_PRICE_MAX = 8000


def random_departure_time():
    hour   = random.randint(5, 22)
    minute = random.choice([0, 15, 30, 45])
    return hour, minute


def ensure_airport(code, name, city, country='Philippines'):
    airport, created = Airport.objects.get_or_create(
        code=code,
        defaults={'name': name, 'city': city, 'country': country}
    )
    if created:
        print(f"  [+] Created airport {code} - {name}")
    else:
        print(f"  [ok] Airport {code} already exists")
    return airport


def get_or_create_route(origin_code, dest_code):
    origin = Airport.objects.get(code=origin_code)
    dest   = Airport.objects.get(code=dest_code)
    route, created = Route.objects.get_or_create(
        origin_airport=origin,
        destination_airport=dest,
        defaults={'base_price': Decimal('3500.00')}
    )
    if created:
        print(f"  [+] Created route {origin_code} -> {dest_code}")
    else:
        print(f"  [ok] Route {origin_code} -> {dest_code} already exists (id={route.id})")
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
    print(f"    [+] Created flight {flight_number} for {airline.code} on {route}")
    return flight, True


def create_schedule(flight, dep_date, hour, minute):
    dep_dt = timezone.make_aware(datetime.combine(dep_date, time(hour, minute)))
    arr_dt = dep_dt + timedelta(minutes=DURATION_MINUTES)
    price  = Decimal(str(random.randint(BASE_PRICE_MIN, BASE_PRICE_MAX)))

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
    print("\n-- Ensuring airports exist --")
    ensure_airport('CRK', 'Clark International Airport', 'Angeles City')
    ensure_airport('ILO', 'Iloilo International Airport', 'Iloilo City')

    airlines = list(Airline.objects.filter(code__in=AIRLINE_CODES))
    if not airlines:
        airlines = list(Airline.objects.all()[:4])
    if not airlines:
        print("[ERROR] No airlines found.")
        return

    print(f"\nUsing airlines: {[a.code for a in airlines]}")

    for origin_code, dest_code in TARGET_ROUTE_PAIRS:
        print(f"\n{'='*60}")
        print(f"Processing route: {origin_code} -> {dest_code}")

        route = get_or_create_route(origin_code, dest_code)

        flights = []
        for airline in airlines:
            flight, _ = get_or_create_flight(route, airline)
            flights.append(flight)

        current = START_DATE
        total_created = 0
        while current <= END_DATE:
            existing = Schedule.objects.filter(
                flight__route=route,
                departure_time__date=current,
                status='Open',
            ).count()

            to_create = max(0, SCHEDULES_PER_DAY - existing)
            if to_create == 0:
                current += timedelta(days=1)
                continue

            for i in range(to_create):
                flight = flights[i % len(flights)]
                hour, minute = random_departure_time()
                create_schedule(flight, current, hour, minute)
                total_created += 1

            print(f"  {current}  +{to_create} schedules  (total so far: {total_created})")
            current += timedelta(days=1)

        print(f"\n[DONE] Total schedules created for {origin_code}->{dest_code}: {total_created}")

    print("\n[ALL DONE]")


if __name__ == '__main__':
    main()
