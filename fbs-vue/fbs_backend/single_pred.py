import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append('c:\\Users\\Crissaunt\\Documents\\GitHub\\fbs-vue\\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from flightapp.ml.predictor import predictor
from django.utils import timezone

flight_data = {
    'flight_number': '5J 123',
    'airline_code': '5J',
    'airline_name': 'Cebu Pacific',
    'origin': 'MNL',
    'destination': 'CEB',
    'total_stops': 0,
    'is_domestic': True,
    'departure_time': timezone.now().isoformat(),
    'arrival_time': (timezone.now() + timedelta(hours=1, minutes=30)).isoformat()
}

print("Running single prediction...")
ml_price = predictor.predict_price(flight_data)
print(f"ML Base Prediction: {ml_price:.2f}")
