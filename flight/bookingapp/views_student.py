from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.template import loader
from datetime import datetime
from flightapp.models import Schedule, Route, Airport, Seat, PassengerInfo, Flight, Airline
from flightapp.models import Booking, BookingDetail, Payment, PassengerInfo, Student, AddOn, SeatClass
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from datetime import date
from django.views.decorators.cache import never_cache
from .utils import login_required, redirect_if_logged_in
from instructorapp.models import Section, SectionEnrollment, Activity, ActivitySubmission, PracticeBooking, ActivityAddOn  # ADD Section HERE
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal
from django.db.models import Avg, Count, Sum, Q  # Add this for grade calculations
from .utils import (
    login_required, redirect_if_logged_in, 
    calculate_activity_score, evaluate_passenger_information_quality,
    evaluate_flight_route_compliance, get_booking_details,
    get_detailed_comparison
)



@login_required
def debug_score_breakdown(request, submission_id):
    """Show EXACT score breakdown from calculate_activity_score"""
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        submission = ActivitySubmission.objects.get(id=submission_id, student=student)
        activity = submission.activity
        booking = submission.booking
        
        print("=== EXACT SCORING BREAKDOWN ===")
        
        # Let's manually trace through the EXACT same logic as calculate_activity_score
        total_points = float(activity.total_points)  # Should be 100.0
        
        # CORRECT WEIGHTS from your function
        base_weight = 0.20              # 20%
        passenger_info_weight = 0.10    # 10%  
        flight_route_weight = 0.10      # 10%
        trip_type_weight = 0.15         # 15%
        travel_class_weight = 0.15      # 15%
        passenger_count_weight = 0.20   # 20%
        addon_weight = 0.10             # 10%
        
        print(f"TOTAL POINTS: {total_points}")
        
        # 1. Base points (20%)
        base_points = total_points * base_weight  # 100 * 0.20 = 20.0
        print(f"1. BASE POINTS: {base_points}")
        
        # 2. Passenger Information Quality (10%)
        from .utils import evaluate_passenger_information_quality
        passenger_info_score = 0.90  # From your debug output
        passenger_info_points = total_points * passenger_info_weight  # 100 * 0.10 = 10.0
        passenger_info_earned = passenger_info_points * passenger_info_score  # 10.0 * 0.90 = 9.0
        passenger_info_earned = round(passenger_info_earned, 2)  # 9.0
        print(f"2. PASSENGER INFO: {passenger_info_earned} (quality: {passenger_info_score})")
        
        # 3. Flight Route Compliance (10%)
        from .utils import evaluate_flight_route_compliance
        flight_route_score = 1.0  # From your debug - both origin and destination match
        flight_route_points = total_points * flight_route_weight  # 100 * 0.10 = 10.0
        flight_route_earned = flight_route_points * flight_route_score  # 10.0 * 1.0 = 10.0
        print(f"3. FLIGHT ROUTE: {flight_route_earned} (score: {flight_route_score})")
        
        # 4. Trip Type Compliance (15%)
        trip_type_match = True  # From your data
        trip_type_points = total_points * trip_type_weight  # 100 * 0.15 = 15.0
        trip_type_earned = trip_type_points if trip_type_match else 0  # 15.0
        print(f"4. TRIP TYPE: {trip_type_earned} (match: {trip_type_match})")
        
        # 5. Travel Class Compliance (15%)
        has_correct_class = True  # From your data
        travel_class_points = total_points * travel_class_weight  # 100 * 0.15 = 15.0
        travel_class_earned = travel_class_points if has_correct_class else 0  # 15.0
        print(f"5. TRAVEL CLASS: {travel_class_earned} (correct: {has_correct_class})")
        
        # 6. Passenger Count Compliance (20%)
        # From your data: 1 adult, 0 children, 0 infants - all match requirements
        passenger_count_points = total_points * passenger_count_weight  # 100 * 0.20 = 20.0
        
        # Since all counts match perfectly, should get full 20 points
        adult_points_ratio = 0.5  # 50% for adults
        child_points_ratio = 0.3  # 30% for children  
        infant_points_ratio = 0.2  # 20% for infants
        
        adult_points = passenger_count_points * adult_points_ratio * 1.0  # 20.0 * 0.5 * 1.0 = 10.0
        child_points = passenger_count_points * child_points_ratio * 1.0  # 20.0 * 0.3 * 1.0 = 6.0
        infant_points = passenger_count_points * infant_points_ratio * 1.0  # 20.0 * 0.2 * 1.0 = 4.0
        
        passenger_count_earned = adult_points + child_points + infant_points  # 10.0 + 6.0 + 4.0 = 20.0
        print(f"6. PASSENGER COUNT: {passenger_count_earned}")
        print(f"   - Adults: 10.0")
        print(f"   - Children: 6.0") 
        print(f"   - Infants: 4.0")
        
        # 7. Add-ons (10%)
        addon_points = total_points * addon_weight  # 100 * 0.10 = 10.0
        addon_score = 0.0  # From your debug - no add-ons selected
        print(f"7. ADD-ONS: {addon_score}")
        
        # CALCULATE TOTAL
        total_calculated = (
            base_points + 
            passenger_info_earned + 
            flight_route_earned + 
            trip_type_earned + 
            travel_class_earned + 
            passenger_count_earned + 
            addon_score
        )
        
        print(f"EXPECTED BREAKDOWN:")
        print(f"Base: 20.0")
        print(f"Passenger Info: 9.0") 
        print(f"Flight Route: 10.0")
        print(f"Trip Type: 15.0")
        print(f"Travel Class: 15.0")
        print(f"Passenger Count: 20.0")
        print(f"Add-ons: 0.0")
        print(f"TOTAL: {total_calculated}")
        print(f"DATABASE SCORE: {submission.score}")
        
        # Check if there's rounding somewhere
        if abs(total_calculated - float(submission.score)) > 0.01:
            print(f"❌ DISCREPANCY FOUND: {total_calculated} vs {submission.score}")
            print(f"Difference: {total_calculated - float(submission.score)}")
        
        return HttpResponse(f"""
        <h2>Exact Score Breakdown</h2>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr><th>Category</th><th>Points</th><th>Weight</th></tr>
            <tr><td>Base Completion</td><td>20.0</td><td>20%</td></tr>
            <tr><td>Passenger Information</td><td>9.0</td><td>10% (90% quality)</td></tr>
            <tr><td>Flight Route</td><td>10.0</td><td>10%</td></tr>
            <tr><td>Trip Type</td><td>15.0</td><td>15%</td></tr>
            <tr><td>Travel Class</td><td>15.0</td><td>15%</td></tr>
            <tr><td>Passenger Count</td><td>20.0</td><td>20%</td></tr>
            <tr><td>Add-ons</td><td>0.0</td><td>10%</td></tr>
            <tr style="font-weight: bold;"><td>TOTAL CALCULATED</td><td>{total_calculated}</td><td>100%</td></tr>
            <tr style="font-weight: bold; color: blue;"><td>DATABASE SCORE</td><td>{submission.score}</td><td></td></tr>
        </table>
        <p><em>Check console for detailed analysis</em></p>
        """)
        
    except Exception as e:
        print(f"Debug error: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {e}")
    



def evaluate_passport_compliance(booking, activity):
    """
    Evaluate passport compliance for ALL passengers when required
    Returns a score between 0 and 1
    """
    print("=== PASSPORT COMPLIANCE EVALUATION ===")
    
    booking_details = booking.details.all()
    total_passengers = len(booking_details)
    
    if total_passengers == 0:
        return 0.0
    
    passengers_with_passport = 0
    
    for detail in booking_details:
        passenger = detail.passenger
        
        # Check if passenger has valid passport information
        has_passport = (
            passenger.passport_number and 
            passenger.passport_number.strip() and
            len(passenger.passport_number.strip()) >= 5  # Basic validation for passport number length
        )
        
        if has_passport:
            passengers_with_passport += 1
            print(f"✅ {passenger.first_name} {passenger.last_name}: Has passport '{passenger.passport_number}'")
        else:
            print(f"❌ {passenger.first_name} {passenger.last_name}: Missing or invalid passport")
    
    compliance_score = passengers_with_passport / total_passengers if total_passengers > 0 else 0.0
    
    print(f"Passport compliance: {passengers_with_passport}/{total_passengers} passengers -> {compliance_score * 100}%")
    print("=====================================")
    
    return compliance_score

def evaluate_flight_route_compliance(booking, activity):
    """Evaluate if the flight route matches activity requirements"""
    score = 1.0  # Start with perfect score
    
    # Get the first booking detail to check route
    first_detail = booking.details.first()
    if not first_detail:
        return 0.0
    
    route = first_detail.schedule.flight.route
    
    # Check origin
    if hasattr(activity, 'required_origin') and activity.required_origin:
        if route.origin_airport.code != activity.required_origin:
            score -= 0.5  # Lose 50% for wrong origin
            print(f"❌ Origin mismatch: required {activity.required_origin}, got {route.origin_airport.code}")
        else:
            print(f"✅ Origin match: {activity.required_origin}")
    
    # Check destination  
    if hasattr(activity, 'required_destination') and activity.required_destination:
        if route.destination_airport.code != activity.required_destination:
            score -= 0.5  # Lose 50% for wrong destination
            print(f"❌ Destination mismatch: required {activity.required_destination}, got {route.destination_airport.code}")
        else:
            print(f"✅ Destination match: {activity.required_destination}")
    
    return max(score, 0.0)  # Ensure score doesn't go below 0

def get_instructor_display_name(instructor_user):
    """Safely get instructor display name from User object"""
    if not instructor_user:
        return "Not assigned"
    
    try:
        # Check if there's an instructor profile linked
        if hasattr(instructor_user, 'instructor_profile') and instructor_user.instructor_profile:
            instructor_profile = instructor_user.instructor_profile
            
            # Build the name from Instructor model fields
            name_parts = []
            if instructor_profile.first_name:
                name_parts.append(instructor_profile.first_name)
            if instructor_profile.middle_initial:
                name_parts.append(f"{instructor_profile.middle_initial}.")
            if instructor_profile.last_name:
                name_parts.append(instructor_profile.last_name)
            
            if name_parts:
                return " ".join(name_parts)
        
        # Fall back to User model fields
        if instructor_user.first_name and instructor_user.last_name:
            return f"{instructor_user.first_name} {instructor_user.last_name}"
        
        # Final fallback to username
        return instructor_user.username
        
    except Exception as e:
        print(f"Error getting instructor display name: {e}")
        return instructor_user.username if instructor_user else "Not assigned"

@login_required
def student_home(request):
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        
        # Get student's enrolled sections with instructor information
        enrolled_sections = SectionEnrollment.objects.filter(
            student=student, 
            is_active=True
        ).select_related(
            'section', 
            'section__instructor',  # This gets the Instructor instance
            'section__instructor__user'  # This gets the User instance linked to Instructor
        )

        # Rest of your view code remains the same...
        activities = Activity.objects.filter(
            section__in=[enrollment.section for enrollment in enrolled_sections],
            is_code_active=True,
            status='published'
        ).select_related('section', 'section__instructor', 'section__instructor__user')
        
        submitted_activities = ActivitySubmission.objects.filter(
            student=student,
            activity__in=activities
        ).values_list('activity_id', flat=True)
        
        template = loader.get_template('booking/student/home.html')
        context = {
            'activities': activities,
            'student': student,
            'submitted_activities': list(submitted_activities),
            'enrolled_sections': enrolled_sections,
        }
        return HttpResponse(template.render(context, request))
        
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('bookingapp:login')


