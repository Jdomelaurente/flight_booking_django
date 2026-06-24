import os
import django
import random
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule, Route, Airline, Aircraft, Seat, SeatClass

def populate_comprehensive():
    routes = list(Route.objects.all())
    airlines = list(Airline.objects.all())
    aircrafts = list(Aircraft.objects.all())

    if not routes:
        print("Error: No routes found.")
        return
    
    # Get all active seat classes
    all_seat_classes = list(SeatClass.objects.filter(is_active=True))
    if not all_seat_classes:
        print("Error: No active seat classes found.")
        return

    today = timezone.now().date()
    total_schedules = 0
    total_seats = 0

    print(f"Processing {len(routes)} routes for the next 30 days...")

    for route in routes:
        # 1. Ensure flights exist for both directions
        # Outbound
        flight_out = Flight.objects.filter(route=route).first()
        if not flight_out:
            airline = random.choice(airlines)
            aircraft = random.choice(aircrafts)
            flight_out = Flight.objects.create(
                flight_number=f"{airline.code}{random.randint(100, 9999)}",
                airline=airline,
                aircraft=aircraft,
                route=route
            )
        
        # Inbound (Check if reverse route exists)
        reverse_route = Route.objects.filter(
            origin_airport=route.destination_airport,
            destination_airport=route.origin_airport
        ).first()
        
        flight_in = None
        if reverse_route:
            flight_in = Flight.objects.filter(route=reverse_route).first()
            if not flight_in:
                airline = flight_out.airline # Keep same airline for simplicity
                aircraft = random.choice(aircrafts)
                flight_in = Flight.objects.create(
                    flight_number=f"{airline.code}{random.randint(100, 9999)}",
                    airline=airline,
                    aircraft=aircraft,
                    route=reverse_route
                )

        # 2. Populate schedules and seats
        for day_offset in range(1, 31): # Next 30 days
            target_date = today + timedelta(days=day_offset)
            
            for flight in [flight_out, flight_in]:
                if not flight: continue
                
                # Check if schedule exists
                if not Schedule.objects.filter(flight=flight, departure_time__date=target_date).exists():
                    # Create one schedule per day
                    hour = random.randint(6, 20)
                    minute = random.choice([0, 15, 30, 45])
                    departure_time = timezone.make_aware(datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute))
                    
                    duration = timedelta(hours=random.randint(1, 4))
                    arrival_time = departure_time + duration
                    
                    price = route.base_price or Decimal('3500.00')
                    
                    try:
                        schedule = Schedule.objects.create(
                            flight=flight,
                            departure_time=departure_time,
                            arrival_time=arrival_time,
                            price=price,
                            status='Open'
                        )
                        total_schedules += 1
                        
                        # Create seats for this schedule
                        # Use classes belonging to this airline OR global classes
                        airline_classes = [sc for sc in all_seat_classes if sc.airline == flight.airline or sc.airline is None]
                        
                        for seat_class in airline_classes:
                            # Create 10 seats for each class
                            for s_num in range(1, 11):
                                seat_label = f"{s_num}{seat_class.name[0].upper()}"
                                Seat.objects.get_or_create(
                                    schedule=schedule,
                                    seat_class=seat_class,
                                    seat_number=seat_label,
                                    defaults={
                                        'is_available': True,
                                        'row': s_num,
                                        'column': seat_class.name[0].upper()
                                    }
                                )
                                total_seats += 1
                    except Exception as e:
                        print(f"  Error creating schedule/seats for {flight.flight_number}: {e}")
                        continue

    print(f"\nPopulation Finished!")
    print(f"Schedules created: {total_schedules}")
    print(f"Seats created: {total_seats}")

if __name__ == "__main__":
    populate_comprehensive()
