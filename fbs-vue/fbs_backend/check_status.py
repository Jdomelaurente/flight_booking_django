
import os
import django
import sys
from datetime import datetime, date
from django.utils import timezone

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule

def check_data():
    mnl = Airport.objects.filter(code='MNL').first()
    ceb = Airport.objects.filter(code='CEB').first()
    
    if mnl and ceb:
        route = Route.objects.filter(origin_airport=mnl, destination_airport=ceb).first()
        if route:
            flights = Flight.objects.filter(route=route)
            flight = flights.first()
            print(f"Using Flight: {flight.flight_number}")
            
            start_date = datetime(2026, 3, 11, tzinfo=timezone.get_current_timezone())
            end_date = datetime(2026, 6, 10, 23, 59, 59, tzinfo=timezone.get_current_timezone())
            
            count = Schedule.objects.filter(flight__in=flights, departure_time__range=(start_date, end_date)).count()
            print(f"Existing schedules from {start_date.date()} to {end_date.date()}: {count}")
            
            if count > 0:
                sample = Schedule.objects.filter(flight__in=flights, departure_time__range=(start_date, end_date)).order_by('departure_time').first()
                print(f"Sample schedule: {sample.departure_time}")

if __name__ == "__main__":
    check_data()
