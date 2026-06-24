import os
import django
from django.utils import timezone
from datetime import timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule

def update_schedules():
    now = timezone.now()
    schedules = list(Schedule.objects.all())[:10]
    
    print(f"Updating {len(schedules)} schedules to 'On Flight' status...")
    
    for s in schedules:
        # Set departure to 1 hour ago and arrival to 1 hour from now
        s.departure_time = now - timedelta(hours=1)
        s.arrival_time = now + timedelta(hours=1)
        # s.save() will automatically call self.status = self.automatic_status
        s.status = 'On Flight'
        s.save()
        print(f"  ✅ {s.flight.flight_number} - Status: {s.status} (Dep: {s.departure_time}, Arr: {s.arrival_time})")

if __name__ == "__main__":
    update_schedules()
