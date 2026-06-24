
import os
import django
import random
import uuid
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from faker import Faker

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import (
    UserProfile, Students, Country, Airline, SeatClass, Aircraft, Airport, 
    Route, Flight, Schedule, SeatRequirement, Seat, InsuranceProvider, 
    InsuranceBenefit, InsuranceCoverageType, TravelInsurancePlan, 
    MealCategory, MealOption, AssistanceService, BaggageOption, 
    PassengerInfo, Booking, BookingContact, BookingDetail, AddOnType, AddOn
)

fake = Faker()

def get_unique_username(base_name):
    username = base_name.lower().replace(' ', '_')
    if not User.objects.filter(username=username).exists():
        return username
    return f"{username}_{uuid.uuid4().hex[:6]}"

def run():
    print("🚀 Starting Bulk Philippine Data Population (50 records per model)...")
    
    # 0. Cleanup
    print("--- Cleaning up existing data ---")
    BookingDetail.objects.all().delete()
    BookingContact.objects.all().delete()
    Booking.objects.all().delete()
    PassengerInfo.objects.all().delete()
    Schedule.objects.all().delete()
    Flight.objects.all().delete()
    Route.objects.all().delete()
    Aircraft.objects.all().delete()
    SeatClass.objects.all().delete()
    Airline.objects.all().delete()
    Airport.objects.all().delete()
    Students.objects.all().delete()
    UserProfile.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete()
    Country.objects.all().delete()
    InsuranceProvider.objects.all().delete()
    TravelInsurancePlan.objects.all().delete()
    MealOption.objects.all().delete()
    BaggageOption.objects.all().delete()

    # 1. Countries
    print("--- Populating Countries ---")
    fake.unique.clear() # Reset unique proxy
    ph, _ = Country.objects.get_or_create(name="Philippines", defaults={'code': "PH", 'currency': "PHP"})
    countries = [ph]
    
    # Mark 'PH' as used in faker unique
    # We can't easily mark it as used in fake.unique.country_code() directly
    # So we'll just check manually
    
    created_count = 0
    while created_count < 49:
        c_name = fake.unique.country()
        c_code = fake.unique.country_code()
        if c_code == "PH":
            continue
            
        country, created = Country.objects.get_or_create(
            name=c_name, 
            defaults={'code': c_code, 'currency': fake.currency_code()}
        )
        if created:
            countries.append(country)
            created_count += 1

    # 2. Users & UserProfiles
    print("--- Populating Users & Profiles ---")
    users = []
    for i in range(50):
        first = fake.first_name()
        last = fake.last_name()
        username = get_unique_username(f"{first}_{last}")
        email = fake.unique.email()
        user = User.objects.create_user(username=username, email=email, password="password123", first_name=first, last_name=last)
        profile = user.userprofile
        profile.role = random.choice(['student', 'instructor', 'admin'])
        profile.save()
        users.append(user)

    # 3. Students
    print("--- Populating Students ---")
    for i in range(50):
        user = users[i % len(users)]
        Students.objects.get_or_create(
            student_number=f"STUD-{2024000 + i}",
            defaults={
                'user': user,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'gender': random.choice(['mr', 'mrs']),
            }
        )

    # 4. Airlines
    print("--- Populating Airlines ---")
    airlines = []
    ph_airlines = [
        ("Philippine Airlines", "PR"),
        ("Cebu Pacific", "5J"),
        ("AirAsia Philippines", "Z2"),
        ("PAL Express", "2P"),
        ("Cebgo", "DG")
    ]
    for name, code in ph_airlines:
        airline, _ = Airline.objects.get_or_create(code=code, defaults={'name': name})
        airlines.append(airline)
    
    for _ in range(45):
        name = fake.unique.company()
        code = fake.unique.lexify(text='??').upper()
        airline, _ = Airline.objects.get_or_create(code=code, defaults={'name': name})
        airlines.append(airline)

    # 5. Seat Classes
    print("--- Populating Seat Classes ---")
    seat_classes = []
    class_types = [
        ("Economy", 1.0), ("Premium Economy", 1.5), 
        ("Business", 2.5), ("First Class", 4.0)
    ]
    for airline in airlines[:15]: # Spread across some airlines
        for name, mult in class_types:
            sc, _ = SeatClass.objects.get_or_create(
                airline=airline, name=name, 
                defaults={'price_multiplier': Decimal(str(mult)), 'color': fake.hex_color()}
            )
            seat_classes.append(sc)

    # 6. Aircraft
    print("--- Populating Aircraft ---")
    aircrafts = []
    models = ["Airbus A320", "Airbus A321", "Boeing 737", "ATR 72", "Boeing 777"]
    
    # Ensure each of the first 5 airlines has at least 2 aircraft
    for airline in airlines[:5]:
        for _ in range(2):
            ac = Aircraft.objects.create(
                model=random.choice(models),
                capacity=random.choice([70, 150, 180, 220]),
                airline=airline
            )
            aircrafts.append(ac)
            
    # Add more to reach 50 total
    for _ in range(40):
        airline = random.choice(airlines)
        ac = Aircraft.objects.create(
            model=random.choice(models),
            capacity=random.choice([70, 150, 180, 220, 300]),
            airline=airline
        )
        aircrafts.append(ac)

    # 7. Airports (PH Centric)
    print("--- Populating Airports ---")
    ph_airports_data = [
        ("MNL", "Ninoy Aquino International", "Manila", 14.5086, 121.0194, 'international'),
        ("CEB", "Mactan-Cebu International", "Cebu", 10.3075, 123.9794, 'international'),
        ("DVO", "Francisco Bangoy International", "Davao", 7.1253, 125.6453, 'international'),
        ("PPS", "Puerto Princesa International", "Palawan", 9.7421, 118.7588, 'international'),
        ("ILO", "Iloilo International", "Iloilo", 10.8328, 122.4933, 'international'),
        ("BCD", "Bacolod-Silay", "Bacolod", 10.7767, 123.0133, 'domestic'),
        ("CGY", "Laguindingan", "Cagayan de Oro", 8.4153, 124.4697, 'domestic'),
        ("ZAM", "Zamboanga International", "Zamboanga", 6.9214, 122.0594, 'international'),
        ("BXU", "Bancasi", "Butuan", 8.9515, 125.4770, 'domestic'),
        ("TAG", "Bohol-Panglao International", "Panglao", 9.6486, 123.8500, 'international'),
        ("MPH", "Godofredo P. Ramos", "Caticlan", 11.9250, 121.9500, 'domestic'),
        ("KLO", "Kalibo International", "Kalibo", 11.5933, 122.3789, 'international'),
        ("USU", "Francisco B. Reyes", "Busuanga", 12.1214, 120.2000, 'domestic'),
        ("TAC", "Daniel Z. Romualdez", "Tacloban", 11.2269, 125.0281, 'domestic'),
        ("LAO", "Laoag International", "Laoag", 18.1812, 120.5317, 'international'),
    ]
    airports = []
    for code, name, city, lat, lng, a_type in ph_airports_data:
        airport, _ = Airport.objects.get_or_create(
            code=code, 
            defaults={
                'name': name, 'city': city, 'country': ph, 
                'latitude': lat, 'longitude': lng, 'airport_type': a_type
            }
        )
        airports.append(airport)
    
    # Add more to reach 50
    for _ in range(35):
        code = fake.unique.lexify(text='???').upper()
        airport, _ = Airport.objects.get_or_create(
            code=code,
            defaults={
                'name': f"{fake.city()} Airport", 'city': fake.city(), 'country': random.choice(countries),
                'latitude': fake.latitude(), 'longitude': fake.longitude(), 
                'airport_type': random.choice(['domestic', 'international'])
            }
        )
        airports.append(airport)

    # 8. Routes
    print("--- Populating Routes ---")
    routes = []
    for _ in range(50):
        origin, dest = random.sample([a for a in airports if a.country == ph], 2)
        route, _ = Route.objects.get_or_create(
            origin_airport=origin, destination_airport=dest,
            defaults={'base_price': Decimal(random.randint(500, 3000))}
        )
        routes.append(route)

    # 9. Flights
    print("--- Populating Flights ---")
    flights = []
    for i in range(50):
        airline = random.choice(airlines[:5])
        route = random.choice(routes)
        # Safe selection of aircraft
        airline_acs = [a for a in aircrafts if a.airline == airline]
        if not airline_acs:
            ac = random.choice(aircrafts)
        else:
            ac = random.choice(airline_acs)
            
        flight, _ = Flight.objects.get_or_create(
            flight_number=f"{airline.code}{100 + i}",
            defaults={'airline': airline, 'aircraft': ac, 'route': route}
        )
        flights.append(flight)

    # 10. Schedules
    print("--- Populating Schedules ---")
    schedules = []
    now = timezone.now()
    for i in range(50):
        flight = flights[i]
        dep = now + timedelta(days=random.randint(-5, 30), hours=random.randint(0, 23))
        arr = dep + timedelta(hours=random.randint(1, 4))
        sched = Schedule.objects.create(
            flight=flight, departure_time=dep, arrival_time=arr,
            price=Decimal(random.randint(1500, 10000)),
            status=random.choice(['Open', 'Closed', 'On Flight', 'Arrived'])
        )
        schedules.append(sched)

    # 11. Add-On Types & Add-Ons
    print("--- Populating Add-Ons ---")
    addon_types_data = ["Meal", "Baggage", "Insurance", "Assistance", "Priority Boarding"]
    addon_types = []
    for name in addon_types_data:
        at, _ = AddOnType.objects.get_or_create(name=name)
        addon_types.append(at)
    
    addons = []
    for i in range(50):
        at = random.choice(addon_types)
        airline = random.choice(airlines[:5])
        ao = AddOn.objects.create(
            airline=airline, type=at, name=f"{at.name} Option {i}",
            price=Decimal(random.randint(200, 1500))
        )
        addons.append(ao)

    # 12. Insurance
    print("--- Populating Insurance ---")
    benefits = []
    for _ in range(10):
        b, _ = InsuranceBenefit.objects.get_or_create(name=fake.unique.word().capitalize() + " Coverage")
        benefits.append(b)
    
    providers = []
    for _ in range(5):
        p, _ = InsuranceProvider.objects.get_or_create(name=fake.unique.company(), code=fake.unique.lexify(text='????').upper())
        providers.append(p)
        
    for i in range(50):
        p = random.choice(providers)
        plan, _ = TravelInsurancePlan.objects.get_or_create(
            provider=p, name=f"{p.name} {fake.unique.word().capitalize()} {i}",
            defaults={
                'retail_price': Decimal(random.randint(300, 2000)), 
                'wholesale_price': Decimal(random.randint(200, 1500))
            }
        )
        plan.benefits.add(*random.sample(benefits, min(3, len(benefits))))

    # 13. Passengers, Bookings & Details
    print("--- Populating Passengers & Bookings ---")
    for i in range(50):
        p = PassengerInfo.objects.create(
            first_name=fake.first_name(), last_name=fake.last_name(),
            title=random.choice(['MR', 'MRS', 'MS']), nationality="Filipino",
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80)
        )
        
        user = random.choice(users)
        booking = Booking.objects.create(
            user=user, trip_type=random.choice(['one_way', 'round_trip']),
            status=random.choice(['Pending', 'Confirmed', 'Cancelled']),
            total_amount=Decimal('0.00')
        )
        
        sched = random.choice(schedules)
        detail = BookingDetail.objects.create(
            booking=booking, passenger=p, schedule=sched,
            price=sched.price, tax_amount=sched.price * Decimal('0.12')
        )
        booking.total_amount = detail.price + detail.tax_amount
        booking.save()

    print("--- Populating Meals & Baggage ---")
    meal_cats = []
    for name in ["Breakfast", "Lunch", "Dinner", "Snacks"]:
        mc, _ = MealCategory.objects.get_or_create(name=name)
        meal_cats.append(mc)
        
    for i in range(50):
        airline = random.choice(airlines[:5])
        MealOption.objects.get_or_create(
            airline=airline, name=f"{airline.code} Meal {i}",
            defaults={'category': random.choice(meal_cats), 'price': Decimal(random.randint(150, 600))}
        )
        
        BaggageOption.objects.get_or_create(
            airline=airline, weight_kg=random.choice([5, 10, 15, 20, 25, 30, 32, 40]),
            defaults={'price': Decimal(random.randint(500, 2000))}
        )

    print("✨ Successfully completed bulk population!")
    print(f"Summary:")
    print(f"- Users/Profiles: {User.objects.count()}")
    print(f"- Students: {Students.objects.count()}")
    print(f"- Countries: {Country.objects.count()}")
    print(f"- Airlines: {Airline.objects.count()}")
    print(f"- Airports: {Airport.objects.count()}")
    print(f"- Aircraft: {Aircraft.objects.count()}")
    print(f"- Routes: {Route.objects.count()}")
    print(f"- Flights: {Flight.objects.count()}")
    print(f"- Schedules: {Schedule.objects.count()}")
    print(f"- Bookings: {Booking.objects.count()}")

if __name__ == "__main__":
    run()
