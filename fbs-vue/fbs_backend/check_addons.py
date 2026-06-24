import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import BookingDetail, Booking

recent_bookings = Booking.objects.order_by('-created_at')[:5]
for b in recent_bookings:
    print(f"\nBooking: {b.pnr} | Activity: {b.activity_id} | Created: {b.created_at}")
    details = BookingDetail.objects.filter(booking=b).prefetch_related('addons', 'passenger')
    for d in details:
        addons = list(d.addons.values('id', 'name'))
        print(f"  Detail {d.id} | Pax: {d.passenger} | Addons ({len(addons)}): {addons}")
