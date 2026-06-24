import os
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import BookingDetail, SeatClass, Booking

def fix_booking_details():
    seat_classes = list(SeatClass.objects.all())
    if not seat_classes:
        print("Error: No SeatClasses found")
        return

    print(f"Fixing {BookingDetail.objects.count()} booking details...")
    
    details_fixed = 0
    for detail in BookingDetail.objects.all():
        needs_save = False
        
        # Assign random seat class if missing
        if not detail.seat_class:
            detail.seat_class = random.choice(seat_classes)
            needs_save = True
            
        # Ensure it has a price for revenue charts
        if not detail.price or detail.price <= 0:
            # Base it on the seat class multiplier if possible
            base = 2500
            detail.price = base * (detail.seat_class.price_multiplier or 1)
            needs_save = True
            
        # Ensure status is something the dashboard counts (Confirmed, Completed, Paid)
        if detail.booking:
            if detail.booking.status not in ['Confirmed', 'Completed', 'Paid']:
                detail.booking.status = 'Confirmed'
                detail.booking.save()

        if needs_save:
            detail.save()
            details_fixed += 1

    # Also ensure there are some 'Completed' and 'Paid' bookings for variety
    bookings = list(Booking.objects.all())
    for i, b in enumerate(bookings):
        if i % 3 == 0:
            b.status = 'Paid'
        elif i % 3 == 1:
            b.status = 'Completed'
        else:
            b.status = 'Confirmed'
        b.save()

    print(f"Done! Fixed {details_fixed} records and randomized statuses.")

if __name__ == "__main__":
    fix_booking_details()
