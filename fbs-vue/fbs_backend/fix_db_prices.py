import os
import django
import sys
from decimal import Decimal

sys.path.append('c:\\Users\\Crissaunt\\Documents\\GitHub\\fbs-vue\\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule
from flightapp.ml.predictor import predictor
from django.utils import timezone

def fix_all_schedules():
    schedules = Schedule.objects.all()
    print(f"Updating {schedules.count()} schedules...")
    
    updated_count = 0
    now = timezone.now()
    stale_schedules = list(schedules)
    
    # 1. Prepare batch data
    flight_data_list = []
    for s in stale_schedules:
        flight_data_list.append({
            'flight_number': s.flight.flight_number,
            'airline_code': s.flight.airline.code,
            'airline_name': s.flight.airline.name,
            'origin': s.flight.route.origin_airport.code,
            'destination': s.flight.route.destination_airport.code,
            'departure_time': s.departure_time.isoformat(),
            'arrival_time': s.arrival_time.isoformat(),
            'total_stops': s.flight.total_stops if hasattr(s.flight, 'total_stops') else 0,
            'is_domestic': s.flight.route.is_domestic,
        })
    
    # 2. Predict batch
    new_prices = predictor.predict_prices_batch(flight_data_list)
    
    # 3. Apply
    for s, price in zip(stale_schedules, new_prices):
        if price <= 0:
            price = 2500  # Fallback
        s.ml_base_price = Decimal(str(price))
        s.ml_price_updated_at = now
        updated_count += 1
        
    # Bulk update
    Schedule.objects.bulk_update(stale_schedules, ['ml_base_price', 'ml_price_updated_at'])
    print(f"Successfully updated {updated_count} schedule prices in the database.")


if __name__ == "__main__":
    fix_all_schedules()
