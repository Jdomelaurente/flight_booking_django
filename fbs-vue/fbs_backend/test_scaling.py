import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from flightapp.ml.dynamic_pricing import dynamic_pricing
from app.models import PricingConfiguration

config = PricingConfiguration.load()

# Base simulation flight 
base_flight = {
    'schedule_id': 1,
    'flight_number': '5J 123',
    'airline_code': '5J',
    'airline_name': 'Cebu Pacific',
    'origin': 'MNL',
    'destination': 'CEB',
    'total_stops': 0,
    'is_domestic': True,
    'base_price': 2500, # Simulated fallback price
}

print("=== PRICE SCALING TEST ===")
print("Testing with 2500 base price and different advance margins...")

for days_out in [0, 1, 3, 7, 14, 30, 45, 60, 90, 120, 180]:
    flight_data = base_flight.copy()
    flight_data['departure_time'] = (datetime.now() + timedelta(days=days_out)).isoformat()
    
    # Passing dummy user mapping
    res = dynamic_pricing.get_price_for_user(flight_data)
    
    final_price = res['final_price']
    demand_factor = res['factors_applied']['demand_factor']
    time_factor = res['factors_applied']['time_factor']
    
    print(f"Days out: {days_out:<3} | Price: \u20b1{final_price:<5} | Demand Factor: {demand_factor:.3f} | Time Factor: {time_factor:.3f}")
