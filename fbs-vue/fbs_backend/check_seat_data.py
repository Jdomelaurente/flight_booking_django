import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Seat, SeatClass, Schedule

print(f"Total Seats: {Seat.objects.count()}")
print(f"Seat Classes: {list(SeatClass.objects.values_list('name', flat=True))}")

# Check seats by class
for sc in SeatClass.objects.all():
    count = Seat.objects.filter(seat_class=sc).count()
    examples = list(Seat.objects.filter(seat_class=sc).values_list('seat_number', flat=True)[:5])
    print(f"Class: {sc.name} | Total Seats: {count} | Examples: {examples}")

# Check schedules
print(f"Total Schedules: {Schedule.objects.count()}")
