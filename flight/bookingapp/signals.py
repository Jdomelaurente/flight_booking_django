# bookingapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from flightapp.models import Booking  # ✅ correct app for Booking


@receiver(post_save, sender=Booking)
def occupy_seats_on_confirm(sender, instance, created, **kwargs):
    """
    When a booking is confirmed, mark all related seats in BookingDetail as occupied.
    Works for one-way, round-trip, and multi-city bookings.
    """
    if instance.status.lower() == "confirmed":
        print(f"[SIGNAL] Booking {instance.id} confirmed — checking seats...")

        for detail in instance.details.all():  # ✅ loop BookingDetail
            if detail.seat and detail.seat.is_available:
                detail.seat.is_available = False
                detail.seat.save()
                print(f"   ✅ Seat {detail.seat.seat_number} for schedule {detail.schedule.id} occupied")

        print(f"[SIGNAL COMPLETE] Booking {instance.id} seats updated.")
