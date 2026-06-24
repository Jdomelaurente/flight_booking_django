
import os
import django
import sys
from datetime import datetime, timedelta, time, date
from django.utils import timezone
from decimal import Decimal

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule

def populate_10_schedules():
    mnl = Airport.objects.filter(code='MNL').first()
    ceb = Airport.objects.filter(code='CEB').first()
    
    if not mnl or not ceb:
        print("Error: MNL or CEB airport not found.")
        return

    route = Route.objects.filter(origin_airport=mnl, destination_airport=ceb).first()
    if not route:
        print("Error: MNL-CEB route not found.")
        return

    # Get all flights on this route to distribute schedules if possible, 
    # but for simplicity we can use the main one or a set of them.
    flights = Flight.objects.filter(route=route)
    if not flights.exists():
        print("Error: No flights found for MNL-CEB route.")
        return
    
    flight = flights.first()
    print(f"Using Route {route} and Flight(s) {[f.flight_number for f in flights]}")

    start_date = date(2026, 3, 11)
    end_date = date(2026, 6, 10)
    
    current_date = start_date
    tz = timezone.get_current_timezone()

    # Fixed times for 10 flights per day
    flight_times = [
        time(6, 0),  time(8, 0),  time(10, 0), 
        time(12, 0), time(14, 0), time(16, 0), 
        time(18, 0), time(20, 0), time(22, 0),
        time(23, 30)
    ]

    total_created = 0
    total_skipped = 0

    while current_date <= end_date:
        for f_time in flight_times:
            departure_dt = datetime.combine(current_date, f_time)
            departure_dt = timezone.make_aware(departure_dt, tz)
            
            # Arrival approx 1h 30m later
            arrival_dt = departure_dt + timedelta(hours=1, minutes=30)
            
            # Check if a schedule at EXACTLY this time already exists to avoid duplication
            # or if we already have 10 and this is a re-run.
            exists = Schedule.objects.filter(
                flight__route=route,
                departure_time=departure_dt
            ).exists()
            
            if not exists:
                try:
                    # Alternating between flights if more than one exists on route
                    current_flight = flights[total_created % flights.count()]
                    
                    base_price = route.base_price if route.base_price > 0 else Decimal('2500.00')
                    
                    Schedule.objects.create(
                        flight=current_flight,
                        departure_time=departure_dt,
                        arrival_time=arrival_dt,
                        price=base_price,
                        status='Open'
                    )
                    total_created += 1
                except Exception as e:
                    print(f"Error creating schedule for {current_date} {f_time}: {e}")
            else:
                total_skipped += 1
        
        current_date += timedelta(days=1)

    print(f"\nFinal Report:")
    print(f"Total Schedules Created: {total_created}")
    print(f"Total Schedules Skipped/Existing: {total_skipped}")

if __name__ == "__main__":
    populate_10_schedules()
