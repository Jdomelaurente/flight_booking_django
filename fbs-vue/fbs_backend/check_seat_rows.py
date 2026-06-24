import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fbs_backend.settings")
django.setup()

from app.models import Seat

# Get a sample of seats and print their row/column properties
seats = Seat.objects.filter(row__isnull=False, column__isnull=False)[:5]
print("Sample Seats with row/col:")
for s in seats:
    print(f"ID: {s.seat_number} -> Row: {s.row}, Col: {s.column} => {s.row}{s.column}")
