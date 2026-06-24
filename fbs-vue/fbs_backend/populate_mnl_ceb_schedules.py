
import os
import django
import sys
from datetime import datetime, timedelta, time
from django.utils import timezone
from decimal import Decimal

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule

def populate_schedules():
    mnl = Airport.objects.filter(code='MNL').first()
    ceb = Airport.objects.filter(code='CEB').first()
    
    if not mnl or not ceb:
        print("Error: MNL or CEB airport not found.")
        return

    route = Route.objects.filter(origin_airport=mnl, destination_airport=ceb).first()
    if not route:
        print("Error: MNL-CEB route not found.")
        return

    flight = Flight.objects.filter(route=route).first()
    if not flight:
        print("Error: No flight found for MNL-CEB route.")
        return

    print(f"Using Flight: {flight.flight_number} for route {route}")

    start_date = date(2026, 3, 11)
    end_date = date(2026, 6, 10)
    
    current_date = start_date
    created_count = 0
    skipped_count = 0

    tz = timezone.get_current_timezone()

    while current_date <= end_date:
        # Departure at 10:00 AM
        departure_dt = datetime.combine(current_date, time(10, 0))
        departure_dt = timezone.make_aware(departure_dt, tz)
        
        # Arrival at 11:30 AM (approx 1h 30m)
        arrival_dt = departure_dt + timedelta(hours=1, minutes=30)
        
        # Check if schedule already exists for this flight and date
        exists = Schedule.objects.filter(
            flight=flight, 
            departure_time__date=current_date
        ).exists()
        
        if not exists:
            try:
                # Use route base price or a default
                base_price = route.base_price if route.base_price > 0 else Decimal('2500.00')
                
                schedule = Schedule.objects.create(
                    flight=flight,
                    departure_time=departure_dt,
                    arrival_time=arrival_dt,
                    price=base_price,
                    status='Open'
                )
                created_count += 1
                print(f"Created: {current_date} {departure_dt.strftime('%H:%M')}")
            except Exception as e:
                print(f"Error creating schedule for {current_date}: {e}")
        else:
            skipped_count += 1
            # print(f"Skipped: {current_date} (already exists)")
        
        current_date += timedelta(days=1)

    print(f"\nFinal Report:")
    print(f"Schedules Created: {created_count}")
    print(f"Schedules Skipped: {skipped_count}")

if __name__ == "__main__":
    from datetime import date # for local use in loop
    populate_schedules()
