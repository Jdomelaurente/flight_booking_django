
import os
import sys
import django
from decimal import Decimal

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import PricingConfiguration, SeatClass

print("Creating/Ensuring PricingConfiguration...")
try:
    config = PricingConfiguration.load()
    print(f"Config ID: {config.pk}")
except Exception as e:
    print(f"Failed to load config: {e}")

seat_classes = {
    'Economy': 1.0,
    'Premium Economy': 1.35,
    'Business': 1.8,
    'First Class': 2.4,
    'Comfort': 1.2,
    'Deluxe': 1.6,
    'Executive': 2.0
}

try:
    for name, imp in seat_classes.items():
        # Update existing
        target = Decimal(str(imp))
        updated_count = SeatClass.objects.filter(name__iexact=name).update(price_multiplier=target)
        print(f"Updated {updated_count} {name} seat classes to {imp}")
        
        # If none exist, create a generic one (airline=None)
        if updated_count == 0:
            SeatClass.objects.create(name=name, price_multiplier=target)
            print(f"Created generic {name} seat class")
except Exception as e:
    print(f"Failed to seed seat classes: {e}")

print("Done.")
