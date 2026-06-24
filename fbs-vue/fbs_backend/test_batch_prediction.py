import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule
from flightapp.ml.predictor import predictor

schedules = Schedule.objects.all().order_by('-id')[:2]
flight_data_list = []
for s in schedules:
    flight_data_list.append({
        'flight_number': s.flight.flight_number,
        'airline_code': s.flight.airline.code,
        'airline_name': s.flight.airline.name,
        'origin': s.flight.route.origin_airport.code,
        'destination': s.flight.route.destination_airport.code,
        'departure_time': s.departure_time.isoformat(),
        'arrival_time': s.arrival_time.isoformat(),
        'total_stops': s.flight.total_stops,
        'is_domestic': s.flight.route.is_domestic,
    })

print("Flight Data List:", flight_data_list)
predictions = predictor.predict_prices_batch(flight_data_list)
print("Predictions:", predictions)
