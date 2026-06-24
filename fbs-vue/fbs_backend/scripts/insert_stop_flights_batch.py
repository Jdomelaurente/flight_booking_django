import os
import django
import sys
from datetime import datetime, timedelta, time
import random
import string

# Set up Django environment
sys.path.append('c:/Users/user/OneDrive/Desktop/Folders/Fbs/fbs-vue/fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.utils import timezone
from app.models import Airport, Route, Flight, Schedule, Aircraft, Airline

def make_aware(dt):
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt

def insert_batch_stops():
    # 1. Get Airports
    try:
        mnl = Airport.objects.get(code='MNL')
        ceb = Airport.objects.get(code='CEB')
    except Airport.DoesNotExist:
        print("MNL or CEB not found!")
        return

    # 2. Get Route
    route, _ = Route.objects.get_or_create(origin_airport=mnl, destination_airport=ceb, defaults={'base_price': 3500})

    airline = Airline.objects.first()
    aircraft = Aircraft.objects.first()

    # 3. Define stop templates
    one_stop_layovers = [
        {"airport": "ILO", "city": "Iloilo", "duration": "45m"},
        {"airport": "BCD", "city": "Bacolod", "duration": "50m"},
        {"airport": "DVO", "city": "Davao", "duration": "1h 00m"}
    ]
    
    two_stop_layovers = [
        [{"airport": "PPS", "city": "Puerto Princesa", "duration": "55m"}, {"airport": "GES", "city": "General Santos", "duration": "1h 10m"}],
        [{"airport": "TAG", "city": "Tagbilaran", "duration": "45m"}, {"airport": "TAC", "city": "Tacloban", "duration": "1h 05m"}]
    ]

    # 4. Generate flights for each day
    start_date = timezone.now().date()
    end_date = datetime(2026, 4, 30).date()
    
    current_date = start_date
    total_created = 0
    
    while current_date <= end_date:
        print(f"Processing stops for {current_date}...")
        
        # 3 per day for 1-stop
        for i in range(3):
            layover = random.choice(one_stop_layovers)
            flight_num = f"PR-1S-{current_date.strftime('%d%m')}-{i}"
            
            # Create flight if not exists
            flight, _ = Flight.objects.get_or_create(
                flight_number=flight_num,
                defaults={
                    'airline': airline,
                    'route': route,
                    'aircraft': aircraft,
                    'total_stops': 1,
                    'layovers_data': [layover]
                }
            )
            
            # Create schedule
            dep_time = make_aware(datetime.combine(current_date, time(7 + i*4, 15)))
            Schedule.objects.create(
                flight=flight,
                departure_time=dep_time,
                arrival_time=dep_time + timedelta(hours=3, minutes=30),
                price=float(route.base_price) + random.randint(1000, 3000),
                status='Open'
            )
            total_created += 1

        # 3 per day for 2-stop
        for i in range(3):
            layovers = random.choice(two_stop_layovers)
            flight_num = f"PR-2S-{current_date.strftime('%d%m')}-{i}"
            
            # Create flight
            flight, _ = Flight.objects.get_or_create(
                flight_number=flight_num,
                defaults={
                    'airline': airline,
                    'route': route,
                    'aircraft': aircraft,
                    'total_stops': 2,
                    'layovers_data': layovers
                }
            )
            
            # Create schedule
            dep_time = make_aware(datetime.combine(current_date, time(8 + i*4, 45)))
            Schedule.objects.create(
                flight=flight,
                departure_time=dep_time,
                arrival_time=dep_time + timedelta(hours=5, minutes=30),
                price=float(route.base_price) + random.randint(3000, 6000),
                status='Open'
            )
            total_created += 1

        current_date += timedelta(days=1)
    
    print(f"Finished! Total schedules with stops created: {total_created}")

if __name__ == "__main__":
    insert_batch_stops()
