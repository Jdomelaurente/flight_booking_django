
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

def add_flight_schedule(origin_code, dest_code, flight_no):
    print(f"🚀 Adding {origin_code} to {dest_code} daily flights for March 2026...")
    
    try:
        origin = Airport.objects.get(code=origin_code)
        dest = Airport.objects.get(code=dest_code)
    except Airport.DoesNotExist as e:
        print(f"❌ Error: {e}")
        return

    route, _ = Route.objects.get_or_create(
        origin_airport=origin,
        destination_airport=dest,
        defaults={'base_price': Decimal('2200.00')}
    )

    airline = Airline.objects.filter(code='PR').first() or Airline.objects.first()
    aircraft = Aircraft.objects.filter(airline=airline).first() or Aircraft.objects.first()
    
    flight, _ = Flight.objects.get_or_create(
        flight_number=flight_no,
        defaults={
            'airline': airline,
            'aircraft': aircraft,
            'route': route
        }
    )

    start_date = datetime(2026, 3, 1).date()
    end_date = datetime(2026, 3, 31).date()
    
    count = 0
    curr = start_date
    while curr <= end_date:
        dep_time = datetime.combine(curr, datetime.min.time()).replace(hour=10, minute=30, tzinfo=dt_timezone.utc)
        arr_time = dep_time + timedelta(minutes=90)
        
        exists = Schedule.objects.filter(flight=flight, departure_time=dep_time).exists()
        if not exists:
            Schedule.objects.create(
                flight=flight,
                departure_time=dep_time,
                arrival_time=arr_time,
                price=Decimal('2450.00'),
                status='Open'
            )
            count += 1
        curr += timedelta(days=1)

    print(f"✨ Successfully added {count} daily schedules for {origin_code} -> {dest_code} (March)!")

if __name__ == "__main__":
    # The user asked for WNJ. I'll add that.
    add_flight_schedule('MNL', 'WNJ', 'PR2200')
    # I already added WNP (Naga) in the previous step, which is also a common PH route.
