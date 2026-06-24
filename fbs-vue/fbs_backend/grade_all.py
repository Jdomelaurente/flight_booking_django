import os
import django
import random
from decimal import Decimal
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import Section, Activity, ActivityStudentBinding
from django.db import transaction

def grade_all_students_activities():
    section_code = 'ABCD'
    
    try:
        section = Section.objects.get(section_code=section_code)
        print(f"Forcing all activities to 'graded' status for section: {section.section_name} ({section.section_code})")
    except Section.DoesNotExist:
        print(f"Error: Section with code {section_code} not found.")
        return

    # Ensure all activities are published and grades released
    Activity.objects.filter(section=section).update(status='published', grades_released=True)

    # Get all bindings for this section's activities
    bindings = ActivityStudentBinding.objects.filter(activity__section=section)
    
    print(f"Found {bindings.count()} total student bindings to process.")

    with transaction.atomic():
        count = 0
        for binding in bindings:
            # Set status to graded
            binding.status = 'graded'
            # Random grade between 75 and 100 if not already graded
            # If already graded, we can leave it or update it. I'll update it to ensure uniformity.
            binding.grade = Decimal(str(random.uniform(75, 100))).quantize(Decimal('0.01'))
            
            if not binding.submitted_at:
                binding.submitted_at = timezone.now() - timezone.timedelta(days=random.randint(1, 15))
            
            binding.save()
            count += 1
        
        print(f"Successfully marked {count} bindings as 'graded'.")

if __name__ == "__main__":
    grade_all_students_activities()
