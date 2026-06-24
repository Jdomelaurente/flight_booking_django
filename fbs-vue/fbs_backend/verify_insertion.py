
import os
import django
import sys
from datetime import datetime
from django.utils import timezone

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule

def verify():
    mnl = Airport.objects.filter(code='MNL').first()
    ceb = Airport.objects.filter(code='CEB').first()
    
    start_date = datetime(2026, 3, 11, tzinfo=timezone.get_current_timezone())
    end_date = datetime(2026, 6, 10, 23, 59, 59, tzinfo=timezone.get_current_timezone())
    
    schedules = Schedule.objects.filter(
        flight__route__origin_airport=mnl,
        flight__route__destination_airport=ceb,
        departure_time__range=(start_date, end_date)
    ).order_by('departure_time')
    
    count = schedules.count()
    print(f"Total schedules found for MNL-CEB (Mar 11 - Jun 10): {count}")
    
    if count > 0:
        first = schedules.first()
        last = schedules.last()
        print(f"First schedule: {first.departure_time}")
        print(f"Last schedule: {last.departure_time}")
        
        # Check if they are daily
        dates = [s.departure_time.date() for s in schedules]
        unique_dates = len(set(dates))
        print(f"Unique days covered: {unique_dates}")

if __name__ == "__main__":
    verify()
