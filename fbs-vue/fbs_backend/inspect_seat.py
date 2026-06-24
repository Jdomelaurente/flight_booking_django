import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import BookingDetail, Seat

try:
    detail = BookingDetail.objects.filter(seat__isnull=False).latest('id')
    print(f"BookingDetail ID: {detail.id}")
    print(f"Seat Object: {detail.seat}")
    print(f"Seat Number: {detail.seat.seat_number}")
    # Inspect all fields of the seat to see what "120" could be
    for field in detail.seat._meta.fields:
        print(f"{field.name}: {getattr(detail.seat, field.name)}")
except Exception as e:
    print(f"Error: {e}")
