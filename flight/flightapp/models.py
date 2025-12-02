# ============================================================
# models.py (FINAL VERSION - CORRECTED)
# ============================================================

from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps  # <- ADD THIS
from decimal import Decimal


# ============================================================
# SIGNAL — AUTO-GENERATE SEATS WHEN A NEW SCHEDULE IS CREATED
# ============================================================
@receiver(post_save)
def create_seats_for_schedule(sender, instance, created, **kwargs):
    # Resolve Schedule model lazily
    Schedule = apps.get_model('flightapp', 'Schedule')
    SeatClass = apps.get_model('flightapp', 'SeatClass')
    Seat = apps.get_model('flightapp', 'Seat')

    # Only run for Schedule saves
    if sender is not Schedule:
        return

    if created:
        aircraft = instance.flight.aircraft
        default_class = SeatClass.objects.first()
        if not default_class:
            return

        seats = [
            Seat(
                schedule=instance,
                seat_class=default_class,
                seat_number=f"{i:02d}",
                is_available=True
            )
            for i in range(1, aircraft.capacity + 1)
        ]
        Seat.objects.bulk_create(seats)




# ============================================================
# COUNTRY MODEL
# ============================================================
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, unique=True, blank=True, null=True)  # e.g., PH, US
    currency = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return self.name
# ============================================================
# USER
# ============================================================
class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
    ]

    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username


# ============================================================
# AIRLINE + SEAT CLASS + AIRCRAFT
# ============================================================
class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class SeatClass(models.Model):
    name = models.CharField(max_length=50)
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="seat_classes", null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("airline", "name")

    def __str__(self):
        return f"{self.name} (x{self.price_multiplier}) - {self.airline.code if self.airline else ''}"


class Aircraft(models.Model):
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="aircrafts")

    def __str__(self):
        return f"{self.model} ({self.airline.code})"


# ============================================================
# AIRPORT (WITH DOMESTIC / INTERNATIONAL TYPE)
# ============================================================
class Airport(models.Model):
    AIRPORT_TYPE_CHOICES = [
        ('domestic', 'Domestic'),
        ('international', 'International'),
        ('unknown', 'Unknown'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="airports")
    location = models.CharField(max_length=150, null=True, blank=True)
    airport_type = models.CharField(max_length=20, choices=AIRPORT_TYPE_CHOICES, default='unknown')

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_airport_type_display()})"

    @property
    def is_international(self):
        return self.airport_type == "international"

    @property
    def is_domestic(self):
        return self.airport_type == "domestic"



# ============================================================
# ROUTE (DOMESTIC OR INTERNATIONAL LOGIC)
# ============================================================
class Route(models.Model):
    origin_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.origin_airport.code} → {self.destination_airport.code}"

    @property
    def is_domestic(self):
        """True if both airports are in the same country."""
        if not (self.origin_airport.country and self.destination_airport.country):
            return (
                self.origin_airport.airport_type in ('domestic', 'unknown') and
                self.destination_airport.airport_type in ('domestic', 'unknown')
            )
        return self.origin_airport.country.strip().lower() == self.destination_airport.country.strip().lower()

    @property
    def is_international(self):
        """True if origin and destination are in different countries."""
        if not (self.origin_airport.country and self.destination_airport.country):
            return (
                self.origin_airport.airport_type == 'international' or
                self.destination_airport.airport_type == 'international'
            )
        return self.origin_airport.country.strip().lower() != self.destination_airport.country.strip().lower()


# ============================================================
# FLIGHT + SCHEDULE + SEAT
# ============================================================
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

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="schedules")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open')

    def __str__(self):
        return f"{self.flight.flight_number} {self.departure_time}"

    def duration(self):
        diff = self.arrival_time - self.departure_time
        total_minutes = int(diff.total_seconds() // 60)
        hours, minutes = divmod(total_minutes, 60)
        days = diff.days

        if days > 0:
            return f"{hours}h {minutes}m (+{days}d)"
        return f"{hours}h {minutes}m"

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


# ============================================================
# PASSENGERS
# ============================================================
class PassengerInfo(models.Model):
    TYPE_CHOICES = [("Adult", "Adult"), ("Child", "Child"), ("Infant", "Infant")]

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    passenger_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="Adult")

    # Infant linked to adult
    linked_adult = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="infants"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.passenger_type})"


# ============================================================
# STUDENT + INSTRUCTOR
# ============================================================
class Student(models.Model):
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=5, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True)
    password = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    student_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        if self.middle_initial:
            return f"{self.student_number} - {self.first_name} {self.middle_initial}. {self.last_name}"
        return f"{self.student_number} - {self.first_name} {self.last_name}"


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile', null=True)
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=5, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True)
    password = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    instructor_id = models.CharField(max_length=50, unique=True, null=True)

    def get_full_name(self):
        parts = [self.first_name, f"{self.middle_initial}." if self.middle_initial else None, self.last_name]
        return " ".join([p for p in parts if p])

    def __str__(self):
        return self.get_full_name()


