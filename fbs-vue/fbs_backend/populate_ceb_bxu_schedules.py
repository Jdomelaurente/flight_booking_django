import os
import django
from decimal import Decimal
from datetime import datetime, timedelta, time
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule, Airline, Aircraft

def populate_schedules():
    print("Starting CEB -> BXU schedule population...")
    
    try:
        ceb = Airport.objects.get(code='CEB')
        bxu = Airport.objects.get(code='BXU')
        
        try:
            airline = Airline.objects.get(code='5J')
        except Airline.DoesNotExist:
            airline = Airline.objects.first()
            
        aircraft = Aircraft.objects.filter(airline=airline).first()
        if not aircraft:
            aircraft = Aircraft.objects.first()
            
        if not ceb or not bxu or not airline or not aircraft:
            print("Error: Missing required base data (Airport, Airline, or Aircraft)")
            return
            
        # Use .model instead of .name for Aircraft
        print(f"Route: {ceb.city} ({ceb.code}) -> {bxu.city} ({bxu.code})")
        print(f"Airline: {airline.name}, Aircraft: {aircraft.model}")
        
    except Exception as e:
        print(f"Error fetching base data: {e}")
        return

    route_ceb_bxu, _ = Route.objects.get_or_create(
        origin_airport=ceb, 
        destination_airport=bxu,
        defaults={'base_price': Decimal('1600.00')}
    )
    
    # Check if a flight with this number already exists
    flight_number = '5J885'
    flight_ceb_bxu = Flight.objects.filter(flight_number=flight_number).first()
    
    if not flight_ceb_bxu:
        flight_ceb_bxu = Flight.objects.create(
            flight_number=flight_number,
            airline=airline,
            aircraft=aircraft,
            route=route_ceb_bxu,
            total_stops=0
        )

    # Date Range: April 15, 2026 to June 30, 2026
    start_date = datetime(2026, 4, 15).date()
    end_date = datetime(2026, 6, 30).date()
    
    # 10 flights per day
    time_slots = [
        time(5, 0), time(7, 30), time(9, 15), time(11, 0),
        time(13, 40), time(15, 20), time(17, 0),
        time(18, 45), time(20, 20), time(22, 0)
    ]

    total_created = 0
    current_date = start_date
    base_p = Decimal('1600.00')

    while current_date <= end_date:
        print(f"Date: {current_date}")
        for t in time_slots:
            slot_time = datetime.combine(current_date, t)
            # Small random variation
            slot_time += timedelta(minutes=random.randint(-10, 10))
            
            tz_aware_depart = slot_time
            tz_aware_arrival = tz_aware_depart + timedelta(minutes=random.randint(45, 60))
            
            # Check if schedule exists for this hour to avoid exact duplicates
            exists = Schedule.objects.filter(
                flight=flight_ceb_bxu,
                departure_time__date=current_date,
                departure_time__hour=tz_aware_depart.hour
            ).exists()
            
            if not exists:
                price = base_p + Decimal(random.randint(-200, 900))
                Schedule.objects.create(
                    flight=flight_ceb_bxu,
                    departure_time=tz_aware_depart,
                    arrival_time=tz_aware_arrival,
                    price=price,
                    ml_base_price=price,
                    status='Open',
                    gate=f"Gate {random.randint(1, 15)}"
                )
                total_created += 1
        
        current_date += timedelta(days=1)

    print(f"Successfully created {total_created} new schedules for CEB -> BXU.")

if __name__ == "__main__":
    populate_schedules()
