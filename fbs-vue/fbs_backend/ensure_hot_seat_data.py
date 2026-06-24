import os
import django
import random
from django.utils import timezone
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule, Route, Airline, Aircraft, Airport, SeatClass

def ensure_hot_seat_data():
    try:
        # Get AirAsia Philippines
        z2 = Airline.objects.get(code='Z2')
        ilo = Airport.objects.get(code='ILO')
        icn = Airport.objects.get(code='ICN')
        
        route = Route.objects.get(origin_airport=ilo, destination_airport=icn)
        route_rev = Route.objects.get(origin_airport=icn, destination_airport=ilo)

        # Get aircraft for Z2
        aircraft = Aircraft.objects.filter(airline=z2).first()
        if not aircraft:
            # Create a dummy aircraft if needed or use existing
            aircraft = Aircraft.objects.first()

        for r in [route, route_rev]:
            # Create/Get AirAsia flight for this route
            flight_number = f"Z2{random.randint(100, 9999)}"
            flight, created = Flight.objects.get_or_create(
                airline=z2,
                route=r,
                defaults={
                    'flight_number': flight_number,
                    'aircraft': aircraft
                }
            )
            
            # Ensure at least 5 schedules per day for next 60 days are on this AirAsia flight
            today = timezone.now().date()
            for day_offset in range(61):
                target_date = today + timedelta(days=day_offset)
                existing_count = Schedule.objects.filter(
                    flight=flight,
                    departure_time__date=target_date
                ).count()
                
                if existing_count < 5:
                    needed = 5 - existing_count
                    for _ in range(needed):
                        hour = random.randint(0, 23)
                        minute = random.choice([0, 15, 30, 45])
                        departure_time = timezone.make_aware(datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute))
                        if departure_time < timezone.now():
                            departure_time = timezone.now() + timedelta(minutes=random.randint(60, 300))
                        
                        duration_hours = random.randint(4, 8)
                        arrival_time = departure_time + timedelta(hours=duration_hours)
                        
                        Schedule.objects.create(
                            flight=flight,
                            departure_time=departure_time,
                            arrival_time=arrival_time,
                            price=float(r.base_price) * random.uniform(0.9, 1.1),
                            status='Open'
                        )
        print("Successfully ensured AirAsia (Hot Seat) flights for ILO-ICN routes.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ensure_hot_seat_data()
