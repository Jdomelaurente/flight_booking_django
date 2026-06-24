
import os
import django
import sys
from django.db.models.functions import TruncDate
from django.db.models import Count
from datetime import datetime
from django.utils import timezone

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Schedule

def check_per_day():
    mnl = Airport.objects.filter(code='MNL').first()
    ceb = Airport.objects.filter(code='CEB').first()
    
    start_date = datetime(2026, 3, 11, tzinfo=timezone.get_current_timezone())
    end_date = datetime(2026, 6, 10, 23, 59, 59, tzinfo=timezone.get_current_timezone())
    
    per_day = Schedule.objects.filter(
        flight__route__origin_airport=mnl,
        flight__route__destination_airport=ceb,
        departure_time__range=(start_date, end_date)
    ).annotate(date=TruncDate('departure_time')).values('date').annotate(count=Count('id')).order_by('date')
    
    for entry in per_day:
        print(f"{entry['date']}: {entry['count']} flights")

if __name__ == "__main__":
    check_per_day()
