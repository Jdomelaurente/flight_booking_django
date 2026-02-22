
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport

airports_data = {
    'MNL': (14.5086, 121.0194),
    'CEB': (10.3075, 123.9794),
    'DVO': (7.1253, 125.6453),
    'PPS': (9.7421, 118.7588),
    'ILO': (10.8328, 122.4933),
    'BCD': (10.7767, 123.0133),
    'CGY': (8.4153, 124.4697),
    'ZAM': (6.9214, 122.0594),
    'BXU': (8.9515, 125.4770), # Butuan
    'WNP': (11.7850, 123.9933), # Naga
    'TAG': (9.6486, 123.8500), # Tagbilaran/Bohol
    'MPH': (11.9250, 121.9500), # Boracay/Caticlan
    'KLO': (11.5933, 122.3789), # Kalibo
    'USU': (12.1214, 120.2000), # Busuanga/Coron
}

updated_count = 0
for code, (lat, lng) in airports_data.items():
    airport = Airport.objects.filter(code=code).first()
    if airport:
        airport.latitude = lat
        airport.longitude = lng
        airport.save()
        print(f"Updated {code} with {lat}, {lng}")
        updated_count += 1

print(f"Sucessfully updated {updated_count} airports.")
