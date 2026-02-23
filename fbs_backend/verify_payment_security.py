
import os
import django
import sys
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.join(os.getcwd(), 'fbs_backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Booking, Schedule, PassengerInfo
from django.contrib.auth.models import User
from flightapp.serializers import CreateBookingSerializer
from rest_framework.test import APIRequestFactory

def verify_payment_security():
    print("PAYMENT SECURITY VERIFICATION")
    print("=============================")
    
    # 1. Create a Booking with a Manipulated Total
    print("\n1. Testing Booking Creation with Manipulated Total")
    
    # Get a user and schedule
    user = User.objects.first()
    schedule = Schedule.objects.first()
    
    if not user or not schedule:
        print("? Error: Need at least one user and one schedule in the database.")
        return
    
    print(f"   User: {user.username}")
    print(f"   Schedule: {schedule.id} ({schedule.flight.flight_number})")
    print(f"   Schedule Price: {schedule.price}")
    
    # Create valid payload with MALICIOUS total_amount
    malicious_total = Decimal('1.00') # Try to pay only 1 peso
    
    payload = {
        'trip_type': 'one_way',
        'passengers': [{
            'title': 'Mr',
            'first_name': 'Test',
            'last_name': 'User',
            'type': 'Adult',
            'date_of_birth': '1990-01-01',
            'nationality': 'Philippines'
        }],
        'contact_info': {
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'test@example.com',
            'phone': '09123456789'
        },
        'selectedOutbound': {
            'id': schedule.id,
            'schedule_id': schedule.id,
            'price': float(schedule.price),
            'class_type': 'Economy'
        },
        'total_amount': float(malicious_total) # ? ATTACK VECTOR
    }
    
    # Validate serializer (should pass now that total_amount is optional/ignored)
    serializer = CreateBookingSerializer(data=payload)
    if not serializer.is_valid():
        print(f"? Serializer failed: {serializer.errors}")
        return

    # Simulate View Logic (which we modified)
    from flightapp.views import _create_booking, _create_booking_detail, _apply_taxes, _update_booking_totals
    
    # Manually run the view logic to test protections
    try:
        # Step 1: Create booking (should ignore total_amount)
        print("   Creating booking...")
        booking = _create_booking(payload, user)
        
        # Check if total_amount was ignored
        print(f"   Booking created. ID: {booking.id}")
        print(f"   Initial Total: {booking.total_amount}")
        
        if booking.total_amount == malicious_total:
             print("? FAIL: Backend accepted malicious total amount!")
        elif booking.total_amount == Decimal('0.00'):
             print("? PASS: Backend ignored malicious total (set to 0.00 initially)")
        else:
             print(f"?? Warning: Unexpected initial total: {booking.total_amount}")

        # Step 2: Create details (should calculate real price)
        print("   Creating booking details...")
        passenger_data = payload['passengers'][0]
        # Mock passenger creation for this test
        passenger = PassengerInfo.objects.create(
            first_name='Test', last_name='User', passenger_type='Adult'
        )
        
        detail = _create_booking_detail(booking, passenger, payload, passenger_data)
        
        if not detail:
             print("? Error creating booking detail")
             return
             
        print(f"   Detail created. Price: {detail.price}")
        
        # Step 3: Update totals
        print("   Updating booking totals...")
        _update_booking_totals(booking)
        
        booking.refresh_from_db()
        print(f"   Final Booking Total: {booking.total_amount}")
        
        # Verify final total matches schedule price (plus taxes if any)
        # For simplicity, assuming no taxes or simple taxes
        expected_min = schedule.price
        
        if booking.total_amount >= expected_min:
            print(f"? PASS: Final total ({booking.total_amount}) is >= base price ({expected_min})")
            print("         Security Check Passed: Malicious total was overwritten.")
        else:
            print(f"? FAIL: Final total ({booking.total_amount}) is less than base price!")

    except Exception as e:
        print(f"? Exception during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_payment_security()
