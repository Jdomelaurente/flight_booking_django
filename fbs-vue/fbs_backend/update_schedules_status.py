import os
import django
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule

def update_status():
    print("🛫 Updating 10 schedules to 'On Flight' status...")
    schedules = list(Schedule.objects.all())
    
    if len(schedules) < 10:
        print(f"⚠️ Only {len(schedules)} schedules found. Need at least 10.")
        return

    # Shuffle or just pick the first 10
    to_update = random.sample(schedules, 10)
    
    for s in to_update:
        s.status = 'On Flight'
        s.save()
        print(f"  ✅ Flight {s.flight.flight_number} ({s.flight.route}) is now ON FLIGHT")

    print(f"\n🌟 Successfully updated {len(to_update)} schedules to 'On Flight'.")

if __name__ == "__main__":
    update_status()
