
import os
import django
import random
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule, Airline, Aircraft

def add_naga_march_schedule():
    print("🚀 Adding MNL to Naga (WNP) daily flights for March 2026...")
    
    # 1. Get Airports
    try:
        origin = Airport.objects.get(code='MNL')
        dest = Airport.objects.filter(city__icontains='Naga').first()
        if not dest:
            print("⚠️ Naga airport not found by city, trying code WNP...")
            dest = Airport.objects.get(code='WNP')
    except Airport.DoesNotExist:
        print("❌ Error: Required airports (MNL or WNP) not found. Please run the seeding script first.")
        return

    # 2. Get/Create Route
    route, created = Route.objects.get_or_create(
        origin_airport=origin,
        destination_airport=dest,
        defaults={'base_price': Decimal('2500.00')}
    )
    if created:
        print(f"✅ Created new route: {origin.code} -> {dest.code}")

    # 3. Get/Create Flight
    # Use Philippine Airlines (PR) as a default if available, else a random one
    airline = Airline.objects.filter(code='PR').first() or Airline.objects.first()
    aircraft = Aircraft.objects.filter(airline=airline).first() or Aircraft.objects.first()
    
    flight, created = Flight.objects.get_or_create(
        flight_number=f"{airline.code}411",
        defaults={
            'airline': airline,
            'aircraft': aircraft,
            'route': route
        }
    )
    if created:
        print(f"✅ Created new flight: {flight.flight_number}")

    # 4. Create Schedules for March 1-31
    start_date = datetime(2026, 3, 1).date()
    end_date = datetime(2026, 3, 31).date()
    
    count = 0
    curr = start_date
    while curr <= end_date:
        # Check if already exists for this day/flight combo to avoid duplicates
        # We'll just create a new one at 08:00 AM each day
        dep_time = datetime.combine(curr, datetime.min.time()).replace(hour=8, minute=0, tzinfo=dt_timezone.utc)
        arr_time = dep_time + timedelta(minutes=75) # 1h 15m flight
        
        # Check if identical schedule exists
        exists = Schedule.objects.filter(flight=flight, departure_time=dep_time).exists()
        if not exists:
            Schedule.objects.create(
                flight=flight,
                departure_time=dep_time,
                arrival_time=arr_time,
                price=Decimal('2800.00'),
                status='Open'
            )
            count += 1
        
        curr += timedelta(days=1)

    print(f"✨ Successfully added {count} daily schedules for MNL -> {dest.code} in March!")
    print(f"Total schedules now in DB: {Schedule.objects.count()}")

if __name__ == "__main__":
    add_naga_march_schedule()
