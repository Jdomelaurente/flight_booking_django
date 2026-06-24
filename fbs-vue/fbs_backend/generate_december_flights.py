import os
import django
import random
from datetime import datetime, time, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule
from django.utils import timezone
import pytz

manila_tz = pytz.timezone('Asia/Manila')

def generate_december_flights():
    try:
        # Configuration
        year = 2026
        month = 12
        flights_per_day = 10
        
        # Get all available flights to pick from
        available_flights = list(Flight.objects.all())
        if not available_flights:
            print("❌ Error: No flights found in the database. Please seed flights first.")
            return

        print(f"🚀 Starting flight generation for December {year}...")
        print(f"Found {len(available_flights)} available flight templates.")

        # Staggered departure slots throughout the day
        departure_slots = [
            (5, 0), (7, 30), (9, 15), (11, 0), (13, 10), 
            (15, 20), (17, 30), (19, 45), (21, 15), (23, 0)
        ]

        total_created = 0
        
        # Loop through each day in December
        for day in range(1, 32):
            print(f"📅 Processing Dec {day}, {year}...")
            
            # Select 10 random flights for this day
            daily_selection = random.sample(available_flights, min(flights_per_day, len(available_flights)))
            
            # Shuffle slots to give variety
            random.shuffle(departure_slots)
            
            for i, flight in enumerate(daily_selection):
                hour, minute = departure_slots[i % len(departure_slots)]
                
                # Create naive datetime then localize to Manila time
                naive_dep = datetime(year, month, day, hour, minute)
                dep_dt = manila_tz.localize(naive_dep)
                
                # Duration between 1 and 3 hours for variety
                duration_mins = random.randint(60, 180)
                arr_dt = dep_dt + timedelta(minutes=duration_mins)
                
                # Check if this exact schedule already exists to avoid duplicates
                if not Schedule.objects.filter(flight=flight, departure_time=dep_dt).exists():
                    schedule = Schedule.objects.create(
                        flight=flight,
                        departure_time=dep_dt,
                        arrival_time=arr_dt,
                        status='Open',
                        price=flight.route.base_price
                    )
                    
                    # Try to update ML price if the method exists
                    try:
                        schedule.update_ml_price(save=True)
                    except Exception as e:
                        # Silently skip if update_ml_price fails or doesn't exist
                        pass
                        
                    total_created += 1
                else:
                    print(f"   ⚠️ Schedule for {flight.flight_number} at {dep_dt} already exists. Skipping.")

        print(f"✅ Successfully created {total_created} new schedules for December {year}.")
        
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_december_flights()
