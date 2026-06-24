import os
import django
import sys
from decimal import Decimal

# Setup Django environment
sys.path.append(r'c:\Users\Choizen\Desktop\fbs-vue\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.views import calculate_submission_score
from fbs_instructor.models import Activity, ActivitySegment, ActivityStudentBinding
from app.models import Booking, BookingDetail, Schedule, Flight, Route, Airport, Seat, SeatClass

def test_grading_logic():
    print("--- Testing Grading Logic ---")
    
    # Mock some data
    activity = Activity(
        title="Test Multi-City",
        required_trip_type='multi_city',
        required_travel_class='economy'
    )
    # We can't easily save to DB without real IDs, but we can check the logic if we mock the relations
    # Let's try to fetch an existing activity if possible
    
    # Since we can't easily unit test the Django view function without real DB objects or heavy mocking,
    # we'll do a basic sanity check on the normalization logic if we extract it, 
    # OR we just rely on manual verification if the environment is too complex for quick scripts.
    
    # Let's try to find a real booking and run the score
    try:
        booking = Booking.objects.first()
        activity = Activity.objects.first()
        if booking and activity:
            score = calculate_submission_score(activity, booking)
            print(f"Calculated Score for {activity.title}: {score['total']}")
            print(f"Breakdown: {score['breakdown']}")
        else:
            print("No real data to test with.")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_grading_logic()
