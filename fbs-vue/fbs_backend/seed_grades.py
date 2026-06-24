import os
import django
import random
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import CourseSection, Activity, StudentActivity

# Find the section
section = CourseSection.objects.filter(section_name__icontains='DOMSSSSSSSSS').first()
if not section:
    # Try exact match or code match
    section = CourseSection.objects.filter(section_code__icontains='DOMSSSSSSSSS').first()

if not section:
    print("Section not found.")
    sys.exit()

activities = Activity.objects.filter(section=section)
if not activities.exists():
    print("No activities found for section.")
    sys.exit()

activity = activities.last()

# Ensure we loop over correct students. CourseSection models have a ManyToMany field 'students' usually mapping to CustomUser.
students = section.enrolled_students.all() if hasattr(section, 'enrolled_students') else getattr(section, 'students').all()
print(f"Found {students.count()} students. Activity: {activity.title}")

added = 0
for student in students:
    # Get or create student activity
    # Check what fields are actually available in StudentActivity
    try:
        sa, created = StudentActivity.objects.get_or_create(
            student=student, 
            activity=activity,
        )
    except Exception as e:
        print(f"Failed getting/creating student activity for {student}: {e}")
        continue
    
    if sa.status != 'graded':
        sa.status = 'graded'
        sa.accuracy_score = random.randint(2, 5)
        sa.tech_skill_score = random.randint(2, 5)
        sa.organization_score = random.randint(2, 5)
        sa.completeness_score = random.randint(2, 5)
        sa.professionalism_score = random.randint(2, 5)
        
        # Calculate grade
        total = sa.accuracy_score + sa.tech_skill_score + sa.organization_score + sa.completeness_score + sa.professionalism_score
        sa.computed_grade = (total / 25) * 100
        sa.grade = sa.computed_grade
        
        sa.is_released = True
        sa.is_failed_due_to_time = False
        sa.save()
        added += 1

print(f"Successfully graded {added} students for activity ID {activity.id}.")
