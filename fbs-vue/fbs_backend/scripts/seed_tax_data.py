
import os
import sys
import django
from decimal import Decimal

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airline, Airport, TaxType, AirportFee, AirlineTax, PassengerTypeTaxRate

def seed_taxes():
    print("--- Seeding Tax and Fee data ---")

    # 1. Create Tax Types
    tax_types_data = [
        {
            'name': 'Passenger Service Charge (Terminal Fee)',
            'code': 'LI',
            'category': 'airport',
            'description': 'Fee collected for the use of airport terminal facilities.',
            'base_amount': 200.00
        },
        {
            'name': 'Fuel Surcharge',
            'code': 'YQ',
            'category': 'airline',
            'description': 'Variable surcharge used by airlines to offset fluctuations in fuel prices.',
            'base_amount': 350.00
        },
        {
            'name': 'Aviation Security Fee',
            'code': 'AE',
            'category': 'airport',
            'description': 'Fee for airport security operations and screening.',
            'base_amount': 15.00
        },
        {
            'name': 'Insurance Surcharge',
            'code': 'YI',
            'category': 'airline',
            'description': 'Surcharge for passenger liability and aircraft insurance.',
            'base_amount': 50.00
        },
        {
            'name': 'PH Travel Tax (TIEZA)',
            'code': 'PH-TAX',
            'category': 'government',
            'description': 'Tax imposed by the Philippine government on individuals departing from the country.',
            'base_amount': 1620.00
        }
    ]

    tax_types = {}
    for data in tax_types_data:
        try:
            tt = TaxType.objects.get(code=data['code'])
            tt.name = data['name']
            tt.category = data['category']
            tt.description = data['description']
            tt.base_amount = data['base_amount']
            tt.save()
            print(f"  Updated Tax Type: {tt.name}")
        except TaxType.DoesNotExist:
            try:
                tt = TaxType.objects.get(name=data['name'])
                tt.code = data['code']
                tt.category = data['category']
                tt.description = data['description']
                tt.base_amount = data['base_amount']
                tt.save()
                print(f"  Updated Tax Type (by name): {tt.name}")
            except TaxType.DoesNotExist:
                tt = TaxType.objects.create(
                    code=data['code'],
                    name=data['name'],
                    category=data['category'],
                    description=data['description'],
                    base_amount=data['base_amount'],
                    is_active=True
                )
                print(f"  Created Tax Type: {tt.name}")
        tax_types[data['code']] = tt

    # 2. Seed Airport Fees for major airports
    major_airports = ['MNL', 'CEB', 'DVO', 'CRK']
    airport_fees_data = [
        ('MNL', 'LI', 550.00),
        ('MNL', 'AE', 15.00),
        ('CEB', 'LI', 850.00),
        ('CEB', 'AE', 15.00),
        ('DVO', 'LI', 200.00),
        ('DVO', 'AE', 15.00),
        ('CRK', 'LI', 600.00),
        ('CRK', 'AE', 15.00),
    ]

    for apt_code, tt_code, amt in airport_fees_data:
        try:
            airport = Airport.objects.get(code=apt_code)
            tax_type = tax_types[tt_code]
            AirportFee.objects.update_or_create(
                airport=airport,
                tax_type=tax_type,
                defaults={'amount': amt}
            )
            print(f"  Processed Airport Fee: {apt_code} - {tax_type.name} (P{amt})")
        except Airport.DoesNotExist:
            print(f"  Warning: Airport {apt_code} not found, skipping fee.")
        except Exception as e:
            print(f"  Error seeding airport fee: {e}")

    # 3. Seed Airline Taxes for major airlines
    airline_taxes_data = [
        ('PR', 'YQ', 550.00),
        ('PR', 'YI', 85.00),
        ('5J', 'YQ', 450.00),
        ('5J', 'YI', 45.00),
        ('Z2', 'YQ', 380.00),
        ('Z2', 'YI', 35.00),
    ]

    for al_code, tt_code, amt in airline_taxes_data:
        try:
            airline = Airline.objects.get(code=al_code)
            tax_type = tax_types[tt_code]
            AirlineTax.objects.update_or_create(
                airline=airline,
                tax_type=tax_type,
                defaults={'amount': amt}
            )
            print(f"  Processed Airline Tax: {al_code} - {tax_type.name} (P{amt})")
        except Airline.DoesNotExist:
            print(f"  Warning: Airline {al_code} not found, skipping tax.")
        except Exception as e:
            print(f"  Error seeding airline tax: {e}")

    # 4. Seed Travel Tax Rates (PassengerTypeTaxRate)
    travel_tax_rates = [
        ('PH-TAX', 'adult', 1620.00),
        ('PH-TAX', 'child', 810.00),
        ('PH-TAX', 'infant', 300.00),
    ]

    for tt_code, p_type, amt in travel_tax_rates:
        try:
            tax_type = tax_types[tt_code]
            PassengerTypeTaxRate.objects.update_or_create(
                tax_type=tax_type,
                passenger_type=p_type,
                defaults={'amount': amt}
            )
            print(f"  Processed Travel Tax Rate: {p_type} - {tax_type.name} (P{amt})")
        except Exception as e:
            print(f"  Error seeding travel tax rate: {e}")

    print("SUCCESS: Tax data seeding completed!")

if __name__ == "__main__":
    seed_taxes()
