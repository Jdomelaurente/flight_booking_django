import os
import django
import sys

# Set up Django environment
sys.path.append(r'c:\Users\user\OneDrive\Desktop\Folders\Fbs\fbs-vue\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import BookingDetail
from flightapp.services.email_service import EmailService

def test_email():
    # Get a booking detail (try the one from the user's error if known, or just the first)
    bd = BookingDetail.objects.first()
    if not bd:
        print("No booking details found")
        return
        
    print(f"Testing email for booking detail ID: {bd.id}")
    booking = bd.booking
    try:
        print(f"Checking contact for Booking PNR: {booking.pnr}")
        contact = getattr(booking, 'contact', None)
        if not contact:
            print("No contact found. Creating a temporary one for this test...")
            from app.models import BookingContact
            contact = BookingContact.objects.create(
                booking=booking,
                first_name="Test",
                last_name="Passenger",
                email="test@example.com",
                phone="09170000000"
            )
        print(f"Contact found: {contact.email}")
    except Exception as e:
        print(f"Error accessing contact: {e}")
        return

    try:
        # Try sending single email first
        success = EmailService.send_checkin_confirmation(bd)
        print(f"Single email success: {success}")

        # Try sending group email
        success_group = EmailService.send_group_checkin_confirmation([bd])
        print(f"Group email success: {success_group}")
        
    except Exception as e:
        import traceback
        print(f"Exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_email()
