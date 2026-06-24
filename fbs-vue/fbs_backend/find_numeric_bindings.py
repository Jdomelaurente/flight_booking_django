import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import ActivityStudentBinding

# Search for numeric patterns in assigned_seats
print("Searching for numeric patterns in assigned_seats...")
bindings = ActivityStudentBinding.objects.exclude(assigned_seats=None)
found_count = 0
for b in bindings:
    seats = b.assigned_seats
    if not isinstance(seats, list):
        print(f"ID: {b.id}, Student: {b.student.student_number}, Seats (Non-list): {seats}")
        continue
        
    for seat in seats:
        if str(seat).isdigit():
            print(f"ID: {b.id}, Student: {b.student.student_number}, Numeric Seat: {seat}")
            found_count += 1
            break
            
    if found_count >= 20:
        break

print(f"Finished searching. Found {found_count} examples with numeric seats.")
