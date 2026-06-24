import os
import django
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule

def check_flights():
    now = timezone.now()
    print(f"🕒 Current Time: {now}")
    
    on_flight = Schedule.objects.filter(status='On Flight')
    print(f"📊 Total 'On Flight' in DB: {on_flight.count()}")
    
    for s in on_flight:
        past_arrival = s.arrival_time < now
        print(f"  ✈️ {s.flight.flight_number} | Arr: {s.arrival_time} | Past? {'❌ YES' if past_arrival else '✅ NO'}")
        
    active_map = Schedule.objects.filter(status__in=['On Flight', 'Closed'], arrival_time__gt=now)
    print(f"🗺️  Eligible for Map (On Flight/Closed & Arrival > Now): {active_map.count()}")

if __name__ == "__main__":
    check_flights()
