import os
import django
from django.utils import timezone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule
schedules = Schedule.objects.all().order_by('-id')[:5]
print("--- NEW SCHEDULES ---")
for s in schedules:
    print(f"ID: {s.id} | Flight: {s.flight.flight_number} | Dep: {s.departure_time} | Status: {s.status}")
