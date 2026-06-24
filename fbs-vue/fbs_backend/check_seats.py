import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Seat

# Check some seats
seats = Seat.objects.all()[:20]
print(f"Total seats: {Seat.objects.count()}")
for s in seats:
    print(f"ID: {s.id}, Number: {s.seat_number}, Class: {s.seat_class.name if s.seat_class else 'N/A'}")

# Search for "102"
numeric_seats = Seat.objects.filter(seat_number='102')
print(f"Seats with number '102': {numeric_seats.count()}")
for s in numeric_seats:
    print(f"ID: {s.id}, Schedule: {s.schedule_id}, Class: {s.seat_class.name if s.seat_class else 'N/A'}")
