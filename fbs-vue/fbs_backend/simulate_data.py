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

def simulate_submissions():
    section_code = 'ABCD'
    
    try:
        section = Section.objects.get(section_code=section_code)
        print(f"Simulating submissions for section: {section.section_name}")
    except Section.DoesNotExist:
        print(f"Error: Section with code {section_code} not found.")
        return

    # Get published activities
    activities = Activity.objects.filter(section=section, status='published')
    
    # Get bindings for these activities
    bindings = ActivityStudentBinding.objects.filter(activity__in=activities)
    
    print(f"Found {bindings.count()} student bindings for {activities.count()} activities.")

    with transaction.atomic():
        count = 0
        for binding in bindings:
            # Only simulate for about 70% of students to make it look real
            if random.random() > 0.3:
                # Set status to graded
                binding.status = 'graded'
                # Random grade between 75 and 100
                binding.grade = Decimal(str(random.uniform(75, 100))).quantize(Decimal('0.01'))
                binding.submitted_at = timezone.now() - timezone.timedelta(days=random.randint(0, 5))
                binding.save()
                count += 1
        
        print(f"Simulated {count} graded submissions.")

if __name__ == "__main__":
    simulate_submissions()
