
import os
import django
import random
import uuid
from datetime import datetime, timedelta, timezone as dt_timezone
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
    PassengerInfo, Booking, BookingContact, BookingDetail, AddOnType, AddOn,
    TaxType, AirlineTax, AirportFee, PassengerTypeTaxRate, Payment, TrackLog,
    BookingTax, CheckInDetail
)
from fbs_instructor.models import Instructor

fake = Faker()

def get_unique_username(base_name):
    username = base_name.lower().replace(' ', '_')
    if not User.objects.filter(username=username).exists():
        return username
    return f"{username}_{uuid.uuid4().hex[:6]}"

def clear_data():
    print("🧹 Cleaning up existing data (except superusers)...")
    models_to_clear = [
        CheckInDetail, BookingTax, BookingDetail, BookingContact, Booking, Payment,
        Seat, Schedule, Flight, Route, Aircraft, SeatClass, Airline,
        Airport, Country, SeatRequirement, AddOnType, PassengerTypeTaxRate,
        AirportFee, AirlineTax, TaxType, PassengerInfo, Students,
        TrackLog, TravelInsurancePlan, InsuranceBenefit, InsuranceCoverageType, InsuranceProvider,
        MealOption, MealCategory, AssistanceService, BaggageOption, Instructor, AddOn
    ]
    for model in models_to_clear:
        try:
            model.objects.all().delete()
        except Exception as e:
            print(f"  ⚠️ Could not clear {model.__name__}: {e}")

    User.objects.exclude(is_superuser=True).delete()
    print("✅ Cleanup complete.")

