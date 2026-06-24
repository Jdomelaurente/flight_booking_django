import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
sys.path.append(os.getcwd())
django.setup()

from app.models import Booking, BookingDetail

def list_non_checkin_pnrs():
    # Find all booking details that are confirmed but not checked-in
    # Status 'confirmed' means paid/confirmed but not checked-in
    # Status 'checkin' means they have performed the check-in process
    pending_details = BookingDetail.objects.filter(status='confirmed').select_related('booking', 'passenger')
    
    if not pending_details.exists():
        print("No pending check-ins found.")
        return

    # Group by PNR
    pnrs = {}
    for detail in pending_details:
        pnr = detail.booking.pnr
        if pnr not in pnrs:
            pnrs[pnr] = []
        pnrs[pnr].append(f"{detail.passenger.get_full_name()} ({detail.passenger.passenger_type})")

    print(f"{'PNR':<10} | {'Passengers'}")
    print("-" * 40)
    for pnr, passengers in pnrs.items():
        print(f"{pnr:<10} | {', '.join(passengers)}")

if __name__ == "__main__":
    list_non_checkin_pnrs()
