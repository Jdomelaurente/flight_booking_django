
import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule, BookingDetail, CheckInDetail
from flightapp.serializers import ScheduleSerializer

def verify_gate_data():
    print("--- Verifying Gate Data ---")
    
    # Check a schedule
    sched = Schedule.objects.last()
    if sched:
        print(f"Schedule ID: {sched.id}")
        print(f"Schedule Gate: {sched.gate}")
        
        # Test serializer
        serializer = ScheduleSerializer(sched)
        print(f"Serializer Data Gate: {serializer.data.get('gate')}")
        
        if serializer.data.get('gate') == sched.gate:
            print("SUCCESS: Serializer correctly includes gate field.")
        else:
            print("FAILURE: Serializer missing or incorrect gate field.")
            
    # Check check-in detail population
    # Simulate the logic in process_dcs_checkin
    if sched:
        booking = BookingDetail.objects.filter(schedule=sched).first()
        if booking:
            print(f"Found booking {booking.id} for schedule {sched.id}")
            gate_val = booking.schedule.gate or 'Gate 7'
            print(f"Calculated gate for check-in: {gate_val}")
            
            # Check if any check-ins exist for this booking
            ci = CheckInDetail.objects.filter(booking_detail=booking).first()
            if ci:
                print(f"Found existing check-in {ci.id}")
                print(f"Check-in Gate Number: {ci.gate_number}")
            else:
                print("No check-in found for this booking to verify gate_number field population.")
        else:
            print("No booking found for the last schedule to verify check-in logic.")
    else:
        print("No schedules found in database.")

if __name__ == "__main__":
    verify_gate_data()