def run_seed():
    clear_data()
    print("\n🚀 Starting CALENDAR-BASED Philippine Domestic population (5 per day: Today -> March 31, 2026)...")

    # 1. Countries (50)
    ph, _ = Country.objects.get_or_create(name="Philippines", defaults={'code': "PH", 'currency': "PHP"})
    for _ in range(49):
        c_code = fake.unique.country_code()
        if c_code == "PH": continue
        Country.objects.get_or_create(name=fake.unique.country(), defaults={'code': c_code, 'currency': fake.currency_code()})

    # 2. Users (50)
    users = [User.objects.create_user(username=get_unique_username(fake.first_name()), email=fake.unique.email(), password="password123", first_name=fake.first_name(), last_name=fake.last_name()) for _ in range(50)]

    # 3. Students & Instructors
    for i, user in enumerate(users):
        Students.objects.create(student_number=f"STUD-{2026000 + i}", user=user, first_name=user.first_name, last_name=user.last_name, email=user.email, gender=random.choice(['mr', 'mrs']))
        Instructor.objects.create(instructor_id=f"INST-{3000 + i}", user=user if i % 2 == 0 else None, first_name=fake.first_name(), last_name=fake.last_name(), email=fake.unique.email())

    # 4. Airlines (50)
    ph_airlines_list = [("Philippine Airlines", "PR"), ("Cebu Pacific", "5J"), ("AirAsia Philippines", "Z2"), ("PAL Express", "2P"), ("Cebgo", "DG"), ("SkyJet Airlines", "M8"), ("AirSwift", "T6")]
    airlines = []
    for name, code in ph_airlines_list:
        a, _ = Airline.objects.get_or_create(code=code, defaults={'name': name})
        airlines.append(a)
    for _ in range(50 - len(airlines)):
        a, _ = Airline.objects.get_or_create(code=fake.unique.lexify(text='??').upper(), defaults={'name': f"PH {fake.unique.company()} Air"})
        airlines.append(a)

    # 5. Aircraft (50)
    aircrafts = [Aircraft.objects.create(model=random.choice(["A320", "A321", "B737", "ATR72"]), capacity=random.choice([70, 180, 220]), airline=random.choice(airlines)) for _ in range(50)]

    # 6. Airports (50)
    ph_airports_data = [
        ("MNL", "Ninoy Aquino International", "Manila", 14.5086, 121.0194),
        ("CEB", "Mactan-Cebu International", "Cebu", 10.3075, 123.9794),
        ("DVO", "Francisco Bangoy International", "Davao", 7.1253, 125.6453),
        ("PPS", "Puerto Princesa International", "Palawan", 9.7421, 118.7588),
        ("ILO", "Iloilo International", "Iloilo", 10.8328, 122.4933),
        ("BCD", "Bacolod-Silay", "Bacolod", 10.7767, 123.0133),
        ("CGY", "Laguindingan", "Cagayan de Oro", 8.4153, 124.4697),
        ("ZAM", "Zamboanga International", "Zamboanga", 6.9214, 122.0594),
        ("BXU", "Bancasi", "Butuan", 8.9515, 125.4770),
        ("TAG", "Bohol-Panglao International", "Panglao", 9.6486, 123.8500),
        ("MPH", "Godofredo P. Ramos", "Caticlan", 11.9250, 121.9500),
        ("KLO", "Kalibo International", "Kalibo", 11.5933, 122.3789),
        ("USU", "Francisco B. Reyes", "Busuanga", 12.1214, 120.2000),
        ("TAC", "Daniel Z. Romualdez", "Tacloban", 11.2269, 125.0281),
        ("LAO", "Laoag International", "Laoag", 18.1812, 120.5317),
        ("WNP", "Naga", "Naga", 11.7850, 123.9933),
    ]
    airports = []
    for code, name, city, lat, lng in ph_airports_data:
        a, _ = Airport.objects.get_or_create(code=code, defaults={'name': name, 'city': city, 'country': ph, 'latitude': lat, 'longitude': lng, 'airport_type': 'international'})
        airports.append(a)
    ph_more = [("Vigan", 17.5747, 120.3869), ("Legazpi", 13.1333, 123.7333), ("Dumaguete", 9.3068, 123.3033), ("GenSan", 6.1167, 125.1667), ("Basco", 20.4500, 121.9667), ("Siargao", 9.8500, 126.0333), ("El Nido", 11.2000, 119.4167), ("Tablas", 12.3833, 122.0167), ("Baguio", 16.4000, 120.6000), ("Coron", 12.1167, 120.2000), ("Camiguin", 9.1667, 124.7167), ("Masbate", 12.3667, 123.6333), ("San Jose", 12.3500, 121.0667), ("Virac", 13.5833, 124.2333), ("Marinduque", 13.4431, 121.8344), ("Roxas", 11.5833, 122.7500), ("Catarman", 12.5000, 124.6333), ("Calbayog", 12.0667, 124.6000), ("Ormoc", 11.0000, 124.6167), ("Maasin", 10.1333, 124.8333), ("Surigao", 9.7833, 125.4833), ("Dipolog", 8.5833, 123.3333), ("Pagadian", 7.8283, 123.4411), ("Ozamiz", 8.1333, 123.8333), ("Cotabato", 7.2167, 124.2500), ("Jolo", 6.0500, 121.0000), ("Tawi-Tawi", 5.0333, 119.7833), ("Baler", 15.7500, 121.5500), ("Daet", 14.1167, 122.9500), ("Sorsogon", 12.9667, 124.0000), ("San Jose de Buenavista", 10.7431, 121.9422), ("Cuyo", 10.8500, 121.0167), ("Tuguegarao", 17.6167, 121.7167), ("Cauayan", 16.9333, 121.7667)]
    for i in range(50 - len(airports)):
        city, lat, lng = ph_more[i]
        a, _ = Airport.objects.get_or_create(code=fake.unique.lexify(text='???').upper(), defaults={'name': f"{city} Airport", 'city': city, 'country': ph, 'latitude': lat, 'longitude': lng, 'airport_type': 'domestic'})
        airports.append(a)

    # 7. Routes (100)
    routes = []
    for _ in range(100):
        origin, dest = random.sample(airports, 2)
        r, _ = Route.objects.get_or_create(origin_airport=origin, destination_airport=dest, defaults={'base_price': Decimal(random.randint(800, 4500))})
        routes.append(r)

    # 8. Flights (100)
    flights = [Flight.objects.get_or_create(flight_number=f"{random.choice(airlines).code}{1000+i}", defaults={'airline': random.choice(airlines), 'aircraft': random.choice(aircrafts), 'route': routes[i]})[0] for i in range(100)]

    # 9. Schedules (5 PER DAY: Today -> March 31, 2026)
    print("--- Schedules (5 per day from Today through March 31) ---")
    now = timezone.now()
    start_date = now.date()
    end_date = datetime(2026, 3, 31).date()
    
    total_days = (end_date - start_date).days + 1
    schedules = []
    
    for i in range(total_days):
        current_day = start_date + timedelta(days=i)
        for j in range(5):
            flight = random.choice(flights)
            # Create varied times throughout the day
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            
            # Use datetime.combine for more robust date/time handling
            dep_dt = datetime.combine(current_day, datetime.min.time()).replace(hour=random_hour, minute=random_minute, tzinfo=dt_timezone.utc)
            
            # Special case for Today: Ensure at least 3 flight are ACTIVE NOW for the map
            if i == 0 and j < 3:
                # Active Now: dep should be 30m ago, arr 1h from now
                dep_dt = now - timedelta(minutes=random.randint(20, 60))
                arr_dt = now + timedelta(hours=random.randint(1, 2))
            else:
                arr_dt = dep_dt + timedelta(hours=random.randint(1, 4))
            
            s = Schedule.objects.create(
                flight=flight,
                departure_time=dep_dt,
                arrival_time=arr_dt,
                price=Decimal(random.randint(1500, 8000))
            )
            schedules.append(s)

    # 10. Bookings (50)
    for _ in range(50):
        p = PassengerInfo.objects.create(first_name=fake.first_name(), last_name=fake.last_name(), nationality="Filipino", passenger_type="Adult")
        b = Booking.objects.create(user=random.choice(users), trip_type='one_way', status='Confirmed', total_amount=Decimal(random.randint(2000, 10000)))
        BookingDetail.objects.create(booking=b, passenger=p, schedule=random.choice(schedules), price=Decimal(2000), status='Confirmed')
        Payment.objects.create(booking=b, amount=b.total_amount, method='Credit Card', status='Completed', transaction_id=uuid.uuid4().hex[:10].upper())

    # 11. Assets
    tax_types = [TaxType.objects.get_or_create(name=f"Tax {i}", defaults={'code':f"T{i}", 'category':'government'})[0] for i in range(50)]
    for i in range(50):
        AirportFee.objects.get_or_create(airport=random.choice(airports), tax_type=random.choice(tax_types), defaults={'amount': Decimal(500)})
        AirlineTax.objects.get_or_create(airline=random.choice(airlines), tax_type=random.choice(tax_types), defaults={'amount': Decimal(200)})
        tt = random.choice(tax_types)
        pt = random.choice(['adult', 'child', 'infant'])
        PassengerTypeTaxRate.objects.get_or_create(tax_type=tt, passenger_type=pt, defaults={'amount': Decimal(100)})
        MealOption.objects.create(airline=random.choice(airlines), name=f"PH Meal {i} {uuid.uuid4().hex[:4]}", price=Decimal(250))
        BaggageOption.objects.get_or_create(airline=random.choice(airlines), weight_kg=random.choice([20, 30, 40]), defaults={'price': Decimal(1000)})
        AssistanceService.objects.create(airline=random.choice(airlines), name=f"Assistance {i}")
        AddOnType.objects.get_or_create(name=f"Add-On Type {i}")
        InsuranceProvider.objects.get_or_create(name=f"Insurer {i}", code=f"IN{i}")

    print(f"\n✨ Successfully seeded {len(schedules)} schedules (5 per day)!")
    active = Schedule.objects.filter(departure_time__lte=now, arrival_time__gte=now).count()
    print(f"Total Days: {total_days}")
    print(f"Active Flights (Markers visible right now): {active}")

if __name__ == "__main__":
    run_seed()
