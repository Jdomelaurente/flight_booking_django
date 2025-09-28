# bookingapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from flightapp.models import Booking

@receiver(post_save, sender=Booking)
def occupy_seats_on_confirm(sender, instance, created, **kwargs):
    if instance.status.lower() == "confirmed":
        print(f"[SIGNAL] Booking {instance.id} confirmed — checking seats...")

        # Outbound seat
        if instance.outbound_seat and instance.outbound_seat.is_available:
            instance.outbound_seat.is_available = False
            instance.outbound_seat.save()
            print(f"   ✅ Outbound seat {instance.outbound_seat.seat_number} occupied")

        # Return seat
        if instance.return_seat and instance.return_seat.is_available:
            instance.return_seat.is_available = False
            instance.return_seat.save()
            print(f"   ✅ Return seat {instance.return_seat.seat_number} occupied")

        print(f"[SIGNAL COMPLETE] Booking {instance.id} seats updated.")
