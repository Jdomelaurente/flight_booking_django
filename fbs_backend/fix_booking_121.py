"""
Fix booking 121: reassign it to the real student user and re-trigger grading.
Run with: python fix_booking_121.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Booking
from django.contrib.auth.models import User
from flightapp.services.grading_service import grade_booking

print("=" * 60)
print("FIXING BOOKING #121")
print("=" * 60)

# 1. Get the booking
try:
    booking = Booking.objects.get(id=121)
    print(f"Found: Booking #{booking.id}, current user={booking.user.username}, status={booking.status}")
except Booking.DoesNotExist:
    print("? Booking 121 not found!")
    exit()

# 2. Get the real student user
real_user = User.objects.filter(username='student').first()
if not real_user:
    print("? Real student user not found!")
    exit()
print(f"Real student user: {real_user.username} (ID={real_user.id})")

# 3. Reassign the booking
booking.user = real_user
booking.save()
print(f"? Booking #{booking.id} reassigned to user '{real_user.username}'")

# 4. Re-trigger grading
if booking.activity:
    print(f"? Re-triggering grading for activity: {booking.activity.title}")
    try:
        result = grade_booking(booking, booking.activity.id)
        print(f"? Grading result: {result}")
    except Exception as e:
        import traceback
        print(f"? Grading error: {e}")
        traceback.print_exc()
else:
    print("?? No activity linked to this booking")

# 5. Check final state
from fbs_instructor.models import ActivityStudentBinding
bindings = ActivityStudentBinding.objects.filter(activity=booking.activity)
print("\n--- Final Binding State ---")
for b in bindings:
    print(f"  Student: {b.student.first_name} {b.student.last_name}")
    print(f"  Status: {b.status}")
    print(f"  Grade: {b.grade}")
    print(f"  Feedback: {str(b.feedback)[:100] if b.feedback else 'None'}")

print("\n" + "=" * 60)
print("Done!")
