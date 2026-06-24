
import os
import django
from django.utils import timezone
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule

def check():
    now = timezone.now()
    active_schedules = Schedule.objects.filter(
        status__in=['On Flight', 'Closed'],
        arrival_time__gt=now
    )
    
    print(f"Current Time: {now}")
    print(f"Active Schedules count: {active_schedules.count()}")
    
    for s in active_schedules:
        origin = s.flight.route.origin_airport
        dest = s.flight.route.destination_airport
        print(f"Flight: {s.flight.flight_number}")
        print(f"  Status: {s.status}")
        print(f"  Arrival: {s.arrival_time}")
        print(f"  Origin: {origin.code} (Lat: {origin.latitude}, Lng: {origin.longitude})")
        print(f"  Dest: {dest.code} (Lat: {dest.latitude}, Lng: {dest.longitude})")
        print("-" * 20)

if __name__ == "__main__":
    check()
