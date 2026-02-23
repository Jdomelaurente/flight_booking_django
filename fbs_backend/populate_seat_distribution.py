
import os
import django
import random
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule, SeatClass, Booking, BookingDetail, PassengerInfo
from django.contrib.auth.models import User

def run():
    print("Starting Seat Class Distribution population...")
    
    # 1. Get or create a basic user
    user, _ = User.objects.get_or_create(username="demo_user", defaults={"email": "demo@example.com"})
    
    # 2. Get or create a passenger (using correct fields)
    # Fields: first_name, last_name, title, date_of_birth, nationality, passenger_type
    passenger, _ = PassengerInfo.objects.get_or_create(
        first_name="Demo",
        last_name="User",
        defaults={
            "title": "MR",
            "date_of_birth": "1990-01-01",
            "nationality": "Filipino",
            "passenger_type": "Adult"
        }
    )
    
    # 3. Get a schedule
    schedule = Schedule.objects.first()
    if not schedule:
        print("No schedule found. Please run populate_philippines.py first.")
        return

    # 4. Create a Booking
    # Fields: user, trip_type, status, total_amount
    booking = Booking.objects.create(
        user=user,
        trip_type="one_way",
        status="Completed",
        total_amount=Decimal('0.00')
    )

    # 5. Create BookingDetails for each SeatClass
    seat_classes = SeatClass.objects.all()
    if not seat_classes.exists():
        print("No SeatClasses found.")
        return

    distribution = {
        "Economy Class": 15,
        "Premium Economy": 8,
        "Business Class": 5,
        "First Class": 2
    }

    total_created = 0
    total_base_fare = Decimal('0.00')
    total_taxes = Decimal('0.00')
    
    for sc in seat_classes:
        # Match class name or use a default count
        count = distribution.get(sc.name, random.randint(3, 10))
        for _ in range(count):
            base_price = Decimal(str(random.randint(1500, 15000)))
            # Assume 12% VAT in PH
            tax_amount = base_price * Decimal('0.12')
            
            BookingDetail.objects.create(
                booking=booking,
                passenger=passenger,
                schedule=schedule,
                seat_class=sc,
                price=base_price,
                tax_amount=tax_amount,
                status="completed"
            )
            total_created += 1
            total_base_fare += base_price
            total_taxes += tax_amount
        print(f"Created {count} booking details for {sc.name}")

    # Update booking total amount and snapshots
    booking.base_fare_total = total_base_fare
    booking.tax_total = total_taxes
    booking.total_amount = total_base_fare + total_taxes
    booking.save()

    print(f"Successfully populated {total_created} booking details for Booking ID {booking.id}.")

if __name__ == "__main__":
    run()
