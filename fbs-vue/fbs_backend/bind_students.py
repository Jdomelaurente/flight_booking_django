import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Students
from fbs_instructor.models import Section, Activity, ActivityStudentBinding, StudentNotification
from django.db import transaction

def bind_new_students():
    section_code = 'ABCD'
    
    try:
        section = Section.objects.get(section_code=section_code)
        print(f"Syncing activities for section: {section.section_name} ({section.section_code})")
    except Section.DoesNotExist:
        print(f"Error: Section with code {section_code} not found.")
        return

    # Get all published activities for this section
    activities = Activity.objects.filter(section=section, status='published')
    
    # Get all students enrolled in this section
    # Using students directly since we want to make sure everyone is bound
    students = Students.objects.filter(section_enrollments__section=section)
    
    print(f"Found {activities.count()} published activities and {students.count()} students.")

    with transaction.atomic():
        binding_count = 0
        notif_count = 0
        
        for activity in activities:
            for student in students:
                # Create binding if it doesn't exist
                binding, created = ActivityStudentBinding.objects.get_or_create(
                    activity=activity,
                    student=student,
                    defaults={'status': 'assigned'}
                )
                
                if created:
                    binding_count += 1
                    # Also create a notification
                    StudentNotification.objects.create(
                        student=student,
                        activity=activity,
                        title="New Activity Assigned",
                        message=f"You have been assigned to: {activity.title}"
                    )
                    notif_count += 1
        
        print(f"Created {binding_count} new bindings and {notif_count} notifications.")

if __name__ == "__main__":
    bind_new_students()
