import os
import django
from django.utils import timezone
from datetime import datetime, time, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule

def add_schedules():
    try:
        f = Flight.objects.get(flight_number='PR999')
        print(f"Found flight: {f.flight_number} ({f.route.origin_airport.code} -> {f.route.destination_airport.code})")
        
        count = 0
        for day in range(1, 32):
            # 9 PM local time (21:00)
            dep_dt = timezone.make_aware(datetime(2026, 3, day, 21, 0, 0))
            # 18-hour flight
            arr_dt = dep_dt + timedelta(hours=18)
            
            # Check if already exists
            if not Schedule.objects.filter(flight=f, departure_time=dep_dt).exists():
                Schedule.objects.create(
                    flight=f, 
                    departure_time=dep_dt, 
                    arrival_time=arr_dt, 
                    status='Open', 
                    price=f.route.base_price
                )
                count += 1
        
        print(f"? Created {count} new schedules for PR999 in March 2026.")
    except Flight.DoesNotExist:
        print("? Error: Flight PR999 not found.")
    except Exception as e:
        print(f"? Error: {e}")

if __name__ == "__main__":
    add_schedules()
