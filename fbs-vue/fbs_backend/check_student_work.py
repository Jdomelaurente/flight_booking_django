"""
Quick check: Show the student's booking and grading data.
Run with: python check_student_work.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')

# Limit environment to avoid ML model loading
import sys
django.setup()

from app.models import Booking
from fbs_instructor.models import ActivityStudentBinding, Activity
from django.contrib.auth.models import User

print("=" * 60)
print("STUDENT BOOKING & GRADING STATUS CHECK")
print("=" * 60)

# 1. Show all bookings linked to an activity
print("\n--- Bookings Linked to Activities (latest 10) ---")
bookings = Booking.objects.filter(activity__isnull=False).order_by('-created_at')[:10]
if not bookings:
    print("  ??  NO bookings are linked to any activity!")
for b in bookings:
    print(f"  Booking #{b.id}:")
    print(f"    User: {b.user.username} (ID={b.user.id})")
    print(f"    Activity: {b.activity.title} (ID={b.activity.id})")
    print(f"    Status: {b.status}")
    print(f"    is_graded: {b.is_graded}")
    print(f"    activity_code_used: {b.activity_code_used}")
    print(f"    is_practice: {b.is_practice}")
    print()

# 2. Show ActivityStudentBinding for activity ID 3
activity = Activity.objects.filter(id=3).first()
if activity:
    print(f"--- Activity: '{activity.title}' (code: {activity.activity_code}) ---")
    bindings = ActivityStudentBinding.objects.filter(activity=activity).select_related('student')
    print(f"  {bindings.count()} student binding(s):")
    for binding in bindings:
        print(f"  Student: {binding.student.first_name} {binding.student.last_name} (#{binding.student.student_number})")
        print(f"    Status: {binding.status}")
        print(f"    Grade: {binding.grade}")
        print(f"    Submitted at: {binding.submitted_at}")
        print(f"    Feedback: {str(binding.feedback)[:100] if binding.feedback else 'None'}")
        print()

# 3. Show bookings for 'student' user
real_user = User.objects.filter(username='student').first()
if real_user:
    print(f"--- Bookings for user 'student' (ID={real_user.id}) ---")
    sb = Booking.objects.filter(user=real_user).order_by('-created_at')[:5]
    if not sb:
        print("  ??  No bookings found for this student!")
    for b in sb:
        print(f"  Booking #{b.id}: status={b.status}, activity={b.activity}, code={b.activity_code_used}")
else:
    print("  ??  User 'student' not found")

print("\n" + "=" * 60)
