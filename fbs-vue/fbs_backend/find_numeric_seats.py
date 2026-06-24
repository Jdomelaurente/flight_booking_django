import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Seat

# Check for numeric seat numbers using regex
print("Searching for numeric seats...")
numeric_seats = Seat.objects.filter(seat_number__regex=r'^[0-9]+$')
count = numeric_seats.count()
print(f"Found {count} numeric seats.")

if count > 0:
    print("First 20 numeric seats:")
    for s in numeric_seats[:20]:
        print(f"ID: {s.id}, Number: {s.seat_number}, Schedule: {s.schedule_id}")
