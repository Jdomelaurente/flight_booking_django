from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

# Custom User model

# Custom User model
class User(AbstractUser):
    # Optional field for role
    role = models.CharField(max_length=50, default="Instructor")


# Class model, linked to the logged-in user
class Class(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject_code = models.CharField(max_length=20)  # e.g., IT 101
    subject_title = models.CharField(max_length=200)  # e.g., Introduction to IT
    instructor = models.CharField(max_length=100, blank=True, null=True)
    schedule = models.CharField(max_length=100, blank=True, null=True)
    
    SEMESTER_CHOICES = [
        ('1st', '1st Semester'),
        ('2nd', '2nd Semester'),
        ('summer', 'Summer'),
    ]
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=9)  # e.g., 2025–2026

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_title} ({self.academic_year})"


# SectionGroup, also linked to user
class SectionGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject_code = models.CharField(max_length=50)
    subject_title = models.CharField(max_length=200, null=True, blank=True)
    instructor = models.CharField(max_length=100)
    num_sections = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject_code} - {self.subject_title} - {self.instructor}"


# Individual Section linked to SectionGroup
class Section(models.Model):
    group = models.ForeignKey(SectionGroup, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=100)
    schedule = models.CharField(max_length=100, default="TBA")

    def __str__(self):
        return f"{self.name} - {self.schedule}"


# Students linked to Section
class Students(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="students")
    student_id = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    institutional_email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        unique_together = ('section', 'institutional_email')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.institutional_email})"


class ExcelRowData(models.Model):
    section = models.ForeignKey("Section", on_delete=models.CASCADE, related_name="excel_rows")
    data = models.JSONField()  # store entire row as JSON {header:value}
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Row {self.id} for {self.section.name}"
    


# models.py
class Booking(models.Model):
    section = models.ForeignKey("Section", on_delete=models.CASCADE, related_name="bookings")

    TRIP_TYPE_CHOICES = [
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
        ('multi_city', 'Multi City'),
        ('non_stop', 'Non Stop'),
    ]

    CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('premium_economy', 'Premium Economy'),
        ('business', 'Business'),
    ]

    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES)
    route = models.CharField(max_length=50, null=True, blank=True)
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    duration = models.DateTimeField(null=True, blank=True)
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    infants_on_lap = models.PositiveIntegerField(default=0)
    travel_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    seat_preference = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        route_str = str(self.route) if self.route else "No Route"
        return f"{route_str} ({self.trip_type})"


class Passenger(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name="passengers")
    title = models.CharField(max_length=10, default="N/A")
    first_name = models.CharField(max_length=100, null=False, blank=False)
    middle_initial = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    dob = models.DateField(null=False, blank=False)
    nationality = models.CharField(max_length=100, null=False, blank=False)
    passport = models.CharField(max_length=50, null=False, blank=False)
    has_declaration = models.BooleanField(default=False)
    is_pwd = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class MultiCityLeg(models.Model):
    booking = models.ForeignKey("Booking", on_delete=models.CASCADE, related_name="legs")
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField()
    duration = models.DateTimeField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.origin} → {self.destination}"