import os
import django
import random
import string
from decimal import Decimal
from django.utils import timezone

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
# Add fbs_backend to path if needed (assuming script is in fbs-vue)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'fbs_backend'))

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

from django.contrib.auth.models import User
from app.models import Booking, BookingDetail, PassengerInfo, Schedule, Seat, BookingContact, CheckInDetail
from fbs_instructor.models import Activity, ActivityStudentBinding

def generate_pnr():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def run_full_simulation():
    print("="*60)
    print(" FLIGHT RESERVATION SYSTEM: FULL PROCESS SIMULATION")
    print("="*60)

    # 1. STUDENT PHASE
    print("\n[PHASE 1] Student Entry")
    student_username = 'student1'
    try:
        student_user = User.objects.get(username=student_username)
        print(f"  -> Student Authenticated: {student_user.get_full_name()} (@{student_username})")
    except User.DoesNotExist:
        print(f"  !! Error: Student '{student_username}' not found. Please run seeder first.")
        return

    # Check for assigned activities
    activities = ActivityStudentBinding.objects.filter(student__user=student_user, status='assigned')
    if activities.exists():
        activity = activities.first().activity
        print(f"  -> Active Activity Found: {activity.title}")
    else:
        print("  -> No pending activities. Proceeding with general simulation.")
        activity = None

    # 2. BOOKING PHASE
    print("\n[PHASE 2] Booking Process")
    
    # Pick a random schedule
    schedule = Schedule.objects.filter(departure_time__gt=timezone.now()).first()
    if not schedule:
        print("  !! Error: No upcoming schedules found.")
        return
    
    print(f"  -> Searching Flights: {schedule.flight.route.origin.code} to {schedule.flight.route.destination.code}")
    print(f"  -> Selected Flight: {schedule.flight.flight_number} departing {schedule.departure_time}")

    # Create Passenger
    passenger = PassengerInfo.objects.create(
        first_name="John",
        last_name="Doe",
        title="MR",
        date_of_birth="1990-05-15",
        nationality="PH"
    )
    print(f"  -> Passenger Created: John Doe (Adult)")

    # Create Booking
    pnr = generate_pnr()
    booking = Booking.objects.create(
        user=student_user,
        trip_type='one_way',
        pnr=pnr,
        status='Pending',
        activity=activity
    )
    
    # Add Contact Info
    BookingContact.objects.create(
        booking=booking,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="09171234567"
    )

    # Select Seat
    seat = Seat.objects.filter(schedule=schedule, is_available=True).first()
    if seat:
        seat.is_available = False
        seat.save()
        print(f"  -> Seat Selected: {seat.seat_number} ({seat.seat_class.name})")
    else:
        print("  !! Error: No seats available.")
        return

    # Create Booking Detail
    detail = BookingDetail.objects.create(
        booking=booking,
        passenger=passenger,
        schedule=schedule,
        seat=seat,
        price=schedule.flight.route.base_price,
        status='confirmed'
    )
    
    booking.status = 'Confirmed'
    booking.save()
    
    print(f"  -> Booking Successful! PNR: {pnr}")
    print(f"  -> Total Amount: PHP {detail.price:,.2f}")

    # 3. CHECK-IN PHASE
    print("\n[PHASE 3] Online Check-in")
    print(f"  -> Retrieving Booking for PNR: {pnr}")
    
    # Simulate Check-in
    checkin = CheckInDetail.objects.create(
        booking_detail=detail,
        status='checked-in',
        has_declared_safety=True,
        baggage_count=1,
        baggage_weight=Decimal("15.5")
    )
    
    detail.status = 'checkin'
    detail.save()
    
    boarding_pass = checkin.generate_boarding_pass()
    print(f"  -> Check-in Complete!")
    print(f"  -> Baggage: {checkin.baggage_count}pc ({checkin.baggage_weight}kg)")
    print(f"  -> Boarding Pass Issued: {boarding_pass}")
    print(f"  -> Gate: {checkin.gate_number or 'TBA'} | Sequence: {checkin.id:03d}")

    print("\n" + "="*60)
    print(" SIMULATION SUCCESSFUL: DATA STORED IN DATABASE")
    print("="*60)

if __name__ == "__main__":
    run_full_simulation()
