from predictor import predictor
from datetime import datetime, timedelta

def test_model():
    """Test the ML model with sample flight data"""
    
    print("=" * 60)
    print("? TESTING FLIGHT PRICE PREDICTION MODEL")
    print("=" * 60)
    
    # Test Case 1: Cebu Pacific, Manila to Cebu, Domestic
    test_flight_1 = {
        'airline_code': '5J',
        'airline_name': 'Cebu Pacific',
        'origin': 'MNL',
        'destination': 'CEB',
        'departure_time': (datetime.now() + timedelta(days=14)).isoformat(),
        'arrival_time': (datetime.now() + timedelta(days=14, hours=1, minutes=15)).isoformat(),
        'total_stops': 0,
        'is_domestic': True,
        'duration_hours': 1.25
    }
    
    # Test Case 2: Philippine Airlines, Manila to Davao
    test_flight_2 = {
        'airline_code': 'PR',
        'airline_name': 'Philippine Airlines',
        'origin': 'MNL',
        'destination': 'DVO',
        'departure_time': (datetime.now() + timedelta(days=7)).isoformat(),
        'arrival_time': (datetime.now() + timedelta(days=7, hours=1, minutes=45)).isoformat(),
        'total_stops': 0,
        'is_domestic': True,
        'duration_hours': 1.75
    }
    
    # Test Case 3: Cebu Pacific, Manila to Caticlan (with stop)
    test_flight_3 = {
        'airline_code': '5J',
        'airline_name': 'Cebu Pacific',
        'origin': 'MNL',
        'destination': 'MPH',
        'departure_time': (datetime.now() + timedelta(days=3)).isoformat(),
        'arrival_time': (datetime.now() + timedelta(days=3, hours=2, minutes=30)).isoformat(),
        'total_stops': 1,
        'is_domestic': True,
        'duration_hours': 2.5
    }
    
    # Test Case 4: Philippine Airlines, Cebu to Manila (Weekend)
    # FIXED: Convert to ISO format string
    departure = (datetime.now() + timedelta(days=2)).replace(hour=8, minute=0)
    arrival = (datetime.now() + timedelta(days=2, hours=1, minutes=15)).replace(hour=9, minute=15)
    
    test_flight_4 = {
        'airline_code': 'PR',
        'airline_name': 'Philippine Airlines',
        'origin': 'CEB',
        'destination': 'MNL',
        'departure_time': departure.isoformat(),  # Convert to string
        'arrival_time': arrival.isoformat(),      # Convert to string
        'total_stops': 0,
        'is_domestic': True,
        'duration_hours': 1.25
    }
    
    test_cases = [
        ("Cebu Pacific - MNL?CEB (14 days out)", test_flight_1),
        ("Philippine Airlines - MNL?DVO (7 days out)", test_flight_2),
        ("Cebu Pacific - MNL?MPH (3 days out, 1 stop)", test_flight_3),
        ("Philippine Airlines - CEB?MNL (2 days out, weekend)", test_flight_4),
    ]
    
    print("\n? PREDICTION RESULTS:")
    print("-" * 60)
    
    for name, flight_data in test_cases:
        price = predictor.predict_price(flight_data)
        
        # Also predict seat class prices
        economy_price = predictor.predict_seat_class_price(price, 'Economy')
        business_price = predictor.predict_seat_class_price(price, 'Business')
        first_price = predictor.predict_seat_class_price(price, 'First')
        
        print(f"\n??  {name}")
        print(f"   Route: {flight_data['origin']} ? {flight_data['destination']}")
        print(f"   Airline: {flight_data['airline_name']}")
        print(f"   Departure: {flight_data['departure_time'][:10]}")
        print(f"   Base Price: ?{price:,.2f}")
        print(f"   Economy: ?{economy_price:,.2f}")
        print(f"   Business: ?{business_price:,.2f}")
        print(f"   First Class: ?{first_price:,.2f}")
    
    print("\n" + "=" * 60)
    print("? Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_model()