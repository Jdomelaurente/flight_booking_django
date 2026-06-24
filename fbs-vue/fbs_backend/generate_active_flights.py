import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airline, Aircraft, Airport, Route, Flight, Schedule

def generate_flights(count=20):
    now = timezone.now()
    airports = list(Airport.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True))
    airlines = list(Airline.objects.all())
    
    if len(airports) < 2 or not airlines:
        print("Error: Missing base data (Airports or Airlines)")
        return

    print(f"Starting generation of {count} active flights...")
    
    # We'll use existing aircrafts if available
    aircrafts = list(Aircraft.objects.all())
    if not aircrafts:
        print("Error: No Aircraft found")
        return

    # Delete existing active schedules to avoid conflicts and start fresh
    Schedule.objects.filter(status__in=['On Flight', 'Closed']).delete()
    print("Cleaned up old active schedules.")

    created = 0
    attempts = 0
    
    while created < count and attempts < 200:
        attempts += 1
        
        # Pick random origin and destination
        origin, dest = random.sample(airports, 2)
        
        airline = random.choice(airlines)
        
        # Find an aircraft for this airline
        airline_aircrafts = [a for a in aircrafts if a.airline_id == airline.id]
        if not airline_aircrafts:
            continue
        aircraft = random.choice(airline_aircrafts)

        # Get or create route
        route, _ = Route.objects.get_or_create(
            origin_airport=origin,
            destination_airport=dest,
            defaults={'base_price': random.randint(1500, 8000)}
        )

        # Create a unique flight number
        flight_num = f"{airline.code}{random.randint(1000, 9999)}"
        while Flight.objects.filter(flight_number=flight_num).exists():
            flight_num = f"{airline.code}{random.randint(1000, 9999)}"

        flight = Flight.objects.create(
            flight_number=flight_num,
            airline=airline,
            aircraft=aircraft,
            route=route
        )

        # Set times so it's currently "On Flight"
        # Departure was 10-90 minutes ago
        dep_time = now - timedelta(minutes=random.randint(10, 90))
        # Total duration 2-4 hours
        duration = timedelta(minutes=random.randint(120, 240))
        arr_time = dep_time + duration

        try:
            # We bypass full clean() if needed, but let's try to be valid
            # The model's save() overrides status based on current time
            schedule = Schedule(
                flight=flight,
                departure_time=dep_time,
                arrival_time=arr_time,
                price=route.base_price
            )
            schedule.save()
            
            if schedule.status == 'On Flight':
                created += 1
                print(f"[{created}/{count}] Created Active Flight: {flight.flight_number} ({origin.code} -> {dest.code})")
        except Exception as e:
            # Likely a conflict (runway conflict)
            continue

    print(f"\nDone! Successfully created {created} active flights.")

if __name__ == "__main__":
    generate_flights(20)
