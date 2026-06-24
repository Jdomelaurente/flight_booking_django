import os
import django
import sys
from datetime import datetime, timedelta, time
import random

# Set up Django environment
sys.path.append('c:/Users/user/OneDrive/Desktop/Folders/Fbs/fbs-vue/fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.utils import timezone
from app.models import Airport, Route, Flight, Schedule, Aircraft, Airline

def make_aware(dt):
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt

def insert_multi_stop():
    # 1. Get Airports
    try:
        mnl = Airport.objects.get(code='MNL')
        ceb = Airport.objects.get(code='CEB')
    except Airport.DoesNotExist:
        print("MNL or CEB not found!")
        return

    # 2. Get Route
    route = Route.objects.filter(origin_airport=mnl, destination_airport=ceb).first()
    if not route:
        route = Route.objects.create(origin_airport=mnl, destination_airport=ceb, base_price=3500)

    # 3. Create a specialized multi-stop flight
    # We'll call it PR-MULTI
    airline = Airline.objects.first()
    aircraft = Aircraft.objects.first()

    flight_num = f"PR-STOP-{random.randint(100, 999)}"
    
    layovers = [
        {"airport": "ILO", "city": "Iloilo", "duration": "45m"},
        {"airport": "PPS", "city": "Puerto Princesa", "duration": "1h 15m"},
        {"airport": "GES", "city": "General Santos", "duration": "50m"}
    ]

    flight = Flight.objects.create(
        flight_number=flight_num,
        airline=airline,
        route=route,
        aircraft=aircraft,
        total_stops=3,
        layovers_data=layovers
    )
    print(f"Created multi-stop flight {flight.flight_number}")

    # 4. Create a schedule for today
    base_time = make_aware(datetime.combine(timezone.now().date(), time(10, 0)))
    
    schedule = Schedule.objects.create(
        flight=flight,
        departure_time=base_time,
        arrival_time=base_time + timedelta(hours=6), # Long journey due to stops
        price=5500,
        status='Open'
    )
    
    try:
        schedule.generate_seats()
    except:
        pass

    print(f"Created multi-stop schedule for {flight.flight_number} at 10:00 AM today.")

if __name__ == "__main__":
    insert_multi_stop()
