from app.models import Schedule, Seat, SeatClass
from django.db.models import Q
import sys

try:
    schedule = Schedule.objects.get(id=1443)
    print(f"Repairing schedule {schedule.id}...")
    
    deleted_count = Seat.objects.filter(schedule=schedule).count()
    Seat.objects.filter(schedule=schedule).delete()
    print(f"Deleted {deleted_count} seats.")

    seat_classes = {
        'First Class': SeatClass.objects.filter(name__iexact='First Class').first(),
        'Business': SeatClass.objects.filter(name__iexact='Business').first(),
        'Economy': SeatClass.objects.filter(name__iexact='Economy').first(),
    }

    created_count = 0
    # A321 Layout approx 180 seats
    # First Class (Rows 1-3)
    for row in range(1, 4):
        for col in ['A', 'C', 'D', 'F']:
            Seat.objects.create(
                schedule=schedule, seat_number=f"{row}{col}",
                seat_class=seat_classes['First Class'], row=row, column=col,
                is_available=True
            )
            created_count += 1
            
    # Business Class (Rows 4-8)
    for row in range(4, 9):
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            Seat.objects.create(
                schedule=schedule, seat_number=f"{row}{col}",
                seat_class=seat_classes['Business'], row=row, column=col,
                is_available=True
            )
            created_count += 1
            
    # Economy Class (Rows 9-31) -> 23 rows * 6 = 138 + 12 + 30 = 180
    for row in range(9, 32):
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            Seat.objects.create(
                schedule=schedule, seat_number=f"{row}{col}",
                seat_class=seat_classes['Economy'], row=row, column=col,
                is_available=True
            )
            created_count += 1
    
    print(f"Created {created_count} new seats.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
