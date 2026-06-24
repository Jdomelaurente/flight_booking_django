
import os
import sys
import django
from decimal import Decimal

# Add project root to path (scripts/test_pricing.py -> ../..)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from flightapp.ml.dynamic_pricing import dynamic_pricing
from app.models import PricingConfiguration, Schedule
from django.utils import timezone

print("\n=== Testing Dynamic Pricing ===")

try:
    # 1. Load configuration
    config = PricingConfiguration.load()
    print(f"? Loaded config: {config}")
    
    # 2. Get a real schedule if possible, or create mock flight data
    schedule = Schedule.objects.first()
    if schedule:
        print(f"Found schedule: {schedule.flight.flight_number} departing {schedule.departure_time}")
        flight_data = {
            'flight_number': schedule.flight.flight_number,
            'departure_time': schedule.departure_time,
            'schedule_id': schedule.id
        }
    else:
        print("Creating mock flight data...")
        flight_data = {
            'flight_number': 'TEST999',
            'departure_time': timezone.now() + timezone.timedelta(days=5),
            'schedule_id': None
        }

    # 3. Test price calculation
    print(f"\nCalculating price for anonymous user...")
    price_info = dynamic_pricing.get_price_for_user(flight_data, user=None, session_id='test_session_123')
    
    print("\n--- Price Breakdown ---")
    print(f"Base Price: {price_info['base_price']}")
    print(f"Final Price: {price_info['final_price']}")
    
    factors = price_info['factors_applied']
    for k, v in factors.items():
        print(f"  {k}: {v:.4f}")

    print("\n? Verification SUCCESSFUL")

except Exception as e:
    print(f"\n? Verification FAILED: {e}")
    import traceback
    traceback.print_exc()
