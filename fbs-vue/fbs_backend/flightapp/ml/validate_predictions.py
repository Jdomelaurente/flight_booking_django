# Create a test script to validate predictions
# flightapp/ml/validate_predictions.py

from app.models import BookingDetail
from decimal import Decimal
import statistics

def validate_predictions():
    """Compare ML predictions with actual booked prices"""
    
    # Get actual bookings from the last 30 days
    bookings = BookingDetail.objects.filter(
        booking__created_at__gte=timezone.now() - timedelta(days=30),
        price__gt=0
    ).select_related('schedule__flight__airline', 'schedule__flight__route')
    
    differences = []
    
    for booking in bookings:
        # Get ML prediction for this flight
        flight_data = {
            'flight_number': booking.schedule.flight.flight_number,
            'airline_code': booking.schedule.flight.airline.code,
            'origin': booking.schedule.flight.route.origin_airport.code,
            'destination': booking.schedule.flight.route.destination_airport.code,
            'departure_time': booking.schedule.departure_time.isoformat(),
            'arrival_time': booking.schedule.arrival_time.isoformat(),
            'total_stops': 0,
            'is_domestic': booking.schedule.flight.route.is_domestic,
        }
        
        ml_price = predictor.predict_price(flight_data)
        actual_price = float(booking.price)
        
        difference = abs(ml_price - actual_price)
        percent_diff = (difference / actual_price) * 100
        
        differences.append(percent_diff)
        
        print(f"{booking.schedule.flight.flight_number}: ML=?{ml_price:.0f}, Actual=?{actual_price:.0f}, Diff={percent_diff:.1f}%")
    
    if differences:
        print(f"\n? Summary:")
        print(f"   Average difference: {statistics.mean(differences):.1f}%")
        print(f"   Median difference: {statistics.median(differences):.1f}%")
        print(f"   Min difference: {min(differences):.1f}%")
        print(f"   Max difference: {max(differences):.1f}%")