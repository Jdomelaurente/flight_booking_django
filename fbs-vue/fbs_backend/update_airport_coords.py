import os
import django
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport

def update_airport_coordinates():
    print("📍 Updating Philippine Airport coordinates for the live map...")
    
    # Mapping of Airport Codes to their actual Latitude & Longitude
    coords_map = {
        "MNL": (14.5086, 121.0194),
        "CEB": (10.3075, 123.9794),
        "DVO": (7.1253, 125.6458),
        "CRK": (15.1858, 120.5597),
        "PPS": (9.7333, 118.7589),
        "KLO": (11.6792, 122.3758),
        "ILO": (10.8322, 122.4933),
        "CGY": (8.6122, 124.4484),
        "GES": (6.0580, 125.0961),
        "TAC": (11.2269, 125.0281),
        "TAG": (9.5639, 123.7644),
        "ZAM": (6.9214, 122.0594),
        "LAO": (18.1783, 120.5317),
        "DGT": (9.3339, 123.3011),
        "RXS": (11.5975, 122.7531),
        "SJI": (12.3589, 121.0317),
        "BXU": (8.9511, 125.4786),
        "TUG": (17.6414, 121.7317),
        "SUG": (9.7550, 125.4850),
        "DPL": (8.5997, 123.3447),
    }

    updated_count = 0
    for code, (lat, lng) in coords_map.items():
        try:
            airport = Airport.objects.get(code=code)
            airport.latitude = Decimal(str(lat))
            airport.longitude = Decimal(str(lng))
            airport.save()
            print(f"  ✅ Updated {code}: ({lat}, {lng})")
            updated_count += 1
        except Airport.DoesNotExist:
            print(f"  ⚠️ Airport {code} not found in database.")

    print(f"\n🌟 Successfully updated {updated_count} airports. The live map should now display flights.")

if __name__ == "__main__":
    update_airport_coordinates()
