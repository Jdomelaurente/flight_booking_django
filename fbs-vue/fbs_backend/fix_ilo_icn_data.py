import os
import django
import random
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule, Route, Airline, Aircraft, Airport

def fix_ilo_icn():
    try:
        ilo = Airport.objects.get(code='ILO')
        icn = Airport.objects.get(code='ICN')
        
        # 1. Create Route if missing
        route, created = Route.objects.get_or_create(
            origin_airport=ilo,
            destination_airport=icn,
            defaults={'base_price': Decimal('8500.00')}
        )
        if created:
            print(f"Created Route: ILO -> ICN")
        else:
            print(f"Route ILO -> ICN already exists")

        # 2. Create Inverse Route for return flights
        route_rev, created_rev = Route.objects.get_or_create(
            origin_airport=icn,
            destination_airport=ilo,
            defaults={'base_price': Decimal('8500.00')}
        )
        if created_rev:
            print(f"Created Route: ICN -> ILO")

        # 3. Ensure flights exist for these routes
        airlines = list(Airline.objects.all())
        aircrafts = list(Aircraft.objects.all())
        
        for r in [route, route_rev]:
            flight = Flight.objects.filter(route=r).first()
            if not flight:
                airline = random.choice(airlines)
                aircraft = random.choice(aircrafts)
                flight_number = f"{airline.code}{random.randint(100, 9999)}"
                flight = Flight.objects.create(
                    flight_number=flight_number,
                    airline=airline,
                    aircraft=aircraft,
                    route=r
                )
                print(f"  Created flight: {flight.flight_number} for {r}")

            # 4. Populate 10 schedules per day for 60 days
            today = timezone.now().date()
            for day_offset in range(61):
                target_date = today + timedelta(days=day_offset)
                existing_count = Schedule.objects.filter(
                    flight__route=r,
                    departure_time__date=target_date,
                    status='Open'
                ).count()
                
                if existing_count < 10:
                    needed = 10 - existing_count
                    for _ in range(needed):
                        hour = random.randint(0, 23)
                        minute = random.choice([0, 15, 30, 45])
                        departure_time = timezone.make_aware(datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute))
                        if departure_time < timezone.now():
                            departure_time = timezone.now() + timedelta(minutes=random.randint(60, 300))
                        
                        duration_hours = random.randint(4, 8)
                        arrival_time = departure_time + timedelta(hours=duration_hours)
                        
                        price = float(r.base_price) * random.uniform(0.85, 1.15)
                        
                        Schedule.objects.create(
                            flight=flight,
                            departure_time=departure_time,
                            arrival_time=arrival_time,
                            price=max(1000, price),
                            status='Open'
                        )
            print(f"  Populated schedules for {r}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_ilo_icn()
