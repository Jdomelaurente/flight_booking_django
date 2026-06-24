import os
import django
from decimal import Decimal
from datetime import datetime, timedelta, time
import random
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule, Airline, Aircraft

def populate_schedules():
    print("🚀 Starting multi-route schedule population...")
    
    # 1. Routes and Airports
    try:
        ceb = Airport.objects.get(code='CEB')
        dvo = Airport.objects.get(code='DVO')
        bxu = Airport.objects.get(code='BXU')
        airline_5j = Airline.objects.get(code='5J')
        aircraft = Aircraft.objects.filter(airline=airline_5j).first()
        
        if not aircraft:
            aircraft = Aircraft.objects.first()
            
        print(f"✅ Airports found: {ceb.city}, {dvo.city}, {bxu.city}")
    except Exception as e:
        print(f"❌ error finding base data: {e}")
        return

    # Route 1: CEB -> DVO
    route_ceb_dvo, _ = Route.objects.get_or_create(
        origin_airport=ceb, 
        destination_airport=dvo,
        defaults={'base_price': Decimal('1500.00')}
    )
    
    flight_ceb_dvo, _ = Flight.objects.get_or_create(
        flight_number='5J1001',
        defaults={
            'airline': airline_5j,
            'aircraft': aircraft,
            'route': route_ceb_dvo,
            'total_stops': 0
        }
    )

    # Route 2: DVO -> BXU
    route_dvo_bxu, _ = Route.objects.get_or_create(
        origin_airport=dvo, 
        destination_airport=bxu,
        defaults={'base_price': Decimal('1200.00')}
    )
    
    flight_dvo_bxu, _ = Flight.objects.get_or_create(
        flight_number='5J2001',
        defaults={
            'airline': airline_5j,
            'aircraft': aircraft,
            'route': route_dvo_bxu,
            'total_stops': 0
        }
    )

    # 2. Date Range: Today (April 2) to April 5
    start_date = datetime(2026, 4, 2).date()
    end_date = datetime(2026, 4, 5).date()
    
    time_slots = [
        time(8, 30),
        time(11, 15),
        time(14, 45),
        time(17, 30),
        time(20, 0)
    ]

    flights_to_process = [
        {'flight': flight_ceb_dvo, 'base_price': Decimal('1800.00')},
        {'flight': flight_dvo_bxu, 'base_price': Decimal('1400.00')}
    ]

    total_created = 0
    current_date = start_date
    while current_date <= end_date:
        print(f"📅 Processing {current_date}...")
        for flight_info in flights_to_process:
            flight = flight_info['flight']
            base_p = flight_info['base_price']
            
            for t in time_slots:
                # Add some random minutes variation
                slot_time = datetime.combine(current_date, t)
                slot_time += timedelta(minutes=random.randint(0, 15))
                
                # Use naive datetime as USE_TZ is False
                tz_aware_depart = slot_time
                tz_aware_arrival = tz_aware_depart + timedelta(minutes=random.randint(45, 90))
                
                # Check if schedule already exists to avoid duplication
                exists = Schedule.objects.filter(
                    flight=flight,
                    departure_time__date=current_date,
                    departure_time__hour=tz_aware_depart.hour
                ).exists()
                
                if not exists:
                    # Randomize price slightly around base
                    price = base_p + Decimal(random.randint(-200, 500))
                    
                    schedule = Schedule.objects.create(
                        flight=flight,
                        departure_time=tz_aware_depart,
                        arrival_time=tz_aware_arrival,
                        price=price,
                        ml_base_price=price,
                        status='Open',
                        gate=f"Gate {random.randint(1, 12)}"
                    )
                    total_created += 1
                    # Note: Seat generation happens automatically via post_save/save in models.py
        
        current_date += timedelta(days=1)

    print(f"✅ Successfully created {total_created} new schedules across 2 routes.")

if __name__ == "__main__":
    populate_schedules()
