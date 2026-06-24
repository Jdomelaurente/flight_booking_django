
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
try:
    django.setup()
except Exception:
    pass

from django.utils import timezone
from app.models import (
    Route, Flight, Schedule, Seat, SeatClass, Aircraft
)

def populate_march_schedules():
    print("Starting March 2026 schedule population...")
    
    # 1. Get all routes and their flights
    flights = Flight.objects.all()
    if not flights.exists():
        print("No flights found. Please run populate_data.py first.")
        return

    # 2. Define the month of March 2026
    year = 2026
    month = 3
    days_in_march = 31

    # 3. Define 10 distinct departure times per day (e.g., every 2 hours from 6 AM)
    base_hours = [6, 8, 10, 12, 14, 16, 18, 20, 22, 23] # 10 slots
    
    # 4. Get seat classes for aircraft mapping
    seat_classes = SeatClass.objects.all()
    
    total_schedules_created = 0
    total_seats_created = 0

    for day in range(1, days_in_march + 1):
        target_date = datetime(year, month, day)
        print(f"Processing {target_date.date()}...")
        
        for flight in flights:
            # Check how many schedules already exist for this flight on this day
            start_of_day = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
            end_of_day = timezone.make_aware(datetime.combine(target_date, datetime.max.time()))
            
            existing_count = Schedule.objects.filter(
                flight=flight,
                departure_time__range=(start_of_day, end_of_day)
            ).count()
            
            needed = max(0, 10 - existing_count)
            
            if needed == 0:
                continue
                
            # Create the remaining schedules
            # We'll use the slots that aren't taken, or just offset them if needed
            # For simplicity, we'll just create 'needed' schedules at unique times
            for i in range(needed):
                hour = base_hours[i % len(base_hours)]
                minute = random.choice([0, 15, 30, 45])
                
                departure_time = timezone.make_aware(datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute)))
                
                # Ensure it's not in the past relative to now (if running in 2026)
                # But since the user asked for March 2026 specifically, we'll just create them
                
                # Check for exact duplicate time for this flight
                if Schedule.objects.filter(flight=flight, departure_time=departure_time).exists():
                    # Shift by 5 minutes if duplicate
                    departure_time += timedelta(minutes=5)

                duration = timedelta(hours=random.uniform(1, 3)) # Standard 1-3 hour flights
                arrival_time = departure_time + duration
                
                schedule = Schedule.objects.create(
                    flight=flight,
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    price=flight.route.base_price,
                    status='Open'
                )
                total_schedules_created += 1
                
                # 5. Create Seats for the new schedule
                # This logic is adapted from populate_data.py
                aircraft = flight.aircraft
                airline = flight.airline
                
                airline_seat_classes = list(SeatClass.objects.filter(airline=airline))
                if not airline_seat_classes:
                    airline_seat_classes = list(SeatClass.objects.filter(airline__isnull=True))
                
                if not airline_seat_classes:
                    print(f"Warning: No seat classes found for airline {airline.code}")
                    continue

                total_capacity = aircraft.capacity
                columns = ['A', 'B', 'C', 'D', 'E', 'F']
                rows_needed = (total_capacity // len(columns)) + 1
                
                seats_to_create = []
                seats_count = 0
                
                for row in range(1, rows_needed + 1):
                    for col in columns:
                        if seats_count >= total_capacity:
                            break
                        
                        # Assign seat class
                        if row <= 4 and len(airline_seat_classes) >= 3:
                            s_class = airline_seat_classes[0]
                        elif row <= 8 and len(airline_seat_classes) >= 2:
                            s_class = airline_seat_classes[1]
                        else:
                            s_class = airline_seat_classes[-1]
                            
                        # Basic features
                        is_window = col in ['A', 'F']
                        is_aisle = col in ['C', 'D']
                        
                        price_adj = Decimal('0.00')
                        if row < 5: price_adj += Decimal('1000.00')
                        
                        seats_to_create.append(Seat(
                            schedule=schedule,
                            seat_class=s_class,
                            row=row,
                            column=col,
                            seat_number=f"{row}{col}",
                            is_available=True,
                            is_window=is_window,
                            is_aisle=is_aisle,
                            price_adjustment=price_adj
                        ))
                        seats_count += 1
                
                Seat.objects.bulk_create(seats_to_create)
                total_seats_created += seats_count
                
    print(f"Population complete!")
    print(f"Schedules created: {total_schedules_created}")
    print(f"Seats created: {total_seats_created}")

if __name__ == "__main__":
    populate_march_schedules()
