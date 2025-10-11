from django.db import models
from django.utils import timezone
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# ---------------------------
# Signal inside models.py
# ---------------------------

@receiver(post_save, sender="flightapp.Schedule")  # ⚠ replace "yourapp" with your Django app name
def create_seats_for_schedule(sender, instance, created, **kwargs):
    if created:
        aircraft = instance.flight.aircraft
        default_class = SeatClass.objects.first()

        if not default_class:
            return  # no SeatClass exists yet

        seats = [
            Seat(
                schedule=instance,
                seat_class=default_class,
                seat_number=f"{i:02d}",  # seat numbering 01, 02, 03...
                is_available=True
            )
            for i in range(1, aircraft.capacity + 1)
        ]
        Seat.objects.bulk_create(seats)


# ---------------------------
# User (Base Table)
# ---------------------------
class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
    ]

    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)  # hashed in real use
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} ({self.role})"


# ---------------------------
# Instructor Profile
# ---------------------------
class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="instructor")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.department})"

# ---------------------------
# Flight & Seat Core
# ---------------------------
class SeatClass(models.Model):
    name = models.CharField(max_length=50)
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} (x{self.price_multiplier})"


class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Aircraft(models.Model):
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    airline = models.ForeignKey("Airline", on_delete=models.CASCADE, related_name="aircrafts")

    def __str__(self):
        return f"{self.model} ({self.airline.code})"


class Airport(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    location = models.CharField(max_length=150, null=True,)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Route(models.Model):
    origin_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    
    def __str__(self):
        return f"{self.origin_airport.code} → {self.destination_airport.code}"



class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="flights")
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name="flights")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")

    def __str__(self):
        return f"{self.flight_number} ({self.airline.code})"


class Schedule(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open for Booking'),
        ('Closed', 'Closed'),
        ('On Flight', 'On Flight'),
        ('Arrived', 'Arrived'),
    ]

    flight = models.ForeignKey("Flight", on_delete=models.CASCADE, related_name="schedules")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open')

    def __str__(self):
        return f"{self.flight.flight_number} ({self.departure_time} - {self.arrival_time})"

    def duration(self):
        diff = self.arrival_time - self.departure_time
        total_minutes = int(diff.total_seconds() // 60)
        hours, minutes = divmod(total_minutes, 60)
        days = diff.days
        if days > 0:
            return f"{hours}h {minutes}m (+{days}d)"
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"

    def update_status(self):
        now = timezone.now()
        if now < self.departure_time - timezone.timedelta(hours=1):
            self.status = 'Open'
        elif self.departure_time - timezone.timedelta(hours=1) <= now < self.departure_time:
            self.status = 'Closed'
        elif self.departure_time <= now < self.arrival_time:
            self.status = 'On Flight'
        else:
            self.status = 'Arrived'
        self.save()

    @property
    def is_open(self):
        return self.status == "Open"


class Seat(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="seats")
    seat_class = models.ForeignKey(SeatClass, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.seat_number} - {self.schedule.flight.flight_number}"


# ---------------------------
# Passenger & Booking
# ---------------------------
class PassengerInfo(models.Model):
    TYPE_CHOICES = [("Adult", "Adult"), ("Child", "Child"), ("Infant", "Infant")]

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)

    passenger_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default="Adult"
    )

    # NEW: link infants to an adult passenger
    linked_adult = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="infants",
        help_text="For infants on lap, assign to the adult passenger"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.passenger_type})"



class Student(models.Model):
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=5, null=True, blank=True)  # optional
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed password
    phone = models.CharField(max_length=20, null=True, blank=True)
    student_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        if self.middle_initial:
            return f"{self.student_number} - {self.first_name} {self.middle_initial}. {self.last_name}"
        return f"{self.student_number} - {self.first_name} {self.last_name}"





    
from django.db import models
from django.utils import timezone
from decimal import Decimal

class Booking(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)  # The booker
    trip_type = models.CharField(
        max_length=20,
        choices=[("one_way", "One Way"), ("round_trip", "Round Trip"), ("multi_city", "Multi City")]
    )
    
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.student.first_name} {self.student.last_name}"

    @property
    def payment(self):
        return self.payment_set.last()

    @property
    def total_amount(self):
        total = Decimal("0.00")
        for detail in self.details.all():
            total += detail.price
        return total

class BookingDetail(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="details")
    passenger = models.ForeignKey(PassengerInfo, on_delete=models.CASCADE)
    schedule = models.ForeignKey("Schedule", on_delete=models.CASCADE)
    seat = models.ForeignKey("Seat", on_delete=models.SET_NULL, null=True, blank=True)
    seat_class = models.ForeignKey("SeatClass", on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.seat:
            base_price = self.schedule.flight.route.base_price
            multiplier = self.seat.seat_class.price_multiplier if self.seat.seat_class else Decimal("1.0")
            days_diff = (self.schedule.departure_time.date() - timezone.now().date()).days
            if days_diff >= 30:
                factor = Decimal("0.8")
            elif 7 <= days_diff <= 29:
                factor = Decimal("1.0")
            else:
                factor = Decimal("1.5")
            self.price = base_price * multiplier * factor
        super().save(*args, **kwargs)




class Payment(models.Model):
    PAYMENT_METHODS = [
        ("GCash", "GCash"),
        ("Credit Card", "Credit Card"),
        ("Cash", "Cash"),
        ("Paypal", "Paypal"),
    ]

    PAYMENT_STATUS = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Pending")

    def __str__(self):
        return f"Payment {self.id} - Booking {self.booking.id}"


class CheckInDetail(models.Model):
    booking_detail = models.ForeignKey(BookingDetail, on_delete=models.CASCADE, related_name="checkins")
    check_in_time = models.DateTimeField(auto_now_add=True)
    boarding_pass = models.CharField(max_length=100, blank=True, null=True)
    baggage_count = models.PositiveIntegerField(default=0)
    baggage_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Check-In {self.id} - Booking {self.booking_detail.booking.id}"


class TrackLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="tracklogs")
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_number} - {self.action}"
