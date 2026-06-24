import os
import django
import sys

# Set up Django environment
sys.path.append('c:/Users/user/OneDrive/Desktop/Folders/Fbs/fbs-vue/fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight

def reset_stops():
    # Identify domestic flights (origin and destination in Philippines)
    flights = Flight.objects.all()
    count = 0
    
    for f in flights:
        origin_country = f.route.origin_airport.country.name.strip().lower() if f.route.origin_airport.country else ""
        dest_country = f.route.destination_airport.country.name.strip().lower() if f.route.destination_airport.country else ""
        
        if origin_country == 'philippines' and dest_country == 'philippines':
            if f.total_stops > 0 or f.layovers_data:
                print(f"Resetting stops for domestic flight {f.flight_number}: {f.route.origin_airport.code} -> {f.route.destination_airport.code}")
                f.total_stops = 0
                f.layovers_data = []
                f.save()
                count += 1
    
    print(f"Finished! Reset stops for {count} domestic flights.")

if __name__ == "__main__":
    reset_stops()
