import os
import django
import sys
import json

# Setup Django environment
sys.path.append(r'c:\Users\Choizen\Desktop\fbs-vue\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.views import get_available_addons
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

def test_available_addons():
    print("--- Testing Available Addons Endpoint ---")
    factory = APIRequestFactory()
    
    # Find a user with instructor profile
    from app.models import UserProfile
    instructor_profile = UserProfile.objects.filter(role='instructor').first()
    if not instructor_profile:
        print("No instructor profiles found.")
        # Fallback to any user if no instructor profile exists (for dev)
        user = User.objects.filter(is_staff=True).first()
    else:
        user = instructor_profile.user
        
    if not user:
        print("No user found to test.")
        return

    print(f"Testing with user: {user.username}")
    
    # Test case 1: No route (should fallback to all)
    request = factory.get('/api/instructor/available-addons/')
    force_authenticate(request, user=user)
    response = get_available_addons(request)
    
    if response.status_code != 200:
        print(f"Error: Status {response.status_code}, {response.data}")
        return
        
    print(f"Total addons (fallback): {len(response.data['available_addons'])}")
    
    # Test case 2: Specific route (if we can find one)
    from app.models import Schedule
    sched = Schedule.objects.first()
    if sched:
        origin = sched.flight.route.origin_airport.code
        dest = sched.flight.route.destination_airport.code
        date = str(sched.departure_time.date())
        
        request = factory.get(f'/api/instructor/available-addons/?origin={origin}&destination={dest}&date={date}')
        force_authenticate(request, user=user)
        response = get_available_addons(request)
        print(f"Addons for {origin}->{dest} on {date}: {len(response.data.get('available_addons', []))}")
        for ad in response.data.get('available_addons', []):
            print(f" - {ad['name']} (Airline: {ad['airline']['code'] if ad['airline'] else 'N/A'})")
    else:
        print("No schedules found to test specific route.")

if __name__ == "__main__":
    test_available_addons()
