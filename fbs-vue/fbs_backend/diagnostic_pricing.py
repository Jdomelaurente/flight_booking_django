import os
import django
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append('c:\\Users\\Crissaunt\\Documents\\GitHub\\fbs-vue\\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from flightapp.ml.dynamic_pricing import dynamic_pricing
from flightapp.ml.predictor import predictor
from django.utils import timezone

def test_pricing_scenarios():
    print("=== Pricing Diagnostic ===")
    
    # Mock flight data
    flight_data_template = {
        'flight_number': '5J 123',
        'airline_code': '5J',
        'airline_name': 'Cebu Pacific',
        'origin': 'MNL',
        'destination': 'CEB',
        'total_stops': 0,
        'is_domestic': True
    }
    
    scenarios = [
        ("Near Date (Tomorrow)", 1),
        ("Near Date (2 days)", 2),
        ("Far Date (1 month)", 30),
        ("Very Far Date (3 months)", 90),
    ]
    
    for label, days in scenarios:
        flight_data = flight_data_template.copy()
        dep_time = timezone.now() + timedelta(days=days)
        flight_data['departure_time'] = dep_time.isoformat()
        flight_data['arrival_time'] = (dep_time + timedelta(hours=1, minutes=30)).isoformat()
        
        print(f"\nScenario: {label} ({days} days out)")
        
        # 1. Base ML Prediction
        # Re-check advance_booking_days handling
        ml_price = predictor.predict_price(flight_data)
        print(f"  ML Base Prediction: {ml_price:.2f}")
        
        # 2. Dynamic Pricing Result
        pricing_result = dynamic_pricing.get_price_for_user(flight_data, user=None, session_id="test_session")
        
        print(f"  Final Price: {pricing_result['final_price']}")
        print(f"  Base Price used in calculation: {pricing_result['base_price']}")
        print(f"  Factors Applied:")
        for factor, value in pricing_result['factors_applied'].items():
            print(f"    - {factor}: {value:.4f}")

if __name__ == "__main__":
    test_pricing_scenarios()
