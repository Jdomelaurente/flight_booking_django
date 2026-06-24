
import os
import django
import sys
from datetime import datetime, timedelta, time
from django.utils import timezone
import random

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule, Aircraft

def populate_schedules():
    tug = Airport.objects.get(code='TUG')
    zam = Airport.objects.get(code='ZAM')
    flight = Flight.objects.get(flight_number='PR300')
    
    start_date = datetime(2026, 3, 1)
    end_date = datetime(2027, 2, 28)
    
    current_date = start_date
    created_count = 0
    
    print(f"Starting population for {flight.flight_number} (TUG -> ZAM)")
    
    while current_date <= end_date:
        # One flight per day at a random time between 8 AM and 4 PM
        hour = random.randint(8, 16)
        minute = random.choice([0, 15, 30, 45])
        
        dep_dt = timezone.make_aware(datetime.combine(current_date.date(), time(hour, minute)))
        # Flight duration roughly 1.5 - 2.5 hours
        arr_dt = dep_dt + timedelta(minutes=random.randint(90, 150))
        
        # Check if schedule already exists to avoid duplicates
        if not Schedule.objects.filter(flight=flight, departure_time=dep_dt).exists():
            schedule = Schedule.objects.create(
                flight=flight,
                departure_time=dep_dt,
                arrival_time=arr_dt,
                price=0.00, # Will be auto-predicted by my new save() logic
                status='Open'
            )
            created_count += 1
            if created_count % 30 == 0:
                print(f"Created {created_count} schedules...")
                
        current_date += timedelta(days=1)
    
    print(f"Finished. Total schedules created: {created_count}")

if __name__ == "__main__":
    populate_schedules()
