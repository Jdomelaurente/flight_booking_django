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

TARGET_ROUTE_PAIRS = [('CRK', 'ILO'), ('ILO', 'CRK')]
SCHEDULES_PER_DAY  = 10
START_DATE         = date(2026, 4, 1)
END_DATE           = date(2026, 4, 7)   # covers this week + a few days
AIRLINE_CODES      = ['5J', 'PR', 'Z2', '2P']
DURATION_MINUTES   = 90
BASE_PRICE_MIN     = 1500
BASE_PRICE_MAX     = 8000

def random_departure_time():
    return random.randint(5, 22), random.choice([0, 15, 30, 45])

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
        print(f"  [ok] Route {origin_code} -> {dest_code} exists (id={route.id})")
    return route

def get_or_create_flight(route, airline):
    flight = Flight.objects.filter(route=route, airline=airline).first()
    if flight:
        return flight, False
    aircraft = Aircraft.objects.filter(airline=airline).first() or Aircraft.objects.first()
    fn = f"{airline.code}{random.randint(100,999)}"
    while Flight.objects.filter(flight_number=fn).exists():
        fn = f"{airline.code}{random.randint(100,999)}"
    flight = Flight.objects.create(
        flight_number=fn, route=route, airline=airline,
        aircraft=aircraft, total_stops=0
    )
    print(f"    [+] Created flight {fn} for {airline.code}")
    return flight, True

def create_schedule(flight, dep_date, hour, minute):
    dep_dt = timezone.make_aware(datetime.combine(dep_date, time(hour, minute)))
    arr_dt = dep_dt + timedelta(minutes=DURATION_MINUTES)
    price  = Decimal(str(random.randint(BASE_PRICE_MIN, BASE_PRICE_MAX)))
    schedule = Schedule.objects.create(
        flight=flight, departure_time=dep_dt,
        arrival_time=arr_dt, price=price, status='Open'
    )
    airline = flight.airline
    seat_classes = SeatClass.objects.filter(airline=airline)
    if not seat_classes.exists():
        seat_classes = SeatClass.objects.filter(airline__isnull=True)
    for sc in seat_classes:
        num_seats = random.randint(20, 50)
        for i in range(1, num_seats + 1):
            Seat.objects.create(
                schedule=schedule, seat_class=sc,
                seat_number=f"{sc.name[:1].upper()}{i:02d}", is_available=True
            )
    return schedule

def main():
    airlines = list(Airline.objects.filter(code__in=AIRLINE_CODES))
    if not airlines:
        airlines = list(Airline.objects.all()[:4])
    if not airlines:
        print("[ERROR] No airlines found.")
        return
    print(f"Using airlines: {[a.code for a in airlines]}")

    for origin_code, dest_code in TARGET_ROUTE_PAIRS:
        print(f"\n{'='*60}")
        print(f"Processing: {origin_code} -> {dest_code} (Apr 1-7, 2026)")
        route = get_or_create_route(origin_code, dest_code)
        flights = [get_or_create_flight(route, a)[0] for a in airlines]

        current = START_DATE
        total_created = 0
        while current <= END_DATE:
            existing = Schedule.objects.filter(
                flight__route=route,
                departure_time__date=current,
                status='Open'
            ).count()
            to_create = max(0, SCHEDULES_PER_DAY - existing)
            if to_create == 0:
                print(f"  {current}  already has {existing} schedules, skipping.")
                current += timedelta(days=1)
                continue
            for i in range(to_create):
                h, m = random_departure_time()
                create_schedule(flights[i % len(flights)], current, h, m)
                total_created += 1
            print(f"  {current}  +{to_create} schedules  (total: {total_created})")
            current += timedelta(days=1)

        print(f"\n[DONE] {origin_code}->{dest_code}: {total_created} schedules created")

    print("\n[ALL DONE]")

if __name__ == '__main__':
    main()
