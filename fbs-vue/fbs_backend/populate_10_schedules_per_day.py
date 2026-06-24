import os
import django
import random
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule, Route, Airline, Aircraft

def populate_schedules():
    routes = list(Route.objects.all())
    airlines = list(Airline.objects.all())
    aircrafts = list(Aircraft.objects.all())

    if not routes:
        print("Error: No routes found in the database.")
        return
    
    if not airlines or not aircrafts:
        print("Error: No airlines or aircrafts found to assign to new flights.")
        return

    print(f"Checking {len(routes)} routes...")
    
    today = timezone.now().date()
    total_created = 0
    
    for route in routes:
        print(f"Processing route: {route.origin_airport.code} -> {route.destination_airport.code}")
        
        # Ensure at least one flight exists for this route
        flight = Flight.objects.filter(route=route).first()
        if not flight:
            airline = random.choice(airlines)
            aircraft = random.choice(aircrafts)
            flight_number = f"{airline.code}{random.randint(100, 9999)}"
            flight = Flight.objects.create(
                flight_number=flight_number,
                airline=airline,
                aircraft=aircraft,
                route=route
            )
            print(f"  Created new flight: {flight.flight_number}")

        for day_offset in range(61): # Today + 60 days
            target_date = today + timedelta(days=day_offset)
            
            # Count existing 'Open' schedules for this route on this specific day
            existing_count = Schedule.objects.filter(
                flight__route=route,
                departure_time__date=target_date,
                status='Open'
            ).count()
            
            if existing_count < 10:
                needed = 10 - existing_count
                print(f"  Day {target_date}: Found {existing_count}, creating {needed} more...")
                
                for _ in range(needed):
                    # Randomize time (spread across the day)
                    hour = random.randint(0, 23)
                    minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
                    
                    departure_time = timezone.make_aware(
                        datetime.combine(target_date, datetime.min.time()) + 
                        timedelta(hours=hour, minutes=minute)
                    )
                    
                    # Prevent creating schedules in the past if today
                    if departure_time < timezone.now():
                        departure_time = timezone.now() + timedelta(minutes=random.randint(60, 300))

                    # Duration: 1-5 hours for domestic, longer for international
                    if route.is_international:
                        duration_hours = random.randint(4, 14)
                    else:
                        duration_hours = random.randint(1, 3)
                        
                    duration_minutes = random.randint(0, 59)
                    arrival_time = departure_time + timedelta(hours=duration_hours, minutes=duration_minutes)
                    
                    # Price variation: base price +/- 15%
                    base_price = route.base_price or Decimal('5000.00')
                    variance = float(base_price) * random.uniform(-0.15, 0.15)
                    price = float(base_price) + variance
                    
                    try:
                        Schedule.objects.create(
                            flight=flight,
                            departure_time=departure_time,
                            arrival_time=arrival_time,
                            price=max(500, price), # Minimum 500
                            status='Open'
                        )
                        total_created += 1
                    except Exception as e:
                        # Skip conflicts (runway conflicts etc defined in clean())
                        continue
                
    print(f"\nFinished! Created a total of {total_created} new schedules.")

if __name__ == "__main__":
    populate_schedules()
