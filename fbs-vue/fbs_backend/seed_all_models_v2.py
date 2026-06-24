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
from fbs_instructor.models import Instructor, UserSession

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

    # For instructors, they might be referenced elsewhere so handle with care
    try:
        Instructor.objects.all().delete()
    except: pass
    
    # Do not delete UserProfile or User to preserve admin login
    User.objects.exclude(username='admin').delete()
    print("✅ Cleanup complete.")

def generate_seats(schedule):
    aircraft = schedule.flight.aircraft
    layout = aircraft.get_layout_config()
    seat_classes_config = layout.get('seat_classes', [])
    
    if not seat_classes_config:
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
                    defaults={
                        'seat_class': seat_class,
                        'row': row_num,
                        'column': col_label,
                        'is_available': True
                    }
                )

def seed_data():
    clear_data()
    print("\n🚀 Seeding new data (20 records per model)...")

    # 1. Countries
    countries = []
    for i in range(20):
        c = Country.objects.create(
            name=f"Country {i}",
            code=f"C{i}",
            currency=random.choice(['PHP', 'USD', 'JPY', 'EUR', 'GBP'])
        )
        countries.append(c)
    print(f"✅ Countries: {len(countries)}")

    # 2. Airlines
    airlines = []
    for i in range(20):
        a = Airline.objects.create(name=f"Airline {i}", code=f"A{i}")
        airlines.append(a)
    print(f"✅ Airlines: {len(airlines)}")

    # 3. SeatClasses (mix per airline)
    seat_classes = []
    for a in airlines:
        for name in ['Economy', 'Business']:
            sc = SeatClass.objects.create(
                airline=a, 
                name=name, 
                price_multiplier=Decimal('1.0') if name=='Economy' else Decimal('2.5')
            )
            seat_classes.append(sc)
    print(f"✅ SeatClasses: {len(seat_classes)}")

    # 4. Airports
    airports = []
    for i in range(20):
        ap = Airport.objects.create(
            name=f"Airport {i}",
            code=f"AP{i}",
            city=f"City {i}",
            country=countries[i % 20],
            airport_type=random.choice(['domestic', 'international'])
        )
        airports.append(ap)
    print(f"✅ Airports: {len(airports)}")

    # 5. Aircrafts
    aircrafts = []
    for i in range(20):
        ac = Aircraft.objects.create(
            model=f"Model {i}", 
            capacity=180, 
            airline=airlines[i % 20]
        )
        aircrafts.append(ac)
    print(f"✅ Aircrafts: {len(aircrafts)}")

    # 6. Routes
    routes = []
    for i in range(20):
        r = Route.objects.create(
            origin_airport=airports[i % 20],
            destination_airport=airports[(i+1) % 20],
            base_price=Decimal(random.randint(2000, 10000))
        )
        routes.append(r)
    print(f"✅ Routes: {len(routes)}")

    # 7. Flights
    flights = []
    for i in range(20):
        f = Flight.objects.create(
            flight_number=f"FL{100+i}",
            airline=airlines[i % 20],
            aircraft=aircrafts[i % 20],
            route=routes[i % 20]
        )
        flights.append(f)
    print(f"✅ Flights: {len(flights)}")

    # 8. Schedules
    schedules = []
    now = timezone.now()
    for i in range(20):
        s = Schedule.objects.create(
            flight=flights[i],
            departure_time=now + timedelta(days=i+1),
            arrival_time=now + timedelta(days=i+1, hours=2),
            status='Open',
            price=flights[i].route.base_price
        )
        generate_seats(s)
        schedules.append(s)
    print(f"✅ Schedules: {len(schedules)} (with seats)")

    # 9. TaxTypes
    tax_types = []
    for i in range(20):
        tt = TaxType.objects.create(
            name=f"Tax {i}",
            code=f"TAX{i}",
            description=f"Tax description {i}",
            category=random.choice(['government', 'airport', 'airline'])
        )
        tax_types.append(tt)
    print(f"✅ TaxTypes: {len(tax_types)}")

    # 10. AirlineTax
    for i in range(20):
        AirlineTax.objects.create(
            airline=airlines[i % 20],
            tax_type=tax_types[i % 20],
            amount=Decimal(random.randint(100, 500))
        )
    print("✅ AirlineTax: 20")

    # 11. AirportFee
    for i in range(20):
        AirportFee.objects.create(
            airport=airports[i % 20],
            tax_type=tax_types[i % 20],
            amount=Decimal(random.randint(100, 500))
        )
    print("✅ AirportFee: 20")

    # 12. PassengerInfo
    passengers = []
    for i in range(20):
        p = PassengerInfo.objects.create(
            first_name=f"Pass{i}",
            last_name=f"Last{i}",
            passenger_type=random.choice(['Adult', 'Child', 'Infant']),
            nationality="Filipino"
        )
        passengers.append(p)
    print(f"✅ PassengerInfo: {len(passengers)}")

    # 13. Bookings
    bookings = []
    admin_user = User.objects.get(username='admin')
    for i in range(20):
        b = Booking.objects.create(
            user=admin_user,
            trip_type='One-way',
            status='confirmed',
            total_amount=Decimal(random.randint(5000, 15000))
        )
        bookings.append(b)
        
        # Booking Detail
        BookingDetail.objects.create(
            booking=b,
            passenger=passengers[i],
            schedule=schedules[i],
            price=schedules[i].price,
            status='confirmed'
        )
        
        # Payment
        Payment.objects.create(
            booking=b,
            amount=b.total_amount,
            payment_method='credit_card',
            status='completed',
            transaction_id=f"TXN{i}"
        )
        
        # Booking Tax
        BookingTax.objects.create(
            booking=b,
            tax_type=tax_types[i % 20],
            amount=Decimal(200),
            passenger_type=passengers[i].passenger_type
        )
    print("✅ Bookings, Details, Payments, BookingTaxes: 20 each")

    # 14. Students & Instructors
    for i in range(20):
        Instructor.objects.create(
            instructor_id=f"INS{i}",
            first_name=f"Ins{i}",
            last_name=f"Last{i}"
        )
        # Students need unique users
        u = User.objects.create_user(username=f"stu{i}", password="password")
        Students.objects.create(
            user=u,
            student_number=f"STU{i}",
            first_name=f"Stu{i}",
            last_name=f"Last{i}"
        )
    print("✅ Instructors & Students: 20 each")

    # 15. Insurance
    provider = InsuranceProvider.objects.create(name="Global Care", code="GC")
    for i in range(20):
        benefit = InsuranceBenefit.objects.create(name=f"Benefit {i}")
        cov_type = InsuranceCoverageType.objects.create(name=f"Coverage {i}", code=f"COV{i}")
        plan = TravelInsurancePlan.objects.create(
            provider=provider,
            name=f"Plan {i}",
            retail_price=Decimal(500 + i*10)
        )
        plan.benefits.add(benefit)
    print("✅ Insurance (Provider, Benefits, CovTypes, Plans): 20 each")

    # 16. TrackLog
    for i in range(20):
        TrackLog.objects.create(
            user=admin_user,
            action=f"Action {i}"
        )
    print("✅ TrackLog: 20")

    print("\n🌟 All 20 records created for every major model successfully!")

if __name__ == "__main__":
    seed_data()
