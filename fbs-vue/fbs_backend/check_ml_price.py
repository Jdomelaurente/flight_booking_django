import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule
schedules = Schedule.objects.all().order_by('-id')[:10]
for s in schedules:
    print(f"Schedule ID {s.id} | Route {s.flight.route.origin_airport.code}-{s.flight.route.destination_airport.code} | Route Base Price: {s.flight.route.base_price} | ML Base Price: {s.ml_base_price} | Price: {s.price}")
