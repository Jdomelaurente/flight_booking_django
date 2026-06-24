import os
import django
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import (
    SeatRequirement, AddOnType, Airline, MealOption, BaggageOption, 
    AssistanceService, AddOn
)

def seed_philippine_assets():
    print("🇵🇭 Seeding Philippine-based Seat Requirements & Detailed Add-ons...")

    # 1. Seat Requirements (Local context)
    seat_reqs = [
        ("Wheelchair Assistance", "WCHR", 0.00, "ph ph-wheelchair", "Full wheelchair assistance for PWD or elderly trainees."),
        ("Medical Oxygen", "OXYG", 2500.00, "ph ph-first-aid", "In-flight medical oxygen supply (Certified)."),
        ("Infant Bassinet", "BSCT", 500.00, "ph ph-baby", "Secure bassinet for infants on long-haul simulation routes."),
        ("Extra Legroom", "EXLR", 1200.00, "ph ph-arrows-out", "Seat requirement for extra space during the simulation."),
        ("Pet in Cabin (Local)", "PETC", 1500.00, "ph ph-paw-print", "Small pet carrier requirement for domestic simulations."),
        ("Deaf/Blind Asst", "BLND", 0.00, "ph ph-eye-slash", "Specialized guidance for sensory-impaired trainees."),
        ("UMNR Service", "UMNR", 2000.00, "ph ph-user", "Unaccompanied minor supervision service."),
        ("Large Persona", "EXST", 3500.00, "ph ph-user-plus", "Extra seat requirement for physical comfort."),
        ("Stretchers", "STCR", 8000.00, "ph ph-bed", "Stretcher installation for medical transport simulations."),
        ("Sports Equipment", "SPEQ", 1000.00, "ph ph-basketball", "Special handling for diving gear, surfboards, etc.")
    ]

    for name, code, price, icon_name, desc in seat_reqs:
        obj, created = SeatRequirement.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'price': Decimal(str(price)),
                'icon': icon_name,
                'description': desc
            }
        )
        print(f"  {'✅ Created' if created else '🔄 Updated'} Seat Req: {code}")

    # 2. Add-On Types
    addon_types = [
        ("In-Flight Meals", "Signature Filipino meals with steamed rice."),
        ("Prepaid Baggage", "Extra weight allowance for pasalubong."),
        ("Assistance Services", "Special services for senior citizens and PWDs."),
        ("Connectivity", "In-flight WiFi and data packages.")
    ]
    
    type_objs = {}
    for name, desc in addon_types:
        obj, created = AddOnType.objects.update_or_create(
            name=name,
            defaults={'description': desc}
        )
        type_objs[name] = obj
        print(f"  {'✅ Created' if created else '🔄 Updated'} Add-on Type: {name}")

    # 3. Airline-Specific Detailed Add-ons (using PAL and Cebu Pacific as targets if they exist)
    target_airline_codes = ["PR", "5J"] # PAL and Cebu Pacific
    airlines = Airline.objects.filter(code__in=target_airline_codes)
    
    if not airlines.exists():
        # Fallback to first 2 airlines if PR/5J not found
        airlines = Airline.objects.all()[:2]
    
    for airline in airlines:
        print(f"\n✈️ Adding detailed assets for {airline.name}...")
        
        # Meals
        meals = [
            ("Chicken Adobo Meal", "Classic chicken adobo with hard-boiled egg and rice.", 450.00, "halal"),
            ("Beef Tapa Breakfast", "Cured beef with garlic rice and fried egg.", 420.00, "standard"),
            ("Vegetable Pancit", "Stir-fried noodles with local vegetables.", 350.00, "vegetarian")
        ]
        for m_name, m_desc, m_price, m_type in meals:
            meal, _ = MealOption.objects.update_or_create(
                airline=airline, name=m_name,
                defaults={
                    'description': m_desc,
                    'price': Decimal(str(m_price)),
                    'meal_type': m_type
                }
            )
            # Link to AddOn
            AddOn.objects.update_or_create(
                airline=airline, name=m_name,
                defaults={
                    'type': type_objs["In-Flight Meals"],
                    'meal_option': meal,
                    'price': meal.price,
                    'description': m_desc
                }
            )
            print(f"    🍱 Linked Meal: {m_name}")

        # Baggage
        weights = [(20, 850.00), (32, 1400.00)]
        for w, b_price in weights:
            bag, _ = BaggageOption.objects.update_or_create(
                airline=airline, weight_kg=w,
                defaults={
                    'name': f"{w}kg Extra Baggage",
                    'price': Decimal(str(b_price)),
                    'description': f"Add {w}kg to your simulation luggage allowance."
                }
            )
            # Link to AddOn
            AddOn.objects.update_or_create(
                airline=airline, name=f"{w}kg Extra Baggage",
                defaults={
                    'type': type_objs["Prepaid Baggage"],
                    'baggage_option': bag,
                    'price': bag.price,
                    'description': bag.description
                }
            )
            print(f"    🧳 Linked Baggage: {w}kg")

        # Assistance Services
        assists = [
            ("PWD Priority Lane", "wheelchair", "Special assistance from check-in to boarding.", 0.00),
            ("Pet Travel Support", "pet", "Assistance for transporting pets during simulations.", 1500.00)
        ]
        for a_name, a_type, a_desc, a_price in assists:
            assist, _ = AssistanceService.objects.update_or_create(
                airline=airline, name=a_name,
                defaults={
                    'service_type': a_type,
                    'description': a_desc,
                    'price': Decimal(str(a_price)),
                    'is_included': a_price == 0
                }
            )
            # Link to AddOn
            AddOn.objects.update_or_create(
                airline=airline, name=a_name,
                defaults={
                    'type': type_objs["Assistance Services"],
                    'assistance_service': assist,
                    'price': assist.price,
                    'description': a_desc
                }
            )
            print(f"    ♿ Linked Assistance: {a_name}")

    print("\n🌟 Successfully seeded all Philippine-contextualized Assets!")

if __name__ == "__main__":
    seed_philippine_assets()
