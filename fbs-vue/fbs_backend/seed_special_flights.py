import os
import django
import random
from datetime import timedelta, datetime
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
try:
    django.setup()
except Exception:
    pass

from app.models import Flight, Schedule, Route, Airline, Aircraft

def seed_special_flights():
    print("🚀 Seeding 5 Special MNL-CEB 2-stop flights...")
    
    # Get or create MNL-CEB route
    try:
        route = Route.objects.get(origin_airport__code='MNL', destination_airport__code='CEB')
    except Route.DoesNotExist:
        print("❌ MNL-CEB route not found. Please ensure airports and routes are populated.")
        return

    airline = Airline.objects.filter(code='PR').first() or Airline.objects.first()
    aircraft = Aircraft.objects.first()

    special_layovers = [
        [
            {"airport": "ILO", "city": "Iloilo", "duration": "1h 30m"},
            {"airport": "BCD", "city": "Bacolod", "duration": "2h 00m"}
        ],
        [
            {"airport": "DVO", "city": "Davao", "duration": "1h 45m"},
            {"airport": "CGY", "city": "Cagayan de Oro", "duration": "1h 15m"}
        ],
        [
            {"airport": "PPS", "city": "Puerto Princesa", "duration": "2h 30m"},
            {"airport": "ENI", "city": "El Nido", "duration": "1h 00m"}
        ],
        [
            {"airport": "SIN", "city": "Singapore", "duration": "3h 00m"},
            {"airport": "HKG", "city": "Hong Kong", "duration": "2h 30m"}
        ],
        [
            {"airport": "MPH", "city": "Caticlan", "duration": "1h 20m"},
            {"airport": "KLO", "city": "Kalibo", "duration": "1h 10m"}
        ]
    ]

    from django.utils import timezone
    base_time = timezone.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=2)

    for i in range(5):
        flight_num = f"PR{2000 + i}"
        
        # Create Flight
        flight, created = Flight.objects.get_or_create(
            flight_number=flight_num,
            defaults={
                'airline': airline,
                'aircraft': aircraft,
                'route': route,
                'total_stops': 2,
                'layovers_data': special_layovers[i]
            }
        )
        
        if not created:
            flight.total_stops = 2
            flight.layovers_data = special_layovers[i]
            flight.save()

        # Create Schedule
        departure_time = base_time + timedelta(hours=i*3)
        arrival_time = departure_time + timedelta(hours=8) # Long duration for 2 stops
        
        schedule, s_created = Schedule.objects.get_or_create(
            flight=flight,
            departure_time=departure_time,
            defaults={
                'arrival_time': arrival_time,
                'price': Decimal('8500.00') + (i * 500),
                'status': 'Scheduled',
                'gate': f'G{i+1}'
            }
        )
        
        if not s_created:
            schedule.departure_time = departure_time
            schedule.arrival_time = arrival_time
            schedule.price = Decimal('8500.00') + (i * 500)
            schedule.save()

        print(f"✅ Created/Updated Special Flight {flight_num}: MNL -> CEB (2 Stops: {', '.join([l['city'] for l in special_layovers[i]])})")

if __name__ == "__main__":
    seed_special_flights()
