import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import SeatRequirement

def seed_requirements():
    requirements = [
        {
            "name": "Wheelchair Assistance",
            "code": "is_wheelchair_accessible",
            "price": Decimal("0.00"),
            "icon": "ph ph-wheelchair",
            "description": "Full wheelchair assistance for PWD or elderly trainees."
        },
        {
            "name": "Medical Oxygen",
            "code": "has_medical_oxygen",
            "price": Decimal("2500.00"),
            "icon": "ph ph-mask-happy",
            "description": "In-flight medical oxygen supply (Certified)."
        },
        {
            "name": "Infant Bassinet",
            "code": "has_bassinet",
            "price": Decimal("500.00"),
            "icon": "ph ph-baby",
            "description": "Secure bassinet for infants on long-haul simulation routes."
        },
        {
            "name": "Extra Legroom",
            "code": "has_extra_legroom",
            "price": Decimal("1200.00"),
            "icon": "ph ph-arrows-out",
            "description": "Seat requirement for extra space during the simulation."
        },
        {
            "name": "Pet in Cabin (Local)",
            "code": "has_pet_in_cabin",
            "price": Decimal("1500.00"),
            "icon": "ph ph-dog",
            "description": "Small pet carrier requirement for domestic simulations."
        },
        {
            "name": "Deaf/Blind Asst",
            "code": "is_deaf_blind",
            "price": Decimal("0.00"),
            "icon": "ph ph-ear-slash",
            "description": "Specialized guidance for sensory-impaired trainees."
        },
        {
            "name": "UMNR Service",
            "code": "is_unaccompanied_minor",
            "price": Decimal("2000.00"),
            "icon": "ph ph-user-focus",
            "description": "Unaccompanied minor supervision service."
        },
        {
            "name": "Large Persona",
            "code": "is_large_persona",
            "price": Decimal("3500.00"),
            "icon": "ph ph-user-plus",
            "description": "Extra seat requirement for physical comfort."
        },
        {
            "name": "Stretchers",
            "code": "has_stretcher",
            "price": Decimal("8000.00"),
            "icon": "ph ph-bed",
            "description": "Stretcher installation for medical transport simulations."
        },
        {
            "name": "Sports Equipment",
            "code": "has_sports_equipment",
            "price": Decimal("1000.00"),
            "icon": "ph ph-basketball",
            "description": "Storage requirement for simulation gear."
        },
    ]

    for req_data in requirements:
        req, created = SeatRequirement.objects.update_or_create(
            code=req_data["code"],
            defaults={
                "name": req_data["name"],
                "price": req_data["price"],
                "icon": req_data["icon"],
                "description": req_data["description"]
            }
        )
        if created:
            print(f"Created requirement: {req.name}")
        else:
            print(f"Updated requirement: {req.name}")

if __name__ == "__main__":
    seed_requirements()
