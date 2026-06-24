import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import ActivityStudentBinding

# Search for "102" in assigned_seats
print("Searching for '102' in assigned_seats...")
# assigned_seats is a JSONField (list of strings)
# We can't easily use __contains for a list in JSONField with SQLite/Postgres across the board without knowing the DB
# So we'll iterate
bindings = ActivityStudentBinding.objects.exclude(assigned_seats=[])
found_count = 0
for b in bindings:
    if any('102' in str(seat) for seat in b.assigned_seats):
        print(f"ID: {b.id}, Student: {b.student.student_number}, Seats: {b.assigned_seats}")
        found_count += 1
        if found_count >= 10:
            break

print(f"Finished searching. Found {found_count} examples.")
