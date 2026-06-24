import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Booking, BookingDetail
from flightapp.services.email_service import EmailService

# Recipient email
RECIPIENT = '242018love@gmail.com'

def send_samples():
    print(f"Starting sample email dispatch to {RECIPIENT}...")
    
    # 1. Booking Confirmation Sample
    try:
        booking = Booking.objects.get(id=80)
        # Temporary override contact email
        if hasattr(booking, 'contact'):
            booking.contact.email = RECIPIENT
        
        print(f"Sending Booking Confirmation (E-ticket + Itinerary PDF)...")
        success = EmailService.send_booking_confirmation(booking)
        if success:
            print("Booking confirmation sent.")
        else:
            print("Failed to send booking confirmation.")
            
    except Exception as e:
        print(f"Error during booking confirmation sample: {e}")

    # 2. Check-in Confirmation Sample
    try:
        detail = BookingDetail.objects.get(id=113)
        # Temporary override passenger email
        if detail.passenger:
             detail.passenger.email = RECIPIENT
        # Also override booking contact email just in case
        if hasattr(detail.booking, 'contact'):
             detail.booking.contact.email = RECIPIENT
        
        print(f"Sending Check-in Confirmation (Boarding Pass PDF)...")
        success = EmailService.send_checkin_confirmation(detail)
        if success:
            print("Check-in confirmation sent.")
        else:
            print("Failed to send check-in confirmation.")
            
    except Exception as e:
        print(f"Error during check-in confirmation sample: {e}")

    print("\nDispatch complete!")

if __name__ == "__main__":
    send_samples()
