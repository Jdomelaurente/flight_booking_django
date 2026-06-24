import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule

print(f"Total schedules: {Schedule.objects.count()}")
print(f"Total flights: {Flight.objects.count()}")
print()
for f in Flight.objects.all().select_related('airline', 'route__origin_airport', 'route__destination_airport'):
    count = Schedule.objects.filter(flight=f).count()
    print(f"  {f.flight_number} | {f.airline.code} | {f.route.origin_airport.code} -> {f.route.destination_airport.code} | base_price={f.route.base_price} | schedules={count}")
