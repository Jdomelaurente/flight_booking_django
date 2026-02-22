import os
import django
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airline, TaxType, AirlineTax, PassengerTypeTaxRate

def seed_taxes():
    # 1. Ensure we have an airline
    airline, _ = Airline.objects.get_or_create(
        code="PR", 
        defaults={"name": "Philippine Airlines", "country": "Philippines"}
    )
    
    # 2. Ensure we have tax types
    tax_types = [
        {"name": "Fuel Surcharge", "code": "YQ", "category": "airline", "description": "Fuel cost recovery"},
        {"name": "Passenger Service Charge", "code": "LI", "category": "airport", "description": "Airport fee"},
        {"name": "Travel Tax", "code": "PH", "category": "government", "description": "PH Government tax"},
    ]
    
    types = []
    for t_data in tax_types:
        t_type, _ = TaxType.objects.get_or_create(code=t_data["code"], defaults=t_data)
        types.append(t_type)
        
    # 3. Create Airline Taxes
    for t_type in types:
        AirlineTax.objects.get_or_create(
            airline=airline,
            tax_type=t_type,
            defaults={"amount": Decimal("1500.00")}
        )
        
    # 4. Create Passenger Type Tax Rates
    passenger_types = ['adult', 'child', 'infant']
    for t_type in types:
        for p_type in passenger_types:
            PassengerTypeTaxRate.objects.get_or_create(
                tax_type=t_type,
                passenger_type=p_type,
                defaults={"amount": Decimal("500.00")}
            )

    print("Successfully seeded tax data.")

if __name__ == "__main__":
    seed_taxes()
