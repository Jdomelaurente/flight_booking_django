# instructorapp/models.py
from django.db import models
from django.utils import timezone
import random
import string
from flightapp.models import Student, User
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)




class Section(models.Model):
    section_name = models.CharField(max_length=200)
    section_code = models.CharField(max_length=50, unique=True)
    semester = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    schedule = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.section_code} - {self.section_name}"

    def enrolled_students_count(self):
        return self.enrollments.filter(is_active=True).count()

class SectionEnrollment(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='section_enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['section', 'student']

    def __str__(self):
        return f"{self.student.student_number} - {self.section.section_code}"

class Activity(models.Model):
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    activity_type = models.CharField(max_length=50, default='Flight Booking')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='activities')
    
    # Flight Booking Requirements (based on flightapp models)
    required_trip_type = models.CharField(
        max_length=20,
        choices=[
            ("one_way", "One Way"),
            ("round_trip", "Round Trip"), 
            ("multi_city", "Multi City")
        ],
        default='one_way'
    )
    required_origin = models.CharField(max_length=100, blank=True)
    required_destination = models.CharField(max_length=100, blank=True)
    required_departure_date = models.DateField(null=True, blank=True)
    required_return_date = models.DateField(null=True, blank=True)
    required_travel_class = models.CharField(
        max_length=20,
        choices=[
            ('economy', 'Economy'),
            ('premium_economy', 'Premium Economy'),
            ('business', 'Business'),
            ('first', 'First Class'),
        ],
        default='economy'
    )
    
    # Passenger Requirements
    required_passengers = models.PositiveIntegerField(default=1)  # Adults
    required_children = models.PositiveIntegerField(default=0)    # Children (2-11 years)
    required_infants = models.PositiveIntegerField(default=0)     # Infants (under 2 years)
    
    # Passenger Information Requirements
    require_passenger_details = models.BooleanField(default=True)
    
    required_max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Instructions & Timing
    instructions = models.TextField()
    total_points = models.DecimalField(max_digits=6, decimal_places=2, default=100.00)
    due_date = models.DateTimeField()
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Code System
    activity_code = models.CharField(max_length=8, unique=True, blank=True, null=True)
    is_code_active = models.BooleanField(default=False)
    code_generated_at = models.DateTimeField(null=True, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['-created_at']

    def generate_activity_code(self):
        """Generate a unique 6-character alphanumeric code"""
        while True:
            characters = string.ascii_uppercase + string.digits
            code = ''.join(random.choice(characters) for _ in range(6))
            if not Activity.objects.filter(activity_code=code).exists():
                return code

    def activate_code(self, expiration_hours=24):
        """Activate the activity code with expiration"""
        if not self.activity_code:
            self.activity_code = self.generate_activity_code()
        
        self.is_code_active = True
        self.code_generated_at = timezone.now()
        self.code_expires_at = timezone.now() + timezone.timedelta(hours=expiration_hours)
        self.status = 'published'
        self.save()

    def get_total_passengers(self):
        """Get total number of passengers including adults, children, and infants"""
        return self.required_passengers + self.required_children + self.required_infants

    def __str__(self):
        return f"{self.title} - {self.section.section_code}"

class ActivityPassenger(models.Model):
    """Model to store passenger details for activities"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)
    
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.activity.title}"
    
    def get_passenger_type(self):
        """Determine passenger type based on age (simplified)"""
        # This is a simplified version - you might want to calculate actual age
        if self.is_primary:
            return "Adult (Primary)"
        return "Adult"

class ActivitySubmission(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activity_submissions')
    booking = models.ForeignKey('flightapp.Booking', on_delete=models.CASCADE, related_name='activity_submissions', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, null=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Submitted'),
            ('graded', 'Graded'),
            ('late', 'Late Submission'),
        ],
        default='submitted'
    )

    required_origin_airport = models.ForeignKey(
        'flightapp.Airport', 
        on_delete=models.CASCADE, 
        related_name='activity_origins',
        null=True, 
        blank=True
    )
    required_destination_airport = models.ForeignKey(
        'flightapp.Airport', 
        on_delete=models.CASCADE, 
        related_name='activity_destinations',
        null=True, 
        blank=True
    )
    
    # Make sure these fields exist:
    required_trip_type = models.CharField(
        max_length=20,
        choices=[
            ("one_way", "One Way"),
            ("round_trip", "Round Trip"), 
        ],
        default='one_way'
    )
    required_travel_class = models.CharField(
        max_length=20,
        choices=[
            ('economy', 'Economy'),
            ('premium_economy', 'Premium Economy'),
            ('business', 'Business'),
            ('first', 'First Class'),
        ],
        default='economy'
    )
    required_passengers = models.PositiveIntegerField(default=1)
    required_children = models.PositiveIntegerField(default=0)
    required_infants = models.PositiveIntegerField(default=0)
    require_passenger_details = models.BooleanField(default=True)
    required_max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    class Meta:
        unique_together = ['activity', 'student']

    def __str__(self):
        return f"{self.student.student_number} - {self.activity.title}"
    


@receiver(post_save, sender=ActivitySubmission)
def log_activity_submission(sender, instance, created, **kwargs):
    if created:
        logger.info(f"NEW ACTIVITY SUBMISSION CREATED: "
                   f"ID: {instance.id}, "
                   f"Activity: {instance.activity.title}, "
                   f"Student: {instance.student.first_name} {instance.student.last_name}, "
                   f"Booking: {instance.booking.id if instance.booking else 'None'}")
        print(f"✅ AUTOMATIC LOG: ActivitySubmission {instance.id} created!")    