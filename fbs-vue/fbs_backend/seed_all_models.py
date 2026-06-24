import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import (
    Country, Airline, Airport, Aircraft, SeatClass, Route, Flight, Schedule,
    Seat, SeatRequirement, Students, AddOnType, TaxType, AirlineTax,
    AirportFee, PassengerTypeTaxRate, Booking, BookingDetail, PassengerInfo,
    Payment
)
from fbs_instructor.models import Instructor

def seed_data():
    print("🚀 Starting comprehensive data seeding (20 records per model)...")

    # 1. Countries
    countries_data = [
        ('Philippines', 'PH', 'PHP'), ('United States', 'US', 'USD'), ('Japan', 'JP', 'JPY'),
        ('South Korea', 'KR', 'KRW'), ('United Kingdom', 'GB', 'GBP'), ('Australia', 'AU', 'AUD'),
        ('Canada', 'CA', 'CAD'), ('Germany', 'DE', 'EUR'), ('France', 'FR', 'EUR'),
        ('Singapore', 'SG', 'SGD'), ('Thailand', 'TH', 'THB'), ('Vietnam', 'VN', 'VND'),
        ('China', 'CN', 'CNY'), ('Italy', 'IT', 'EUR'), ('Spain', 'ES', 'EUR'),
        ('United Arab Emirates', 'AE', 'AED'), ('Saudi Arabia', 'SA', 'SAR'),
        ('Qatar', 'QA', 'QAR'), ('Switzerland', 'CH', 'CHF'), ('New Zealand', 'NZ', 'NZD')
    ]
    countries = []
    for name, code, currency in countries_data:
        c, _ = Country.objects.get_or_create(name=name, defaults={'code': code, 'currency': currency})
        countries.append(c)
    print(f"✅ Countries: {len(countries)}")

    # 2. Airlines
    airlines_data = [
        ('Philippine Airlines', 'PR'), ('Cebu Pacific', '5J'), ('AirAsia Philippines', 'Z2'),
        ('All Nippon Airways', 'NH'), ('Japan Airlines', 'JL'), ('Korean Air', 'KE'),
        ('Asiana Airlines', 'OZ'), ('Singapore Airlines', 'SQ'), ('Cathay Pacific', 'CX'),
        ('Thai Airways', 'TG'), ('Emirates', 'EK'), ('Qatar Airways', 'QR'),
        ('Etihad Airways', 'EY'), ('Delta Air Lines', 'DL'), ('United Airlines', 'UA'),
        ('American Airlines', 'AA'), ('British Airways', 'BA'), ('Lufthansa', 'LH'),
        ('Air France', 'AF'), ('KLM', 'KL')
    ]
    airlines = []
    for name, code in airlines_data:
        a, _ = Airline.objects.get_or_create(code=code, defaults={'name': name})
        airlines.append(a)
    print(f"✅ Airlines: {len(airlines)}")

    # 3. SeatClasses (3 per airline to ensure mix)
    seat_classes = []
    class_names = ['Economy', 'Premium Economy', 'Business', 'First Class']
    for a in airlines:
        for name in random.sample(class_names, 3):
            multiplier = 1.0 if name == 'Economy' else (1.5 if name == 'Premium Economy' else (2.5 if name == 'Business' else 5.0))
            sc, _ = SeatClass.objects.get_or_create(airline=a, name=name, defaults={'price_multiplier': multiplier})
            seat_classes.append(sc)
    print(f"✅ SeatClasses: {len(seat_classes)}")

    # 4. Airports
    airports_data = [
        ('Ninoy Aquino International', 'MNL', 'Manila', countries[0], 'international'),
        ('Mactan-Cebu International', 'CEB', 'Cebu', countries[0], 'international'),
        ('Francisco Bangoy International', 'DVO', 'Davao', countries[0], 'international'),
        ('Clark International', 'CRK', 'Angeles', countries[0], 'international'),
        ('Laguindingan', 'CGY', 'Cagayan de Oro', countries[0], 'domestic'),
        ('Panglao', 'TAG', 'Bohol', countries[0], 'domestic'),
        ('Puerto Princesa', 'PPS', 'Palawan', countries[0], 'international'),
        ('Narita International', 'NRT', 'Tokyo', countries[2], 'international'),
        ('Haneda', 'HND', 'Tokyo', countries[2], 'international'),
        ('Kansai International', 'KIX', 'Osaka', countries[2], 'international'),
        ('Incheon International', 'ICN', 'Seoul', countries[3], 'international'),
        ('Los Angeles International', 'LAX', 'Los Angeles', countries[1], 'international'),
        ('John F. Kennedy', 'JFK', 'New York', countries[1], 'international'),
        ('Heathrow', 'LHR', 'London', countries[4], 'international'),
        ('Changi', 'SIN', 'Singapore', countries[9], 'international'),
        ('Suvarnabhumi', 'BKK', 'Bangkok', countries[10], 'international'),
        ('Dubai International', 'DXB', 'Dubai', countries[15], 'international'),
        ('Charles de Gaulle', 'CDG', 'Paris', countries[8], 'international'),
        ('Frankfurt', 'FRA', 'Frankfurt', countries[7], 'international'),
        ('Sydney', 'SYD', 'Sydney', countries[5], 'international')
    ]
    airports = []
    for name, code, city, country, atype in airports_data:
        ap, _ = Airport.objects.get_or_create(code=code, defaults={
            'name': name, 'city': city, 'country': country, 'airport_type': atype
        })
        airports.append(ap)
    print(f"✅ Airports: {len(airports)}")

    # 5. Aircrafts
    aircraft_models = ['Boeing 737', 'Airbus A320', 'Airbus A321', 'Boeing 777', 'Airbus A350', 'Boeing 787']
    aircrafts = []
    for i in range(20):
        model = random.choice(aircraft_models)
        capacity = random.randint(150, 350)
        airline = random.choice(airlines)
        ac, _ = Aircraft.objects.get_or_create(model=f"{model} - {i}", airline=airline, defaults={'capacity': capacity})
        aircrafts.append(ac)
    print(f"✅ Aircrafts: {len(aircrafts)}")

    # 6. Routes
    routes = []
    for i in range(20):
        origin = random.choice(airports)
        dest = random.choice([a for a in airports if a != origin])
        base_price = Decimal(random.randint(1500, 15000))
        r, _ = Route.objects.get_or_create(origin_airport=origin, destination_airport=dest, defaults={'base_price': base_price})
        routes.append(r)
    print(f"✅ Routes: {len(routes)}")

    # 7. Flights
    flights = []
    for i in range(20):
        airline = random.choice(airlines)
        route = random.choice(routes)
        ac = random.choice(Aircraft.objects.filter(airline=airline)) if Aircraft.objects.filter(airline=airline).exists() else aircrafts[i]
        f, _ = Flight.objects.get_or_create(flight_number=f"{airline.code}{300+i}", defaults={
            'airline': airline, 'aircraft': ac, 'route': route
        })
        flights.append(f)
    print(f"✅ Flights: {len(flights)}")

    # 8. Schedules (Clear and create 20 fresh)
    Schedule.objects.all().delete()
    schedules = []
    now = timezone.now()
    for i in range(20):
        f = flights[i % len(flights)]
        dep = now + timedelta(days=i+1, hours=random.randint(1, 12))
        arr = dep + timedelta(hours=random.randint(1, 14))
        s = Schedule.objects.create(
            flight=f, departure_time=dep, arrival_time=arr, status='Open', price=f.route.base_price
        )
        schedules.append(s)
    print(f"✅ Schedules: {len(schedules)}")

    # 9. SeatRequirements
    req_data = [
        ('Exit Row', 'exit_row', 500), ('Extra Legroom', 'extra_legroom', 1000), 
        ('Window Seat', 'window_seat', 300), ('Aisle Seat', 'aisle_seat', 300),
        ('Bulkhead', 'bulkhead', 800), ('Bassinet', 'bassinet', 600),
        ('Power Outlet', 'power', 200), ('WiFi', 'wifi', 500),
        ('Quiet Zone', 'quiet', 400), ('Meal Included', 'meal', 700)
    ]
    for name, code, price in req_data:
        SeatRequirement.objects.get_or_create(code=code, defaults={'name': name, 'price': Decimal(price)})
    print(f"✅ SeatRequirements: {len(req_data)}")

    # 10. Students
    for i in range(20):
        email = f"student{i}@example.com"
        if not User.objects.filter(username=f"student{i}").exists():
            user = User.objects.create_user(username=f"student{i}", email=email, password="password123")
            Students.objects.create(user=user, student_number=f"2026-000{i}", first_name=f"Student", last_name=f"Last {i}", email=email)
    print("✅ Students: 20")

    # 11. Instructors
    for i in range(20):
        email = f"instructor{i}@example.com"
        if not Instructor.objects.filter(instructor_id=f"INS-000{i}").exists():
            Instructor.objects.create(instructor_id=f"INS-000{i}", first_name=f"Ins", last_name=f"Last {i}", email=email)
    print("✅ Instructors: 20")

    # 12. AddOnTypes
    addons_data = ['Travel Insurance', 'Extra Baggage (10kg)', 'Extra Baggage (20kg)', 'Meal Upgrade', 'Priority Boarding']
    for name in addons_data:
        AddOnType.objects.get_or_create(name=name, defaults={'description': f'Description for {name}'})
    print(f"✅ AddOnTypes: {len(addons_data)}")

    # 13. TaxTypes
    tax_names = ['VAT', 'Airport Fee', 'Terminal Fee', 'Fuel Surcharge', 'Security Fee']
    tax_types = []
    for name in tax_names:
        tt, _ = TaxType.objects.get_or_create(name=name, defaults={'description': f'Description for {name}'})
        tax_types.append(tt)
    print(f"✅ TaxTypes: {len(tax_types)}")

    # 14. PassengerInfo
    passengers = []
    for i in range(20):
        p = PassengerInfo.objects.create(
            first_name=f"Pass", last_name=f"Last {i}", 
            date_of_birth="1990-01-01", nationality="Filipino", 
            passenger_type=random.choice(['Adult', 'Child', 'Infant'])
        )
        passengers.append(p)
    print(f"✅ PassengerInfo: {len(passengers)}")

    # 15. Bookings & BookingDetails
    for i in range(20):
        user = User.objects.first()
        b = Booking.objects.create(user=user, trip_type='One-way', status='confirmed', total_amount=Decimal(random.randint(5000, 20000)))
        schedule = random.choice(schedules)
        passenger = passengers[i]
        BookingDetail.objects.create(
            booking=b, passenger=passenger, schedule=schedule, 
            booking_date=now, price=schedule.price, status='confirmed'
        )
    print("✅ Bookings & Details: 20")

    print("\n🌟 Comprehensive Data Seeding Completed!")

if __name__ == "__main__":
    seed_data()
