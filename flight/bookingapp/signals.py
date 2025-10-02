# bookingapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from flightapp.models import Booking  # ✅ correct app for Booking


@receiver(post_save, sender=Booking)
def occupy_seats_on_confirm(sender, instance, created, **kwargs):
    if instance.status.lower() == "confirmed":
        print(f"[SIGNAL] Booking {instance.id} confirmed — checking seats...")

        for detail in instance.details.all():
            if detail.passenger.passenger_type != "Infant":  # ✅ skip infants
                if detail.seat and detail.seat.is_available:
                    detail.seat.is_available = False
                    detail.seat.save()
                    print(f"   ✅ Seat {detail.seat.seat_number} occupied")
            else:
                print(f"   👶 Infant {detail.passenger} linked to {detail.guardian or 'Adult'} (no seat needed)")
