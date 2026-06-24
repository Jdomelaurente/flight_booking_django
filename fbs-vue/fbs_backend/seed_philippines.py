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
    Payment, TrackLog, BookingTax, CheckInDetail, UserProfile,
    InsuranceProvider, InsuranceBenefit, InsuranceCoverageType, TravelInsurancePlan
)
from fbs_instructor.models import Instructor

def clear_data():
    print("🧹 Cleaning up existing data (except admin user and profiles)...")
    models_to_clear = [
        CheckInDetail, BookingTax, BookingDetail, Booking, Payment,
        Seat, Schedule, Flight, Route, Aircraft, SeatClass, Airline,
        Airport, Country, SeatRequirement, AddOnType, PassengerTypeTaxRate,
        AirportFee, AirlineTax, TaxType, PassengerInfo, Students,
        TrackLog, TravelInsurancePlan, InsuranceBenefit, InsuranceCoverageType, InsuranceProvider
    ]
    for model in models_to_clear:
        try:
            model.objects.all().delete()
        except Exception as e:
            print(f"  ⚠️ Could not clear {model.__name__}: {e}")

    try:
        Instructor.objects.all().delete()
    except: pass
    
    # Preserve admin
    User.objects.exclude(username='admin').delete()
    print("✅ Cleanup complete.")

def generate_seats(schedule):
    aircraft = schedule.flight.aircraft
    layout = aircraft.get_layout_config()
    seat_classes_config = layout.get('seat_classes', [])
    
    if not seat_classes_config:
        sc = SeatClass.objects.filter(airline=aircraft.airline).first()
        if not sc: return
        for r in range(1, 11):
            for c in ['A', 'B', 'C', 'D']:
                Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=f"{r}{c}",
                    defaults={'seat_class': sc, 'row': r, 'column': c, 'is_available': True}
                )
        return
        
    for sc_config in seat_classes_config:
        class_id = sc_config.get('class_id')
        rows = sc_config.get('rows', 0)
        columns = sc_config.get('columns', 0)
        start_row = sc_config.get('start_row', 1)
        
        try:
            seat_class = SeatClass.objects.get(id=class_id)
        except SeatClass.DoesNotExist:
            continue
            
        for r in range(rows):
            row_num = start_row + r
            for c in range(columns):
                col_label = chr(65 + c)
                Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=f"{row_num}{col_label}",
                    defaults={'seat_class': seat_class, 'row': row_num, 'column': col_label, 'is_available': True}
                )

