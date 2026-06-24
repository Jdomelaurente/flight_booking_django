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
    print("Starting BXU -> DVO schedule population...")
    
    try:
        bxu = Airport.objects.get(code='BXU')
        dvo = Airport.objects.get(code='DVO')
        
        try:
            airline = Airline.objects.get(code='5J')
        except Airline.DoesNotExist:
            airline = Airline.objects.first()
            
        aircraft = Aircraft.objects.filter(airline=airline).first()
        if not aircraft:
            aircraft = Aircraft.objects.first()
            
        if not bxu or not dvo or not airline or not aircraft:
            print("Error: Missing required base data (Airport, Airline, or Aircraft)")
            return
            
        print(f"Route: {bxu.city} ({bxu.code}) -> {dvo.city} ({dvo.code})")
        print(f"Airline: {airline.name}, Aircraft: {aircraft.model}")
        
    except Exception as e:
        print(f"Error fetching base data: {e}")
        return

    route_bxu_dvo, _ = Route.objects.get_or_create(
        origin_airport=bxu, 
        destination_airport=dvo,
        defaults={'base_price': Decimal('1400.00')}
    )
    
    flight_number = '5J991'
    flight_bxu_dvo = Flight.objects.filter(flight_number=flight_number).first()
    
    if not flight_bxu_dvo:
        flight_bxu_dvo = Flight.objects.create(
            flight_number=flight_number,
            airline=airline,
            aircraft=aircraft,
            route=route_bxu_dvo,
            total_stops=0
        )

    start_date = datetime(2026, 4, 15).date()
    end_date = datetime(2026, 6, 30).date()
    
    time_slots = [
        time(6, 0), time(8, 30), time(10, 15), time(12, 0),
        time(14, 40), time(16, 20), time(18, 0),
        time(19, 45), time(21, 20), time(23, 0)
    ]

    total_created = 0
    current_date = start_date
    base_p = Decimal('1400.00')

    while current_date <= end_date:
        print(f"Date: {current_date}")
        for t in time_slots:
            slot_time = datetime.combine(current_date, t)
            slot_time += timedelta(minutes=random.randint(-10, 10))
            
            tz_aware_depart = slot_time
            tz_aware_arrival = tz_aware_depart + timedelta(minutes=random.randint(45, 60))
            
            exists = Schedule.objects.filter(
                flight=flight_bxu_dvo,
                departure_time__date=current_date,
                departure_time__hour=tz_aware_depart.hour
            ).exists()
            
            if not exists:
                price = base_p + Decimal(random.randint(-200, 700))
                Schedule.objects.create(
                    flight=flight_bxu_dvo,
                    departure_time=tz_aware_depart,
                    arrival_time=tz_aware_arrival,
                    price=price,
                    ml_base_price=price,
                    status='Open',
                    gate=f"Gate {random.randint(1, 10)}"
                )
                total_created += 1
        
        current_date += timedelta(days=1)

    print(f"Successfully created {total_created} new schedules for BXU -> DVO.")

if __name__ == "__main__":
    populate_schedules()
