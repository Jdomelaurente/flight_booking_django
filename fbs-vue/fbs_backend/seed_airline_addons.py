
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airline, BaggageOption, MealOption, MealCategory, AssistanceService

def seed_addons():
    # 1. Create Meal Categories
    main_course, _ = MealCategory.objects.get_or_create(name='Main Course', defaults={'display_order': 1})
    beverage, _ = MealCategory.objects.get_or_create(name='Beverages', defaults={'display_order': 2})
    light_meal, _ = MealCategory.objects.get_or_create(name='Light Meals', defaults={'display_order': 3})

    # Airline IDs (based on shell check)
    PR_ID = 81
    CEB_ID = 82
    AA_ID = 83

    airlines = Airline.objects.filter(id__in=[PR_ID, CEB_ID, AA_ID])
    airline_map = {a.id: a for a in airlines}

    # Helper to check if airline exists
    for aid in [PR_ID, CEB_ID, AA_ID]:
        if aid not in airline_map:
            print(f"Warning: Airline ID {aid} not found in database.")

    # ---------------------------------------------------------
    # PHILIPPINE AIRLINES (PR)
    # ---------------------------------------------------------
    if PR_ID in airline_map:
        pr = airline_map[PR_ID]
        print(f"Seeding addons for {pr.name}...")
        
        # Baggage
        BaggageOption.objects.get_or_create(airline=pr, weight_kg=10, defaults={'name': '10kg Extra Baggage', 'price': 800.00, 'display_order': 1})
        BaggageOption.objects.get_or_create(airline=pr, weight_kg=20, defaults={'name': '20kg Extra Baggage', 'price': 1400.00, 'display_order': 2})
        BaggageOption.objects.get_or_create(airline=pr, weight_kg=30, defaults={'name': '30kg Extra Baggage', 'price': 2000.00, 'display_order': 3})

        # Meals
        MealOption.objects.get_or_create(airline=pr, name='Filipino Favorite - Chicken Adobo', defaults={
            'description': 'Tender chicken marinated in soy and vinegar, served with garlic rice.',
            'meal_type': 'standard', 'category': main_course, 'price': 450.00, 'display_order': 1
        })
        MealOption.objects.get_or_create(airline=pr, name='Cattleman\'s Roast Beef', defaults={
            'description': 'Slow-roasted beef with mushroom gravy and mashed potatoes.',
            'meal_type': 'standard', 'category': main_course, 'price': 550.00, 'display_order': 2
        })
        MealOption.objects.get_or_create(airline=pr, name='Seafood Pasta with White Wine Sauce', defaults={
            'description': 'Fresh catch from the islands in a light creamy sauce.',
            'meal_type': 'standard', 'category': main_course, 'price': 480.00, 'display_order': 3
        })

        # Assistance
        AssistanceService.objects.get_or_create(airline=pr, name='PAL Wheelchair Assistance', defaults={
            'service_type': 'wheelchair', 'level': 'standard', 'description': 'Full gate-to-aircraft assistance.', 
            'price': 0.00, 'is_included': True, 'display_order': 1
        })
        AssistanceService.objects.get_or_create(airline=pr, name='Mabuhay Lounge Access', defaults={
            'service_type': 'boarding', 'level': 'premium', 'description': 'Exclusive lounge entry at major terminals.', 
            'price': 1200.00, 'is_included': False, 'display_order': 2
        })

    # ---------------------------------------------------------
    # CEBU PACIFIC (5J)
    # ---------------------------------------------------------
    if CEB_ID in airline_map:
        ceb = airline_map[CEB_ID]
        print(f"Seeding addons for {ceb.name}...")
        
        # Baggage
        for w, p in [(20, 650), (24, 850), (28, 1150), (32, 1450)]:
            BaggageOption.objects.get_or_create(airline=ceb, weight_kg=w, defaults={'name': f'{w}kg Prepaid Baggage', 'price': p})

        # Meals (Santan)
        MealOption.objects.get_or_create(airline=ceb, name='Beef Pares with Garlic Rice', defaults={
            'description': 'Classic Filipino beef stew with savory-sweet sauce.',
            'meal_type': 'standard', 'category': main_course, 'price': 350.00, 'display_order': 1
        })
        MealOption.objects.get_or_create(airline=ceb, name='Chicken Sisig Meal', defaults={
            'description': 'Spicy minced chicken with calamansi, topped on rice.',
            'meal_type': 'standard', 'category': main_course, 'price': 350.00, 'display_order': 2
        })
        MealOption.objects.get_or_create(airline=ceb, name='Vegetable Salpicao (V)', defaults={
            'description': 'Sautéed assorted mushrooms with garlic and bell peppers.',
            'meal_type': 'vegetarian', 'category': light_meal, 'price': 280.00, 'display_order': 3
        })

        # Assistance
        AssistanceService.objects.get_or_create(airline=ceb, name='CEB Wheelchair Service', defaults={
            'service_type': 'wheelchair', 'description': 'Assistance for passengers with reduced mobility.', 
            'price': 0.00, 'is_included': True
        })

    # ---------------------------------------------------------
    # AIRASIA (Z2)
    # ---------------------------------------------------------
    if AA_ID in airline_map:
        aa = airline_map[AA_ID]
        print(f"Seeding addons for {aa.name}...")
        
        # Baggage
        for w, p in [(20, 550), (25, 750), (30, 950), (40, 1350)]:
            BaggageOption.objects.get_or_create(airline=aa, weight_kg=w, defaults={'name': f'{w}kg Value Baggage', 'price': p})

        # Meals (Santan)
        MealOption.objects.get_or_create(airline=aa, name='Pak Nasser\'s Nasi Lemak', defaults={
            'description': 'The legendary coconut rice with spicy sambal and rendant.',
            'meal_type': 'standard', 'category': main_course, 'price': 250.00, 'display_order': 1
        })
        MealOption.objects.get_or_create(airline=aa, name='Uncle Chin\'s Chicken Rice', defaults={
            'description': 'Traditional Hainanese style chicken rice.',
            'meal_type': 'standard', 'category': main_course, 'price': 250.00, 'display_order': 2
        })

        # Assistance
        AssistanceService.objects.get_or_create(airline=aa, name='Xpress Boarding Service', defaults={
            'service_type': 'boarding', 'description': 'Skip the line and board first.', 
            'price': 400.00, 'is_included': False
        })
        AssistanceService.objects.get_or_create(airline=aa, name='AirAsia Assistance', defaults={
            'service_type': 'wheelchair', 'description': 'Airport assistance for all zones.', 
            'price': 0.00, 'is_included': True
        })

    print("Seeding complete.")

if __name__ == '__main__':
    seed_addons()
