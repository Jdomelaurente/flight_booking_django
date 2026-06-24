# flightapp/management/commands/generate_price_trend_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
from app.models import Airline, Aircraft, Airport, Route, Flight, Schedule, Seat, SeatClass, Country
from flightapp.ml.dynamic_pricing import dynamic_pricing

class Command(BaseCommand):
    help = 'Generates 60 days of flight schedules and simulates occupancy for price trend visualization'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data generation for 60-day price trend...'))

        # 1. Ensure we have the necessary base data
        philippines, _ = Country.objects.get_or_create(name='Philippines', defaults={'code': 'PH', 'currency': 'PHP'})
        
        mnl, _ = Airport.objects.get_or_create(
            code='MNL', 
            defaults={'name': 'Ninoy Aquino International Airport', 'city': 'Manila', 'country': philippines, 'airport_type': 'international'}
        )
        ceb, _ = Airport.objects.get_or_create(
            code='CEB', 
            defaults={'name': 'Mactan-Cebu International Airport', 'city': 'Cebu', 'country': philippines, 'airport_type': 'international'}
        )

        airline, _ = Airline.objects.get_or_create(code='AP', defaults={'name': 'Air Pilipinas'})
        
        aircraft, _ = Aircraft.objects.get_or_create(
            model='Airbus A320-Trend', 
            airline=airline, 
            defaults={'capacity': 180}
        )

        route, _ = Route.objects.get_or_create(
            origin_airport=mnl, 
            destination_airport=ceb,
            defaults={'base_price': Decimal('2500.00')}
        )

        flight, _ = Flight.objects.get_or_create(
            flight_number='AP-TREND-101',
            airline=airline,
            aircraft=aircraft,
            route=route
        )

        # Ensure seat classes exist
        econ, _ = SeatClass.objects.get_or_create(name='Economy', airline=airline, defaults={'price_multiplier': Decimal('1.00')})
        biz, _ = SeatClass.objects.get_or_create(name='Business', airline=airline, defaults={'price_multiplier': Decimal('1.80')})

        # 2. Clear old schedules for this flight to avoid clutter
        Schedule.objects.filter(flight=flight).delete()

        # 3. Generate 60 days of data
        start_date = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        for i in range(60):
            departure = start_date + timedelta(days=i)
            arrival = departure + timedelta(hours=1, minutes=30)
            
            # Create Schedule
            schedule = Schedule.objects.create(
                flight=flight,
                departure_time=departure,
                arrival_time=arrival,
                status='Open'
            )

            # 4. Simulate Occupancy (Randomized Load Factor)
            # Some flights are full (90%), some are empty (15%), most are average (50-70%)
            if i % 7 == 0: # Weekends/Special spikes
                load_factor = random.uniform(0.75, 0.95)
            elif i < 5: # Flights very close to today are usually fuller
                load_factor = random.uniform(0.60, 0.90)
            else:
                load_factor = random.uniform(0.15, 0.70)

            # Generate seats
            total_seats = aircraft.capacity
            occupied_count = int(total_seats * load_factor)
            
            seats_to_create = []
            for s_idx in range(1, total_seats + 1):
                is_avail = s_idx > occupied_count
                # Mix of Biz and Econ
                s_class = biz if s_idx <= 12 else econ # First 2 rows biz
                row = (s_idx - 1) // 6 + 1
                col = chr(65 + (s_idx - 1) % 6) # A-F
                
                seats_to_create.append(Seat(
                    schedule=schedule,
                    seat_class=s_class,
                    seat_number=f"{row}{col}",
                    row=row,
                    column=col,
                    is_available=is_avail
                ))
            
            Seat.objects.bulk_create(seats_to_create)

            # 5. Calculate ML Base Price
            # We bypass the actual ML call for speed in this sim if we want, 
            # but let's use the actual predictor to get realistic base starts.
            schedule.update_ml_price(save=True)

            if i % 10 == 0:
                self.stdout.write(f"Generated day {i}/60: {departure.date()} (Load: {load_factor:.1%})")

        self.stdout.write(self.style.SUCCESS(f'Successfully generated 60 days of price trend data for {flight.flight_number}'))
