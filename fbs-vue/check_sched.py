from app.models import Schedule
try:
    sched = Schedule.objects.get(id=1851)
    print(f"ID: {sched.id}")
    print(f"Flight: {sched.flight.flight_number}")
    print(f"Departure: {sched.departure_time}")
except Exception as e:
    print(f"Error: {e}")