def seed_data():
    clear_data()
    print("\n🇵🇭 Seeding Philippines-based Data (20 records per model)...")

    # 1. Countries (PH and neighbors)
    neighbor_names = [
        "Philippines", "Singapore", "Japan", "South Korea", "Vietnam", 
        "Thailand", "Malaysia", "Indonesia", "Taiwan", "Hong Kong",
        "China", "Australia", "New Zealand", "United States", "Canada",
        "United Arab Emirates", "Saudi Arabia", "Qatar", "Kuwait", "Oman"
    ]
    neighbor_codes = ["PH", "SG", "JP", "KR", "VN", "TH", "MY", "ID", "TW", "HK", "CN", "AU", "NZ", "US", "CA", "AE", "SA", "QA", "KW", "OM"]
    countries = []
    for i in range(20):
        c = Country.objects.create(
            name=neighbor_names[i], 
            code=neighbor_codes[i], 
            currency='PHP' if neighbor_codes[i] == 'PH' else 'USD'
        )
        countries.append(c)
    ph_country = countries[0]
    print(f"✅ Countries: {len(countries)}")

    # 2. Airlines (PH Local)
    ph_airlines_list = [
        ("Philippine Airlines", "PR"), ("Cebu Pacific", "5J"), ("AirAsia Philippines", "Z2"), 
        ("PAL Express", "2P"), ("Cebgo", "DG"), ("SkyJet Airlines", "M8"), 
        ("Sunlight Air", "2S"), ("AirSwift", "T6"), ("Royal Air Philippines", "RW"), 
        ("Pan Pacific Airlines", "8Y"), ("South East Asian Airlines", "XO"),
        ("Island Transvoyager", "ITI"), ("Northsky Air", "NS"), ("Asian Aerospace", "AA"),
        ("Lionair", "LNR"), ("Pacificair", "PAC"), ("Aero-Phil", "APL"),
        ("Philippine Cargo", "PCG"), ("Mactan Air", "MAI"), ("Davao Wings", "DWG")
    ]
    airlines = []
    for name, code in ph_airlines_list:
        a = Airline.objects.create(name=name, code=code)
        airlines.append(a)
    print(f"✅ Airlines: {len(airlines)}")

    # 3. SeatClasses
    seat_classes = []
    for a in airlines:
        sc1 = SeatClass.objects.create(airline=a, name='Economy Class', price_multiplier=Decimal('1.0'), color='#3b82f6')
        sc2 = SeatClass.objects.create(airline=a, name='Premium Economy', price_multiplier=Decimal('1.5'), color='#8b5cf6')
        sc3 = SeatClass.objects.create(airline=a, name='Business Class', price_multiplier=Decimal('2.5'), color='#fe3787')
        seat_classes.extend([sc1, sc2, sc3])
    print(f"✅ SeatClasses: {len(seat_classes)}")

    # 4. Airports (PH Cities with Coordinates)
    ph_airports_list = [
        ("Ninoy Aquino International Airport", "MNL", "Manila", 14.5086, 121.0194),
        ("Mactan-Cebu International Airport", "CEB", "Cebu", 10.3075, 123.9794),
        ("Francisco Bangoy International Airport", "DVO", "Davao", 7.1253, 125.6458),
        ("Clark International Airport", "CRK", "Pampanga", 15.1858, 120.5597),
        ("Puerto Princesa Airport", "PPS", "Palawan", 9.7333, 118.7589),
        ("Kalibo International Airport", "KLO", "Aklan", 11.6792, 122.3758),
        ("Iloilo International Airport", "ILO", "Iloilo", 10.8322, 122.4933),
        ("Laguindingan Airport", "CGY", "Cagayan de Oro", 8.6122, 124.4484),
        ("General Santos International Airport", "GES", "General Santos", 6.0580, 125.0961),
        ("Daniel Z. Romualdez Airport", "TAC", "Tacloban", 11.2269, 125.0281),
        ("Bohol-Panglao International Airport", "TAG", "Panglao", 9.5639, 123.7644),
        ("Zamboanga International Airport", "ZAM", "Zamboanga", 6.9214, 122.0594),
        ("Laoag International Airport", "LAO", "Laoag", 18.1783, 120.5317),
        ("Sibulan Airport", "DGT", "Dumaguete", 9.3339, 123.3011),
        ("Roxas Airport", "RXS", "Roxas City", 11.5975, 122.7531),
        ("San Jose Airport", "SJI", "San Jose", 12.3589, 121.0317),
        ("Butuan Airport", "BXU", "Butuan", 8.9511, 125.4786),
        ("Tuguegarao Airport", "TUG", "Tuguegarao", 17.6414, 121.7317),
        ("Surigao Airport", "SUG", "Surigao", 9.7550, 125.4850),
        ("Dipolog Airport", "DPL", "Dipolog", 8.5997, 123.3447)
    ]
    airports = []
    for i, (name, code, city, lat, lng) in enumerate(ph_airports_list):
        ap = Airport.objects.create(
            name=name, code=code, city=city,
            latitude=Decimal(str(lat)), longitude=Decimal(str(lng)),
            country=ph_country, airport_type='international' if i < 10 else 'domestic'
        )
        airports.append(ap)
    print(f"✅ Airports: {len(airports)}")

    # 5. Aircrafts
    aircraft_models = [
        "Airbus A321neo", "Airbus A320ceon", "Airbus A330-300", "Airbus A350-900",
        "Boeing 777-300ER", "ATR 72-600", "Bombardier Q400", "Airbus A321-200",
        "Airbus A320-200", "Boeing 737-800", "Airbus A330-900", "ATR 72-500",
        "Cessna 208 Caravan", "British Aerospace 146", "Beechcraft King Air",
        "Fokker 50", "Embraer 190", "Dornier 328", "Pipistrel Alpha", "A321LR"
    ]
    aircrafts = []
    for i in range(20):
        ac = Aircraft.objects.create(
            model=aircraft_models[i], 
            capacity=random.choice([180, 230, 300, 78, 12, 120]), 
            airline=airlines[i % len(airlines)]
        )
        aircrafts.append(ac)
    print(f"✅ Aircrafts: {len(aircrafts)}")

    # 6. Routes (PH Inter-island)
    routes = []
    for i in range(20):
        origin = airports[i]
        dest = airports[(i + 1) % 20]
        r = Route.objects.create(
            origin_airport=origin, 
            destination_airport=dest,
            base_price=Decimal(random.randint(1500, 8000))
        )
        routes.append(r)
    print(f"✅ Routes: {len(routes)}")

    # 7. Flights
    flights = []
    for i in range(20):
        f = Flight.objects.create(
            flight_number=f"{airlines[i].code}{1000 + i}", 
            airline=airlines[i],
            aircraft=aircrafts[i], 
            route=routes[i]
        )
        flights.append(f)
    print(f"✅ Flights: {len(flights)}")

    # 8. Schedules (Mix of Active and Open)
    schedules = []
    now = timezone.now()
    for i in range(20):
        # First 10 are active "On Flight"
        if i < 10:
            status = 'On Flight'
            dep = now - timedelta(minutes=random.randint(20, 90))
            arr = now + timedelta(minutes=random.randint(30, 120))
        else:
            status = 'Open'
            dep = now + timedelta(days=i-9, hours=random.randint(5, 20))
            arr = dep + timedelta(hours=2)

        s = Schedule.objects.create(
            flight=flights[i], 
            departure_time=dep,
            arrival_time=arr, 
            status=status,
            price=flights[i].route.base_price
        )
        generate_seats(s)
        schedules.append(s)
    print(f"✅ Schedules & Seats: 20 (10 Active 'On Flight')")

    # 9. TaxTypes
    tax_names = ["VAT", "PH Travel Tax", "Terminal Fee", "Fuel Surcharge", "Security Fee", "Passenger Service Charge", "Insurance Fee", "Admin Fee", "Check-in Fee", "Airport Tax"]
    tax_types = []
    for i in range(20):
        tt = TaxType.objects.create(
            name=tax_names[i % len(tax_names)] + f" {i}", 
            code=f"TAX{i:03d}", 
            category='government' if i < 5 else 'airline', 
            per_passenger=True
        )
        tax_types.append(tt)
    print(f"✅ TaxTypes: {len(tax_types)}")

    # 10. Passenger Names (PH)
    ph_first_names = ["Juan", "Maria", "Jose", "Pedro", "Rosa", "Elena", "Carlos", "Luis", "Teresa", "Antonio", "Manuel", "Ricardo", "Carmen", "Francisca", "Gloria", "Isabel", "Lucia", "Miguel", "Ramon", "Victoria"]
    ph_last_names = ["Dela Cruz", "Santos", "Reyes", "Garcia", "Ramos", "Mendoza", "Flores", "Lopez", "Castillo", "Bautista", "Villanueva", "Castro", "Rivera", "Aquino", "Corpuz", "Solis", "Valenzuela", "Galang", "Panganiban", "Santiago"]
    passengers = []
    for i in range(20):
        p = PassengerInfo.objects.create(
            first_name=ph_first_names[i], 
            last_name=ph_last_names[i], 
            passenger_type='Adult', 
            nationality="Filipino",
            passport_number=f"P{random.randint(1000000, 9999999)}A"
        )
        passengers.append(p)
    print(f"✅ PassengerInfo: 20")

    # 11. Bookings & Payments
    admin_user = User.objects.get(username='admin')
    for i in range(20):
        b = Booking.objects.create(
            user=admin_user, 
            trip_type='One-way', 
            status='confirmed', 
            total_amount=schedules[i].price + Decimal(500)
        )
        bd = BookingDetail.objects.create(
            booking=b, 
            passenger=passengers[i], 
            schedule=schedules[i],
            price=schedules[i].price, 
            status='confirmed'
        )
        Payment.objects.create(
            booking=b, 
            amount=b.total_amount, 
            method='Credit Card',
            status='Completed', 
            transaction_id=f"PH-TXN-{10000+i}"
        )
        CheckInDetail.objects.create(booking_detail=bd, boarding_pass=f"BP-PH-{i:03d}")
        TrackLog.objects.create(user=admin_user, action=f"Seeded PH record {i}")
    print("✅ Bookings, Payments, CheckIns, Logs: 20 each")

    # 12. Students & Instructors (PH)
    for i in range(20):
        # Instructors
        Instructor.objects.create(
            instructor_id=f"INS-PH-{i:03d}", 
            first_name=ph_first_names[(i+5)%20], 
            last_name=ph_last_names[(i+5)%20]
        )
        # Students
        uname = f"ph_student_{i}"
        u, created = User.objects.get_or_create(username=uname)
        if created:
            u.set_password("password123")
            u.first_name = ph_first_names[(i+10)%20]
            u.last_name = ph_last_names[(i+10)%20]
            u.email = f"{uname}@example.com"
            u.save()
        
        Students.objects.create(
            user=u, 
            student_number=f"SN-2024-{i:04d}", 
            first_name=u.first_name, 
            last_name=u.last_name,
            gender=random.choice(['mr', 'mrs'])
        )
    print("✅ Instructors & Students: 20 each")

    # 13. Insurance
    provider = InsuranceProvider.objects.create(name="PhilAm Life", code="PALIFE")
    insurance_benefits = [
        "Medical Emergency", "Trip Cancellation", "Baggage Loss", "Delayed Departure",
        "Personal Accident", "Legal Assistance", "Hotel Extension", "Flight Rebooking"
    ]
    for i in range(20):
        benefit = InsuranceBenefit.objects.create(name=insurance_benefits[i % len(insurance_benefits)] + f" {i}")
        plan = TravelInsurancePlan.objects.create(
            provider=provider, 
            name=f"PH Voyager Plan {i}", 
            retail_price=Decimal(random.randint(500, 2000)), 
            wholesale_price=Decimal(random.randint(300, 1500))
        )
        plan.benefits.add(benefit)
    print("✅ Insurance: 20")

    print("\n🇵🇭 Mabuhay! Philippines-based seeding complete with 20 records per model.")

if __name__ == "__main__":
    seed_data()