@login_required
def student_activity_detail(request, activity_id):
    student_id = request.session.get('student_id')
    
    if not student_id:
        messages.error(request, "Please log in to access this activity.")
        return redirect('bookingapp:login')
    
    try:
        print(f"=== DEBUG: Loading activity {activity_id} for student {student_id} ===")
        
        activity = get_object_or_404(Activity, id=activity_id, status='published')
        student = Student.objects.get(id=student_id)
        
        print(f"Activity found: {activity.title}")
        print(f"Student found: {student.first_name} {student.last_name}")
        
        # Check if student is enrolled in this section
        enrollment_check = SectionEnrollment.objects.filter(
            section=activity.section, 
            student=student, 
            is_active=True
        ).exists()
        
        print(f"Enrollment check: {enrollment_check}")
        
        if not enrollment_check:
            messages.error(request, "You are not enrolled in this section.")
            return redirect('studentapp:student_home')
        
        # Check if student has already submitted
        existing_submission = ActivitySubmission.objects.filter(
            activity=activity, 
            student=student
        ).first()
        
        print(f"Existing submission: {existing_submission}")
        
        # Get pre-defined passengers for this activity
        try:
            passengers = activity.passengers.all()
            print(f"Predefined passengers: {passengers.count()}")
        except Exception as e:
            print(f"Error getting passengers: {e}")
            passengers = []
        
        # Handle code verification if form was submitted
        code_error = None
        if request.method == 'POST' and 'verify_code' in request.POST:
            entered_code = request.POST.get('activity_code', '').strip().upper()
            
            # Validate code format
            if not entered_code:
                code_error = "Please enter an activity code."
            elif len(entered_code) != 6:
                code_error = "Activity code must be 6 characters long."
            elif entered_code == activity.activity_code:
                # Code is correct - redirect to main booking page with activity context
                messages.success(request, "Activity code verified successfully! You can now start your booking.")
                return redirect(f"{reverse('bookingapp:main')}?activity_id={activity.id}&activity_code={entered_code}")
            else:
                code_error = "Invalid activity code. Please check the code and try again."
        
        template = loader.get_template('booking/student/activity_detail.html')
        context = {
            'activity': activity,
            'student': student,
            'existing_submission': existing_submission,
            'passengers': passengers,
            'code_active': activity.is_code_active,
            'code_expired': activity.is_due_date_passed,
            'code_error': code_error,
        }
        
        print("=== DEBUG: Successfully built context, rendering template ===")
        return HttpResponse(template.render(context, request))
        
    except Activity.DoesNotExist:
        print(f"Activity.DoesNotExist: Activity {activity_id} not found")
        messages.error(request, "Activity not found or not available.")
        return redirect('studentapp:student_home')
    except Student.DoesNotExist:
        print(f"Student.DoesNotExist: Student {student_id} not found")
        messages.error(request, "Student information not found.")
        return redirect('bookingapp:login')
    except Exception as e:
        print(f"General Exception in student_activity_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"An error occurred while loading the activity: {str(e)}")
        return redirect('studentapp:student_home')
    
    
    
def validate_booking_for_activity(booking, activity):
    """Validate if the booking meets activity requirements"""
    try:
        print(f"=== VALIDATION DEBUG ===")
        print(f"Booking ID: {booking.id}")
        print(f"Activity: {activity.title}")
        
        # Check if booking has details
        if not booking.details.exists():
            print("❌ No booking details")
            return False
            
        # Check trip type
        if booking.trip_type != activity.required_trip_type:
            print(f"❌ Trip type mismatch: {booking.trip_type} vs {activity.required_trip_type}")
            return False
            
        # Get all passengers from booking
        booking_passengers = booking.details.all()
        
        # Count passenger types
        adult_count = 0
        child_count = 0
        infant_count = 0
        
        for detail in booking_passengers:
            passenger_type = detail.passenger.passenger_type.lower()
            if passenger_type == 'adult':
                adult_count += 1
            elif passenger_type == 'child':
                child_count += 1
            elif passenger_type == 'infant':
                infant_count += 1
        
        print(f"Passenger counts - Adults: {adult_count}, Children: {child_count}, Infants: {infant_count}")
        print(f"Required - Adults: {activity.required_passengers}, Children: {activity.required_children}, Infants: {activity.required_infants}")
        
        # Check passenger counts
        if (adult_count != activity.required_passengers or 
            child_count != activity.required_children or 
            infant_count != activity.required_infants):
            print("❌ Passenger count mismatch")
            return False
            
        # Check total price if max price is specified
        # if activity.required_max_price:
        #     total_amount = sum(detail.price for detail in booking_passengers if detail.passenger.passenger_type.lower() != 'infant')
        #     print(f"Total amount: {total_amount}, Max allowed: {activity.required_max_price}")
        #     if total_amount > activity.required_max_price:
        #         print("❌ Price exceeds maximum")
        #         return False
        
        print("✅ Validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False
    


@login_required
def student_activities(request):
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        
        # Get student's enrolled sections
        enrolled_sections = SectionEnrollment.objects.filter(
            student=student, 
            is_active=True
        ).select_related('section', 'section__instructor', 'section__instructor__user')
        
        # Get all activities from enrolled sections
        all_activities = Activity.objects.filter(
            section__in=[enrollment.section for enrollment in enrolled_sections]
        ).select_related('section', 'section__instructor', 'section__instructor__user')
        
        # Get submitted activities
        submitted_activities = ActivitySubmission.objects.filter(
            student=student
        ).select_related('activity', 'booking')
        
        # DEBUG PRINT
        print(f"=== STUDENT ACTIVITIES DEBUG ===")
        print(f"Student: {student.first_name} {student.last_name}")
        print(f"Total activities: {all_activities.count()}")
        print(f"Submitted activities: {submitted_activities.count()}")
        
        for submission in submitted_activities:
            print(f"Submission: {submission.id} - Activity: {submission.activity.title} - Activity ID: {submission.activity.id}")
        
        for activity in all_activities:
            has_submission = submitted_activities.filter(activity=activity).exists()
            print(f"Activity: {activity.title} (ID: {activity.id}) - Has submission: {has_submission}")
        
        template = loader.get_template('booking/student/activities.html')
        context = {
            'all_activities': all_activities,
            'student': student,
            'submitted_activities': submitted_activities,
            'enrolled_sections': enrolled_sections,
            
        }
        return HttpResponse(template.render(context, request))
        
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('bookingapp:login')

# Add this helper function to get instructor name properly
def get_instructor_full_name(instructor):
    """Get full name from Instructor instance"""
    if not instructor:
        return "Not assigned"
    
    name_parts = []
    if instructor.first_name:
        name_parts.append(instructor.first_name)
    if instructor.middle_initial:
        name_parts.append(f"{instructor.middle_initial}.")
    if instructor.last_name:
        name_parts.append(instructor.last_name)
    
    return " ".join(name_parts) if name_parts else instructor.user.username


# Add this import at the top with other imports
from django.db.models import Avg, Count, Sum, Q
from decimal import Decimal

# Add this function after the existing views, before the test views

@login_required
def student_section_grade_report(request, section_id, student_id):
    """
    Generate a comprehensive grade report for a specific student in a section
    """
    # Get section and student
    section = get_object_or_404(Section, id=section_id)
    student = get_object_or_404(Student, id=student_id)
    
    # Verify the requesting student can only view their own report
    current_student_id = request.session.get('student_id')
    if not current_student_id or int(current_student_id) != int(student_id):
        messages.error(request, "You can only view your own grade reports.")
        return redirect('studentapp:student_home')
    
    # Verify enrollment
    enrollment = get_object_or_404(
        SectionEnrollment, 
        section=section, 
        student=student, 
        is_active=True
    )
    
    # Get all activities for this section
    activities = Activity.objects.filter(section=section).prefetch_related(
        'submissions__student',
        'activity_addons'
    ).order_by('due_date')
    
    # Get submissions for this student
    submissions = ActivitySubmission.objects.filter(
        activity__section=section,
        student=student
    ).select_related('activity')
    
    # Calculate statistics
    total_activities = activities.count()
    completed_activities = submissions.count()
    
    # Calculate completion percentage
    completion_percentage = (completed_activities / total_activities * 100) if total_activities > 0 else 0
    
    # Calculate average score (only for graded submissions)
    graded_submissions = submissions.exclude(score__isnull=True)
    average_score = graded_submissions.aggregate(
        avg_score=Avg('score')
    )['avg_score'] or 0
    
    # Count late submissions
    late_submissions = submissions.filter(status='late').count()
    
    # Calculate overall percentage (weighted average)
    total_possible_points = sum(float(activity.total_points) for activity in activities)
    total_earned_points = sum(
        float(submission.total_score_with_addons) 
        for submission in submissions 
        if submission.score is not None
    )
    
    overall_percentage = (total_earned_points / total_possible_points * 100) if total_possible_points > 0 else 0
    
    # Calculate letter grade
    letter_grade = calculate_letter_grade(overall_percentage)
    
    # Prepare context for template
    context = {
        'section': section,
        'student': student,
        'enrollment': enrollment,
        'activities': activities,
        'submissions': submissions,
        'total_activities': total_activities,
        'completed_activities': completed_activities,
        'completion_percentage': completion_percentage,
        'average_score': average_score,
        'late_submissions': late_submissions,
        'overall_percentage': overall_percentage,
        'letter_grade': letter_grade,
        'total_earned_points': total_earned_points,
        'total_possible_points': total_possible_points,
    }
    
    return render(request, 'booking/student/section_grade_report.html', context)

def calculate_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 97: return 'A+'
    elif percentage >= 93: return 'A'
    elif percentage >= 90: return 'A-'
    elif percentage >= 87: return 'B+'
    elif percentage >= 83: return 'B'
    elif percentage >= 80: return 'B-'
    elif percentage >= 77: return 'C+'
    elif percentage >= 73: return 'C'
    elif percentage >= 70: return 'C-'
    elif percentage >= 67: return 'D+'
    elif percentage >= 63: return 'D'
    elif percentage >= 60: return 'D-'
    else: return 'F'





from django.contrib import messages
from django.shortcuts import render, redirect
from flightapp.models import Student
from django.contrib.auth.hashers import make_password

@redirect_if_logged_in
def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Required fields
        if not all([first_name, last_name, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return redirect('bookingapp:register')

        # Password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('bookingapp:register')

        # Check email uniqueness
        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please use a different email.")
            return redirect('bookingapp:register')

        try:
            # Generate student number
            student_count = Student.objects.count()
            student_number = f"STU{student_count + 1:04d}"

            # Create student with hashed password
            student = Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone if phone else None,  # Handle optional phone
                password=make_password(password),  # Hash the password
                student_number=student_number
            )

            messages.success(request, "Registration successful! Please login.")
            return redirect('bookingapp:login')

        except Exception as e:
            messages.error(request, "An error occurred during registration. Please try again.")
            print(f"Registration error: {e}")

        messages.success(request, "Registration successful! Please login.")
        return redirect('bookingapp:login')
    
    template = loader.get_template("booking/auth/register.html")

    context = {

    }

    return HttpResponse(template.render(context, request))

from django.contrib.auth.hashers import check_password

@redirect_if_logged_in
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email').strip()
        password = request.POST.get('password')

        # Basic validation
        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect('bookingapp:login')

        try:
            student = Student.objects.get(email=email)
            if check_password(password, student.password):
                request.session['student_id'] = student.id
                messages.success(request, f"Welcome {student.first_name}!")
                # Redirect to student dashboard
                return redirect('studentapp:student_home')
            else:
                messages.error(request, "Incorrect password.")
        except Student.DoesNotExist:
            messages.error(request, "Email not registered.")
        except Exception as e:
            messages.error(request, "An error occurred during login. Please try again.")
            print(f"Login error: {e}")    

    template = loader.get_template("booking/auth/login.html")
    context = {}
    return HttpResponse(template.render(context, request))


def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('bookingapp:login')




# Add to bookingapp/views.py
@login_required
def debug_student_activities(request):
    """Debug view to check student's available activities"""
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('bookingapp:login')
    
    student = Student.objects.get(id=student_id)
    
    print("=== STUDENT ACTIVITIES DEBUG ===")
    print(f"Student: {student.first_name} {student.last_name} (ID: {student.id})")
    
    # Get enrolled sections
    enrolled_sections = SectionEnrollment.objects.filter(
        student=student, 
        is_active=True
    ).select_related('section')
    
    print("Enrolled sections:")
    for enrollment in enrolled_sections:
        print(f"  - {enrollment.section.section_code}: {enrollment.section.section_name}")
    
    # Get active activities
    activities = Activity.objects.filter(
        section__in=[enrollment.section for enrollment in enrolled_sections],
        is_code_active=True,
        status='published'
    )
    
    print("Available activities:")
    for activity in activities:
        print(f"  - {activity.id}: {activity.title} (Code: {activity.activity_code})")
        print(f"    Section: {activity.section.section_code}")
        print(f"    Status: {activity.status}, Active: {activity.is_code_active}")
    
    return HttpResponse("Check console for debug output")

def get_booking_details(booking):
    """Get detailed information about what was actually booked"""
    print(f"=== GET_BOOKING_DETAILS DEBUG ===")
    print(f"Booking ID: {booking.id}")
    
    booking_details = booking.details.all().select_related(
        'passenger', 'schedule', 'schedule__flight', 'schedule__flight__route'
    )
    
    print(f"Found {booking_details.count()} booking details")
    
    details = {
        'passengers': [],
        'flights': {},
        'total_cost': 0,
        'seat_classes_used': set()
    }
    
    # Group by flight schedule
    flight_groups = {}
    for detail in booking_details:
        print(f"Processing detail: {detail.id} - Passenger: {detail.passenger.first_name}")
        schedule_id = detail.schedule.id
        if schedule_id not in flight_groups:
            flight_groups[schedule_id] = {
                'schedule': detail.schedule,
                'passengers': [],
                'total_seats': 0
            }
        
        flight_groups[schedule_id]['passengers'].append({
            'passenger': detail.passenger,
            'seat_class': detail.seat_class,
            'seat_number': detail.seat.seat_number if detail.seat else 'Not assigned',
            'price': detail.price
        })
        flight_groups[schedule_id]['total_seats'] += 1
        
        # Add to overall details
        details['seat_classes_used'].add(detail.seat_class)
        if detail.passenger.passenger_type.lower() != 'infant':
            details['total_cost'] += float(detail.price)
    
    details['flights'] = flight_groups
    details['seat_classes_used'] = list(details['seat_classes_used'])
    
    print(f"Flight groups: {len(flight_groups)}")
    
    # Get all passengers with their details
    for detail in booking_details:
        passenger_info = {
            'name': f"{detail.passenger.first_name} {detail.passenger.last_name}",
            'type': detail.passenger.passenger_type,
            'date_of_birth': detail.passenger.date_of_birth,
            'gender': detail.passenger.gender,
            'passport': detail.passenger.passport_number,
            'nationality': detail.passenger.nationality,
            'flights': []
        }
        
        # Add flight details for this passenger
        for flight_group in flight_groups.values():
            for passenger in flight_group['passengers']:
                if passenger['passenger'].id == detail.passenger.id:
                    passenger_info['flights'].append({
                        'route': f"{flight_group['schedule'].flight.route.origin_airport.code} → {flight_group['schedule'].flight.route.destination_airport.code}",
                        'date': flight_group['schedule'].departure_time.date(),
                        'seat_class': passenger['seat_class'],
                        'seat_number': passenger['seat_number'],
                        'price': passenger['price']
                    })
        
        # Only add each passenger once
        if not any(p['name'] == passenger_info['name'] for p in details['passengers']):
            details['passengers'].append(passenger_info)
    
    print(f"Final passengers count: {len(details['passengers'])}")
    print(f"Final flights count: {len(details['flights'])}")
    print("=== END GET_BOOKING_DETAILS ===")
    
    return details



# Add to bookingapp/views.py

# @login_required
# def submission_detail(request, submission_id):
#     """Show detailed comparison between activity requirements and student submission"""
#     student_id = request.session.get('student_id')
    
#     if not student_id:
#         return redirect('bookingapp:login')
    
#     try:
#         print(f"=== ACCESSING SUBMISSION DETAIL ===")
#         print(f"Submission ID: {submission_id}")
#         print(f"Student ID: {student_id}")
        
#         student = Student.objects.get(id=student_id)
#         submission = get_object_or_404(ActivitySubmission, id=submission_id, student=student)
        
#         print(f"Found submission: {submission.id}")
#         print(f"Activity: {submission.activity.title}")
#         print(f"Booking: {submission.booking.id if submission.booking else 'No booking'}")
        
#         activity = submission.activity
#         booking = submission.booking
        
#         # Get comparison data
#         comparison_data = get_submission_comparison(submission, activity, booking)
#         booking_details = get_booking_details(booking)
        
#         print(f"Comparison data: {comparison_data is not None}")
#         print(f"Booking details: {booking_details is not None}")
        
#         # Use render instead of loader.get_template for better error handling
#         return render(request, 'booking/student/submission_detail.html', {
#             'submission': submission,
#             'activity': activity,
#             'booking': booking,
#             'comparison': comparison_data,
#             'booking_details': booking_details,
#             'student': student,
#         })
        
#     except ActivitySubmission.DoesNotExist:
#         print(f"Submission {submission_id} not found for student {student_id}")
#         messages.error(request, "Submission not found.")
#         return redirect('bookingapp:student_activities')
#     except Exception as e:
#         print(f"Error in submission_detail: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         messages.error(request, f"Error loading submission: {str(e)}")
#         return redirect('bookingapp:student_activities')
    



def get_submission_comparison(submission, activity, booking):
    """Generate detailed comparison between requirements and submission"""
    
    # Get booking details
    booking_details = booking.details.all()
    booking_info = get_booking_details(booking)
    
    # Count passenger types in booking
    adult_count = 0
    child_count = 0
    infant_count = 0
    total_price = booking_info['total_cost']
    
    for passenger in booking_info['passengers']:
        passenger_type = passenger['type'].lower()
        if passenger_type == 'adult':
            adult_count += 1
        elif passenger_type == 'child':
            child_count += 1
        elif passenger_type == 'infant':
            infant_count += 1
    
    # Check travel class compliance
    has_correct_class = any(
        seat_class.lower() == activity.required_travel_class.lower() 
        for seat_class in booking_info['seat_classes_used']
    )
    
    # Get actual seat classes used
    actual_classes = ", ".join([cls.title() for cls in booking_info['seat_classes_used']])
    
    # Calculate deductions with specific details
    deductions = []
    recommendations = []
    
    # Passenger count deductions
    if adult_count != activity.required_passengers:
        deductions.append({
            'category': 'Passenger Count',
            'issue': f'Adults: Required {activity.required_passengers}, You booked {adult_count}',
            'details': f'You booked {adult_count} adult(s) but the activity required {activity.required_passengers} adult(s)',
            'points_lost': 'Up to 15%',
            'type': 'passenger_count'
        })
        recommendations.append(f"Book exactly {activity.required_passengers} adult passenger(s) for full points")
    
    if child_count != activity.required_children:
        deductions.append({
            'category': 'Passenger Count', 
            'issue': f'Children: Required {activity.required_children}, You booked {child_count}',
            'details': f'You booked {child_count} child(ren) but the activity required {activity.required_children} child(ren)',
            'points_lost': 'Up to 9%',
            'type': 'passenger_count'
        })
        recommendations.append(f"Book exactly {activity.required_children} child passenger(s) for full points")
    
    if infant_count != activity.required_infants:
        deductions.append({
            'category': 'Passenger Count',
            'issue': f'Infants: Required {activity.required_infants}, You booked {infant_count}',
            'details': f'You booked {infant_count} infant(s) but the activity required {activity.required_infants} infant(s)',
            'points_lost': 'Up to 6%',
            'type': 'passenger_count'
        })
        recommendations.append(f"Book exactly {activity.required_infants} infant passenger(s) for full points")
    
    # Price compliance
    # if activity.required_max_price and total_price > float(activity.required_max_price):
    #     overage_amount = total_price - float(activity.required_max_price)
    #     overage_percentage = (overage_amount / float(activity.required_max_price)) * 100
    #     deductions.append({
    #         'category': 'Budget',
    #         'issue': f'Budget exceeded by ${overage_amount:.2f}',
    #         'details': f'Your booking cost ${total_price:.2f} but the maximum allowed was ${activity.required_max_price} (${overage_amount:.2f} over budget)',
    #         'points_lost': 'Up to 20%',
    #         'type': 'budget'
    #     })
    #     recommendations.append(f"Look for cheaper flight options or different travel dates to stay within ${activity.required_max_price} budget")
    
    # Travel class compliance
    if not has_correct_class:
        deductions.append({
            'category': 'Travel Class',
            'issue': f'Required {activity.required_travel_class.title()}, You booked {actual_classes}',
            'details': f'The activity required {activity.required_travel_class.title()} class, but you booked {actual_classes}',
            'points_lost': 'Up to 10%',
            'type': 'travel_class'
        })
        recommendations.append(f"Select {activity.required_travel_class.title()} class when booking flights for this activity")
    
    # Trip type compliance
    if booking.trip_type != activity.required_trip_type:
        deductions.append({
            'category': 'Trip Type',
            'issue': f'Required {activity.required_trip_type.title()}, You booked {booking.trip_type.title()}',
            'details': f'The activity required a {activity.required_trip_type.title()} trip, but you booked a {booking.trip_type.title()} trip',
            'points_lost': 'Up to 10%',
            'type': 'trip_type'
        })
        recommendations.append(f"Select {activity.required_trip_type.title()} trip type when searching for flights")
    
    # Check if origin/destination match
    if hasattr(activity, 'required_origin') and activity.required_origin:
        # Get first flight's origin
        first_flight = next(iter(booking_info['flights'].values()), None)
        if first_flight:
            booked_origin = first_flight['schedule'].flight.route.origin_airport.code
            if booked_origin != activity.required_origin:
                deductions.append({
                    'category': 'Flight Route',
                    'issue': f'Origin: Required {activity.required_origin}, You booked from {booked_origin}',
                    'details': f'The activity required flights from {activity.required_origin}, but you booked from {booked_origin}',
                    'points_lost': 'Up to 10%',
                    'type': 'route'
                })
                recommendations.append(f"Start your flight search from {activity.required_origin} airport")
    
    if hasattr(activity, 'required_destination') and activity.required_destination:
        # Get first flight's destination
        first_flight = next(iter(booking_info['flights'].values()), None)
        if first_flight:
            booked_destination = first_flight['schedule'].flight.route.destination_airport.code
            if booked_destination != activity.required_destination:
                deductions.append({
                    'category': 'Flight Route',
                    'issue': f'Destination: Required {activity.required_destination}, You booked to {booked_destination}',
                    'details': f'The activity required flights to {activity.required_destination}, but you booked to {booked_destination}',
                    'points_lost': 'Up to 10%',
                    'type': 'route'
                })
                recommendations.append(f"Search for flights going to {activity.required_destination} airport")
    
    return {
        'passenger_comparison': {
            'required_adults': activity.required_passengers,
            'submitted_adults': adult_count,
            'required_children': activity.required_children,
            'submitted_children': child_count,
            'required_infants': activity.required_infants,
            'submitted_infants': infant_count,
            'adults_match': adult_count == activity.required_passengers,
            'children_match': child_count == activity.required_children,
            'infants_match': infant_count == activity.required_infants,
        },
        'price_comparison': {
            'submitted_total': total_price,
            'within_budget': True,  # Always true since budget is removed
            'overage': 0,  # Always 0 since budget is removed
        },
        'flight_comparison': {
            'required_trip_type': activity.required_trip_type,
            'submitted_trip_type': booking.trip_type,
            'trip_type_match': booking.trip_type == activity.required_trip_type,
            'required_travel_class': activity.required_travel_class,
            'actual_travel_classes': actual_classes,
            'has_correct_class': has_correct_class,
            'required_origin': getattr(activity, 'required_origin', None),
            'required_destination': getattr(activity, 'required_destination', None),
        },
        'deductions': deductions,
        'recommendations': recommendations,
        'score_breakdown': {
            'base_points': float(activity.total_points) * 0.3,
            'passenger_points': calculate_passenger_points(adult_count, child_count, infant_count, activity),
            'price_points': calculate_price_points(total_price, activity),
            'compliance_points': calculate_compliance_points(booking, activity, has_correct_class),
        }
    }

def calculate_passenger_points(adult_count, child_count, infant_count, activity):
    """Calculate points for passenger requirements"""
    total_points = float(activity.total_points) * 0.3
    match_percentage = 0
    
    if adult_count == activity.required_passengers:
        match_percentage += 0.5
    if child_count == activity.required_children:
        match_percentage += 0.3
    if infant_count == activity.required_infants:
        match_percentage += 0.2
    
    return total_points * match_percentage

def calculate_price_points(total_price, activity):
    """Calculate points for price compliance - now always full points"""
    return float(activity.total_points) * 0.2  # Always full points since budget is removed

def calculate_compliance_points(booking, activity, has_correct_class):
    """Calculate points for trip type and travel class compliance"""
    compliance_points = float(activity.total_points) * 0.2
    match_percentage = 0
    
    if booking.trip_type == activity.required_trip_type:
        match_percentage += 0.5
    if has_correct_class:
        match_percentage += 0.5
    
    return compliance_points * match_percentage



@login_required
def student_work_detail(request, submission_id):
    """Detailed view showing student's work compared to activity requirements"""
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        submission = get_object_or_404(ActivitySubmission, id=submission_id, student=student)
        activity = submission.activity
        booking = submission.booking
        
        print(f"=== STUDENT WORK DETAIL DEBUG ===")
        print(f"Submission: {submission.id}")
        print(f"Activity: {activity.title}")
        print(f"Booking: {booking.id}")
        print(f"Submission Score: {submission.score}")
        print(f"Add-on Score: {submission.addon_score}")
        
        # Get detailed booking information
        booking_details = get_booking_details(booking)
        
        # Get comprehensive comparison data
        comparison_data = get_detailed_comparison(activity, booking, booking_details, submission)
        
        # Calculate add-on score
        addon_score, max_addon_points = submission.calculate_addon_score()
        
        # Update submission with add-on scores if not already set
        if not submission.addon_score:
            submission.addon_score = addon_score
            submission.max_addon_points = max_addon_points
            submission.save()
        
        # Get student's selected add-ons
        student_addons = submission.get_student_selected_addons()
        
        # Calculate overall compliance percentage
        total_requirements = len([req for req in comparison_data['requirements'] if not req.get('optional', False)])
        met_requirements = len([req for req in comparison_data['requirements'] if req.get('met', False) and not req.get('optional', False)])
        
        compliance_percentage = (met_requirements / total_requirements * 100) if total_requirements > 0 else 0
        
        # Get activity required add-ons for template
        activity_required_addons = [req.addon for req in activity.activity_addons.all()]
        
        # Get activity passengers (if any were predefined)
        activity_passengers = activity.passengers.all()
        
        # Get passenger-specific information
        passenger_details = []
        passenger_addons_data = {}
        
        if booking:
            print(f"=== BOOKING DEBUG ===")
            print(f"Booking ID: {booking.id}")
            print(f"Number of booking details: {booking.details.count()}")
            
            # Group booking details by passenger to avoid duplicates
            from collections import defaultdict
            passenger_booking_map = defaultdict(list)
            
            for booking_detail in booking.details.all():
                passenger = booking_detail.passenger
                passenger_booking_map[passenger].append(booking_detail)
            
            # Process each passenger and their booking details
            for passenger, booking_details_list in passenger_booking_map.items():
                passenger_key = f"{passenger.first_name}_{passenger.last_name}"
                
                print(f"Processing passenger: {passenger.first_name} {passenger.last_name}")
                
                # Collect all add-ons for this passenger across all booking details
                passenger_addons_list = []
                for booking_detail in booking_details_list:
                    print(f"  Booking Detail ID: {booking_detail.id}")
                    print(f"  Number of addons: {booking_detail.addons.count()}")
                    
                    for addon in booking_detail.addons.all():
                        print(f"    - Addon: {addon.name} (ID: {addon.id})")
                        addon_data = {
                            'addon': addon,
                            'quantity': 1,
                        }
                        passenger_addons_list.append(addon_data)
                
                # Store passenger add-ons data
                passenger_addons_data[passenger_key] = {
                    'addons': passenger_addons_list
                }
                
                # Use the first booking detail for seat information
                primary_booking_detail = booking_details_list[0]
                passenger_details.append({
                    'passenger': passenger,
                    'booking_detail': primary_booking_detail,
                    'seat': primary_booking_detail.seat,
                    'seat_class': primary_booking_detail.seat_class,
                })
        
        # Build the comparison context for the template
        # score_breakdown = comparison_data.get('score_breakdown', {})
        
        # # Calculate the total WITHOUT add-ons for display purposes
        # calculated_without_addons = (
        #     score_breakdown.get('base_points', 0) +
        #     score_breakdown.get('passenger_points', 0) + 
        #     score_breakdown.get('price_points', 0) +
        #     score_breakdown.get('compliance_points', 0)
        # )
        
        # # For template display, we want to show the breakdown WITHOUT add-ons
        # # since add-ons are displayed separately
        # display_score_breakdown = score_breakdown.copy()
        # display_score_breakdown['total_earned'] = calculated_without_addons

        # Use the ACTUAL score breakdown from the comparison data
        score_breakdown = comparison_data.get('score_breakdown', {})

        # Debug: Print what's actually in the score breakdown
        print("=== SCORE BREAKDOWN DEBUG ===")
        print(f"Score breakdown keys: {score_breakdown.keys()}")
        for key, value in score_breakdown.items():
            print(f"  {key}: {value}")
        print("=============================")

        # Use the actual breakdown as-is
        display_score_breakdown = score_breakdown
        
        comparison_context = {
            'passenger_comparison': comparison_data.get('passenger_comparison', {}),
            'price_comparison': comparison_data.get('price_comparison', {}),
            'flight_comparison': comparison_data.get('flight_comparison', {}),
            'score_breakdown': display_score_breakdown,  # Use display version without add-ons
            'requirements': comparison_data.get('requirements', []),
            'deductions': comparison_data.get('deductions', []),
            'recommendations': comparison_data.get('recommendations', []),
        }
        
        return render(request, 'booking/student/work_detail.html', {
            'submission': submission,
            'activity': activity,
            'booking': booking,
            'booking_details': booking_details,
            'comparison': comparison_context,
            'student': student,
            'compliance_percentage': compliance_percentage,
            'met_requirements': met_requirements,
            'total_requirements': total_requirements,
            'activity_required_addons': activity_required_addons,
            'activity_passengers': activity_passengers,
            'student_addons': student_addons,
            'passenger_details': passenger_details,
            'passenger_addons_data': passenger_addons_data,
        })
        
    except Exception as e:
        print(f"Error in student_work_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, "Error loading work details.")
        return redirect('studentapp:student_activities')

def get_detailed_comparison(activity, booking, booking_details, submission=None):
    """Get detailed comparison between activity requirements and student work"""
    
    # Initialize counts
    adult_count = 0
    child_count = 0
    infant_count = 0
    total_price = booking_details.get('total_cost', 0)
    
    # Count passenger types
    for passenger in booking_details.get('passengers', []):
        passenger_type = passenger.get('type', '').lower()
        if passenger_type == 'adult':
            adult_count += 1
        elif passenger_type == 'child':
            child_count += 1
        elif passenger_type == 'infant':
            infant_count += 1
    
    # Check travel class compliance
    seat_classes_used = booking_details.get('seat_classes_used', [])
    seat_class_names = [seat_class.name.lower() for seat_class in seat_classes_used]
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower() 
        for seat_class_name in seat_class_names
    )
    
    # Get actual seat classes used
    actual_classes = ", ".join([seat_class.name for seat_class in seat_classes_used]) if seat_classes_used else "Not specified"
    
    # Get trip type from booking
    submitted_trip_type = getattr(booking, 'trip_type', 'Not specified')

    # Get airport information from booking
    origin_match = True
    destination_match = True
    booked_origin = None
    booked_destination = None
    
    # Extract airport info from booking details
    if booking_details.get('flights'):
        first_flight = next(iter(booking_details['flights'].values()), None)
        if first_flight:
            booked_origin = first_flight['schedule'].flight.route.origin_airport
            booked_destination = first_flight['schedule'].flight.route.destination_airport
            
            # Check if activity has specific airport requirements
            if hasattr(activity, 'required_origin') and activity.required_origin:
                origin_match = booked_origin.code == activity.required_origin
            if hasattr(activity, 'required_destination') and activity.required_destination:
                destination_match = booked_destination.code == activity.required_destination
    
    # Evaluate passenger information quality
    passenger_info_score = evaluate_passenger_information_quality(booking, activity)
    
    # Build passenger comparison
    passenger_comparison = {
        'required_adults': activity.required_passengers,
        'submitted_adults': adult_count,
        'required_children': activity.required_children,
        'submitted_children': child_count,
        'required_infants': activity.required_infants,
        'submitted_infants': infant_count,
        'adults_match': adult_count == activity.required_passengers,
        'children_match': child_count == activity.required_children,
        'infants_match': infant_count == activity.required_infants,
        'information_quality_score': passenger_info_score,
        'information_quality_percentage': passenger_info_score * 100,
    }
    
    # Build price comparison
    price_comparison = {
        'submitted_total': total_price,
        'within_budget': True,
        'overage': 0,
    }
    
    # Build flight comparison
    flight_comparison = {
        'required_trip_type': activity.required_trip_type,
        'submitted_trip_type': submitted_trip_type,
        'trip_type_match': submitted_trip_type == activity.required_trip_type,
        'required_travel_class': activity.required_travel_class,
        'actual_travel_classes': actual_classes,
        'has_correct_class': has_correct_class,
        'required_origin': getattr(activity, 'required_origin', None),
        'required_destination': getattr(activity, 'required_destination', None),
        'booked_origin': booked_origin.code if booked_origin else 'Not specified',
        'booked_destination': booked_destination.code if booked_destination else 'Not specified',
        'origin_match': origin_match,
        'destination_match': destination_match,
    }
    
    # Calculate score breakdown using CORRECT weights
    total_points = float(activity.total_points)
    
    # CORRECT WEIGHTS (matching calculate_activity_score):
    base_weight = 0.20              # 20%
    passenger_info_weight = 0.10    # 10%  
    flight_route_weight = 0.10      # 10%
    trip_type_weight = 0.15         # 15%
    travel_class_weight = 0.15      # 15%
    passenger_count_weight = 0.20   # 20%  # FIXED: Was 0.25, should be 0.20
    addon_weight = 0.10             # 10%
    
    # Calculate each component with CORRECT weights
    base_points = total_points * base_weight
    
    # Passenger information points
    passenger_info_points = total_points * passenger_info_weight * passenger_info_score
    
    # Flight route points - FIXED: Use correct weight (0.10 instead of 0.15)
    flight_route_score = 1.0 if (origin_match and destination_match) else 0.0
    flight_route_points = total_points * flight_route_weight * flight_route_score
    
    # Trip type points
    trip_type_match = 1.0 if booking.trip_type == activity.required_trip_type else 0.0
    trip_type_points = total_points * trip_type_weight * trip_type_match
    
    # Travel class points
    travel_class_match = 1.0 if has_correct_class else 0.0
    travel_class_points = total_points * travel_class_weight * travel_class_match
    
    # Passenger count points - FIXED: Use correct weight (0.20 instead of 0.25)
    passenger_match = 0
    if adult_count == activity.required_passengers:
        passenger_match += 0.5  # 50% of passenger count points
    if child_count == activity.required_children:
        passenger_match += 0.3  # 30% of passenger count points
    if infant_count == activity.required_infants:
        passenger_match += 0.2  # 20% of passenger count points
    passenger_points = total_points * passenger_count_weight * passenger_match
    
    # Add-on points
    addon_points = float(submission.addon_score) if submission and submission.addon_score else 0.0
    
    # Calculate total earned
    total_earned = (
        base_points + 
        passenger_info_points + 
        flight_route_points + 
        trip_type_points + 
        travel_class_points + 
        passenger_points + 
        addon_points
    )
    
    # Build the score breakdown with CORRECT weights
    score_breakdown = {
        'base_points': float(base_points),
        'passenger_info_points': float(passenger_info_points),
        'flight_route_points': float(flight_route_points),
        'trip_type_points': float(trip_type_points),
        'travel_class_points': float(travel_class_points),
        'passenger_points': float(passenger_points),
        'addon_points': float(addon_points),
        'total_earned': float(total_earned),
        'total_possible': float(total_points),
        # For template percentage calculations
        'total_possible_base_points': float(total_points) * base_weight,
        'total_possible_passenger_info_points': float(total_points) * passenger_info_weight,
        'total_possible_flight_route_points': float(total_points) * flight_route_weight,
        'total_possible_trip_type_points': float(total_points) * trip_type_weight,
        'total_possible_travel_class_points': float(total_points) * travel_class_weight,
        'total_possible_passenger_points': float(total_points) * passenger_count_weight,  # FIXED: 20% not 25%
        'total_possible_addon_points': float(total_points) * addon_weight,
    }
    
    # Build requirements list
    requirements = []
    deductions = []
    recommendations = []
    
    # 1. Trip Type Requirement
    requirements.append({
        'category': 'Trip Type',
        'requirement': f'{activity.required_trip_type.title()} Trip',
        'student_work': f'{booking.trip_type.title()} Trip',
        'met': booking.trip_type == activity.required_trip_type,
        'icon': '✓' if booking.trip_type == activity.required_trip_type else '✗',
        'weight': 'High'
    })
    
    # 2. Passenger Count Requirements
    requirements.append({
        'category': 'Passengers',
        'requirement': f'{activity.required_passengers} Adult(s)',
        'student_work': f'{adult_count} Adult(s)',
        'met': adult_count == activity.required_passengers,
        'icon': '✓' if adult_count == activity.required_passengers else '✗',
        'weight': 'High'
    })

    if activity.required_children > 0:
        requirements.append({
            'category': 'Passengers',
            'requirement': f'{activity.required_children} Child(ren)',
            'student_work': f'{child_count} Child(ren)',
            'met': child_count == activity.required_children,
            'icon': '✓' if child_count == activity.required_children else '✗',
            'weight': 'Medium'
        })

    if activity.required_infants > 0:
        requirements.append({
            'category': 'Passengers',
            'requirement': f'{activity.required_infants} Infant(s)',
            'student_work': f'{infant_count} Infant(s)',
            'met': infant_count == activity.required_infants,
            'icon': '✓' if infant_count == activity.required_infants else '✗',
            'weight': 'Medium'
        })
    
    # 3. Travel Class Requirement
    requirements.append({
        'category': 'Travel Class',
        'requirement': f'{activity.required_travel_class.title()} Class',
        'student_work': actual_classes,
        'met': has_correct_class,
        'icon': '✓' if has_correct_class else '✗',
        'weight': 'High'
    })

    # 4. Passenger Information Quality Requirement
    requirements.append({
        'category': 'Passenger Information',
        'requirement': 'Complete passenger details',
        'student_work': f'{passenger_info_score * 100:.1f}% complete',
        'met': passenger_info_score >= 0.8,
        'icon': '✓' if passenger_info_score >= 0.8 else '⚠',
        'weight': 'Medium',
        'details': 'Includes names, dates of birth, gender, and contact information'
    })

    # 5. Origin Airport Requirement (if specified)
    if hasattr(activity, 'required_origin') and activity.required_origin:
        requirements.append({
            'category': 'Flight Route',
            'requirement': f'Depart from {activity.required_origin}',
            'student_work': f'Depart from {booked_origin.code if booked_origin else "Not specified"}',
            'met': origin_match,
            'icon': '✓' if origin_match else '✗',
            'weight': 'Medium'
        })
    
    # 6. Destination Airport Requirement (if specified)
    if hasattr(activity, 'required_destination') and activity.required_destination:
        requirements.append({
            'category': 'Flight Route',
            'requirement': f'Arrive at {activity.required_destination}',
            'student_work': f'Arrive at {booked_destination.code if booked_destination else "Not specified"}',
            'met': destination_match,
            'icon': '✓' if destination_match else '✗',
            'weight': 'Medium'
        })
    
    # Add recommendations based on passenger information quality
    if passenger_info_score < 0.8:
        recommendations.append("Ensure all passenger details are complete including names, dates of birth, gender, and contact information")
    
    # Add deductions for poor passenger information
    if passenger_info_score < 0.5:
        deductions.append({
            'category': 'Passenger Information',
            'issue': 'Incomplete passenger details',
            'details': f'Passenger information quality score: {passenger_info_score * 100:.1f}%',
            'points_lost': f'Up to {total_points * 0.10 * (1 - passenger_info_score):.1f} points',
            'type': 'passenger_info'
        })
    
    return {
        'passenger_comparison': passenger_comparison,
        'price_comparison': price_comparison,
        'flight_comparison': flight_comparison,
        'requirements': requirements,
        'deductions': deductions,
        'recommendations': recommendations,
        'score_breakdown': score_breakdown,
    }




def calculate_detailed_score_breakdown(activity, booking, booking_details, seat_class_names):
    """Calculate detailed score breakdown for display with CORRECT weights"""
    total_points = float(activity.total_points)
    
    # CORRECTED WEIGHTS (matching calculate_activity_score):
    # Base: 25%, Passengers: 25%, Price: 20%, Compliance: 15%, Add-ons: 15%
    
    # Count passenger types
    adult_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'adult'])
    child_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'child'])
    infant_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'infant'])
    
    # Base completion points (25%)
    base_points = total_points * 0.25
    
    # Passenger points (25%)
    passenger_match = 0
    if adult_count == activity.required_passengers:
        passenger_match += 0.5  # 50% weight for adults
    if child_count == activity.required_children:
        passenger_match += 0.3  # 30% weight for children  
    if infant_count == activity.required_infants:
        passenger_match += 0.2  # 20% weight for infants
    
    passenger_points = (total_points * 0.25) * passenger_match
    
    # Price points (20%)
    total_price = booking_details['total_cost']
    price_points = total_points * 0.20
    if activity.required_max_price and total_price > float(activity.required_max_price):
        overage_percentage = min((total_price - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
        price_points *= (1 - overage_percentage)
    
    # Compliance points (15%)
    compliance_match = 0
    if booking.trip_type == activity.required_trip_type:
        compliance_match += 0.5  # 50% weight for trip type
    
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower() 
        for seat_class_name in seat_class_names
    )
    if has_correct_class:
        compliance_match += 0.5  # 50% weight for travel class
    
    compliance_points = (total_points * 0.15) * compliance_match
    
    # Add-on points (15%) - This should come from the actual submission
    addon_points = total_points * 0.15  # Default full points if no specific add-on grading
    
    return {
        'base_points': base_points,  # 25 pts
        'passenger_points': passenger_points,  # Up to 25 pts
        'price_points': price_points,  # Up to 20 pts  
        'compliance_points': compliance_points,  # Up to 15 pts
        'addon_points': addon_points,  # Up to 15 pts
        'total_earned': base_points + passenger_points + price_points + compliance_points + addon_points,
        'total_possible': total_points,
    }




def get_booking_details(booking):
    """Get detailed information about what was actually booked"""
    print(f"=== GET_BOOKING_DETAILS DEBUG ===")
    print(f"Booking ID: {booking.id}")
    
    # FIX: Use list() to evaluate the queryset first, then process
    try:
        booking_details_list = list(booking.details.all().select_related(
            'passenger', 'schedule', 'schedule__flight', 'schedule__flight__route'
        ))
    except Exception as e:
        print(f"Error in select_related: {e}")
        # Fallback: get details without select_related
        booking_details_list = list(booking.details.all())
    
    print(f"Found {len(booking_details_list)} booking details")
    
    details = {
        'passengers': [],
        'flights': {},
        'total_cost': 0,
        'seat_classes_used': set()
    }
    
    # Rest of your function remains the same, but use booking_details_list instead of booking_details
    # Group by flight schedule
    flight_groups = {}
    for detail in booking_details_list:
        print(f"Processing detail: {detail.id} - Passenger: {detail.passenger.first_name}")
        schedule_id = detail.schedule.id
        if schedule_id not in flight_groups:
            flight_groups[schedule_id] = {
                'schedule': detail.schedule,
                'passengers': [],
                'total_seats': 0
            }
        
        flight_groups[schedule_id]['passengers'].append({
            'passenger': detail.passenger,
            'seat_class': detail.seat_class,
            'seat_number': detail.seat.seat_number if detail.seat else 'Not assigned',
            'price': detail.price
        })
        flight_groups[schedule_id]['total_seats'] += 1
        
        # Add to overall details
        details['seat_classes_used'].add(detail.seat_class)
        if detail.passenger.passenger_type.lower() != 'infant':
            details['total_cost'] += float(detail.price)
    
    details['flights'] = flight_groups
    details['seat_classes_used'] = list(details['seat_classes_used'])
    
    print(f"Flight groups: {len(flight_groups)}")
    
    # Get all passengers with their details
    for detail in booking_details_list:
        # Build the full name with middle name if available
        if detail.passenger.middle_name:
            full_name = f"{detail.passenger.first_name} {detail.passenger.middle_name} {detail.passenger.last_name}"
        else:
            full_name = f"{detail.passenger.first_name} {detail.passenger.last_name}"
        
        passenger_info = {
            'name': full_name,
            'type': detail.passenger.passenger_type,
            'date_of_birth': detail.passenger.date_of_birth,
            'gender': detail.passenger.gender,
            'passport': detail.passenger.passport_number,
            'flights': []
        }
        
        # Add flight details for this passenger
        for flight_group in flight_groups.values():
            for passenger in flight_group['passengers']:
                if passenger['passenger'].id == detail.passenger.id:
                    passenger_info['flights'].append({
                        'route': f"{flight_group['schedule'].flight.route.origin_airport.code} → {flight_group['schedule'].flight.route.destination_airport.code}",
                        'date': flight_group['schedule'].departure_time.date(),
                        'seat_class': passenger['seat_class'].name if passenger['seat_class'] else 'Not assigned',
                        'seat_number': passenger['seat_number'],
                        'price': passenger['price']
                    })
        
        # Only add each passenger once
        if not any(p['name'] == passenger_info['name'] for p in details['passengers']):
            details['passengers'].append(passenger_info)
    
    print(f"Final passengers count: {len(details['passengers'])}")
    print(f"Final flights count: {len(details['flights'])}")
    print("=== END GET_BOOKING_DETAILS ===")
    
    return details


from decimal import Decimal

# def get_detailed_comparison(activity, booking, booking_details, submission=None):
#     """Get detailed comparison between activity requirements and student work"""
    
#     # Initialize counts
#     adult_count = 0
#     child_count = 0
#     infant_count = 0
#     total_price = booking_details.get('total_cost', 0)
    
#     # Count passenger types
#     for passenger in booking_details.get('passengers', []):
#         passenger_type = passenger.get('type', '').lower()
#         if passenger_type == 'adult':
#             adult_count += 1
#         elif passenger_type == 'child':
#             child_count += 1
#         elif passenger_type == 'infant':
#             infant_count += 1
    
#     # Check travel class compliance
#     seat_classes_used = booking_details.get('seat_classes_used', [])
#     seat_class_names = [seat_class.name.lower() for seat_class in seat_classes_used]
#     has_correct_class = any(
#         seat_class_name == activity.required_travel_class.lower() 
#         for seat_class_name in seat_class_names
#     )
    
#     # Get actual seat classes used
#     actual_classes = ", ".join([seat_class.name for seat_class in seat_classes_used]) if seat_classes_used else "Not specified"
    
#     # Get trip type from booking
#     submitted_trip_type = getattr(booking, 'trip_type', 'Not specified')

#     # Get airport information from booking
#     origin_match = True
#     destination_match = True
#     booked_origin = None
#     booked_destination = None
    
#     # Extract airport info from booking details
#     if booking_details.get('flights'):
#         first_flight = next(iter(booking_details['flights'].values()), None)
#         if first_flight:
#             booked_origin = first_flight['schedule'].flight.route.origin_airport
#             booked_destination = first_flight['schedule'].flight.route.destination_airport
            
#             # Check if activity has specific airport requirements
#             if hasattr(activity, 'required_origin') and activity.required_origin:
#                 origin_match = booked_origin.code == activity.required_origin
#             if hasattr(activity, 'required_destination') and activity.required_destination:
#                 destination_match = booked_destination.code == activity.required_destination
    
#     # NEW: Evaluate passenger information quality
#     passenger_info_score = evaluate_passenger_information_quality(booking, activity)
    
#     # Build passenger comparison - UPDATED with information quality
#     passenger_comparison = {
#         'required_adults': activity.required_passengers,
#         'submitted_adults': adult_count,
#         'required_children': activity.required_children,
#         'submitted_children': child_count,
#         'required_infants': activity.required_infants,
#         'submitted_infants': infant_count,
#         'adults_match': adult_count == activity.required_passengers,
#         'children_match': child_count == activity.required_children,
#         'infants_match': infant_count == activity.required_infants,
#         'information_quality_score': passenger_info_score,  # NEW
#         'information_quality_percentage': passenger_info_score * 100,  # NEW
#     }
    
#     # Build price comparison
#     price_comparison = {
#         'submitted_total': total_price,
#         'within_budget': True,  # Always true since budget is removed
#         'overage': 0,  # Always 0 since budget is removed
#     }
    
#     # Build flight comparison
#     flight_comparison = {
#         'required_trip_type': activity.required_trip_type,
#         'submitted_trip_type': submitted_trip_type,
#         'trip_type_match': submitted_trip_type == activity.required_trip_type,
#         'required_travel_class': activity.required_travel_class,
#         'actual_travel_classes': actual_classes,
#         'has_correct_class': has_correct_class,
#         'required_origin': getattr(activity, 'required_origin', None),
#         'required_destination': getattr(activity, 'required_destination', None),
#         'booked_origin': booked_origin.code if booked_origin else 'Not specified',
#         'booked_destination': booked_destination.code if booked_destination else 'Not specified',
#         'origin_match': origin_match,
#         'destination_match': destination_match,
#     }
    
#     # Build requirements list
#     requirements = []
#     deductions = []
#     recommendations = []
    
#     # 1. Trip Type Requirement
#     requirements.append({
#         'category': 'Trip Type',
#         'requirement': f'{activity.required_trip_type.title()} Trip',
#         'student_work': f'{booking.trip_type.title()} Trip',
#         'met': booking.trip_type == activity.required_trip_type,
#         'icon': '✓' if booking.trip_type == activity.required_trip_type else '✗',
#         'weight': 'High'
#     })
    
#     # 2. Passenger Count Requirements
#     requirements.append({
#         'category': 'Passengers',
#         'requirement': f'{activity.required_passengers} Adult(s)',
#         'student_work': f'{adult_count} Adult(s)',
#         'met': adult_count == activity.required_passengers,
#         'icon': '✓' if adult_count == activity.required_passengers else '✗',
#         'weight': 'High'
#     })

#     if activity.required_children > 0:
#         requirements.append({
#             'category': 'Passengers',
#             'requirement': f'{activity.required_children} Child(ren)',
#             'student_work': f'{child_count} Child(ren)',
#             'met': child_count == activity.required_children,
#             'icon': '✓' if child_count == activity.required_children else '✗',
#             'weight': 'Medium'
#         })

#     if activity.required_infants > 0:
#         requirements.append({
#             'category': 'Passengers',
#             'requirement': f'{activity.required_infants} Infant(s)',
#             'student_work': f'{infant_count} Infant(s)',
#             'met': infant_count == activity.required_infants,
#             'icon': '✓' if infant_count == activity.required_infants else '✗',
#             'weight': 'Medium'
#         })
    
#     # 3. Travel Class Requirement
#     requirements.append({
#         'category': 'Travel Class',
#         'requirement': f'{activity.required_travel_class.title()} Class',
#         'student_work': actual_classes,
#         'met': has_correct_class,
#         'icon': '✓' if has_correct_class else '✗',
#         'weight': 'High'
#     })

#     # 4. Passenger Information Quality Requirement - NEW
#     requirements.append({
#         'category': 'Passenger Information',
#         'requirement': 'Complete passenger details',
#         'student_work': f'{passenger_info_score * 100:.1f}% complete',
#         'met': passenger_info_score >= 0.8,  # Consider 80% as meeting requirement
#         'icon': '✓' if passenger_info_score >= 0.8 else '⚠',
#         'weight': 'Medium',
#         'details': 'Includes names, dates of birth, gender, and contact information'
#     })

#     # 5. Origin Airport Requirement (if specified)
#     if hasattr(activity, 'required_origin') and activity.required_origin:
#         requirements.append({
#             'category': 'Flight Route',
#             'requirement': f'Depart from {activity.required_origin}',
#             'student_work': f'Depart from {booked_origin.code if booked_origin else "Not specified"}',
#             'met': origin_match,
#             'icon': '✓' if origin_match else '✗',
#             'weight': 'Medium'
#         })
    
#     # 6. Destination Airport Requirement (if specified)
#     if hasattr(activity, 'required_destination') and activity.required_destination:
#         requirements.append({
#             'category': 'Flight Route',
#             'requirement': f'Arrive at {activity.required_destination}',
#             'student_work': f'Arrive at {booked_destination.code if booked_destination else "Not specified"}',
#             'met': destination_match,
#             'icon': '✓' if destination_match else '✗',
#             'weight': 'Medium'
#         })
    
#     # Calculate score breakdown using the ACTUAL calculated points
#     total_points = float(activity.total_points)
    
#     # Use the submission's actual score if available
#     if submission and submission.score is not None:
#         actual_score = float(submission.score)
        
#         # Calculate the ACTUAL earned points from each category
#         base_points = total_points * 0.20  # 20% for completion
        
#         # Calculate passenger count points based on actual match
#         passenger_match = 0
#         if adult_count == activity.required_passengers:
#             passenger_match += 0.5  # 50% of passenger count points
#         if child_count == activity.required_children:
#             passenger_match += 0.3  # 30% of passenger count points
#         if infant_count == activity.required_infants:
#             passenger_match += 0.2  # 20% of passenger count points
#         passenger_points = (total_points * 0.25) * passenger_match
        
#         # Passenger information quality points (10% of total)
#         passenger_info_points = total_points * 0.10 * passenger_info_score
        
#         # FIX: Calculate flight route compliance points (15%)
#         flight_route_score = evaluate_flight_route_compliance(booking, activity)
#         flight_route_points = total_points * 0.15 * flight_route_score  # ADD THIS LINE
        
#         # Trip type compliance points (15%)
#         trip_type_match = 1.0 if booking.trip_type == activity.required_trip_type else 0.0
#         trip_type_points = total_points * 0.15 * trip_type_match
        
#         # Travel class compliance points (15%)
#         travel_class_match = 1.0 if has_correct_class else 0.0
#         travel_class_points = total_points * 0.15 * travel_class_match
        
#         # Use actual add-on score from submission (convert to float if it's Decimal)
#         addon_points = float(submission.addon_score) if submission.addon_score else 0.0
        
#     else:
#         # Fallback calculation if no submission
#         base_points = total_points * 0.20  # 20% for completion
        
#         passenger_match = 0
#         if adult_count == activity.required_passengers:
#             passenger_match += 0.5
#         if child_count == activity.required_children:
#             passenger_match += 0.3  
#         if infant_count == activity.required_infants:
#             passenger_match += 0.2
#         passenger_points = (total_points * 0.25) * passenger_match
        
#         # Passenger information quality points (10% of total)
#         passenger_info_points = total_points * 0.10 * passenger_info_score
        
#         # FIX: Calculate flight route compliance points (15%)
#         flight_route_score = evaluate_flight_route_compliance(booking, activity)
#         flight_route_points = total_points * 0.15 * flight_route_score  # ADD THIS LINE
        
#         # Price points - always full points since budget is removed
#         price_points = total_points * 0.20
        
#         trip_type_match = 0
#         if booking.trip_type == activity.required_trip_type:
#             trip_type_match += 0.5
#         trip_type_points = total_points * 0.15 * trip_type_match
        
#         travel_class_match = 0
#         if has_correct_class:
#             travel_class_match += 0.5
#         travel_class_points = total_points * 0.15 * travel_class_match
        
#         addon_points = total_points * 0.10  # 10% for add-ons
    
#     # Calculate total earned ensuring all values are floats
#     total_earned = float(base_points) + float(passenger_points) + float(passenger_info_points) + float(flight_route_points) + float(trip_type_points) + float(travel_class_points)
#     if activity.addon_grading_enabled:
#         total_earned += float(addon_points)
    
#     # Build the final score breakdown with ACTUAL earned points
#     score_breakdown = {
#         'base_points': float(base_points),
#         'passenger_points': float(passenger_points),
#         'passenger_info_points': float(passenger_info_points),
#         'flight_route_points': float(flight_route_points),  # NOW THIS IS DEFINED
#         'trip_type_points': float(trip_type_points),
#         'travel_class_points': float(travel_class_points),
#         'addon_points': float(addon_points) if activity.addon_grading_enabled else 0.0,
#         'total_earned': total_earned,
#         'total_possible': float(total_points),
#         'total_possible_base_points': float(total_points) * 0.20,
#         'total_possible_passenger_points': float(total_points) * 0.25,
#         'total_possible_passenger_info_points': float(total_points) * 0.10,
#         'total_possible_flight_route_points': float(total_points) * 0.15,  # ADD THIS
#         'total_possible_trip_type_points': float(total_points) * 0.15,     # ADD THIS
#         'total_possible_travel_class_points': float(total_points) * 0.15,  # ADD THIS
#         'total_possible_addon_points': float(total_points) * 0.10 if activity.addon_grading_enabled else 0.0,
#     }
    
#     # Add recommendations based on passenger information quality
#     if passenger_info_score < 0.8:
#         recommendations.append("Ensure all passenger details are complete including names, dates of birth, gender, and contact information")
#     if passenger_info_score < 0.6:
#         recommendations.append("Double-check passenger information for accuracy and completeness - missing details can affect travel")
    
#     # Add deductions for poor passenger information
#     if passenger_info_score < 0.5:
#         deductions.append({
#             'category': 'Passenger Information',
#             'issue': 'Incomplete passenger details',
#             'details': f'Passenger information quality score: {passenger_info_score * 100:.1f}%',
#             'points_lost': f'Up to {total_points * 0.15 * (1 - passenger_info_score):.1f} points',
#             'type': 'passenger_info'
#         })
    
#     return {
#         'passenger_comparison': passenger_comparison,
#         'price_comparison': price_comparison,
#         'flight_comparison': flight_comparison,
#         'requirements': requirements,
#         'deductions': deductions,
#         'recommendations': recommendations,
#         'score_breakdown': score_breakdown,
#     }



def evaluate_passenger_information_quality(booking, activity):
    """
    Evaluate the quality and completeness of passenger information
    Returns a score between 0 and 1
    """
    print("=== PASSENGER INFORMATION EVALUATION ===")
    
    booking_details = booking.details.all()
    total_passengers = len(booking_details)
    
    # FIRST: Check if we have the right number of passengers
    required_total = activity.required_passengers + activity.required_children + activity.required_infants
    if total_passengers != required_total:
        print(f"❌ Passenger count mismatch: required {required_total}, got {total_passengers}")
        # Apply penalty for wrong passenger count
        count_penalty = 0.3  # 30% penalty for wrong passenger count
    else:
        count_penalty = 0.0
        print(f"✅ Correct passenger count: {total_passengers}")
    
    if total_passengers == 0:
        return 0.0
    
    total_score = 0.0
    passenger_scores = []
    
    # Count passenger types to verify requirements
    adult_count = 0
    child_count = 0
    infant_count = 0
    
    # Get predefined passengers for this activity
    predefined_passengers = activity.passengers.all()
    has_predefined_passengers = predefined_passengers.exists()
    
    print(f"Predefined passengers check: {has_predefined_passengers} ({predefined_passengers.count()} passengers)")
    
    for detail in booking_details:
        passenger = detail.passenger
        passenger_type = passenger.passenger_type.lower()
        
        # Count passenger types
        if passenger_type == 'adult':
            adult_count += 1
        elif passenger_type == 'child':
            child_count += 1
        elif passenger_type == 'infant':
            infant_count += 1
        
        passenger_score = 0.0
        passenger_deductions = []
        
        print(f"Evaluating passenger: {passenger.first_name} {passenger.last_name} ({passenger_type})")
        
        # 1. Name completeness (40% of passenger score)
        name_score = 0.0
        if passenger.first_name and passenger.first_name.strip():
            name_score += 0.5
        else:
            passenger_deductions.append("Missing first name")
            
        if passenger.last_name and passenger.last_name.strip():
            name_score += 0.5
        else:
            passenger_deductions.append("Missing last name")
        
        passenger_score += name_score * 0.4
        
        # 2. Date of birth validity (30% of passenger score)
        dob_score = 0.0
        if passenger.date_of_birth:
            # Check if DOB is reasonable (not in future and not too old)
            today = timezone.now().date()
            age = today.year - passenger.date_of_birth.year - (
                (today.month, today.day) < (passenger.date_of_birth.month, passenger.date_of_birth.day)
            )
            
            if age >= 0 and age <= 120:  # Reasonable age range
                dob_score = 1.0
            else:
                dob_score = 0.5
                passenger_deductions.append(f"Unrealistic age: {age} years")
        else:
            passenger_deductions.append("Missing date of birth")
            
        passenger_score += dob_score * 0.3
        
        # 3. Gender information (20% of passenger score)
        gender_score = 1.0 if passenger.gender and passenger.gender.strip() else 0.0
        if not gender_score:
            passenger_deductions.append("Missing gender")
        passenger_score += gender_score * 0.2
        
        # 4. Passport information (10% of passenger score)
        passport_score = 1.0  # Default full points
        
        # NEW: Check if we need to match predefined passenger passport
        passport_mismatch = False
        predefined_passport = None
        
        if has_predefined_passengers:
            # Try to find matching predefined passenger by name or position
            # For simplicity, we'll match by order (first predefined with first submitted, etc.)
            passenger_index = list(booking_details).index(detail)
            if passenger_index < len(predefined_passengers):
                predefined_passenger = predefined_passengers[passenger_index]
                predefined_passport = predefined_passenger.passport_number
                
                print(f"  Comparing with predefined passenger: {predefined_passenger.first_name} {predefined_passenger.last_name}")
                print(f"  Predefined passport: {predefined_passport}")
                print(f"  Submitted passport: {passenger.passport_number}")
                
                if predefined_passport and predefined_passport.strip():
                    # Predefined passenger has passport - must match exactly
                    if passenger.passport_number and passenger.passport_number.strip():
                        if passenger.passport_number.strip() == predefined_passport.strip():
                            passport_score = 1.0
                            print(f"  ✅ Passport matches predefined: {passenger.passport_number}")
                        else:
                            passport_score = 0.0
                            passport_mismatch = True
                            passenger_deductions.append(f"Passport doesn't match predefined ({predefined_passport})")
                            print(f"  ❌ Passport mismatch: expected '{predefined_passport}', got '{passenger.passport_number}'")
                    else:
                        passport_score = 0.0
                        passport_mismatch = True
                        passenger_deductions.append(f"Missing passport (required to match predefined: {predefined_passport})")
                        print(f"  ❌ Missing passport that should match predefined: {predefined_passport}")
        
        # If no predefined passport matching required, use existing logic
        if not passport_mismatch:
            # Check if activity requires passports
            if activity.require_passport:
                # Passport is REQUIRED for all passengers
                if passenger.passport_number and passenger.passport_number.strip():
                    # Basic validation for passport number
                    if len(passenger.passport_number.strip()) >= 5:
                        passport_score = 1.0
                        print(f"  ✅ Valid passport: {passenger.passport_number}")
                    else:
                        passport_score = 0.5
                        passenger_deductions.append("Passport number too short")
                        print(f"  ⚠️ Short passport number: {passenger.passport_number}")
                else:
                    passport_score = 0.0
                    passenger_deductions.append("Missing passport (required)")
                    print(f"  ❌ Missing required passport")
            else:
                # Passport is optional, but check if this might be an international flight
                if hasattr(activity, 'required_origin') and hasattr(activity, 'required_destination'):
                    origin_airport = Airport.objects.filter(code=activity.required_origin).first()
                    dest_airport = Airport.objects.filter(code=activity.required_destination).first()
                    
                    if origin_airport and dest_airport:
                        # If either airport is international, passport becomes important
                        if (origin_airport.airport_type == 'international' or 
                            dest_airport.airport_type == 'international'):
                            
                            if passenger.passport_number and passenger.passport_number.strip():
                                passport_score = 1.0
                            else:
                                passport_score = 0.0
                                passenger_deductions.append("Missing passport for international flight")
        
        passenger_score += passport_score * 0.1
        
        # Store individual passenger score
        passenger_scores.append(passenger_score)
        total_score += passenger_score
        
        print(f"  Passenger score: {passenger_score:.2f}")
        if passenger_deductions:
            print(f"  Deductions: {', '.join(passenger_deductions)}")
    
    # Calculate average score across all passengers
    average_score = total_score / total_passengers if total_passengers > 0 else 0.0
    
    # SECOND: Check if passenger types match requirements
    type_penalty = 0.0
    if adult_count != activity.required_passengers:
        type_penalty += 0.1
        print(f"❌ Adult count mismatch: required {activity.required_passengers}, got {adult_count}")
    if child_count != activity.required_children:
        type_penalty += 0.1
        print(f"❌ Child count mismatch: required {activity.required_children}, got {child_count}")
    if infant_count != activity.required_infants:
        type_penalty += 0.1
        print(f"❌ Infant count mismatch: required {activity.required_infants}, got {infant_count}")
    
    # Apply penalties
    final_score = average_score * (1 - count_penalty - type_penalty)
    final_score = max(final_score, 0.0)  # Ensure score doesn't go below 0
    
    print(f"Raw passenger information quality: {average_score:.2f}")
    print(f"Count penalty: {count_penalty:.2f}")
    print(f"Type penalty: {type_penalty:.2f}")
    print(f"Final passenger information quality: {final_score:.2f}")
    print("=======================================")
    
    return final_score




def calculate_detailed_score_breakdown(activity, booking, booking_details, seat_class_names):
    """Calculate detailed score breakdown for display with correct percentages"""
    total_points = float(activity.total_points)
    
    # Base completion points (25%)
    base_points = total_points * 0.25
    
    # Passenger points (25%)
    adult_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'adult'])
    child_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'child'])
    infant_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'infant'])
    
    passenger_match = 0
    if adult_count == activity.required_passengers:
        passenger_match += 0.5  # 50% weight for adults
    if child_count == activity.required_children:
        passenger_match += 0.3  # 30% weight for children  
    if infant_count == activity.required_infants:
        passenger_match += 0.2  # 20% weight for infants
    
    passenger_points = (total_points * 0.25) * passenger_match
    
    # Price points (20%)
    total_price = booking_details['total_cost']
    price_points = total_points * 0.20
    if activity.required_max_price and total_price > float(activity.required_max_price):
        overage_percentage = min((total_price - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
        price_points *= (1 - overage_percentage)
    
    # Compliance points (15%)
    compliance_match = 0
    if booking.trip_type == activity.required_trip_type:
        compliance_match += 0.5  # 50% weight for trip type
    
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower() 
        for seat_class_name in seat_class_names
    )
    if has_correct_class:
        compliance_match += 0.5  # 50% weight for travel class
    
    compliance_points = (total_points * 0.15) * compliance_match
    
    # Add-on points (15%) - This should come from the submission, not recalculated here
    # We'll use the actual submission data
    
    return {
        'base_points': base_points,  # 25 pts
        'passenger_points': passenger_points,  # Up to 25 pts
        'price_points': price_points,  # Up to 20 pts  
        'compliance_points': compliance_points,  # Up to 15 pts
        'total_earned': base_points + passenger_points + price_points + compliance_points,
        'total_possible': total_points,
        # Add these for template percentage calculations
        'total_possible_passenger_points': total_points * 0.25,  # 25 pts
        'total_possible_price_points': total_points * 0.20,      # 20 pts
        'total_possible_compliance_points': total_points * 0.15, # 15 pts
        'total_possible_addon_points': total_points * 0.15,      # 15 pts
    }





def calculate_detailed_score_breakdown(activity, booking, booking_details, seat_class_names):
    """Calculate detailed score breakdown for display with CORRECT weights"""
    total_points = float(activity.total_points)
    
    # CORRECTED WEIGHTS (matching calculate_activity_score):
    # Base: 25%, Passengers: 25%, Price: 20%, Compliance: 15%, Add-ons: 15%
    
    # Base completion points (25%)
    base_points = total_points * 0.25
    
    # Passenger points (25%)
    adult_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'adult'])
    child_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'child'])
    infant_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'infant'])
    
    passenger_match = 0
    if adult_count == activity.required_passengers:
        passenger_match += 0.5  # 50% weight for adults
    if child_count == activity.required_children:
        passenger_match += 0.3  # 30% weight for children  
    if infant_count == activity.required_infants:
        passenger_match += 0.2  # 20% weight for infants
    
    passenger_points = (total_points * 0.25) * passenger_match
    
    # Price points (20%)
    total_price = booking_details['total_cost']
    price_points = total_points * 0.20
    if activity.required_max_price and total_price > float(activity.required_max_price):
        overage_percentage = min((total_price - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
        price_points *= (1 - overage_percentage)
    
    # Compliance points (15%)
    compliance_match = 0
    if booking.trip_type == activity.required_trip_type:
        compliance_match += 0.5  # 50% weight for trip type
    
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower() 
        for seat_class_name in seat_class_names
    )
    if has_correct_class:
        compliance_match += 0.5  # 50% weight for travel class
    
    compliance_points = (total_points * 0.15) * compliance_match
    
    return {
        'base_points': base_points,  # 25 pts
        'passenger_points': passenger_points,  # Up to 25 pts
        'price_points': price_points,  # Up to 20 pts  
        'compliance_points': compliance_points,  # Up to 15 pts
        'total_earned': base_points + passenger_points + price_points + compliance_points,
        'total_possible': total_points,
        # Add these for template percentage calculations
        'total_possible_passenger_points': total_points * 0.25,  # 25 pts
        'total_possible_price_points': total_points * 0.20,      # 20 pts
        'total_possible_compliance_points': total_points * 0.15, # 15 pts
        'total_possible_addon_points': total_points * 0.15,      # 15 pts
    }





@login_required
def debug_scoring(request, submission_id):
    """Debug view to see exactly why scores are deducted"""
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        submission = get_object_or_404(ActivitySubmission, id=submission_id, student=student)
        activity = submission.activity
        booking = submission.booking
        
        print(f"=== SCORING DEBUG FOR SUBMISSION {submission_id} ===")
        print(f"Activity: {activity.title}")
        print(f"Final Score: {submission.score}/{activity.total_points}")
        
        # Get detailed booking information
        booking_details = get_booking_details(booking)
        
        # Debug passenger counts
        adult_count = 0
        child_count = 0 
        infant_count = 0
        
        for passenger in booking_details['passengers']:
            passenger_type = passenger['type'].lower()
            if passenger_type == 'adult':
                adult_count += 1
            elif passenger_type == 'child':
                child_count += 1
            elif passenger_type == 'infant':
                infant_count += 1
        
        print(f"Passenger Counts - Booked: {adult_count}A, {child_count}C, {infant_count}I")
        print(f"Passenger Required: {activity.required_passengers}A, {activity.required_children}C, {activity.required_infants}I")
        
        # Check trip type
        print(f"Trip Type - Booked: {booking.trip_type}, Required: {activity.required_trip_type}")
        
        # Check travel class
        seat_class_names = [seat_class.name.lower() for seat_class in booking_details['seat_classes_used']]
        print(f"Travel Class - Booked: {seat_class_names}, Required: {activity.required_travel_class}")
        
        # Check budget
        total_price = booking_details['total_cost']
        print(f"Total Cost: ${total_price:.2f}, Max Allowed: ${activity.required_max_price if activity.required_max_price else 'None'}")
        
        # Manual score calculation to see breakdown
        total_points = float(activity.total_points)
        
        # Base points (30%)
        base_points = total_points * 0.3
        print(f"Base points (completion): {base_points}")
        
        # Passenger points (30%)
        passenger_match = 0
        if adult_count == activity.required_passengers:
            passenger_match += 0.5
            print("✅ Adult count matches")
        else:
            print(f"❌ Adult count: required {activity.required_passengers}, booked {adult_count}")
            
        if child_count == activity.required_children:
            passenger_match += 0.3
            print("✅ Child count matches")
        else:
            print(f"❌ Child count: required {activity.required_children}, booked {child_count}")
            
        if infant_count == activity.required_infants:
            passenger_match += 0.2
            print("✅ Infant count matches")
        else:
            print(f"❌ Infant count: required {activity.required_infants}, booked {infant_count}")
            
        passenger_points = total_points * 0.3 * passenger_match
        print(f"Passenger points: {passenger_points}")
        
        # Price points (20%)
        price_points = total_points * 0.2
        if activity.required_max_price and total_price > float(activity.required_max_price):
            overage_percentage = min((total_price - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
            price_deduction = price_points * overage_percentage
            price_points -= price_deduction
            print(f"❌ Over budget: ${total_price - float(activity.required_max_price):.2f} over")
            print(f"Price points after deduction: {price_points}")
        else:
            print("✅ Within budget")
        
        # Compliance points (20%)
        compliance_match = 0
        if booking.trip_type == activity.required_trip_type:
            compliance_match += 0.5
            print("✅ Trip type matches")
        else:
            print(f"❌ Trip type: required {activity.required_trip_type}, booked {booking.trip_type}")
            
        has_correct_class = any(
            seat_class_name == activity.required_travel_class.lower() 
            for seat_class_name in seat_class_names
        )
        if has_correct_class:
            compliance_match += 0.5
            print("✅ Travel class matches")
        else:
            print(f"❌ Travel class: required {activity.required_travel_class}, booked {seat_class_names}")
            
        compliance_points = total_points * 0.2 * compliance_match
        print(f"Compliance points: {compliance_points}")
        
        # Total
        calculated_total = base_points + passenger_points + price_points + compliance_points
        print(f"Calculated total: {calculated_total}")
        print(f"Actual submission score: {submission.score}")
        
        return HttpResponse(f"Check console for detailed scoring breakdown. Submission: {submission_id}")
        
    except Exception as e:
        print(f"Debug error: {e}")
        return HttpResponse(f"Error: {e}")
    

@login_required
def check_original_scoring(request, submission_id):
    """Check how the score was originally calculated"""
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        submission = get_object_or_404(ActivitySubmission, id=submission_id, student=student)
        
        print(f"=== ORIGINAL SCORING INVESTIGATION ===")
        print(f"Submission ID: {submission.id}")
        print(f"Created at: {submission.submitted_at}")
        print(f"Original Score: {submission.score}")
        print(f"Activity Total Points: {submission.activity.total_points}")
        
        # Check if there's any manual adjustment or different scoring logic
        print(f"Submission fields:")
        print(f"  - required_trip_type: {submission.required_trip_type}")
        print(f"  - required_travel_class: {submission.required_travel_class}")
        print(f"  - required_passengers: {submission.required_passengers}")
        print(f"  - required_children: {submission.required_children}")
        print(f"  - required_infants: {submission.required_infants}")
        print(f"  - required_max_price: {submission.required_max_price}")
        
        # Let's recalculate using the original calculate_activity_score function
        from .utils import calculate_activity_score  # Make sure this import works
        
        original_calculation = calculate_activity_score(submission.booking, submission.activity)
        print(f"Recalculated with original function: {original_calculation}")
        
        return HttpResponse(f"Check console for original scoring investigation")
        
    except Exception as e:
        print(f"Error in check_original_scoring: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {e}")


@login_required
def deep_debug_scoring(request, submission_id):
    """Deep debug to find the missing 10 points"""
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        submission = get_object_or_404(ActivitySubmission, id=submission_id, student=student)
        activity = submission.activity
        booking = submission.booking
        
        print(f"=== DEEP SCORING DEBUG ===")
        print(f"Looking for missing 10 points...")
        
        # Check the original calculate_activity_score function in detail
        print("=== ORIGINAL SCORING FUNCTION BREAKDOWN ===")
        
        # Manually run through the original scoring logic
        total_points = float(activity.total_points)
        points_earned = 0
        deduction_reasons = []
        
        # Base points (30%)
        base_points = total_points * 0.3
        points_earned += base_points
        print(f"1. Base points: {base_points}")
        
        # Passenger points (30%)
        passenger_points = total_points * 0.3
        booking_details = booking.details.all()
        
        adult_count = 0
        child_count = 0
        infant_count = 0
        
        for detail in booking_details:
            passenger_type = detail.passenger.passenger_type.lower()
            if passenger_type == 'adult':
                adult_count += 1
            elif passenger_type == 'child':
                child_count += 1
            elif passenger_type == 'infant':
                infant_count += 1
        
        passenger_match = 0
        if adult_count == activity.required_passengers:
            passenger_match += 0.5
        else:
            deduction_reasons.append(f"Adult passenger count mismatch")
        
        if child_count == activity.required_children:
            passenger_match += 0.3
        else:
            deduction_reasons.append(f"Child passenger count mismatch")
        
        if infant_count == activity.required_infants:
            passenger_match += 0.2
        else:
            deduction_reasons.append(f"Infant passenger count mismatch")
        
        passenger_earned = passenger_points * passenger_match
        points_earned += passenger_earned
        print(f"2. Passenger points: {passenger_earned}/{passenger_points} (match: {passenger_match})")
        
        # Price points (20%)
        price_points = total_points * 0.2
        if activity.required_max_price:
            total_amount = sum(detail.price for detail in booking_details if detail.passenger.passenger_type.lower() != 'infant')
            
            if total_amount <= activity.required_max_price:
                points_earned += price_points
                print(f"3. Price points: {price_points}/{price_points} (within budget)")
            else:
                overage_percentage = min((float(total_amount) - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
                price_deduction = price_points * overage_percentage
                points_earned += price_points - price_deduction
                deduction_reasons.append(f"Exceeded budget by {overage_percentage * 100:.1f}%")
                print(f"3. Price points: {price_points - price_deduction}/{price_points} (over budget)")
        else:
            points_earned += price_points
            print(f"3. Price points: {price_points}/{price_points} (no budget limit)")
        
        # Compliance points (20%)
        compliance_points = total_points * 0.2
        compliance_match = 0
        
        if booking.trip_type == activity.required_trip_type:
            compliance_match += 0.5
        else:
            deduction_reasons.append(f"Trip type mismatch")
        
        has_correct_class = any(
            detail.seat_class and str(detail.seat_class.name).lower() == activity.required_travel_class.lower() 
            for detail in booking_details
        )
        if has_correct_class:
            compliance_match += 0.5
        else:
            deduction_reasons.append(f"Travel class mismatch")
        
        compliance_earned = compliance_points * compliance_match
        points_earned += compliance_earned
        print(f"4. Compliance points: {compliance_earned}/{compliance_points} (match: {compliance_match})")
        
        # Final score
        from decimal import Decimal
        final_score = Decimal(str(min(points_earned, total_points)))
        
        print(f"FINAL CALCULATION: {final_score}")
        print(f"ACTUAL SCORE IN DB: {submission.score}")
        print(f"DIFFERENCE: {float(final_score) - float(submission.score)}")
        
        if deduction_reasons:
            print(f"Deduction reasons from original function: {deduction_reasons}")
        
        return HttpResponse(f"Deep debug completed. Check console.")
        
    except Exception as e:
        print(f"Deep debug error: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {e}")        
    




@login_required
def practice_booking_home(request):
    """Home page for practice bookings"""
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        
        # Get student's practice bookings
        practice_bookings = PracticeBooking.objects.filter(
            student=student
        ).select_related('booking').order_by('-created_at')[:5]  # Last 5 practice bookings
        
        template = loader.get_template('booking/student/practice_home.html')
        context = {
            'student': student,
            'practice_bookings': practice_bookings,
        }
        return HttpResponse(template.render(context, request))
        
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('bookingapp:login')

@login_required
def start_practice_booking(request):
    """Start a new practice booking session"""
    # Clear any activity-related session data
    request.session.pop('activity_id', None)
    request.session.pop('activity_requirements', None)
    
    # Clear previous booking session data
    booking_keys = [
        'trip_type', 'origin', 'destination', 'departure_date', 'return_date',
        'adults', 'children', 'infants', 'passenger_count',
        'passengers', 'selected_seats', 'confirm_depart_schedule', 
        'confirm_return_schedule', 'current_booking_id',
        'selected_addons'  # Clear add-ons too
    ]
    
    for key in booking_keys:
        request.session.pop(key, None)
    
    # Set practice mode flag
    request.session['is_practice_booking'] = True
    request.session.modified = True
    
    messages.info(request, "Practice booking mode activated. This booking won't be graded.")
    return redirect('bookingapp:main')

@login_required
def guided_practice(request):
    """Start a guided practice with specific requirements"""
    if request.method == 'POST':
        # Get practice scenario from form
        scenario_type = request.POST.get('scenario_type')
        requirements = {}
        
        # Set requirements based on scenario type
        if scenario_type == 'business_trip':
            requirements = {
                'trip_type': 'round_trip',
                'passengers': 1,
                'travel_class': 'business',
                'max_price': 2000,
                'description': 'Business trip for one executive'
            }
        elif scenario_type == 'family_vacation':
            requirements = {
                'trip_type': 'round_trip', 
                'passengers': 2,
                'children': 2,
                'travel_class': 'economy',
                'max_price': 1500,
                'description': 'Family vacation with 2 adults and 2 children'
            }
        elif scenario_type == 'budget_travel':
            requirements = {
                'trip_type': 'one_way',
                'passengers': 1,
                'travel_class': 'economy', 
                'max_price': 300,
                'description': 'Budget one-way trip'
            }
        else:
            # Custom requirements
            requirements = {
                'trip_type': request.POST.get('trip_type', 'one_way'),
                'passengers': int(request.POST.get('passengers', 1)),
                'children': int(request.POST.get('children', 0)),
                'infants': int(request.POST.get('infants', 0)),
                'travel_class': request.POST.get('travel_class', 'economy'),
                'max_price': float(request.POST.get('max_price', 0)) if request.POST.get('max_price') else None,
                'description': request.POST.get('description', 'Custom practice scenario')
            }
        
        # Store practice requirements in session
        request.session['practice_requirements'] = requirements
        request.session['is_practice_booking'] = True
        request.session['is_guided_practice'] = True
        
        # Clear previous data
        booking_keys = [
            'trip_type', 'origin', 'destination', 'departure_date', 'return_date',
            'adults', 'children', 'infants', 'passenger_count',
            'selected_addons'  # Clear add-ons too
        ]
        for key in booking_keys:
            request.session.pop(key, None)
        
        # Pre-fill based on requirements
        request.session['trip_type'] = requirements['trip_type']
        request.session['adults'] = requirements['passengers']
        request.session['children'] = requirements.get('children', 0)
        request.session['infants'] = requirements.get('infants', 0)
        
        messages.info(request, f"Guided practice started: {requirements['description']}")
        return redirect('bookingapp:main')
    
    
     # GET request - show guided practice options
    student_id = request.session.get('student_id')
    student = None
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            pass


    # GET request - show guided practice options
    template = loader.get_template('booking/student/guided_practice.html')
    context = {
        'student': student,
    }
    return HttpResponse(template.render(context, request))

@login_required
def save_practice_booking(request):
    """Save a completed practice booking and show success page"""
    booking_id = request.session.get('current_booking_id')
    student_id = request.session.get('student_id')
    
    if not booking_id or not student_id:
        messages.error(request, "No booking found to save as practice.")
        return redirect('bookingapp:main')
    
    try:
        student = Student.objects.get(id=student_id)
        booking = Booking.objects.get(id=booking_id)
        
        # Determine practice type
        practice_type = 'guided_practice' if request.session.get('is_guided_practice') else 'free_practice'
        requirements = request.session.get('practice_requirements')
        
        # Create practice booking record
        practice_booking = PracticeBooking.objects.create(
            student=student,
            booking=booking,
            practice_type=practice_type,
            scenario_description=requirements.get('description') if requirements else 'Free practice booking',
            practice_requirements=requirements,
            is_completed=True
        )
        
        # Clear practice session data but keep what's needed for success page
        keys_to_clear = [
            "is_practice_booking", "is_guided_practice", "practice_requirements",
            "selected_addons", "passengers", "selected_seats", "confirm_depart_schedule",
            "confirm_return_schedule", "trip_type", "origin", "destination", 
            "departure_date", "return_date", "passenger_count", "contact_info", 
            "adults", "children", "infants"
        ]
        
        for key in keys_to_clear:
            request.session.pop(key, None)
        
        # Keep student login
        request.session['student_id'] = student_id
        request.session.modified = True
        
        print(f"✅ Practice booking saved: {practice_booking.id}")
        messages.success(request, "Practice booking completed successfully!")
        
        # Render success page instead of redirecting
        return render(request, "booking/payment_success.html", {
            'booking': booking,
            'student': student,
            'practice_booking': practice_booking,
            'is_practice_booking': True
        })
        
    except Exception as e:
        print(f"Error saving practice booking: {e}")
        messages.error(request, "Error saving practice booking.")
        return redirect('bookingapp:payment_success')
    






# testing UI/UX


def test_home(request):
    from_airport = Airport.objects.all()
    to_airports = Airport.objects.all()


    today = timezone.now().date()
    template = loader.get_template("ui_test/home.html")
    context ={
        'origins' : from_airport,
        'destinations' : to_airports,
        'today': today.isoformat()
    }

    return HttpResponse(template.render(context, request))




def test_schedule(request):
    if request.method == 'POST':
        # Get form data
        trip_type = request.POST.get('trip_type', 'one_way')
        from_airport_id = request.POST.get('from_airport')
        to_airport_id = request.POST.get('to_airport')
        depart_date = request.POST.get('depart_date')
        return_date = request.POST.get('return_date')
        adults = int(request.POST.get('adults', 1))
        children = int(request.POST.get('children', 0))
        infants = int(request.POST.get('infants', 0))
        
        # Validate required fields
        if not all([from_airport_id, to_airport_id, depart_date]):
            return redirect('test_home')
        
        # Get airport objects
        try:
            from_airport = Airport.objects.get(id=from_airport_id)
            to_airport = Airport.objects.get(id=to_airport_id)
        except Airport.DoesNotExist:
            return redirect('test_home')
        
        # Parse dates
        depart_date_obj = datetime.strptime(depart_date, '%Y-%m-%d').date()
        return_date_obj = None
        
        if trip_type == 'round_trip' and return_date:
            return_date_obj = datetime.strptime(return_date, '%Y-%m-%d').date()
        
        # Calculate total passengers
        total_passengers = adults + children + infants
        
        # Query flights for depart date
        depart_flights = Flight.objects.filter(
            departure_airport=from_airport,
            arrival_airport=to_airport,
            departure_time__date=depart_date_obj
        ).select_related('departure_airport', 'arrival_airport', 'airline')
        
        # Query return flights if round trip
        return_flights = None
        if trip_type == 'round_trip' and return_date_obj:
            return_flights = Flight.objects.filter(
                departure_airport=to_airport,
                arrival_airport=from_airport,
                departure_time__date=return_date_obj
            ).select_related('departure_airport', 'arrival_airport', 'airline')
        
        template = loader.get_template("ui_test/schedule.html")
        context = {
            'trip_type': trip_type,
            'from_airport': from_airport,
            'to_airport': to_airport,
            'depart_date': depart_date_obj,
            'return_date': return_date_obj,
            'adults': adults,
            'children': children,
            'infants': infants,
            'total_passengers': total_passengers,
            'depart_flights': depart_flights,
            'return_flights': return_flights,
        }
        
        return HttpResponse(template.render(context, request))
    
    # If not POST, redirect to home
    return redirect('test_home')

def test_selected_schedule(request):
    template = loader.get_template("ui_test/selected_schedule.html")
    context ={
    }
    return HttpResponse(template.render(context, request))

def test_passenger(request):
    template = loader.get_template("ui_test/passenger.html")
    context ={

    }

    return HttpResponse(template.render(context, request))

def test_addons(request):
    template = loader.get_template("ui_test/add_ons.html")
    context ={

    }

    return HttpResponse(template.render(context, request))
def test_booking_summary(request):
    template = loader.get_template("ui_test/booking_summary.html")
    context ={

    }

    return HttpResponse(template.render(context, request))





@login_required
def debug_scoring_breakdown(request, submission_id):
    """Debug the exact scoring breakdown"""
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        submission = ActivitySubmission.objects.get(id=submission_id, student=student)
        activity = submission.activity
        booking = submission.booking
        
        print("=== EXACT SCORING BREAKDOWN ===")
        
        # Import and run the actual function
        from .utils import calculate_activity_score
        final_score = calculate_activity_score(booking, activity)
        
        # Let's manually trace through what should happen
        print("Based on your template display:")
        print(f"Base (20%): 20.0")
        print(f"Passenger Info (15% * 60%): 9.0") 
        print(f"Flight Route (10%): 10.0")
        print(f"Trip Type (15%): 15.0")
        print(f"Travel Class (15%): 15.0")
        print(f"Passenger Count (25% * 70%): 17.5") 
        print(f"Add-ons (10%): 10.0")
        print(f"EXPECTED TOTAL: 96.5")
        print(f"ACTUAL DATABASE SCORE: {submission.score}")
        print(f"ACTUAL FUNCTION RESULT: {final_score}")
        
        # The discrepancy suggests different weights are being used
        print("\n=== INVESTIGATING WEIGHTS ===")
        print("If score is 84.63, the weights might be:")
        
        # Reverse engineer from 84.63
        # Let's assume the same percentages but different base
        actual_base = 20.0 * (84.63/96.5)  # Scale down proportionally
        actual_passenger_info = 9.0 * (84.63/96.5)
        actual_flight_route = 10.0 * (84.63/96.5)
        actual_trip_type = 15.0 * (84.63/96.5)
        actual_travel_class = 15.0 * (84.63/96.5)
        actual_passenger_count = 17.5 * (84.63/96.5)
        actual_addons = 10.0 * (84.63/96.5)
        
        print(f"Scaled Base: {actual_base:.2f}")
        print(f"Scaled Passenger Info: {actual_passenger_info:.2f}")
        print(f"Scaled Flight Route: {actual_flight_route:.2f}")
        print(f"Scaled Trip Type: {actual_trip_type:.2f}")
        print(f"Scaled Travel Class: {actual_travel_class:.2f}")
        print(f"Scaled Passenger Count: {actual_passenger_count:.2f}")
        print(f"Scaled Add-ons: {actual_addons:.2f}")
        print(f"TOTAL SCALED: {actual_base + actual_passenger_info + actual_flight_route + actual_trip_type + actual_travel_class + actual_passenger_count + actual_addons:.2f}")
        
        return HttpResponse(f"""
        Debug complete!<br>
        Expected: 96.5<br>
        Actual: {submission.score}<br>
        Function: {final_score}<br>
        Check console for breakdown.
        """)
        
    except Exception as e:
        print(f"Debug error: {e}")
        return HttpResponse(f"Error: {e}")

