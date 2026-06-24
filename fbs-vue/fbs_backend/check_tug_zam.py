
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight

def check_route():
    tug = Airport.objects.filter(code='TUG').first()
    zam = Airport.objects.filter(code='ZAM').first()
    
    if not tug:
        print("TUG airport not found")
    if not zam:
        print("ZAM airport not found")
        
    if tug and zam:
        route = Route.objects.filter(origin_airport=tug, destination_airport=zam).first()
        if route:
            print(f"Route found: {route}")
            flight = Flight.objects.filter(route=route).first()
            if flight:
                print(f"Flight found: {flight.flight_number}")
            else:
                print("No flight found for this route")
        else:
            print("Route TUG to ZAM not found")

if __name__ == "__main__":
    check_route()
