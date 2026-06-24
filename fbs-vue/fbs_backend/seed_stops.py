import os
import django
import random
from datetime import timedelta
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
try:
    django.setup()
except Exception:
    pass

from app.models import Flight, Schedule

def seed_stops():
    print("🚀 Seeding 1-stop and 2-stop flights...")
    
    # Get some flights to modify
    flights = list(Flight.objects.all())
    if not flights:
        print("❌ No flights found in database. Please run a population script first.")
        return

    # Select random flights to have 1 stop (10% of total)
    num_1_stop = max(1, len(flights) // 10)
    flights_1_stop = random.sample(flights, num_1_stop)
    
    for f in flights_1_stop:
        f.total_stops = 1
        f.save()
        print(f"✅ Updated {f.flight_number} to 1-stop")

    # Select random flights to have 2 stops (15% of total)
    remaining_flights = [f for f in flights if f.total_stops == 0]
    num_2_stops = max(2, len(remaining_flights) // 7)
    flights_2_stops = random.sample(remaining_flights, num_2_stops)
    
    for f in flights_2_stops:
        f.total_stops = 2
        f.save()
        print(f"✅ Updated {f.flight_number} to 2-stops")

    # Update arrival times and prices for schedules of these flights
    schedules = Schedule.objects.filter(flight__in=flights_1_stop)
    for s in schedules:
        # Add 2 hours for layover
        s.arrival_time = s.arrival_time + timedelta(hours=2)
        s.price = s.price * Decimal('1.25') # Slightly more expensive
        s.save()
    
    schedules_2 = Schedule.objects.filter(flight__in=flights_2_stops)
    for s in schedules_2:
        # Add 5 hours for layovers
        s.arrival_time = s.arrival_time + timedelta(hours=5)
        s.price = s.price * Decimal('1.45') # Even more expensive
        s.save()

    print(f"✅ Seeded {len(flights_1_stop)} 1-stop flights and {len(flights_2_stops)} 2-stop flights with realistic durations.")

if __name__ == "__main__":
    seed_stops()
