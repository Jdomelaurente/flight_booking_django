
import os
import sys
import django
from decimal import Decimal

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airline, MealCategory, MealOption, AssistanceService, BaggageOption

def seed_addons():
    print("Seeding Add-ons Data...")
    
    # Get or create Meal Categories
    main_course, _ = MealCategory.objects.get_or_create(name='Main Course', defaults={'display_order': 1})
    beverages, _ = MealCategory.objects.get_or_create(name='Beverages', defaults={'display_order': 2})
    light_meals, _ = MealCategory.objects.get_or_create(name='Light Meals', defaults={'display_order': 3})
    
    # Get Airlines
    pr = Airline.objects.filter(code='PR').first()
    ceb = Airline.objects.filter(code='5J').first()
    
    if not pr or not ceb:
        print("Error: Airlines PR or 5J not found. Please run airline seeders first.")
        return

    # --- MEAL OPTIONS ---
    meals = [
        # Philippine Airlines
        {
            'airline': pr, 'name': 'Beef Caldereta with Rice', 'meal_type': 'standard', 'category': main_course,
            'price': 450.00, 'description': 'Tender beef stew in rich tomato sauce with potatoes and carrots.',
            'calories': 650, 'contains': 'Beef, Soy, Tomato', 'allergens': 'Soy'
        },
        {
            'airline': pr, 'name': 'Garlic Herb Chicken', 'meal_type': 'standard', 'category': main_course,
            'price': 420.00, 'description': 'Roasted chicken breast with garlic butter and steamed vegetables.',
            'calories': 550, 'contains': 'Chicken, Dairy', 'allergens': 'Milk'
        },
        {
            'airline': pr, 'name': 'Vegetarian Pasta', 'meal_type': 'vegetarian', 'category': main_course,
            'price': 380.00, 'description': 'Penne pasta with roasted vegetables and marinara sauce.',
            'calories': 480, 'contains': 'Wheat, Tomato', 'allergens': 'Gluten'
        },
        {
            'airline': pr, 'name': 'Filipino Breakfast (Tapsilog)', 'meal_type': 'standard', 'category': light_meals,
            'price': 350.00, 'description': 'Cured beef, garlic rice, and fried egg.',
            'calories': 700, 'contains': 'Beef, Egg, Rice', 'allergens': 'Egg', 'available_for_breakfast': True
        },
        
        # Cebu Pacific
        {
            'airline': ceb, 'name': 'Chicken Adobo on Rice', 'meal_type': 'standard', 'category': main_course,
            'price': 350.00, 'description': 'Classic Filipino chicken adobo served with steamed rice.',
            'calories': 600, 'contains': 'Chicken, Soy', 'allergens': 'Soy'
        },
        {
            'airline': ceb, 'name': 'Beef Pares', 'meal_type': 'standard', 'category': main_course,
            'price': 380.00, 'description': 'Sweet and savory beef stew with garlic rice.',
            'calories': 750, 'contains': 'Beef, Star Anise', 'allergens': 'None'
        },
        {
            'airline': ceb, 'name': 'Egg Mayo Sandwich', 'meal_type': 'vegetarian', 'category': light_meals,
            'price': 180.00, 'description': 'Fresh egg salad on whole wheat bread.',
            'calories': 320, 'contains': 'Egg, Wheat', 'allergens': 'Egg, Gluten'
        }
    ]

    for m in meals:
        obj, created = MealOption.objects.get_or_create(
            airline=m['airline'], 
            name=m['name'],
            defaults={
                'meal_type': m['meal_type'],
                'category': m['category'],
                'price': Decimal(str(m['price'])),
                'description': m.get('description', ''),
                'calories': m.get('calories'),
                'contains': m.get('contains', ''),
                'allergens': m.get('allergens', ''),
                'available_for_breakfast': m.get('available_for_breakfast', False),
                'available_for_lunch': True,
                'available_for_dinner': True
            }
        )
        if created:
            print(f"Created Meal: {m['name']} for {m['airline'].code}")

    # --- ASSISTANCE SERVICES ---
    assistance = [
        # Philippine Airlines
        {
            'airline': pr, 'name': 'Standard Wheelchair (Ramp)', 'service_type': 'wheelchair', 'level': 'standard',
            'price': 0.00, 'is_included': True, 'description': 'Assistance from check-in to aircraft door.'
        },
        {
            'airline': pr, 'name': 'Standard Wheelchair (Cabin)', 'service_type': 'wheelchair', 'level': 'premium',
            'price': 0.00, 'is_included': True, 'description': 'Assistance to seat inside the cabin.'
        },
        {
            'airline': pr, 'name': 'Unaccompanied Minor Service', 'service_type': 'unaccompanied_minor', 'level': 'premium',
            'price': 2500.00, 'is_included': False, 'description': 'Full escort service for minors traveling alone.'
        },
        
        # Cebu Pacific
        {
            'airline': ceb, 'name': 'CEB Wheelchair Assist', 'service_type': 'wheelchair', 'level': 'standard',
            'price': 0.00, 'is_included': True, 'description': 'Standard wheelchair assistance.'
        },
        {
            'airline': ceb, 'name': 'CEB Pet-in-Cabin Handling', 'service_type': 'pet', 'level': 'standard',
            'price': 1500.00, 'is_included': False, 'description': 'Processing fee for pets traveling in cabin.'
        }
    ]

    for a in assistance:
        obj, created = AssistanceService.objects.get_or_create(
            airline=a['airline'],
            name=a['name'],
            defaults={
                'service_type': a['service_type'],
                'level': a['level'],
                'price': Decimal(str(a['price'])),
                'is_included': a['is_included'],
                'description': a.get('description', '')
            }
        )
        if created:
            print(f"Created Assistance: {a['name']} for {a['airline'].code}")

    # --- BAGGAGE OPTIONS ---
    weights = [20, 25, 32, 40]
    baggage_prices = {
        'PR': {20: 800, 25: 1200, 32: 1800, 40: 2500},
        '5J': {20: 600, 25: 950, 32: 1500, 40: 2100}
    }

    for airline in [pr, ceb]:
        for w in weights:
            price = baggage_prices[airline.code][w]
            obj, created = BaggageOption.objects.get_or_create(
                airline=airline,
                weight_kg=w,
                defaults={
                    'name': f"{w}kg Prepaid Baggage",
                    'price': Decimal(str(price)),
                    'is_included': False,
                    'description': f"Prepaid baggage allowance of up to {w} kilograms."
                }
            )
            print(f"Created Baggage: {w}kg for {airline.code}")

    print("Seeding Complete!")

if __name__ == "__main__":
    seed_addons()
