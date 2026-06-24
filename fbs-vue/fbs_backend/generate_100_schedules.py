import os
import django
import random
from django.utils import timezone
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule

def generate_schedules(count=100):
    flights = list(Flight.objects.all())
    if not flights:
        print("Error: No flights found in the database. Please add some flights first.")
        return

    print(f"Found {len(flights)} flights. Generating {count} schedules...")
    
    now = timezone.now()
    start_date = now + timedelta(days=1)
    
    created_count = 0
    
    for i in range(count):
        # Pick a random flight
        flight = random.choice(flights)
        
        # Pick a random day in the next 30 days
        days_ahead = random.randint(0, 30)
        hour = random.randint(0, 23)
        minute = random.choice([0, 15, 30, 45])
        
        departure_time = timezone.make_aware(
            datetime(start_date.year, start_date.month, start_date.day) + 
            timedelta(days=days_ahead, hours=hour, minutes=minute)
        )
        
        # Ensure year/month/day calculation handles month rollover correctly if start_date is at end of month
        # Actually timedelta handles it fine. Let's simplify:
        departure_time = start_date.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
        
        # Flight duration between 1 and 12 hours
        duration_hours = random.randint(1, 12)
        arrival_time = departure_time + timedelta(hours=duration_hours)
        
        # Price: Use route base price with some random variation (+/- 10%)
        base_price = flight.route.base_price
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
        created_count += 1
        
        if created_count % 10 == 0:
            print(f"Created {created_count} schedules...")

    print(f"Successfully generated {created_count} schedules!")

if __name__ == "__main__":
    generate_schedules(100)