# ============================================================
# BOOKING SYSTEM
# ============================================================
class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    trip_type = models.CharField(
        max_length=20,
        choices=[
            ("one_way", "One Way"),
            ("round_trip", "Round Trip"),
            ("multi_city", "Multi City"),
        ]
    )

    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.student.first_name} {self.student.last_name}"

    @property
    def payment(self):
        return self.payments.last()

    @property
    def total_amount(self):
        total = Decimal('0.00')
        for detail in self.details.all():
            total += Decimal(detail.price or Decimal('0.00'))
        return total


# ============================================================
# ADD-ONS
# ============================================================
class AddOnType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class AddOn(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="addons", null=True)

    seat_class = models.ForeignKey(
        SeatClass, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="addons"
    )

    type = models.ForeignKey(
        AddOnType, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="addons"
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    included = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - ₱{self.price}"


# ============================================================
# BOOKING DETAIL
# ============================================================
class BookingDetail(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="details")
    passenger = models.ForeignKey(PassengerInfo, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True)
    seat_class = models.ForeignKey(SeatClass, on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    addons = models.ManyToManyField(AddOn, blank=True, related_name='booking_details')

    def save(self, *args, **kwargs):
        if self.seat:
            base_price = self.schedule.flight.route.base_price
            multiplier = self.seat.seat_class.price_multiplier if self.seat.seat_class else Decimal("1.0")

            days_diff = (self.schedule.departure_time.date() - timezone.now().date()).days

            if days_diff >= 30:
                factor = Decimal("0.8")      # advance booking discount
            elif 7 <= days_diff <= 29:
                factor = Decimal("1.0")      # normal
            else:
                factor = Decimal("1.5")      # last-minute fare increase

            self.price = base_price * multiplier * factor

        super().save(*args, **kwargs)


# ============================================================
# TAX SYSTEM FOR FLIGHT BOOKINGS
# ============================================================

class TaxType(models.Model):
    """
    Defines a tax or fee, example:
    - PH Domestic Passenger Service Charge (Terminal Fee)
    - PH Travel Tax (Intl outbound)
    - Fuel Surcharge
    - Aviation Security Fee
    - VAT
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    # Whether this applies per passenger (most do)
    per_passenger = models.BooleanField(default=True)

    # Does it apply only to adults?
    adult_only = models.BooleanField(default=False)

    # Domestic / International applicability
    applies_domestic = models.BooleanField(default=True)
    applies_international = models.BooleanField(default=True)

    # Price is stored but can be overridden by airline
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.code})"


class AirlineTax(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="tax_rates")
    tax_type = models.ForeignKey(TaxType, on_delete=models.CASCADE, related_name="airline_rates")

    # Overrides government rate (if airline charges different)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('airline', 'tax_type')

    def __str__(self):
        return f"{self.airline.code} - {self.tax_type.code}"


class AirportFee(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="fees")
    tax_type = models.ForeignKey(TaxType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('airport', 'tax_type')

    def __str__(self):
        return f"{self.airport.code} - {self.tax_type.name}"


class TravelTaxRate(models.Model):
    """
    PH Travel Tax (TIEZA) rates:
    - Adult: ₱1,620 economy
    - Child: ₱810
    - Infant: Exempt
    - Applies only outbound international departing PH
    """
    passenger_type = models.CharField(max_length=10, choices=[
        ("Adult", "Adult"),
        ("Child", "Child"),
        ("Infant", "Infant"),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.passenger_type} - ₱{self.amount}"


class BookingTax(models.Model):
    """Stores the actual tax amounts applied to each booking detail"""
    booking_detail = models.ForeignKey(BookingDetail, on_delete=models.CASCADE, related_name="taxes")
    tax_type = models.ForeignKey(TaxType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Booking Taxes"

    def __str__(self):
        return f"{self.tax_type.name} - ₱{self.amount}"


class InsurancePlan(models.Model):
    """Travel insurance plans offered by airlines"""
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="insurance_plans")
    name = models.CharField(max_length=150)
    coverage_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.airline.code} - {self.name}"


class BookingDetailInsurance(models.Model):
    """Links insurance plans to booking details"""
    booking_detail = models.ForeignKey(BookingDetail, on_delete=models.CASCADE, related_name="insurance")
    plan = models.ForeignKey(InsurancePlan, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Booking Detail Insurances"

    def __str__(self):
        return f"{self.booking_detail.id} - {self.plan.name}"


# ============================================================
# PAYMENT
# ============================================================
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
        return f"Payment {self.id} (Booking {self.booking.id})"


# ============================================================
# CHECK-IN DETAIL
# ============================================================
class CheckInDetail(models.Model):
    booking_detail = models.ForeignKey(BookingDetail, on_delete=models.CASCADE, related_name="checkins")
    check_in_time = models.DateTimeField(auto_now_add=True)
    boarding_pass = models.CharField(max_length=100, blank=True, null=True)
    baggage_count = models.PositiveIntegerField(default=0)
    baggage_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Check-In {self.id} (Booking {self.booking_detail.booking.id})"


# ============================================================
# TRACK LOGS
# ============================================================
class TrackLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="tracklogs")
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_number} - {self.action}"


# ============================================================
# UTILITY FUNCTIONS FOR TAX CALCULATION
# ============================================================

def calculate_taxes_for_booking_detail(detail):
    """
    Calculate and apply all taxes for a booking detail.
    This is called automatically when a BookingDetail is saved.
    """
    schedule = detail.schedule
    flight = schedule.flight
    route = flight.route
    passenger = detail.passenger
    airline = flight.airline

    # Clear old taxes
    detail.taxes.all().delete()

    # Determine route type
    is_domestic = route.is_domestic
    is_international = route.is_international

    # Apply Airline Taxes
    for airline_tax in airline.tax_rates.all():
        tax_type = airline_tax.tax_type

        # Check applicability
        if is_domestic and not tax_type.applies_domestic:
            continue
        if is_international and not tax_type.applies_international:
            continue

        # Check passenger restrictions
        if tax_type.adult_only and passenger.passenger_type != "Adult":
            continue

        amount = airline_tax.amount

        if amount > 0:
            BookingTax.objects.create(
                booking_detail=detail,
                tax_type=tax_type,
                amount=amount,
                description=f"{tax_type.name} ({airline.code})"
            )

    # Apply Airport Fees
    origin_airport = route.origin_airport
    for fee in origin_airport.fees.all():
        tax_type = fee.tax_type
        
        # Check applicability
        if is_domestic and not tax_type.applies_domestic:
            continue
        if is_international and not tax_type.applies_international:
            continue

        # Check passenger restrictions
        if tax_type.adult_only and passenger.passenger_type != "Adult":
            continue

        BookingTax.objects.create(
            booking_detail=detail,
            tax_type=tax_type,
            amount=fee.amount,
            description=f"{tax_type.name} ({origin_airport.code})"
        )

    if is_international and origin_airport.country:
        travel_tax_country = origin_airport.country.name
        
        travel_tax_type, created = TaxType.objects.get_or_create(
            code=f"TRAVEL_TAX_{travel_tax_country.upper()}",
            defaults={
                "name": f"{travel_tax_country} Travel Tax",
                "description": f"Travel Tax for international departures from {travel_tax_country}",
                "applies_domestic": False,
                "applies_international": True,
                "adult_only": False,
                "per_passenger": True,
                "base_amount": 1620.00,  # default or dynamic per country
            }
        )


        # Get rate based on passenger type
        try:
            rate = TravelTaxRate.objects.get(passenger_type=passenger.passenger_type)
            if rate.amount > 0:
                BookingTax.objects.create(
                    booking_detail=detail,
                    tax_type=travel_tax_type,
                    amount=rate.amount,
                    description=f"PH Travel Tax ({passenger.passenger_type})"
                )
        except TravelTaxRate.DoesNotExist:
            pass  # No travel tax for this passenger type


def get_total_tax_amount(booking_detail):
    """Calculate total tax amount for a booking detail."""
    total = Decimal('0.00')
    for tax in booking_detail.taxes.all():
        total += tax.amount
    return total


def get_insurance_amount(booking_detail):
    """Calculate total insurance amount for a booking detail."""
    total = Decimal('0.00')
    for insurance in booking_detail.insurance.all():
        total += insurance.plan.price
    return total


# ============================================================
# MODIFY BookingDetail.save() TO AUTO-CALCULATE TAXES
# ============================================================

# First, let's save the original save method
_original_booking_detail_save = BookingDetail.save

def new_booking_detail_save(self, *args, **kwargs):
    # Call the original save method first
    _original_booking_detail_save(self, *args, **kwargs)
    
    # Calculate and apply taxes
    calculate_taxes_for_booking_detail(self)

# Replace the save method
BookingDetail.save = new_booking_detail_save

# ============================================================
# ADD HELPER PROPERTIES
# ============================================================

# Add property to BookingDetail
@property
def booking_detail_total_with_taxes(self):
    """Calculate total for this booking detail including taxes and insurance."""
    base_price = self.price or Decimal('0.00')
    taxes = get_total_tax_amount(self)
    insurance = get_insurance_amount(self)
    return base_price + taxes + insurance

@property
def booking_detail_tax_amount(self):
    """Calculate tax amount for this booking detail."""
    return get_total_tax_amount(self)

BookingDetail.total_with_taxes = booking_detail_total_with_taxes
BookingDetail.tax_amount = booking_detail_tax_amount

# Add properties to Booking
@property
def booking_total_with_taxes(self):
    """Calculate total booking amount including taxes and insurance."""
    total = Decimal('0.00')
    for detail in self.details.all():
        total += detail.total_with_taxes
    return total

@property 
def booking_tax_total(self):
    """Calculate total taxes for the booking."""
    total = Decimal('0.00')
    for detail in self.details.all():
        total += detail.tax_amount
    return total

@property
def booking_insurance_total(self):
    """Calculate total insurance for the booking."""
    total = Decimal('0.00')
    for detail in self.details.all():
        total += get_insurance_amount(detail)
    return total

Booking.total_with_taxes = booking_total_with_taxes
Booking.tax_total = booking_tax_total
Booking.insurance_total = booking_insurance_total

