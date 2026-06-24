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
        # Fallback if no layout config
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
    print("\n🚀 Seeding new data (20 records per model)...")

    # 1. Countries
    countries = []
    for i in range(20):
        c = Country.objects.create(name=f"Country {i}", code=f"C{i:02d}", currency='PHP')
        countries.append(c)
    print(f"✅ Countries: {len(countries)}")

    # 2. Airlines
    airlines = []
    for i in range(20):
        a = Airline.objects.create(name=f"Airline {i}", code=f"A{i:02d}")
        airlines.append(a)
    print(f"✅ Airlines: {len(airlines)}")

    # 3. SeatClasses
    seat_classes = []
    for a in airlines:
        sc1 = SeatClass.objects.create(airline=a, name='Economy', price_multiplier=Decimal('1.0'))
        sc2 = SeatClass.objects.create(airline=a, name='Business', price_multiplier=Decimal('2.5'))
        seat_classes.extend([sc1, sc2])
    print(f"✅ SeatClasses: {len(seat_classes)}")

    # 4. Airports
    airports = []
    for i in range(20):
        ap = Airport.objects.create(
            name=f"Airport {i}", code=f"AP{i:02d}", city=f"City {i}",
            country=countries[i], airport_type='international'
        )
        airports.append(ap)
    print(f"✅ Airports: {len(airports)}")

    # 5. Aircrafts
    aircrafts = []
    for i in range(20):
        ac = Aircraft.objects.create(model=f"Model {i}", capacity=180, airline=airlines[i])
        aircrafts.append(ac)
    print(f"✅ Aircrafts: {len(aircrafts)}")

    # 6. Routes
    routes = []
    for i in range(20):
        r = Route.objects.create(
            origin_airport=airports[i], destination_airport=airports[(i+1)%20],
            base_price=Decimal(random.randint(2000, 5000))
        )
        routes.append(r)
    print(f"✅ Routes: {len(routes)}")

    # 7. Flights
    flights = []
    for i in range(20):
        f = Flight.objects.create(
            flight_number=f"FL{100+i}", airline=airlines[i],
            aircraft=aircrafts[i], route=routes[i]
        )
        flights.append(f)
    print(f"✅ Flights: {len(flights)}")

    # 8. Schedules
    schedules = []
    now = timezone.now()
    for i in range(20):
        s = Schedule.objects.create(
            flight=flights[i], departure_time=now + timedelta(days=i+1),
            arrival_time=now + timedelta(days=i+1, hours=2), status='Open',
            price=flights[i].route.base_price
        )
        generate_seats(s)
        schedules.append(s)
    print(f"✅ Schedules & Seats: 20")

    # 9. TaxTypes
    tax_types = []
    for i in range(20):
        tt = TaxType.objects.create(
            name=f"Tax {i}", code=f"TAX{i:02d}", category='government', per_passenger=True
        )
        tax_types.append(tt)
    print(f"✅ TaxTypes: {len(tax_types)}")

    # 10. PassengerInfo
    passengers = []
    for i in range(20):
        p = PassengerInfo.objects.create(
            first_name=f"Pass{i}", last_name=f"Last{i}", passenger_type='Adult', nationality="PH"
        )
        passengers.append(p)
    print(f"✅ PassengerInfo: 20")

    # 11. Bookings & Payments
    admin_user = User.objects.get(username='admin')
    for i in range(20):
        b = Booking.objects.create(user=admin_user, trip_type='One-way', status='confirmed', total_amount=Decimal(5000))
        bd = BookingDetail.objects.create(
            booking=b, passenger=passengers[i], schedule=schedules[i],
            price=schedules[i].price, status='confirmed'
        )
        Payment.objects.create(
            booking=b, amount=Decimal(5000), method='Cash',
            status='Completed', transaction_id=f"TXN{i}"
        )
        CheckInDetail.objects.create(booking_detail=bd, boarding_pass=f"BP{i}")
        TrackLog.objects.create(user=admin_user, action=f"Seeded record {i}")
    print("✅ Bookings, Payments, CheckIns, Logs: 20 each")

    # 12. Students & Instructors
    for i in range(20):
        Instructor.objects.create(instructor_id=f"INS{i:03d}", first_name=f"Ins{i}", last_name=f"Last{i}")
        u = User.objects.create_user(username=f"stu_user_{i}", password="password")
        Students.objects.create(user=u, student_number=f"STU{i:03d}", first_name=f"Stu{i}", last_name=f"Last{i}")
    print("✅ Instructors & Students: 20 each")

    # 13. Insurance
    provider = InsuranceProvider.objects.create(name="InsureCorp", code="IC")
    for i in range(20):
        benefit = InsuranceBenefit.objects.create(name=f"Benefit {i}")
        plan = TravelInsurancePlan.objects.create(
            provider=provider, name=f"Plan {i}", retail_price=Decimal(500), wholesale_price=Decimal(400)
        )
        plan.benefits.add(benefit)
    print("✅ Insurance: 20")

    print("\n🌟 All 20 records created for every major model successfully!")

if __name__ == "__main__":
    seed_data()
