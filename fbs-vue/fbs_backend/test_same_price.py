import os
import django
import sys
from django.utils import timezone
from datetime import timedelta

# Setup Django environment
sys.path.append('c:\\Users\\Crissaunt\\Documents\\GitHub\\fbs-vue\\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule
from flightapp.ml.dynamic_pricing import dynamic_pricing
from flightapp.ml.predictor import predictor

def check_prices():
    # Find some schedules coming up in the next 7 days
    now = timezone.now()
    end = now + timedelta(days=7)
    
    schedules = Schedule.objects.filter(departure_time__range=[now, end]).order_by('departure_time')[:10]
    
    if not schedules:
        print("No schedules found in the next 7 days.")
        return
        
    print(f"Testing {len(schedules)} upcoming flights:")
    
    for s in schedules:
        flight_data = {
            'schedule_id': s.id,
            'flight_number': s.flight.flight_number,
            'airline_code': s.flight.airline.code,
            'airline_name': s.flight.airline.name,
            'origin': s.flight.route.origin_airport.code,
            'destination': s.flight.route.destination_airport.code,
            'departure_time': s.departure_time.isoformat(),
            'arrival_time': s.arrival_time.isoformat(),
            'total_stops': s.flight.total_stops,
            'is_domestic': s.flight.route.is_domestic,
        }
        
        print(f"\n--- {s.flight.flight_number} | {flight_data['origin']}-{flight_data['destination']} | {s.departure_time.strftime('%Y-%m-%d %H:%M')} ---")
        
        base_price = predictor.predict_price(flight_data)
        print(f"ML Base Price: PHP {base_price:.2f}")
        
        pricing_result = dynamic_pricing.get_price_for_user(flight_data, session_id="test_same_price")
        
        print(f"Final Price: PHP {pricing_result['final_price']}")
        print("Factors applied: ")
        for factor, val in pricing_result['factors_applied'].items():
            print(f"  - {factor}: {val:.4f}")

if __name__ == "__main__":
    check_prices()
