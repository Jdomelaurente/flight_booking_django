import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule, Seat

def verify():
    sch = Schedule.objects.filter(
        flight__route__origin_airport__code='ILO', 
        flight__route__destination_airport__code='ICN', 
        departure_time__date='2026-04-03'
    ).first()
    
    if sch:
        print(f"Schedule ID: {sch.id}")
        print(f"Airline: {sch.flight.airline.code}")
        hot_seat_count = Seat.objects.filter(schedule=sch, seat_class__name='Hot Seat').count()
        print(f"Hot Seat Count: {hot_seat_count}")
    else:
        print("No schedule found for 2026-04-03 ILO-ICN")

if __name__ == "__main__":
    verify()
