import os
import django
import random
from django.utils import timezone
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule, Route, Airline, Aircraft

def ensure_50_schedules_per_route():
    routes = list(Route.objects.all())
    airlines = list(Airline.objects.all())
    aircrafts = list(Aircraft.objects.all())

    if not routes:
        print("Error: No routes found in the database.")
        return

    print(f"Checking {len(routes)} routes for schedule density...")
    
    now = timezone.now()
    start_date = now + timedelta(days=1)
    
    total_created = 0
    
    for route in routes:
        # Count existing schedules for this route
        existing_count = Schedule.objects.filter(flight__route=route).count()
        print(f"Route {route.origin_airport.code} -> {route.destination_airport.code} (ID: {route.id}) has {existing_count} schedules.")
        
        if existing_count >= 50:
            print(f"  Route already has enough schedules. Skipping.")
            continue
            
        needed = 50 - existing_count
        print(f"  Need to create {needed} more schedules.")
        
        # Ensure there's a flight for this route
        flight = Flight.objects.filter(route=route).first()
        if not flight:
            print(f"  No flight found for this route. Creating a new one...")
            airline = random.choice(airlines)
            aircraft = random.choice(aircrafts)
            flight_number = f"{airline.code}{random.randint(1000, 9999)}"
            flight = Flight.objects.create(
                flight_number=flight_number,
                airline=airline,
                aircraft=aircraft,
                route=route
            )
            print(f"  Created flight {flight.flight_number}.")
            
        # Generate missing schedules
        for i in range(needed):
            # Pick a random day in the next 60 days to spread them out more
            days_ahead = random.randint(0, 60)
            hour = random.randint(0, 23)
            minute = random.choice([0, 15, 30, 45])
            
            departure_time = start_date.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
            
            # Flight duration between 1 and 12 hours
            duration_hours = random.randint(1, 12)
            arrival_time = departure_time + timedelta(hours=duration_hours)
            
            # Use route base price with some random variation (+/- 10%)
            base_price = route.base_price
            variance = float(base_price) * random.uniform(-0.1, 0.1)
            price = float(base_price) + variance
            
            # Create schedule
            Schedule.objects.create(
                flight=flight,
                departure_time=departure_time,
                arrival_time=arrival_time,
                price=price,
                status='Open'
            )
            total_created += 1
            
        print(f"  Added {needed} schedules to Route {route.id}.")

    print(f"Finished! Created a total of {total_created} new schedules.")

if __name__ == "__main__":
    ensure_50_schedules_per_route()
