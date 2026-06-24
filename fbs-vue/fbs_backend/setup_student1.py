import os
import django
import random
from decimal import Decimal
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import Section, Activity, ActivityStudentBinding, StudentNotification
from app.models import Students
from django.db import transaction

def setup_student1_performance():
    section_id = 7
    student_username = 'student1'
    
    try:
        section = Section.objects.get(id=section_id)
        student_record = Students.objects.get(user__username=student_username)
        print(f"Target Section: {section.section_name}")
        print(f"Target Student: {student_username}")
    except (Section.DoesNotExist, Students.DoesNotExist):
        print("Error: Required data not found.")
        return

    # Count current activities
    current_activities = Activity.objects.filter(section=section)
    needed = 10 - current_activities.count()
    
    if needed > 0:
        print(f"Creating {needed} new activities...")
        activity_types = ['Flight Booking', 'Seat Selection', 'Passenger Management', 'Baggage Handling']
        
        for i in range(needed):
            Activity.objects.create(
                section=section,
                title=f"Advanced Simulation Module {i+5}",
                activity_type=random.choice(activity_types),
                instructions="Complete the specialized simulation tasks as outlined in the module manual.",
                due_date=timezone.now() + timezone.timedelta(days=7),
                status='published',
                grades_released=True,
                required_trip_type='round_trip',
                required_travel_class='Economy',
                required_passengers=1
            )
    
    # Refresh activities list
    all_activities = Activity.objects.filter(section=section)
    print(f"Total activities in section: {all_activities.count()}")

    with transaction.atomic():
        # Bind ALL students to ALL activities (for consistency)
        all_students = Students.objects.filter(section_enrollments__section=section)
        for activity in all_activities:
            for student in all_students:
                binding, created = ActivityStudentBinding.objects.get_or_create(
                    activity=activity,
                    student=student,
                    defaults={'status': 'assigned'}
                )
                if created:
                    StudentNotification.objects.create(
                        student=student,
                        activity=activity,
                        title="New Activity Added",
                        message=f"You have a new activity: {activity.title}"
                    )

        # Specifically set 'student1' status to 'graded' for all 10 activities
        student1_bindings = ActivityStudentBinding.objects.filter(student=student_record, activity__section=section)
        count = 0
        for binding in student1_bindings:
            binding.status = 'graded'
            # Random high grades for student1
            binding.grade = Decimal(str(random.uniform(88, 98))).quantize(Decimal('0.01'))
            binding.submitted_at = timezone.now() - timezone.timedelta(days=random.randint(1, 10))
            binding.save()
            count += 1
        
        print(f"Updated {count} activities to 'graded' status for {student_username}.")

if __name__ == "__main__":
    setup_student1_performance()
