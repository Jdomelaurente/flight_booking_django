import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Route, Schedule

def verify():
    routes = Route.objects.all()
    today = timezone.now().date()
    
    print(f"{'Route':<20} | {'Date':<12} | {'Schedules':<10}")
    print("-" * 50)
    
    # Check first 3 routes for first 3 days as sample
    for route in routes[:3]:
        for day in range(3):
            date = today + timedelta(days=day)
            count = Schedule.objects.filter(
                flight__route=route,
                departure_time__date=date,
                status='Open'
            ).count()
            print(f"{str(route):<20} | {str(date):<12} | {count:<10}")

if __name__ == "__main__":
    verify()
