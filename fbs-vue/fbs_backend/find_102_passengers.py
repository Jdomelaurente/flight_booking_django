import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import ActivityPassenger

# Search for "102" in seat_preference
print("Searching for '102' in seat_preference...")
passengers = ActivityPassenger.objects.filter(seat_preference__icontains='102')
print(f"Found {passengers.count()} passengers with '102' in seat_preference.")

for p in passengers[:10]:
    print(f"ID: {p.id}, Name: {p.first_name} {p.last_name}, Pref: {p.seat_preference}")
