from django.db import models
from django.contrib.auth.models import User
from django.db import models
from datetime import timedelta
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
# Airport
# ---------------------------
class Airport(models.Model):
    code = models.CharField(max_length=10, unique=True)   # e.g., MNL, LAX
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"


# ---------------------------
# Airline
# ---------------------------
class Airline(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"


# ---------------------------
# Aircraft
# ---------------------------
class Aircraft(models.Model):
    model = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # Domestic or International
    capacity = models.IntegerField()
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="aircraft")

    def __str__(self):
        return f"{self.model} ({self.type})"


# ---------------------------
# Flight Route
# ---------------------------
class Route(models.Model):
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="routes")
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name="routes")
    distance = models.IntegerField()   # in km
    duration = models.IntegerField()   # in minutes

    def __str__(self):
        return f"{self.departure_airport.code} → {self.arrival_airport.code}"


# ---------------------------
# Flight
# ---------------------------
class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="flights")
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name="flights")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")

    def __str__(self):
        return f"{self.flight_number} - {self.airline.code}"


# ---------------------------
# Schedule
# ---------------------------
from django.db import models
from django.utils import timezone

class Schedule(models.Model):
    flight = models.ForeignKey("Flight", related_name="schedules", on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def get_status(self):
        current_time = timezone.localtime(timezone.now())
        if current_time < self.departure_time:
            return "Standby"
        elif self.departure_time <= current_time < self.arrival_time:
            return "On Flight"
        return "Arrived"

    def __str__(self):
        return f"Schedule for {self.flight} ({self.departure_time} - {self.arrival_time})"

        
# ---------------------------
# Seat Class
# ---------------------------
class SeatClass(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} (x{self.price_multiplier})"


# ---------------------------
# Seat
# ---------------------------
class Seat(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=10)
    seat_class = models.ForeignKey(SeatClass, on_delete=models.CASCADE, related_name="seats")
    available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.seat_number} ({self.schedule.flight.flight_number})"


# ---------------------------
# Student
# ---------------------------
class Student(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# ---------------------------
# Booking
# ---------------------------
class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="bookings")
    reference = models.CharField(max_length=10, unique=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled"),
    ], default="Pending")
    payment_status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ], default="Pending")

    def __str__(self):
        return f"Booking {self.reference} - {self.student.username}"


# ---------------------------
# Booking Detail
# ---------------------------
class BookingDetail(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="details")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="booking_details")
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True, related_name="booking_details")
    seat_class = models.ForeignKey(SeatClass, on_delete=models.CASCADE, related_name="booking_details")
    quantity = models.PositiveIntegerField(default=1)
    passenger_first_name = models.CharField(max_length=50)
    passenger_last_name = models.CharField(max_length=50)
    passenger_email = models.EmailField(blank=True, null=True)
    passenger_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.passenger_first_name} {self.passenger_last_name} ({self.booking.reference})"


# ---------------------------
# Payment
# ---------------------------
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
        return f"Payment {self.id} - Booking {self.booking.reference}"


# ---------------------------
# Check-In
# ---------------------------
class CheckInDetail(models.Model):
    booking_detail = models.ForeignKey(BookingDetail, on_delete=models.CASCADE, related_name="checkins")
    check_in_time = models.DateTimeField(auto_now_add=True)
    boarding_pass = models.CharField(max_length=100, blank=True, null=True)
    baggage_count = models.PositiveIntegerField(default=0)
    baggage_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Check-In {self.id} - {self.booking_detail.booking.reference}"
