import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import Activity, ActivityStudentBinding
from app.models import Booking

activity_id = 37
try:
    activity = Activity.objects.get(id=activity_id)
    print(f"Activity: {activity.title}")
    
    bindings = ActivityStudentBinding.objects.filter(activity=activity)
    print(f"Total bindings: {bindings.count()}")
    
    bookings = Booking.objects.filter(activity=activity)
    print(f"Total bookings for activity: {bookings.count()}")
    
    for b in bookings:
        print(f"Booking ID: {b.id}, User: {b.user.username}, Status: {b.status}")
        for d in b.details.all():
            print(f"  Detail ID: {d.id}, Schedule: {d.schedule_id}")
            if d.schedule:
                print(f"    Flight: {d.schedule.flight.flight_number}, Dep: {d.schedule.departure_time}")
            else:
                print(f"    Warning: Schedule is NULL")

except Exception as e:
    print(f"Error: {e}")
