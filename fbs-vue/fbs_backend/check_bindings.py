import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import ActivityStudentBinding

# Check some bindings
bindings = ActivityStudentBinding.objects.exclude(assigned_seats=[])[:10]
print(f"Total bindings with seats: {ActivityStudentBinding.objects.exclude(assigned_seats=[]).count()}")
for b in bindings:
    print(f"ID: {b.id}, Student: {b.student.student_number}, Seats: {b.assigned_seats}")
