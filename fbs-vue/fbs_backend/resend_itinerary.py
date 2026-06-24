"""
Script to resend the itinerary email for a specific booking.
Usage: python resend_itinerary.py
"""
import os
import sys
import django

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Booking
from flightapp.services.email_service import EmailService

PNR = "EEX3R8"
LAST_NAME = "LAURENTE"

try:
    booking = Booking.objects.get(pnr=PNR)
    print(f"[OK] Found booking: {booking.pnr} (ID: {booking.id})")

    # Verify passenger match
    details = booking.details.select_related('passenger').all()
    matched = any(
        d.passenger and LAST_NAME.upper() in d.passenger.last_name.upper()
        for d in details
    )

    if not matched:
        print(f"[WARN] No passenger with last name '{LAST_NAME}' found in this booking.")
        print("   Passengers found:")
        for d in details:
            if d.passenger:
                print(f"     - {d.passenger.get_full_name()}")
    else:
        print(f"[OK] Passenger '{LAST_NAME}' found in booking.")

    # Resend itinerary email
    print(f"\n[INFO] Resending itinerary email for PNR {PNR}...")
    result = EmailService.send_booking_confirmation(booking, attach_pdf=True)

    if result:
        contact = getattr(booking, 'contact', None)
        email_addr = contact.email if contact else "unknown"
        print(f"[SENT] Itinerary email sent successfully to {email_addr}!")
    else:
        print("[FAIL] Failed to send itinerary email. Check the logs above for details.")

except Booking.DoesNotExist:
    print(f"[ERROR] No booking found with PNR: {PNR}")
except Exception as e:
    import traceback
    print(f"[ERROR] {e}")
    traceback.print_exc()
