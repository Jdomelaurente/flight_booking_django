import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import Section
from fbs_instructor.views import send_bulk_student_schedule_notification
from django.contrib.auth.models import User

def notify_all():
    print("Starting manual enrollment notification blast...")
    
    sections = Section.objects.filter(is_active=True)
    total_sections = sections.count()
    
    if total_sections == 0:
        print("No active sections found.")
        return

    print(f"Found {total_sections} active sections. Sending notifications...")

    for section in sections:
        instructor = section.instructor
        print(f"  - Notifying students in: {section.section_name} ({section.section_code})")
        print(f"    Instructor: {instructor.username}")
        
        success = send_bulk_student_schedule_notification(section, instructor)
        if success:
            print(f"    Notifications sent for {section.section_code}")
        else:
            print(f"    Some issues occurred while notifying {section.section_code}")

    print("\nDone! All enrolled students have been notified.")

if __name__ == "__main__":
    notify_all()
