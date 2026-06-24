import os
import sys
import django
from decimal import Decimal
from django.utils import timezone
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Booking, BookingDetail, Schedule, SeatClass, Seat, PassengerInfo, Students
from fbs_instructor.models import Instructor, Section, SectionEnrollment, Activity, ActivityStudentBinding
from flightapp.services.grading_service import grade_booking
from flightapp.views import _create_booking, _update_booking_totals

def run():
    print("? Starting Grading Verification...")

    # 1. Setup Test Data
    # Create Instructor
    instructor_user, _ = User.objects.get_or_create(username="test_instructor", defaults={'email': 'inst@test.com'})
    instructor, _ = Instructor.objects.get_or_create(user=instructor_user, defaults={
        'first_name': 'Dr.', 'last_name': 'Strange', 'email': 'inst@test.com'
    })
    
    # Create Section
    section, _ = Section.objects.get_or_create(instructor=instructor_user, section_code="TEST101", defaults={
        'section_name': 'Flight Operations 101', 
        'semester': '1st Semester',
        'academic_year': '2024-2025',
        'schedule': 'Monday 09:00-12:00'
    })

    # Create Activity
    activity, _ = Activity.objects.get_or_create(section=section, title="Book Manila to Cebu", defaults={
        'description': 'Book a one-way flight from MNL to CEB in Economy',
        'activity_type': 'individual',
        'total_points': Decimal('100.00'),
        'required_trip_type': 'one_way',
        'required_origin': 'Manila',
        'required_destination': 'Cebu',
        'required_travel_class': 'economy'
    })
    print(f"? Activity Created: {activity.title} (ID: {activity.id})")

    # Create Student
    student_user, _ = User.objects.get_or_create(username="test_student", defaults={'email': 'student@test.com'})
    student, _ = Students.objects.get_or_create(user=student_user, defaults={
        'student_number': '20240001', 'first_name': 'Peter', 'last_name': 'Parker', 'email': 'student@test.com'
    })
    
    # Enroll Student
    files_enrolled, _ = SectionEnrollment.objects.get_or_create(student=student, section=section)
    print(f"? Student Enrolled: {student.first_name}")

    # 2. Simulate Booking (Success Case)
    print("\n? Test Case 1: Correct Booking")
    
    # Create Booking
    booking_data = {'trip_type': 'one_way', 'activity_id': activity.id}
    booking = _create_booking(booking_data, student_user)
    booking.activity = activity # Manually link as _create_booking does it via view logic
    booking.save()

    # Create dummy schedule matching requirements
    # Assuming Schedule/Route exists or creating simplified mock for BookingDetail
    # Ideally we fetch a real schedule 
    schedule = Schedule.objects.filter(flight__route__origin__city__icontains='Manila', flight__route__destination__city__icontains='Cebu').first()
    
    if not schedule:
        print("?? No matching schedule found in DB. Creating dummy for test.")
        # Create minimal needed objects... skipping for brevity, hoping for existing data
        # If no schedule, we can't create detail easily.
        # Let's try to find ANY schedule and see what it is
        schedule = Schedule.objects.first()
        if schedule:
            print(f"   Using fallback schedule: {schedule.flight.route.origin.city} -> {schedule.flight.route.destination.city}")
    
    if schedule:
        # Create Detail
        pax_info, _ = PassengerInfo.objects.get_or_create(first_name="Peter", last_name="Parker")
        detail = BookingDetail.objects.create(
            booking=booking,
            passenger=pax_info,
            schedule=schedule,
            seat_class=SeatClass.objects.filter(name__icontains='Economy').first()
        )
        
        # Run Grading
        grade_booking(booking, activity.id)
        
        # Check Result
        binding = ActivityStudentBinding.objects.get(activity=activity, student=student)
        print(f"   Grade: {binding.grade}/{activity.total_points}")
        print(f"   Status: {binding.status}")
        print(f"   Feedback: {binding.feedback}")
        
    else:
        print("? Cannot proceed without schedule data.")

    print("\n? Verification Complete")

if __name__ == "__main__":
    run()
