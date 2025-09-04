from django.db import models
from django.utils import timezone


# ---------------------------
# Custom User (optional)
# ---------------------------
class MyUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)  # store hashed password
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

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
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="aircrafts")

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
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE, related_name="schedules")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # NEW

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
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")])
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    passport_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed password
    phone = models.CharField(max_length=20, null=True, blank=True)
    student_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.student_number} - {self.first_name} {self.last_name}"


class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="bookings")
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="bookings")
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled"),
    ], default="Pending")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Booking {self.id} - {self.student.first_name} {self.student.last_name}"


class BookingDetail(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="details")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True)
    seat_class = models.ForeignKey(SeatClass, on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.booking.id} - {self.flight.flight_number}"


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
