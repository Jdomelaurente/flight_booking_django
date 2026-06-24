import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import Section, Activity, ActivityStudentBinding

try:
    section = Section.objects.filter(section_code__icontains='DOMSS').first()
    if not section:
        print("No section DOMSS")
        import sys; sys.exit(0)
    
    activity = Activity.objects.filter(section=section).last()
    
    bindings = ActivityStudentBinding.objects.filter(activity=activity)
    print(f"Updating grades for {bindings.count()} students for activity {activity.title}")
    
    updated = 0
    for binding in bindings:
        binding.status = 'graded'
        
        accuracy = random.randint(3, 5)
        tech = random.randint(3, 5)
        org = random.randint(3, 5)
        comp = random.randint(3, 5)
        prof = random.randint(3, 5)
        
        binding.rubric_breakdown = [
            {'label': 'Accuracy', 'level': accuracy, 'ratio': accuracy/5},
            {'label': 'Technical', 'level': tech, 'ratio': tech/5},
            {'label': 'Organization', 'level': org, 'ratio': org/5},
            {'label': 'Completeness', 'level': comp, 'ratio': comp/5},
            {'label': 'Professionalism', 'level': prof, 'ratio': prof/5}
        ]
        
        total = accuracy + tech + org + comp + prof
        binding.grade = (total / 25) * 100
        binding.is_released = False
        binding.save()
        updated += 1

    print(f"Done updating {updated} grades.")

except Exception as e:
    import traceback
    traceback.print_exc()
