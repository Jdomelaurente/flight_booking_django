import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import SeatRequirement

requirements = [
    {
        'name': 'Exit Row Seat',
        'code': 'is_exit_row',
        'price': Decimal('150.00'),
        'icon': 'ph ph-exit',
        'description': 'Seat and emergency exit row (additional responsibility)'
    },
    {
        'name': 'Wheelchair Accessible',
        'code': 'is_wheelchair_accessible',
        'price': Decimal('0.00'),
        'icon': 'ph ph-wheelchair',
        'description': 'Priority for passengers with reduced mobility'
    },
    {
        'name': 'Bassinet Position',
        'code': 'has_bassinet',
        'price': Decimal('200.00'),
        'icon': 'ph ph-baby',
        'description': 'For passengers with infants'
    },
    {
        'name': 'Nut Allergy Zone',
        'code': 'has_nut_allergy',
        'price': Decimal('0.00'),
        'icon': 'ph ph-nut',
        'description': 'No nuts to be served in this area'
    },
    {
        'name': 'Unaccompanied Minor Service',
        'code': 'is_unaccompanied_minor',
        'price': Decimal('300.00'),
        'icon': 'ph ph-user-focus',
        'description': 'Special supervision required'
    },
    {
        'name': 'Extra Legroom',
        'code': 'has_extra_legroom',
        'price': Decimal('500.00'),
        'icon': 'ph ph-ruler',
        'description': 'Additional legroom for comfort'
    },
    {
        'name': 'Bulkhead',
        'code': 'is_bulkhead',
        'price': Decimal('400.00'),
        'icon': 'ph ph-wall',
        'description': 'Front row with extra legroom'
    },
    {
        'name': 'Window Seat',
        'code': 'is_window',
        'price': Decimal('100.00'),
        'icon': 'ph ph-airplane-takeoff',
        'description': 'Window view seat'
    },
    {
        'name': 'Aisle Seat',
        'code': 'is_aisle',
        'price': Decimal('120.00'),
        'icon': 'ph ph-walk',
        'description': 'Easy access aisle seat'
    }
]

for req_data in requirements:
    obj, created = SeatRequirement.objects.update_or_create(
        code=req_data['code'],
        defaults=req_data
    )
    if created:
        print(f"Created {obj.name}")
    else:
        print(f"Updated {obj.name}")

print("Seeding complete.")
