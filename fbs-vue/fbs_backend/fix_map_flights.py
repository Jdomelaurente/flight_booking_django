import os
import django
from django.utils import timezone
from datetime import timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule

def fix_arrival_times():
    now = timezone.now()
    print(f"🕒 Current Time: {now}")
    
    # 1. Get all On Flight flights
    on_flight = Schedule.objects.filter(status='On Flight')
    print(f"🛫 Fixing {on_flight.count()} 'On Flight' schedules...")
    
    for s in on_flight:
        # Set departure to 1 hour ago and arrival to 2 hours from now
        s.departure_time = now - timedelta(hours=1)
        s.arrival_time = now + timedelta(hours=2)
        s.save()
        print(f"  ✅ Fixed {s.flight.flight_number}: Arriving at {s.arrival_time}")

    # 2. Also ensure we have exactly 10 for better variety
    if on_flight.count() < 10:
        others = Schedule.objects.exclude(status='On Flight')[:(10 - on_flight.count())]
        for s in others:
            s.status = 'On Flight'
            s.departure_time = now - timedelta(hours=1)
            s.arrival_time = now + timedelta(hours=2)
            s.save()
            print(f"  ✅ Added {s.flight.flight_number} to Active Flights")

    print("\n🌟 All active flights now have future arrival times and will show on the map!")

if __name__ == "__main__":
    fix_arrival_times()
