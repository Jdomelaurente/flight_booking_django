from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from flightapp.models import Schedule, Route,  Airport,Seat, PassengerInfo
from flightapp.models import Booking, BookingDetail, Payment, PassengerInfo, Student,AddOn, SeatClass
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from datetime import date
from django.views.decorators.cache import never_cache
from .utils import login_required, redirect_if_logged_in
from instructorapp.models import Activity, ActivitySubmission, SectionEnrollment, PracticeBooking
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone

from decimal import Decimal

def calculate_activity_score(booking, activity):
    """
    Calculate score based on how well the booking matches activity requirements
    """
    total_points = float(activity.total_points)  # Convert Decimal to float for calculations
    points_earned = 0
    deduction_reasons = []
    
    print(f"=== SCORING DEBUG ===")
    print(f"Activity: {activity.title}")
    print(f"Total points available: {total_points}")
    
    # Base points for completing the booking
    base_points = total_points * 0.3  # 30% for just completing
    points_earned += base_points
    print(f"Base points (completion): {base_points}")
    
    # Check passenger requirements (30% of total)
    passenger_points = total_points * 0.3
    booking_details = booking.details.all()
    
    # Count passenger types in booking
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
    
    print(f"Required - Adults: {activity.required_passengers}, Children: {activity.required_children}, Infants: {activity.required_infants}")
    print(f"Actual - Adults: {adult_count}, Children: {child_count}, Infants: {infant_count}")
    
    # Calculate passenger match percentage
    passenger_match = 0
    if adult_count == activity.required_passengers:
        passenger_match += 0.5  # 50% for adults
    else:
        deduction_reasons.append(f"Adult passenger count mismatch")
    
    if child_count == activity.required_children:
        passenger_match += 0.3  # 30% for children
    else:
        deduction_reasons.append(f"Child passenger count mismatch")
    
    if infant_count == activity.required_infants:
        passenger_match += 0.2  # 20% for infants
    else:
        deduction_reasons.append(f"Infant passenger count mismatch")
    
    points_earned += passenger_points * passenger_match
    print(f"Passenger match: {passenger_match * 100}% -> {passenger_points * passenger_match} points")
    
    # Check price compliance (20% of total)
    price_points = total_points * 0.2
    if activity.required_max_price:
        total_amount = sum(detail.price for detail in booking_details if detail.passenger.passenger_type.lower() != 'infant')
        
        if total_amount <= activity.required_max_price:
            points_earned += price_points
            print(f"Price compliance: Within budget -> {price_points} points")
        else:
            # Deduct points proportionally for going over budget
            overage_percentage = min((float(total_amount) - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
            price_deduction = price_points * overage_percentage
            points_earned += price_points - price_deduction
            deduction_reasons.append(f"Exceeded budget by {overage_percentage * 100:.1f}%")
            print(f"Price compliance: Over budget -> {price_points - price_deduction} points")
    
    # Check trip type and class (20% of total)
    compliance_points = total_points * 0.2
    compliance_match = 0
    
    if booking.trip_type == activity.required_trip_type:
        compliance_match += 0.5
    else:
        deduction_reasons.append(f"Trip type mismatch")
    
    # Check if any booking detail matches the required travel class
    has_correct_class = any(
        detail.seat_class and detail.seat_class.name.lower() == activity.required_travel_class.lower() 
        for detail in booking_details
    )
    if has_correct_class:
        compliance_match += 0.5
    else:
        deduction_reasons.append(f"Travel class mismatch")
    
    points_earned += compliance_points * compliance_match
    print(f"Compliance match: {compliance_match * 100}% -> {compliance_points * compliance_match} points")
    
    # Ensure score doesn't exceed total points and convert back to Decimal
    final_score = Decimal(str(min(points_earned, total_points)))
    
    print(f"Final score: {final_score}/{activity.total_points}")
    if deduction_reasons:
        print(f"Deduction reasons: {', '.join(deduction_reasons)}")
    print("=====================")
    
    return final_score

@login_required
def student_home(request):
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        student = Student.objects.get(id=student_id)
        
        # Get student's enrolled sections
        enrolled_sections = SectionEnrollment.objects.filter(
            student=student, 
            is_active=True
        ).select_related('section')
        
        # Get active activities from enrolled sections - REMOVE invalid select_related fields
        activities = Activity.objects.filter(
            section__in=[enrollment.section for enrollment in enrolled_sections],
            is_code_active=True,
            status='published'
        ).select_related('section')  # Only select_related on valid fields
        
        # Check which activities the student has already submitted
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


# bookingapp/views.py - Update the student_activity_detail view
@login_required
def student_activity_detail(request, activity_id):
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('bookingapp:login')
    
    try:
        activity = get_object_or_404(Activity, id=activity_id, status='published')
        student = Student.objects.get(id=student_id)
        
        # Check if student is enrolled in this section
        if not SectionEnrollment.objects.filter(
            section=activity.section, 
            student=student, 
            is_active=True
        ).exists():
            messages.error(request, "You are not enrolled in this section.")
            return redirect('bookingapp:student_home')
        
        # Check if student has already submitted
        existing_submission = ActivitySubmission.objects.filter(
            activity=activity, 
            student=student
        ).first()
        
        # Get pre-defined passengers for this activity
        passengers = activity.passengers.all()
        
        template = loader.get_template('booking/student/activity_detail.html')
        context = {
            'activity': activity,
            'student': student,
            'existing_submission': existing_submission,
            'passengers': passengers,
            'code_active': activity.is_code_active,  # Add this
            'code_expired': activity.code_expires_at and activity.code_expires_at < timezone.now(),  # Add this
        }
        return HttpResponse(template.render(context, request))
        
    except Activity.DoesNotExist:
        messages.error(request, "Activity not found or not available.")
        return redirect('bookingapp:student_home')
    
    
    
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
        if activity.required_max_price:
            total_amount = sum(detail.price for detail in booking_passengers if detail.passenger.passenger_type.lower() != 'infant')
            print(f"Total amount: {total_amount}, Max allowed: {activity.required_max_price}")
            if total_amount > activity.required_max_price:
                print("❌ Price exceeds maximum")
                return False
        
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
        
        # Get all activities (both active and completed) for the student
        enrolled_sections = SectionEnrollment.objects.filter(
            student=student, 
            is_active=True
        ).select_related('section')
        
        # Get all activities from enrolled sections
        all_activities = Activity.objects.filter(
            section__in=[enrollment.section for enrollment in enrolled_sections]
        ).select_related('section')
        
        # Get submitted activities - FIX: Use filter() instead of values_list()
        submitted_activities = ActivitySubmission.objects.filter(
            student=student
        ).select_related('activity')
        
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
            'submitted_activities': submitted_activities,  # Pass the queryset directly
            'enrolled_sections': enrolled_sections,
        }
        return HttpResponse(template.render(context, request))
        
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('bookingapp:login')



@login_required
def home(request):
    from_airports = Airport.objects.all()
    to_airports = Airport.objects.all()

    print("=== HOME PAGE SESSION DEBUG ===")
    print(f"Session activity_id: {request.session.get('activity_id')}")
    print(f"GET params - activity_id: {request.GET.get('activity_id')}, activity_code: {request.GET.get('activity_code')}")
    print(f"Practice mode: {request.session.get('is_practice_booking')}")


    

    
    # Check for activity code from modal OR activity_id from URL
    activity_code = request.GET.get('activity_code')
    activity_id = request.GET.get('activity_id')
    activity = None
    
    # Clear any previous activity data if we're starting fresh
    if 'clear_activity' in request.GET:
        request.session.pop('activity_id', None)
        request.session.pop('activity_requirements', None)
        print("🧹 Cleared previous activity data")
    
    # If we have activity_id from GET parameters, verify it has an active code
       # If we have BOTH activity_id AND activity_code (from modal form)
    if activity_id and activity_code:
        try:
            activity = Activity.objects.get(
                id=activity_id,
                activity_code=activity_code.upper().strip(),
                is_code_active=True,
                status='published'
            )
            # Check if code is expired
            if activity.code_expires_at and activity.code_expires_at < timezone.now():
                messages.error(request, "This activity code has expired. Please contact your instructor for a new code.")
                activity = None
            else:
                # SET ACTIVITY SESSION DATA
                request.session['activity_id'] = activity.id
                request.session['activity_requirements'] = {
                    'max_price': float(activity.required_max_price) if activity.required_max_price else None,
                    'travel_class': activity.required_travel_class,
                    'require_passenger_details': activity.require_passenger_details,
                }
                print(f"🎯 ACTIVITY SESSION SET via code+ID: {activity.title} (ID: {activity.id})")
                messages.success(request, f"Activity '{activity.title}' loaded successfully!")
                
        except Activity.DoesNotExist:
            print(f"❌ Activity not found with code {activity_code} and ID {activity_id}")
            messages.error(request, "Invalid activity code or ID. Please check with your instructor.")
    
    # Check if we have activity from session - verify it's still active
    elif request.session.get('activity_id'):
        try:
            activity = Activity.objects.get(
                id=request.session.get('activity_id'), 
                is_code_active=True,  # REQUIRE active code
                status='published'
            )
            # Check if code is expired
            if activity.code_expires_at and activity.code_expires_at < timezone.now():
                messages.error(request, "This activity code has expired. Please contact your instructor for a new code.")
                request.session.pop('activity_id', None)
                request.session.pop('activity_requirements', None)
                activity = None
            else:
                print(f"🎯 ACTIVITY FROM SESSION: {activity.title} (ID: {activity.id})")
        except Activity.DoesNotExist:
            print(f"❌ Session activity not found or inactive: {request.session.get('activity_id')}")
            request.session.pop('activity_id', None)
            request.session.pop('activity_requirements', None)
            messages.error(request, "Activity session expired or code deactivated.")
    
    # If we have a valid activity, set up flight requirements
    if activity:
        print(f"⚙️ Setting up activity requirements for: {activity.title}")
        # Clear any previous booking session data but KEEP activity data
        booking_keys = [
            'trip_type', 'origin', 'destination', 'departure_date', 'return_date',
            'adults', 'children', 'infants', 'passenger_count'
        ]
        for key in booking_keys:
            request.session.pop(key, None)
        
        # Set flight requirements from activity
        if hasattr(activity, 'required_origin') and activity.required_origin:
            try:
                origin_airport = Airport.objects.get(code=activity.required_origin)
                request.session['origin'] = origin_airport.id
                print(f"  - Origin: {activity.required_origin}")
            except Airport.DoesNotExist:
                print(f"  - ❌ Origin airport not found: {activity.required_origin}")
                pass
                
        if hasattr(activity, 'required_destination') and activity.required_destination:
            try:
                dest_airport = Airport.objects.get(code=activity.required_destination)
                request.session['destination'] = dest_airport.id
                print(f"  - Destination: {activity.required_destination}")
            except Airport.DoesNotExist:
                print(f"  - ❌ Destination airport not found: {activity.required_destination}")
                pass
        
        request.session['trip_type'] = activity.required_trip_type
        request.session['adults'] = activity.required_passengers
        request.session['children'] = activity.required_children
        request.session['infants'] = activity.required_infants
        
        print(f"  - Trip type: {activity.required_trip_type}")
        print(f"  - Passengers: {activity.required_passengers} adults, {activity.required_children} children, {activity.required_infants} infants")
        
        messages.info(request, f"Activity mode: {activity.title} - Requirements have been pre-filled.")

    # If in practice mode, show practice info
    practice_requirements = request.session.get('practice_requirements')

    template = loader.get_template('booking/home.html')
    context = {
        "origins": from_airports,
        "destinations": to_airports,
        "activity": activity,
        "practice_requirements": practice_requirements,
        "is_practice_booking": request.session.get('is_practice_booking', False),

    }
    return HttpResponse(template.render(context, request))


@login_required
def search_flight(request):
    # Preserve activity_id if it exists
    activity_id = request.session.get('activity_id')
    
    # Validate activity is still active if this is an activity booking
    if activity_id:
        try:
            activity = Activity.objects.get(
                id=activity_id, 
                is_code_active=True,
                status='published'
            )
            # Check if code expired
            if activity.code_expires_at and activity.code_expires_at < timezone.now():
                messages.error(request, "Activity code has expired. Please contact your instructor.")
                request.session.pop('activity_id', None)
                request.session.pop('activity_requirements', None)
                return redirect('bookingapp:main')
        except Activity.DoesNotExist:
            messages.error(request, "Activity is no longer available.")
            request.session.pop('activity_id', None)
            request.session.pop('activity_requirements', None)
            return redirect('bookingapp:main')
    
    if request.method == 'POST':
        trip_type = request.POST.get('trip_type')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_date = request.POST.get('departure_date')
        return_date = request.POST.get('return_date')
        adults = int(request.POST.get('adults', 1))
        children = int(request.POST.get('children', 0))
        infants = int(request.POST.get('infants', 0))
        
        print(f"=== SEARCH_FLIGHT DEBUG ===")
        print(f"Activity ID in session: {activity_id}")
        
        if not trip_type and not origin and not destination and not departure_date and not return_date and (adults + children + infants == 0):
            return redirect('bookingapp:main')

        if trip_type:
            request.session['trip_type'] = trip_type
        if origin:    
            request.session['origin'] = int(origin)
        if destination:
            request.session['destination'] = int(destination)
        if departure_date:    
            request.session['departure_date'] = departure_date
        if return_date:    
            request.session['return_date'] = return_date

        request.session['adults'] = adults
        request.session['children'] = children
        request.session['infants'] = infants
        request.session['passenger_count'] = adults + children + infants
        request.session['seat'] = None

        # Preserve activity_id if it exists
        if activity_id:
            request.session['activity_id'] = activity_id
            print(f"✅ Preserved activity_id: {activity_id}")

        return redirect("bookingapp:flight_schedules")

@never_cache
@login_required
def flight_schedules(request):
    activity_id = request.session.get('activity_id')
    print(f"=== FLIGHT_SCHEDULES DEBUG ===")
    print(f"Activity ID: {activity_id}")
    origin_id = request.session.get('origin')
    destination_id = request.session.get('destination')
    depart_date = request.session.get('departure_date')
    dates = range(1, 8)

    if not origin_id or not destination_id or not depart_date:
        return redirect('bookingapp:main')

    origin = Airport.objects.get(id=origin_id)
    destination = Airport.objects.get(id=destination_id)

    # Departure date
    departure_obj = datetime.strptime(depart_date, "%Y-%m-%d")
    departure_date = departure_obj.strftime("%d %b %Y")

    # Return date
    return_date_str = request.session.get('return_date', '')
    return_schedules = None
    if return_date_str:
        return_obj = datetime.strptime(return_date_str, "%Y-%m-%d")
        return_date = return_obj.strftime("%d %b %Y")
        return_schedules = Schedule.objects.filter(
            flight__route__origin_airport=destination,
            flight__route__destination_airport=origin,
            departure_time__date=return_obj.date()
        )
    else:
        return_date = None

    passenger_count = request.session.get('passenger_count')

    # Departure schedules with optimized queries
    schedules = Schedule.objects.filter(
        flight__route__origin_airport=origin,
        flight__route__destination_airport=destination,
        departure_time__date=departure_obj.date()
    ).select_related(
        'flight__airline',
        'flight__aircraft',
        'flight__route__origin_airport',
        'flight__route__destination_airport'
    ).prefetch_related(
        'seats__seat_class'
    )

    # Get all seat classes and add-ons in optimized queries
    airline_ids = set()
    
    for schedule in schedules:
        airline_ids.add(schedule.flight.airline.id)
    
    # Fetch optional add-ons
    optional_addons_dict = {}
    if airline_ids:
        optional_addons = AddOn.objects.filter(
            airline_id__in=airline_ids,
            included=False
        ).select_related('type', 'seat_class')
        
        for addon in optional_addons:
            if addon.airline_id not in optional_addons_dict:
                optional_addons_dict[addon.airline_id] = []
            optional_addons_dict[addon.airline_id].append(addon)
    
    # Attach add-ons to schedules
    for schedule in schedules:
        airline_id = schedule.flight.airline.id
        
        # For included add-ons, we need to check based on seat classes available
        schedule_seat_classes = SeatClass.objects.filter(
            seats__schedule=schedule,
            seats__is_available=True
        ).distinct()
        
        # Get included add-ons for these seat classes
        included_addons = AddOn.objects.filter(
            seat_class__in=schedule_seat_classes,
            included=True
        ).select_related('type', 'seat_class')
        
        schedule.included_addons = list(included_addons)
        schedule.optional_addons = optional_addons_dict.get(airline_id, [])
        
        # Get available seat classes for this schedule
        schedule.available_seat_classes = schedule_seat_classes

    # Similarly for return schedules
    if return_schedules:
        return_schedules = return_schedules.select_related(
            'flight__airline',
            'flight__aircraft',
            'flight__route__origin_airport',
            'flight__route__destination_airport'
        ).prefetch_related(
            'seats__seat_class'
        )
        
        # Process return schedules similarly
        for schedule in return_schedules:
            airline_id = schedule.flight.airline.id
            
            # Get included add-ons for available seat classes
            schedule_seat_classes = SeatClass.objects.filter(
                seats__schedule=schedule,
                seats__is_available=True
            ).distinct()
            
            included_addons = AddOn.objects.filter(
                seat_class__in=schedule_seat_classes,
                included=True
            ).select_related('type', 'seat_class')
            
            schedule.included_addons = list(included_addons)
            schedule.optional_addons = optional_addons_dict.get(airline_id, [])
            
            schedule.available_seat_classes = schedule_seat_classes

    template = loader.get_template('booking/schedule.html')
    context = {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "passenger_count": passenger_count,
        "schedules": schedules,
        "return_schedules": return_schedules,
        'dates': dates,
        "origin_airport": origin,
        "destination_airport": destination,
    }
    return HttpResponse(template.render(context, request))

@login_required
def reset_selection(request):
    if request.method == "POST":
        request.session.pop('depart_schedule_id', None)
        request.session.pop('return_schedule_id', None)
    return redirect('bookingapp:flight_schedules')

@login_required
def cancel_selected_schedule(request):
    # remove selected schedules from session
    request.session.pop("depart_schedule_id", None)
    request.session.pop("return_schedule_id", None)
    # keep trip_type so roundtrip still works
    return redirect("bookingapp:flight_schedules")


@never_cache
@login_required
def select_schedule(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        trip_type = request.session.get('trip_type', 'one_way')
        
        try:
            schedule = Schedule.objects.select_related(
                'flight__airline',
                'flight__route__origin_airport',
                'flight__route__destination_airport'
            ).get(id=schedule_id)
            
            # Store the selected schedule in session
            if trip_type == 'round_trip':
                # Check if we're selecting departure or return
                if not request.session.get('depart_schedule_id'):
                    # First selection is departure
                    request.session['depart_schedule_id'] = schedule_id
                    messages.success(request, "Departure flight selected. Now select your return flight.")
                    return redirect('bookingapp:flight_schedules')
                else:
                    # Second selection is return
                    request.session['return_schedule_id'] = schedule_id
                    # Redirect to review both schedules
                    return redirect('bookingapp:review_selected_scheduled')
            else:
                # One-way trip - store as departure and go to review
                request.session['depart_schedule_id'] = schedule_id
                return redirect('bookingapp:review_selected_scheduled')
            
        except Schedule.DoesNotExist:
            messages.error(request, "Selected schedule not found.")
            return redirect('bookingapp:flight_schedules')
    
    # If not POST, redirect to flight schedules
    return redirect('bookingapp:flight_schedules')

@never_cache
@login_required
def proceed_to_passengers(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        optional_addons = request.POST.getlist('optional_addons')
        
        # Store in session for the booking process
        request.session['selected_schedule'] = schedule_id
        request.session['selected_optional_addons'] = optional_addons
        
        # Redirect to passenger details page
        return redirect('bookingapp:passenger_details')
    
    return redirect('bookingapp:flight_schedules')



""" review selected schedule  """
@never_cache   
@login_required
def review_scheduled(request):
    depart_id = request.session.get('depart_schedule_id')
    return_id = request.session.get('return_schedule_id')
    
    print(f"=== REVIEW SCHEDULED DEBUG ===")
    print(f"Depart ID: {depart_id}")
    print(f"Return ID: {return_id}")

    if not depart_id:
        messages.error(request, "Please select a departure flight first.")
        return redirect("bookingapp:flight_schedules")
        
    depart_schedule = Schedule.objects.filter(id=depart_id).first()
    return_schedule = Schedule.objects.filter(id=return_id).first() if return_id else None

    template = loader.get_template('booking/selected_scheduled.html')
    context = {
        'depart_schedule': depart_schedule,
        'return_schedule': return_schedule,
    }
    return HttpResponse(template.render(context, request))

@login_required
def confirm_schedule(request):
    if request.method == 'POST':
        depart_id = request.POST.get('depart_schedule')
        return_id = request.POST.get('return_schedule')

        if depart_id:
            request.session['confirm_depart_schedule'] = depart_id
        if return_id:
            request.session['confirm_return_schedule'] = return_id

        print("confirm_depart_schedule:", request.session.get('confirm_depart_schedule'))
        print("confirm_return_schedule:", request.session.get('confirm_return_schedule'))

        # Clear the selection session data
        request.session.pop('depart_schedule_id', None)
        request.session.pop('return_schedule_id', None)

        if depart_id:  
            return redirect('bookingapp:passenger_information')
        else:
            return redirect('bookingapp:flight_schedules')




@login_required
def passenger_information(request):
    activity_id = request.session.get('activity_id')
    print(f"=== PASSENGER_INFORMATION DEBUG ===")
    print(f"Activity ID: {activity_id}")
    adults = request.session.get('adults', 1)
    children = request.session.get('children', 0)
    infants = request.session.get('infants', 0)

    total_passengers = adults + children + infants
    if total_passengers == 0:
        return redirect('bookingapp:main')

    passenger_list = []
    adult_numbers = list(range(1, adults + 1))

    # Adults
    for i in adult_numbers:
        passenger_list.append({"number": i, "type": "Adult"})

    # Children
    for i in range(1, children + 1):
        passenger_list.append({"number": adults + i, "type": "Child"})

    # Infants
    for i in range(1, infants + 1):
        passenger_list.append({"number": adults + children + i, "type": "Infant", "adult_options": adult_numbers})

    request.session['passenger_count'] = total_passengers
    request.session['passenger_list'] = passenger_list  # 🔹 Save here

    student = None
    student_id = request.session.get("student_id")
    if student_id:
        student = Student.objects.filter(id=student_id).first()

    context = {
        'passenger_list': passenger_list,
        'student': student,
    }
    return render(request, 'booking/passenger.html', context)



@login_required
def save_passengers(request):
    if request.method != 'POST':
        return redirect('bookingapp:passenger_information')

    passenger_count = request.session.get('passenger_count', 1)
    passenger_list = request.session.get('passenger_list', [])
    passengers = []

    print("=== SAVE_PASSENGERS DEBUG ===")
    print(f"Passenger count: {passenger_count}")
    print(f"Passenger list from session: {passenger_list}")
    
    for i in range(passenger_count):
        # Assign a unique string ID to each passenger
        passenger_data = {
            "id": str(i),  # IDs: "0", "1", "2", "3"
            "gender": request.POST.get(f"gender_{i+1}", "").strip(),
            "first_name": request.POST.get(f"first_name_{i+1}", "").strip(),
            "mi": request.POST.get(f"mi_{i+1}", "").strip(),
            "last_name": request.POST.get(f"last_name_{i+1}", "").strip(),
            "dob_day": request.POST.get(f"dob_day_{i+1}", "").strip(),
            "dob_month": request.POST.get(f"dob_month_{i+1}", "").strip(),
            "dob_year": request.POST.get(f"dob_year_{i+1}", "").strip(),
            "passport": request.POST.get(f"passport_{i+1}", "").strip(),
            "nationality": request.POST.get(f"nationality_{i+1}", "").strip(),
            "passenger_type": passenger_list[i]["type"] if passenger_list else "Adult"
        }

        # For infants, link to the selected adult
        if passenger_data["passenger_type"].lower() == "infant":
            adult_selection = request.POST.get(f"infant_adult_{i+1}")
            # Convert the adult selection (1-based) to passenger ID (0-based)
            if adult_selection:
                adult_id = str(int(adult_selection) - 1)  # Convert 1-based to 0-based
                passenger_data["adult_id"] = adult_id
                print(f"Infant {i+1} linked to adult selection: {adult_selection} -> passenger ID: {adult_id}")
            else:
                # Default to first adult if no selection
                adult_id = "0"
                passenger_data["adult_id"] = adult_id
                print(f"Infant {i+1} defaulted to adult ID: {adult_id}")

        passengers.append(passenger_data)
        print(f"Passenger {i}: {passenger_data['first_name']} ({passenger_data['passenger_type']}) - ID: {passenger_data['id']} - Adult ID: {passenger_data.get('adult_id', 'N/A')}")

    # Contact info
    contact_info = {
        "first_name": request.POST.get("f_name_contact", "").strip(),
        "mi": request.POST.get("m_name_contact", "").strip(),
        "last_name": request.POST.get("l_name_contact", "").strip(),
        "number": request.POST.get("number_contact", "").strip(),
        "email": request.POST.get("email_contact", "").strip(),
    }

    request.session['passengers'] = passengers
    request.session['contact_info'] = contact_info
    request.session.modified = True

    print("=== FINAL PASSENGERS IN SESSION ===")
    for p in passengers:
        print(f"ID: {p['id']}, Name: {p['first_name']}, Type: {p['passenger_type']}, Adult ID: {p.get('adult_id', 'N/A')}")
    print("===================================")

    return redirect('bookingapp:add_ons')

@login_required
def add_ons(request):
    """Page where each passenger can select individual add-ons"""
    depart_schedule_id = request.session.get('confirm_depart_schedule')
    return_schedule_id = request.session.get('confirm_return_schedule')
    
    print(f"=== ADD_ONS DEBUG ===")
    print(f"Depart schedule ID: {depart_schedule_id}")
    print(f"Return schedule ID: {return_schedule_id}")
    
    if not depart_schedule_id:
        messages.error(request, "Please select flights first.")
        return redirect('bookingapp:flight_schedules')
    
    try:
        # Get the schedules
        depart_schedule = Schedule.objects.get(id=depart_schedule_id)
        return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None
        
        # Get passengers from session
        passengers = request.session.get('passengers', [])
        
        print(f"Passengers in session: {len(passengers)}")
        for p in passengers:
            print(f"  - {p['first_name']} {p['last_name']} (ID: {p['id']})")
        
        if not passengers:
            messages.error(request, "Please enter passenger information first.")
            return redirect('bookingapp:passenger_information')
        
        # Get airline from departure flight
        airline = depart_schedule.flight.airline
        print(f"Airline: {airline.name} ({airline.code})")
        
        # Get available add-ons for this airline (only optional ones, not included)
        available_addons = AddOn.objects.filter(
            airline=airline,
            included=False  # Only show optional add-ons that passengers can choose
        ).select_related('type').order_by('type__name', 'name')
        
        print(f"Available add-ons: {available_addons.count()}")
        
        # Group add-ons by type for better organization
        addons_by_type = {}
        for addon in available_addons:
            type_name = addon.type.name if addon.type else "Other"
            if type_name not in addons_by_type:
                addons_by_type[type_name] = []
            addons_by_type[type_name].append(addon)
        
        # Get previously selected add-ons from session
        selected_addons = request.session.get('selected_addons', {})
        print(f"Selected add-ons from session: {selected_addons}")
        
        context = {
            'depart_schedule': depart_schedule,
            'return_schedule': return_schedule,
            'passengers': passengers,
            'addons_by_type': addons_by_type,
            'selected_addons': selected_addons,
            'airline': airline,
        }
        
        return render(request, 'booking/add_ons.html', context)
        
    except Schedule.DoesNotExist:
        messages.error(request, "Selected schedule not found.")
        return redirect('bookingapp:flight_schedules')
    except Exception as e:
        print(f"Error in add_ons view: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, "Error loading add-ons.")
        return redirect('bookingapp:passenger_information')

@login_required
def save_add_ons(request):
    """Save add-on selections for each passenger"""
    if request.method != 'POST':
        return redirect('bookingapp:add_ons')
    
    try:
        passengers = request.session.get('passengers', [])
        selected_addons = {}
        
        # Process add-on selections for each passenger
        for passenger in passengers:
            passenger_id = str(passenger['id'])
            
            # Get selected add-ons for this passenger
            passenger_addons = request.POST.getlist(f'addons_{passenger_id}')
            
            # Store with passenger ID as key
            selected_addons[passenger_id] = passenger_addons
        
        # Save to session
        request.session['selected_addons'] = selected_addons
        request.session.modified = True
        
        print(f"=== SAVED ADD-ONS DEBUG ===")
        print(f"Selected add-ons: {selected_addons}")
        
        messages.success(request, "Add-ons selected successfully!")
        return redirect('bookingapp:select_seat')  # Now proceed to seat selection
        
    except Exception as e:
        print(f"Error saving add-ons: {e}")
        messages.error(request, "Error saving add-on selections.")
        return redirect('bookingapp:add_ons')

@login_required
def select_seat(request):
    depart_id = request.session.get('confirm_depart_schedule')
    return_id = request.session.get('confirm_return_schedule')

    if not depart_id:
        return redirect("bookingapp:flight_schedules")

    depart_schedule = Schedule.objects.get(id=depart_id)
    return_schedule = Schedule.objects.filter(id=return_id).first() if return_id else None

    # Fetch all seats, not just available ones
    depart_seats = depart_schedule.seats.all().order_by("seat_number")
    return_seats = return_schedule.seats.all().order_by("seat_number") if return_schedule else None

    passengers = request.session.get("passengers", [])
    selected_seats = request.session.get("selected_seats", {})  # { passenger_id: {"depart": "A1", "return": "B1"} }

    context = {
        'depart_schedule' : depart_schedule,
        'return_schedule' : return_schedule,
        "depart_seats": depart_seats,
        "return_seats": return_seats,
        "passengers": passengers,
        "selected_seats": selected_seats,
    }
    return render(request, "booking/select_seats.html", context)



from django.db import transaction
from django.http import JsonResponse

# @csrf_exempt
@login_required
def confirm_seat(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."})

    seat_number = request.POST.get("seat_number")
    passenger_id = request.POST.get("passenger_id")
    trip = request.POST.get("trip")  # 'depart' or 'return'

    if not all([seat_number, passenger_id, trip]):
        return JsonResponse({"success": False, "message": "Missing required data."})

    # Initialize session storage
    selected_seats = request.session.get('selected_seats', {})
    passengers = request.session.get("passengers", [])

    # Find the selecting passenger to determine their type
    selecting_passenger = None
    for p in passengers:
        if str(p.get("id")) == passenger_id:
            selecting_passenger = p
            break

    # Assign seat to the passenger (adult or child)
    if passenger_id not in selected_seats:
        selected_seats[passenger_id] = {}
    selected_seats[passenger_id][trip] = seat_number

    # Handle infant seat assignment based on passenger type
    if selecting_passenger:
        passenger_type = selecting_passenger.get("passenger_type", "").lower()
        
        if passenger_type == "adult":
            # If an adult selects a seat, assign same seat to their infant(s)
            for p in passengers:
                p_type = p.get("passenger_type", "").lower()
                adult_id = str(p.get("adult_id", ""))
                pid = str(p.get("id"))

                if p_type == "infant" and adult_id == passenger_id:
                    if pid not in selected_seats:
                        selected_seats[pid] = {}
                    selected_seats[pid][trip] = seat_number
        elif passenger_type == "child":
            # If a child selects a seat, infants don't get assigned (infants only share with adults)
            pass  # Children don't have infants attached to them
        elif passenger_type == "infant":
            # If an infant somehow selects a seat directly, handle accordingly
            pass  # Infants shouldn't be selecting seats directly

    # Save back to session
    request.session['selected_seats'] = selected_seats
    request.session.modified = True

    # Debugging logs
    print("=== PASSENGER SEAT SELECTION ===")
    for p in passengers:
        pid = str(p.get("id"))
        seat_info = selected_seats.get(pid, {})
        print(f"{p.get('first_name')} ({p.get('passenger_type')}): {seat_info}")
    print("===============================")
    print("POST data:", request.POST)
    print("Session selected_seats:", selected_seats)

    return JsonResponse({
        "success": True,
        "seat": seat_number,
        "passenger_id": passenger_id,
        "trip": trip
    })


from decimal import Decimal

@login_required
def booking_summary(request):
    activity_id = request.session.get('activity_id')
    print(f"=== BOOKING_SUMMARY DEBUG ===")
    print(f"Activity ID: {activity_id}")
    
    depart_schedule_id = request.session.get('confirm_depart_schedule')
    return_schedule_id = request.session.get('confirm_return_schedule')

    if not depart_schedule_id and not return_schedule_id:
        return redirect("bookingapp:main")

    depart_schedule = Schedule.objects.filter(id=depart_schedule_id).first() if depart_schedule_id else None
    return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None

    passengers = request.session.get('passengers', [])
    seats = request.session.get('selected_seats', {})

    # Get selected add-ons and calculate total cost
    selected_addons = request.session.get('selected_addons', {})
    addons_details = {}
    addons_total = Decimal('0.00')
    
    # Calculate add-ons cost
    for passenger_id, addon_ids in selected_addons.items():
        addons_details[passenger_id] = []
        for addon_id in addon_ids:
            try:
                addon = AddOn.objects.get(id=addon_id)
                addons_details[passenger_id].append(addon)
                addons_total += addon.price
            except AddOn.DoesNotExist:
                continue

    # DEBUG PRINT START
    print("=== SESSION PASSENGERS & SELECTED SEATS ===")
    for passenger in passengers:
        pid = str(passenger["id"])
        seat_info = seats.get(pid, {})
        print(f"{passenger['first_name']} ({passenger['passenger_type']}): {seat_info}")
    print("Full selected_seats dict:", seats)
    print("Selected add-ons:", selected_addons)
    print("Add-ons total:", addons_total)
    print("=========================================")
    # DEBUG PRINT END

    passenger_data = []
    for passenger in passengers:
        pid = str(passenger.get("id"))
        seat_info = seats.get(pid, {})  # fetch the seat info of this passenger

        # Only infants inherit adult seat if they haven't selected one
        if passenger["passenger_type"].lower() == "infant" and not seat_info:
            adult_id = passenger.get("adult_id")
            if adult_id:
                seat_info = seats.get(str(adult_id), {})

        passenger_data.append({
            "full_name": f"{passenger['first_name']} {passenger.get('mi', '')} {passenger['last_name']}",
            "depart_seat": seat_info.get("depart", "Not selected"),
            "return_seat": seat_info.get("return", "Not selected"),
            "gender": passenger['gender'],
            "dob": f"{passenger['dob_month']}/{passenger['dob_day']}/{passenger['dob_year']}",
            "passport": passenger.get('passport', ''),
            "nationality": passenger.get('nationality', ''),
            'passenger_type' : passenger.get('passenger_type', ''),
            'id': passenger['id'],  # Add passenger ID for add-ons display
            'selected_addons': addons_details.get(pid, [])  # Add selected add-ons for this passenger
        })

    contact_info = request.session.get('contact_info', {})

    # **CORRECT PRICE CALCULATION - INCLUDING ADD-ONS**
    subtotal = Decimal('0.00')
    num_passengers = len(passengers)
    
    # Count passenger types
    adult_child_count = sum(1 for p in passengers if p.get('passenger_type', '').lower() in ['adult', 'child'])
    infant_count = sum(1 for p in passengers if p.get('passenger_type', '').lower() == 'infant')
    
    print(f"📊 Booking Summary Calculation:")
    print(f"  - Total passengers: {num_passengers}")
    print(f"  - Adults/Children: {adult_child_count}")
    print(f"  - Infants: {infant_count}")

    # Calculate price for each adult/child passenger using EXACT SAME LOGIC as BookingDetail.save()
    for passenger in passengers:
        passenger_type = passenger.get('passenger_type', '').lower()
        
        # Infants are FREE (PHP 0.00)
        if passenger_type == 'infant':
            continue
            
        passenger_price = Decimal('0.00')
        pid = str(passenger.get("id"))
        seat_info = seats.get(pid, {})
        
        # Departure flight price
        if depart_schedule:
            base_price = depart_schedule.flight.route.base_price
            
            # Get seat class multiplier for this passenger
            depart_seat_number = seat_info.get("depart")
            multiplier = Decimal('1.0')  # Default multiplier
            
            if depart_seat_number and depart_schedule:
                try:
                    seat_obj = Seat.objects.get(
                        schedule=depart_schedule, 
                        seat_number=depart_seat_number
                    )
                    if seat_obj.seat_class:
                        multiplier = seat_obj.seat_class.price_multiplier
                        print(f"  - {passenger['first_name']} depart seat class: {seat_obj.seat_class.name} (multiplier: {multiplier})")
                except Seat.DoesNotExist:
                    print(f"  - {passenger['first_name']} depart seat not found: {depart_seat_number}")
                    pass
            
            # Calculate days difference factor (same as model logic)
            days_diff = (depart_schedule.departure_time.date() - timezone.now().date()).days
            if days_diff >= 30:
                factor = Decimal("0.8")
            elif 7 <= days_diff <= 29:
                factor = Decimal("1.0")
            else:
                factor = Decimal("1.5")
            
            depart_price = base_price * multiplier * factor
            passenger_price += depart_price
            print(f"  - {passenger['first_name']} depart: {base_price} × {multiplier} × {factor} = {depart_price}")
        
        # Return flight price (if applicable)
        if return_schedule:
            return_base_price = return_schedule.flight.route.base_price
            
            # Get seat class multiplier for return flight
            return_seat_number = seat_info.get("return")
            return_multiplier = Decimal('1.0')  # Default multiplier
            
            if return_seat_number and return_schedule:
                try:
                    return_seat_obj = Seat.objects.get(
                        schedule=return_schedule, 
                        seat_number=return_seat_number
                    )
                    if return_seat_obj.seat_class:
                        return_multiplier = return_seat_obj.seat_class.price_multiplier
                        print(f"  - {passenger['first_name']} return seat class: {return_seat_obj.seat_class.name} (multiplier: {return_multiplier})")
                except Seat.DoesNotExist:
                    print(f"  - {passenger['first_name']} return seat not found: {return_seat_number}")
                    pass
            
            # Calculate days difference factor for return flight
            return_days_diff = (return_schedule.departure_time.date() - timezone.now().date()).days
            if return_days_diff >= 30:
                return_factor = Decimal("0.8")
            elif 7 <= return_days_diff <= 29:
                return_factor = Decimal("1.0")
            else:
                return_factor = Decimal("1.5")
            
            return_price = return_base_price * return_multiplier * return_factor
            passenger_price += return_price
            print(f"  - {passenger['first_name']} return: {return_base_price} × {return_multiplier} × {return_factor} = {return_price}")
        
        subtotal += passenger_price
        print(f"  - {passenger['first_name']} total passenger price: {passenger_price}")
    
    # Taxes and insurance (ALL passengers pay these, including infants)
    taxes = Decimal('20.00') * num_passengers  # PHP 20 per passenger
    insurance = Decimal('515.00') * num_passengers  # PHP 515 per passenger
    
    # Calculate totals INCLUDING ADD-ONS
    total_flight_price = subtotal + taxes + insurance
    grand_total = total_flight_price + addons_total

    print(f"💰 Final Calculation:")
    print(f"  - Subtotal (flight fares): {subtotal}")
    print(f"  - Taxes ({num_passengers} passengers × PHP 20): {taxes}")
    print(f"  - Insurance ({num_passengers} passengers × PHP 515): {insurance}")
    print(f"  - Flight Total: {total_flight_price}")
    print(f"  - Add-ons Total: {addons_total}")
    print(f"  - Grand Total: {grand_total}")

    template = loader.get_template("booking/booking_summary.html")
    context = {
        "depart_schedule": depart_schedule,
        "return_schedule": return_schedule,
        "passengers": passenger_data,
        "contact_info": contact_info,
        "num_passengers": num_passengers,
        "adult_child_count": adult_child_count,
        "infant_count": infant_count,
        "subtotal": subtotal,
        "taxes": taxes,
        "insurance": insurance,
        "total_flight_price": total_flight_price,
        "selected_addons": selected_addons,
        "addons_details": addons_details,
        "addons_total": addons_total,
        "grand_total": grand_total,
    }

    return HttpResponse(template.render(context, request))


from django.db import transaction
from django.contrib import messages
from datetime import date

@login_required
@transaction.atomic
def confirm_booking(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('bookingapp:booking_summary')
    
    passengers = request.session.get('passengers', [])
    seats = request.session.get('selected_seats', {})
    depart_schedule_id = request.session.get('confirm_depart_schedule')
    return_schedule_id = request.session.get('confirm_return_schedule')
    student_id = request.session.get('student_id')
    selected_addons = request.session.get('selected_addons', {})

    # Validate required data
    if not (depart_schedule_id and student_id and passengers):
        messages.error(request, "Booking data is missing. Please start over.")
        return redirect('bookingapp:main')

    try:
        depart_schedule = Schedule.objects.get(id=depart_schedule_id)
        return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None
        student = Student.objects.get(id=student_id)

        # 1️⃣ Create Booking
        booking = Booking.objects.create(
            student=student,
            trip_type=request.session.get('trip_type', 'one_way'),
            status="Pending"
        )

        print("=== CONFIRM_BOOKING DEBUG ===")
        print(f"Created booking: {booking.id}")
        print("Selected add-ons:", selected_addons)
        print("=============================")

        # Store created PassengerInfo objects for infant linking
        passenger_objects = {}
        
        # First pass: Create all PassengerInfo objects
        for p in passengers:
            pid = str(p.get("id"))
            
            print(f"Creating PassengerInfo for {p.get('first_name', 'No Name')} (ID: {pid}, Type: {p.get('passenger_type')})")

            # Validate required passenger data
            if not all([p.get('first_name'), p.get('last_name'), p.get('dob_year'), p.get('dob_month'), p.get('dob_day')]):
                raise ValueError(f"Missing required data for passenger {pid}")

            # Create date of birth
            dob = date(
                int(p['dob_year']), 
                int(p['dob_month']), 
                int(p['dob_day'])
            )
            
            # Create PassengerInfo
            passenger_obj = PassengerInfo.objects.create(
                first_name=p['first_name'],
                middle_name=p.get('mi', ''),
                last_name=p['last_name'],
                gender=p.get('gender', ''),
                date_of_birth=dob,
                passport_number=p.get('passport', ''),
                email=student.email,
                phone=student.phone,
                passenger_type=p.get('passenger_type', 'Adult')
            )
            
            # Store for later reference
            passenger_objects[pid] = passenger_obj
            print(f"✅ Created PassengerInfo: {passenger_obj}")

        # Track which seats we've already processed to avoid double-booking
        processed_seats = {
            'depart': set(),
            'return': set()
        }

        # Second pass: Link infants to adults and create BookingDetails
        for p in passengers:
            pid = str(p.get("id"))
            passenger_obj = passenger_objects[pid]
            seat_info = seats.get(pid, {})
            depart_seat_number = seat_info.get("depart")
            return_seat_number = seat_info.get("return")

            print(f"Processing bookings for {p.get('first_name', 'No Name')} (ID: {pid}, Type: {p.get('passenger_type')}): {seat_info}")

            # For infants, link to the adult passenger
            if p.get('passenger_type', '').lower() == 'infant' and p.get('adult_id'):
                adult_pid = p.get('adult_id')
                if adult_pid in passenger_objects:
                    adult_passenger = passenger_objects[adult_pid]
                    passenger_obj.linked_adult = adult_passenger
                    passenger_obj.save()
                    print(f"✅ Linked infant {p['first_name']} to adult {adult_passenger.first_name}")
                else:
                    print(f"⚠️ Could not find adult passenger with ID: {adult_pid}")

            # Handle departure flight booking
            if depart_seat_number:
                try:
                    # Check if this seat has already been processed for this schedule
                    seat_key = f"{depart_schedule.id}_{depart_seat_number}"
                    if seat_key in processed_seats['depart']:
                        print(f"ℹ️ Seat {depart_seat_number} already processed for depart schedule, reusing...")
                        # Seat already processed, find the existing seat object
                        outbound_seat_obj = Seat.objects.get(
                            schedule=depart_schedule, 
                            seat_number=depart_seat_number
                        )
                    else:
                        # First time processing this seat, lock and mark as unavailable
                        outbound_seat_obj = Seat.objects.select_for_update().get(
                            schedule=depart_schedule, 
                            seat_number=depart_seat_number,
                            is_available=True
                        )
                        # Mark seat as unavailable immediately
                        outbound_seat_obj.is_available = False
                        outbound_seat_obj.save()
                        processed_seats['depart'].add(seat_key)
                        print(f"✅ Marked seat {depart_seat_number} as unavailable for depart")
                    
                    # Create booking detail for departure
                    BookingDetail.objects.create(
                        booking=booking,
                        passenger=passenger_obj,
                        schedule=depart_schedule,
                        seat=outbound_seat_obj,
                        seat_class=outbound_seat_obj.seat_class,
                        price=0.00 if p.get('passenger_type', '').lower() == 'infant' else depart_schedule.price
                    )

                    print(f"✅ Created depart booking for {p['first_name']} ({p.get('passenger_type')}) - Seat: {depart_seat_number}")        

                except Seat.DoesNotExist:
                    print(f"❌ Seat {depart_seat_number} not found or unavailable for depart schedule")
                    raise ValueError(f"Seat {depart_seat_number} is not available for departure flight")

            # Handle return flight booking
            if return_schedule and return_seat_number:
                try:
                    # Check if this seat has already been processed for this schedule
                    seat_key = f"{return_schedule.id}_{return_seat_number}"
                    if seat_key in processed_seats['return']:
                        print(f"ℹ️ Seat {return_seat_number} already processed for return schedule, reusing...")
                        # Seat already processed, find the existing seat object
                        return_seat_obj = Seat.objects.get(
                            schedule=return_schedule, 
                            seat_number=return_seat_number
                        )
                    else:
                        # First time processing this seat, lock and mark as unavailable
                        return_seat_obj = Seat.objects.select_for_update().get(
                            schedule=return_schedule, 
                            seat_number=return_seat_number,
                            is_available=True
                        )
                        # Mark seat as unavailable immediately
                        return_seat_obj.is_available = False
                        return_seat_obj.save()
                        processed_seats['return'].add(seat_key)
                        print(f"✅ Marked seat {return_seat_number} as unavailable for return")
                    
                    BookingDetail.objects.create(
                        booking=booking,
                        passenger=passenger_obj,
                        schedule=return_schedule,
                        seat=return_seat_obj,
                        seat_class=return_seat_obj.seat_class,
                        price=0.00 if p.get('passenger_type', '').lower() == 'infant' else return_schedule.price
                    )
                    print(f"✅ Created return booking for {p['first_name']} ({p.get('passenger_type')}) - Seat: {return_seat_number}")
                    
                except Seat.DoesNotExist:
                    print(f"❌ Seat {return_seat_number} not found or unavailable for return schedule")
                    raise ValueError(f"Seat {return_seat_number} is not available for return flight")

        print("✅ Booking created successfully! ID:", booking.id)
        
        # CRITICAL FIX: Save booking ID to session and ensure it persists
        request.session['current_booking_id'] = booking.id
        request.session.modified = True  # Force session save
        
        print(f"✅ Session updated - current_booking_id: {request.session.get('current_booking_id')}")
        
        # Debug session state before redirect
        print("=== SESSION STATE BEFORE REDIRECT ===")
        for key, value in request.session.items():
            print(f"{key}: {value}")
        print("====================================")

    except Exception as e:
        print(f"❌ Unexpected error in confirm_booking: {str(e)}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('bookingapp:booking_summary')

    return redirect('bookingapp:payment_method')

from decimal import Decimal
from django.contrib import messages



@login_required
def payment_method(request):
    booking_id = request.session.get('current_booking_id')
    activity_id = request.session.get('activity_id')
    
    print(f"=== PAYMENT_METHOD DEBUG ===")
    print(f"Booking ID from session: {booking_id}")
    print(f"Activity ID from session: {activity_id}")

    try:
        booking = Booking.objects.get(id=booking_id)
        
        print(f"✅ Found booking: {booking.id}")

        # **ENHANCED DETAILED CALCULATION INCLUDING ADD-ONS**
        print("=== ENHANCED PRICE CALCULATION BREAKDOWN ===")
        
        # Initialize detailed breakdown
        calculation_breakdown = {
            'flight_fares': {
                'departure': Decimal('0.00'),
                'return': Decimal('0.00'),
                'total': Decimal('0.00')
            },
            'passengers': {
                'adults': 0,
                'children': 0,
                'infants': 0,
                'total': 0
            },
            'taxes_per_passenger': Decimal('20.00'),
            'insurance_per_passenger': Decimal('515.00'),
            'totals': {
                'subtotal': Decimal('0.00'),
                'taxes': Decimal('0.00'),
                'insurance': Decimal('0.00'),
                'grand_total': Decimal('0.00')
            }
        }
        
        # FIX: Get UNIQUE passengers to avoid double counting
        unique_passengers = set()
        passenger_types = {
            'adults': 0,
            'children': 0, 
            'infants': 0
        }
        
        # Calculate flight fares for each booking detail
        for detail in booking.details.all():
            passenger = detail.passenger
            passenger_type = passenger.passenger_type.lower()
            
            # Count UNIQUE passengers only once
            if passenger.id not in unique_passengers:
                unique_passengers.add(passenger.id)
                
                # Count passenger types
                if passenger_type == 'adult':
                    passenger_types['adults'] += 1
                elif passenger_type == 'child':
                    passenger_types['children'] += 1
                elif passenger_type == 'infant':
                    passenger_types['infants'] += 1
            
            # Add to flight fares (infants are free)
            if passenger_type != 'infant':
                calculation_breakdown['flight_fares']['total'] += detail.price
                
                # Determine if this is departure or return flight
                # Simple heuristic: first occurrence is departure, subsequent are return
                if calculation_breakdown['flight_fares']['departure'] == Decimal('0.00'):
                    calculation_breakdown['flight_fares']['departure'] += detail.price
                else:
                    calculation_breakdown['flight_fares']['return'] += detail.price
        
        # Update passenger counts with unique values
        calculation_breakdown['passengers']['adults'] = passenger_types['adults']
        calculation_breakdown['passengers']['children'] = passenger_types['children']
        calculation_breakdown['passengers']['infants'] = passenger_types['infants']
        calculation_breakdown['passengers']['total'] = len(unique_passengers)
        
        print(f"📊 PASSENGER COUNT DEBUG:")
        print(f"  - Unique passengers: {len(unique_passengers)}")
        print(f"  - Adults: {passenger_types['adults']}")
        print(f"  - Children: {passenger_types['children']}")
        print(f"  - Infants: {passenger_types['infants']}")
        
        # Calculate taxes and insurance (ALL passengers pay these)
        calculation_breakdown['totals']['taxes'] = (
            calculation_breakdown['taxes_per_passenger'] * calculation_breakdown['passengers']['total']
        )
        calculation_breakdown['totals']['insurance'] = (
            calculation_breakdown['insurance_per_passenger'] * calculation_breakdown['passengers']['total']
        )
        
        # Calculate subtotal and grand total
        calculation_breakdown['totals']['subtotal'] = calculation_breakdown['flight_fares']['total']
        
        # **ADD ADD-ONS TO THE CALCULATION**
        selected_addons = request.session.get('selected_addons', {})
        addons_total = Decimal('0.00')
        
        for passenger_id, addon_ids in selected_addons.items():
            for addon_id in addon_ids:
                try:
                    addon = AddOn.objects.get(id=addon_id)
                    addons_total += addon.price
                except AddOn.DoesNotExist:
                    continue
        
        # Use the calculated totals INCLUDING ADD-ONS
        calculation_breakdown['totals']['addons'] = addons_total
        calculation_breakdown['totals']['grand_total'] = (
            calculation_breakdown['totals']['subtotal'] + 
            calculation_breakdown['totals']['taxes'] + 
            calculation_breakdown['totals']['insurance'] +
            calculation_breakdown['totals']['addons']
        )

        total_amount = calculation_breakdown['totals']['grand_total']

        print(f"💰 FINAL PAYMENT CALCULATION:")
        print(f"  - Flight fares: {calculation_breakdown['flight_fares']['total']}")
        print(f"  - Taxes ({calculation_breakdown['passengers']['total']} passengers): {calculation_breakdown['totals']['taxes']}")
        print(f"  - Insurance ({calculation_breakdown['passengers']['total']} passengers): {calculation_breakdown['totals']['insurance']}")
        print(f"  - Add-ons: {addons_total}")
        print(f"  - Grand Total: {total_amount}")

        if request.method == "POST":
            method = request.POST.get("payment_method")
            if method:
                try:
                    with transaction.atomic():
                        # Create Payment
                        payment = Payment.objects.create(
                            booking=booking,
                            amount=total_amount,
                            method=method,
                            status="Completed",
                            transaction_id=f"MOCK{booking.id:05d}"
                        )

                        # Mark booking as Paid
                        booking.status = "Paid"
                        booking.save()

                        # FIX: Get unique seat IDs and verify they're properly reserved
                        seat_ids = list(booking.details
                                       .filter(seat__isnull=False)
                                       .values_list('seat_id', flat=True)
                                       .distinct())
                        
                        if seat_ids:
                            # Just verify seats are properly marked as unavailable
                            unavailable_seats = Seat.objects.filter(
                                id__in=seat_ids, 
                                is_available=True
                            )
                            if unavailable_seats.exists():
                                unavailable_seats.update(is_available=False)
                                print(f"⚠️ Fixed {unavailable_seats.count()} seats that were not properly reserved")

                        # IMPORTANT: Don't clear current_booking_id and activity_id yet!
                        keys_to_clear = [
                            "passengers", "selected_seats", "confirm_depart_schedule",
                            "confirm_return_schedule", "trip_type",
                            "origin", "destination", "departure_date", "return_date",
                            "passenger_count", "contact_info", "adults", "children", "infants",
                            "selected_addons"  # Clear add-ons too
                        ]
                        
                        student_id = request.session.get('student_id')
                        for key in keys_to_clear:
                            request.session.pop(key, None)
                        
                        # Keep these for payment_success
                        request.session['student_id'] = student_id
                        # current_booking_id and activity_id remain in session
                        request.session.modified = True

                        print(f"✅ Payment completed. Keeping booking_id ({booking_id}) and activity_id for payment_success")
                        messages.success(request, "Payment completed successfully!")

                        return redirect("bookingapp:payment_success")

                except Exception as e:
                    print(f"❌ Payment error: {str(e)}")
                    messages.error(request, f"Payment failed: {str(e)}")
                    return redirect("bookingapp:payment_method")
        
        # Render payment page with enhanced breakdown data INCLUDING ADD-ONS
        return render(request, "booking/payment.html", {
            "booking": booking,
            "payment_methods": Payment.PAYMENT_METHODS,
            "total_amount": total_amount,
            "calculation_breakdown": calculation_breakdown,  # Pass breakdown to template
            "subtotal": calculation_breakdown['totals']['subtotal'],
            "taxes": calculation_breakdown['totals']['taxes'],
            "insurance": calculation_breakdown['totals']['insurance'],
            "addons_total": addons_total,
            "num_passengers": calculation_breakdown['passengers']['total'],  # Pass correct passenger count
        })

    except Booking.DoesNotExist:
        messages.error(request, "Booking not found.")
        return redirect("bookingapp:main")



@login_required
def payment_success(request):
    booking_id = request.session.get('current_booking_id')
    activity_id = request.session.get('activity_id')
    
    print(f"=== PAYMENT_SUCCESS DEBUG ===")
    print(f"Booking ID from session: {booking_id}")
    print(f"Activity ID from session: {activity_id}")
    print(f"Practice Booking: {request.session.get('is_practice_booking')}")

     # Check if this is a practice booking
    if request.session.get('is_practice_booking'):
        return save_practice_booking(request)
    
    if booking_id and activity_id:
        try:
            booking = Booking.objects.get(id=booking_id)
            activity = Activity.objects.get(id=activity_id)
            student = Student.objects.get(id=request.session.get('student_id'))
            
            print(f"✅ Database objects found:")
            print(f"   - Booking: {booking.id} (Status: {booking.status})")
            print(f"   - Activity: {activity.title} (ID: {activity.id})")
            print(f"   - Student: {student.first_name} {student.last_name} (ID: {student.id})")
            
            # Check if submission already exists
            existing_submission = ActivitySubmission.objects.filter(
                activity=activity, 
                student=student
            ).first()
            
            if existing_submission:
                print(f"⚠️ Submission already exists: {existing_submission.id}")
                messages.info(request, f"You have already submitted this activity.")
            else:
                print("🆕 No existing submission found - creating new submission")
                
                # Calculate score before creating submission
                score = calculate_activity_score(booking, activity)
                print(f"📊 Calculated score: {score}/{activity.total_points}")
                
                # Create activity submission with score
                try:
                    submission = ActivitySubmission.objects.create(
                        activity=activity,
                        student=student,
                        booking=booking,
                        status='submitted',
                        required_trip_type=activity.required_trip_type,
                        required_travel_class=activity.required_travel_class,
                        required_passengers=activity.required_passengers,
                        required_children=activity.required_children,
                        required_infants=activity.required_infants,
                        require_passenger_details=activity.require_passenger_details,
                        required_max_price=activity.required_max_price,
                        score=score  # Add the calculated score
                    )
                    print(f"✅ SUCCESS: Created submission: {submission.id}")
                    print(f"   Submission details - Activity: {submission.activity.title}, Student: {submission.student.first_name}, Booking: {submission.booking.id}, Score: {submission.score}")
                    messages.success(request, f"Activity '{activity.title}' submitted successfully! Score: {score}/{activity.total_points}")
                    
                except Exception as create_error:
                    print(f"❌ ERROR creating submission: {create_error}")
                    import traceback
                    traceback.print_exc()
                    messages.error(request, f"Error creating submission: {create_error}")
            
            # NOW clear the session data after successful submission creation
            request.session.pop('activity_id', None)
            request.session.pop('activity_requirements', None)
            request.session.pop('current_booking_id', None)
            request.session.modified = True
            print("🧹 Cleared activity and booking data from session")
            
        except Exception as e:
            print(f"❌ Error in payment_success: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, "Error processing submission. Please contact support.")

    else:
        print("❌ Missing required session data:")
        if not booking_id:
            print("   - No booking_id in session")
        if not activity_id:
            print("   - No activity_id in session")


    # Keep student login only
    student_id = request.session.get('student_id')
    print(f"🔑 Student ID: {student_id}")

    return render(request, "booking/payment_success.html")


@login_required
def book_again(request):
    # Clear all booking-related session data but keep student login
    keys_to_clear = [
        "passengers",
        "selected_seats",
        "confirm_depart_schedule",
        "confirm_return_schedule",
        "current_booking_id",
        "trip_type",
        "origin",
        "destination",
        "departure_date",
        "return_date",
        "passenger_count",
        "contact_info",
        "selected_addons"  # Clear add-ons too
    ]
    student_id = request.session.get('student_id')
    for key in keys_to_clear:
        request.session.pop(key, None)
    request.session['student_id'] = student_id

    return redirect('bookingapp:main')






@login_required
def print_booking_info(request):
    # Get selected schedule
    schedule_id = request.session.get('confirm_schedule')
    schedule = None
    if schedule_id:
        schedule = Schedule.objects.filter(id=schedule_id).first()

    # Get passengers, seats, and contact info
    passengers = request.session.get('passengers', [])
    seats = request.session.get('seats', {})
    contact_info = request.session.get('contact_info', {}) 

    print("===== BOOKING INFO =====")
    if schedule:
        print(f"Selected Schedule: {schedule.flight.route.origin_airport} -> {schedule.flight.route.destination_airport}")
        print(f"Departure: {schedule.departure_time}")
        print(f"Flight: {schedule.flight}")
    else:
        print("No schedule selected.")

    print("\n--- Passengers ---")
    for idx, passenger in enumerate(passengers):
        seat = seats.get(str(idx), "Not selected")
        print(f"{idx+1}. {passenger['first_name']} {passenger['mi']} {passenger['last_name']} | Seat: {seat} | Gender: {passenger['gender']} | DOB: {passenger['dob_month']}/{passenger['dob_day']}/{passenger['dob_year']} | Passport: {passenger['passport']} | Nationality: {passenger['nationality']}")

    print("\n--- Booker / Contact Info ---")
    if contact_info:
        print(f"{contact_info.get('first_name', '')} {contact_info.get('mi', '')} {contact_info.get('last_name', '')}")
        print(f"Email: {contact_info.get('email', '')}")
        print(f"Phone: {contact_info.get('number', '')}")
    else:
        print("No contact info.")

    print("=========================\n")

    return HttpResponse("Booking info printed to terminal.")





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
                return redirect('bookingapp:student_home')
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
    if activity.required_max_price and total_price > float(activity.required_max_price):
        overage_amount = total_price - float(activity.required_max_price)
        overage_percentage = (overage_amount / float(activity.required_max_price)) * 100
        deductions.append({
            'category': 'Budget',
            'issue': f'Budget exceeded by ${overage_amount:.2f}',
            'details': f'Your booking cost ${total_price:.2f} but the maximum allowed was ${activity.required_max_price} (${overage_amount:.2f} over budget)',
            'points_lost': 'Up to 20%',
            'type': 'budget'
        })
        recommendations.append(f"Look for cheaper flight options or different travel dates to stay within ${activity.required_max_price} budget")
    
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
            'required_max_price': activity.required_max_price,
            'submitted_total': total_price,
            'within_budget': not activity.required_max_price or total_price <= float(activity.required_max_price),
            'overage': total_price - float(activity.required_max_price) if activity.required_max_price and total_price > float(activity.required_max_price) else 0,
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
    """Calculate points for price compliance"""
    if not activity.required_max_price:
        return float(activity.total_points) * 0.2
    
    price_points = float(activity.total_points) * 0.2
    if total_price <= float(activity.required_max_price):
        return price_points
    else:
        overage_percentage = min((total_price - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
        return price_points * (1 - overage_percentage)

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
        
        # Get detailed booking information
        booking_details = get_booking_details(booking)
        
        # Get comprehensive comparison data
        comparison_data = get_detailed_comparison(activity, booking, booking_details)
        
        # Calculate overall compliance percentage
        total_requirements = len([req for req in comparison_data['requirements'] if not req.get('optional', False)])
        met_requirements = len([req for req in comparison_data['requirements'] if req.get('met', False) and not req.get('optional', False)])
        
        compliance_percentage = (met_requirements / total_requirements * 100) if total_requirements > 0 else 0
        
        return render(request, 'booking/student/work_detail.html', {
            'submission': submission,
            'activity': activity,
            'booking': booking,
            'booking_details': booking_details,
            'comparison': comparison_data,
            'student': student,
            'compliance_percentage': compliance_percentage,
            'met_requirements': met_requirements,
            'total_requirements': total_requirements,
        })
        
    except Exception as e:
        print(f"Error in student_work_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, "Error loading work details.")
        return redirect('bookingapp:student_activities')
    



def get_detailed_comparison(activity, booking, booking_details):
    """Get detailed comparison between activity requirements and student work"""
    
    # Count passenger types
    adult_count = 0
    child_count = 0
    infant_count = 0
    total_price = booking_details['total_cost']
    
    for passenger in booking_details['passengers']:
        passenger_type = passenger['type'].lower()
        if passenger_type == 'adult':
            adult_count += 1
        elif passenger_type == 'child':
            child_count += 1
        elif passenger_type == 'infant':
            infant_count += 1
    
    # Check travel class compliance
    seat_class_names = [seat_class.name.lower() for seat_class in booking_details['seat_classes_used']]
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower() 
        for seat_class_name in seat_class_names
    )
    
    # Get actual seat classes used
    actual_classes = ", ".join([seat_class.name for seat_class in booking_details['seat_classes_used']])
    
    # Build detailed requirements comparison
    requirements = []
    
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
    
    # 4. Budget Requirement
    if activity.required_max_price:
        requirements.append({
            'category': 'Budget',
            'requirement': f'Under ${activity.required_max_price}',
            'student_work': f'${total_price:.2f}',
            'met': total_price <= float(activity.required_max_price),
            'icon': '✓' if total_price <= float(activity.required_max_price) else '✗',
            'weight': 'High',
            'overage': total_price - float(activity.required_max_price) if total_price > float(activity.required_max_price) else 0
        })
    
    # 5. Origin/Destination Requirements
    if hasattr(activity, 'required_origin') and activity.required_origin:
        first_flight = next(iter(booking_details['flights'].values()), None)
        booked_origin = first_flight['schedule'].flight.route.origin_airport.code if first_flight else 'N/A'
        requirements.append({
            'category': 'Flight Route',
            'requirement': f'Depart from {activity.required_origin}',
            'student_work': f'Depart from {booked_origin}',
            'met': booked_origin == activity.required_origin,
            'icon': '✓' if booked_origin == activity.required_origin else '✗',
            'weight': 'Medium'
        })
    
    if hasattr(activity, 'required_destination') and activity.required_destination:
        first_flight = next(iter(booking_details['flights'].values()), None)
        booked_destination = first_flight['schedule'].flight.route.destination_airport.code if first_flight else 'N/A'
        requirements.append({
            'category': 'Flight Route',
            'requirement': f'Arrive at {activity.required_destination}',
            'student_work': f'Arrive at {booked_destination}',
            'met': booked_destination == activity.required_destination,
            'icon': '✓' if booked_destination == activity.required_destination else '✗',
            'weight': 'Medium'
        })
    
    # 6. Flight Details (informational)
    for flight_id, flight_data in booking_details['flights'].items():
        schedule = flight_data['schedule']
        route = schedule.flight.route
        requirements.append({
            'category': 'Flight Details',
            'requirement': f'Flight {schedule.flight.flight_number}',
            'student_work': f'{route.origin_airport.code} → {route.destination_airport.code} on {schedule.departure_time.strftime("%b %d, %Y")}',
            'met': True,
            'icon': '✓',
            'weight': 'Info',
            'optional': True
        })
    
    # Calculate score breakdown
    score_breakdown = calculate_detailed_score_breakdown(activity, booking, booking_details, seat_class_names)
    
    return {
        'requirements': requirements,
        'score_breakdown': score_breakdown,
        'summary': {
            'total_passengers': adult_count + child_count + infant_count,
            'total_flights': len(booking_details['flights']),
            'total_cost': total_price,
            'seat_classes': actual_classes
        }
    }

def calculate_detailed_score_breakdown(activity, booking, booking_details, seat_class_names):
    """Calculate detailed score breakdown for display"""
    total_points = float(activity.total_points)
    
    # Base completion points
    base_points = total_points * 0.3
    
    # Passenger points (30%)
    adult_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'adult'])
    child_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'child'])
    infant_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'infant'])
    
    passenger_match = 0
    if adult_count == activity.required_passengers:
        passenger_match += 0.5
    if child_count == activity.required_children:
        passenger_match += 0.3
    if infant_count == activity.required_infants:
        passenger_match += 0.2
    
    passenger_points = total_points * 0.3 * passenger_match
    
    # Price points (20%)
    total_price = booking_details['total_cost']
    price_points = total_points * 0.2
    if activity.required_max_price and total_price > float(activity.required_max_price):
        overage_percentage = min((total_price - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
        price_points *= (1 - overage_percentage)
    
    # Compliance points (20%)
    compliance_match = 0
    if booking.trip_type == activity.required_trip_type:
        compliance_match += 0.5
    
    # FIXED: Use seat_class_names instead of booking_details['seat_classes_used']
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower() 
        for seat_class_name in seat_class_names
    )
    if has_correct_class:
        compliance_match += 0.5
    
    compliance_points = total_points * 0.2 * compliance_match
    
    return {
        'base_points': base_points,
        'passenger_points': passenger_points,
        'price_points': price_points,
        'compliance_points': compliance_points,
        'total_earned': base_points + passenger_points + price_points + compliance_points,
        'total_possible': total_points
    }





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
    
    # Get all passengers with their details - USING CORRECT FIELD NAMES FROM YOUR MODEL
    for detail in booking_details:
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
            'email': detail.passenger.email,
            'phone': detail.passenger.phone,
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


def get_detailed_comparison(activity, booking, booking_details):
    """Get detailed comparison between activity requirements and student work"""
    
    # Count passenger types
    adult_count = 0
    child_count = 0
    infant_count = 0
    total_price = booking_details['total_cost']
    
    for passenger in booking_details['passengers']:
        passenger_type = passenger['type'].lower()
        if passenger_type == 'adult':
            adult_count += 1
        elif passenger_type == 'child':
            child_count += 1
        elif passenger_type == 'infant':
            infant_count += 1
    
    # Check travel class compliance - FIXED: Get seat class names
    seat_class_names = [seat_class.name.lower() for seat_class in booking_details['seat_classes_used']]
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower() 
        for seat_class_name in seat_class_names
    )
    
    # Get actual seat classes used - FIXED: Use names instead of objects
    actual_classes = ", ".join([seat_class.name for seat_class in booking_details['seat_classes_used']])
    
    # Build detailed requirements comparison
    requirements = []
    
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
    
    # 4. Budget Requirement
    if activity.required_max_price:
        requirements.append({
            'category': 'Budget',
            'requirement': f'Under ${activity.required_max_price}',
            'student_work': f'${total_price:.2f}',
            'met': total_price <= float(activity.required_max_price),
            'icon': '✓' if total_price <= float(activity.required_max_price) else '✗',
            'weight': 'High',
            'overage': total_price - float(activity.required_max_price) if total_price > float(activity.required_max_price) else 0
        })
    
    # 5. Origin/Destination Requirements
    if hasattr(activity, 'required_origin') and activity.required_origin:
        first_flight = next(iter(booking_details['flights'].values()), None)
        booked_origin = first_flight['schedule'].flight.route.origin_airport.code if first_flight else 'N/A'
        requirements.append({
            'category': 'Flight Route',
            'requirement': f'Depart from {activity.required_origin}',
            'student_work': f'Depart from {booked_origin}',
            'met': booked_origin == activity.required_origin,
            'icon': '✓' if booked_origin == activity.required_origin else '✗',
            'weight': 'Medium'
        })
    
    if hasattr(activity, 'required_destination') and activity.required_destination:
        first_flight = next(iter(booking_details['flights'].values()), None)
        booked_destination = first_flight['schedule'].flight.route.destination_airport.code if first_flight else 'N/A'
        requirements.append({
            'category': 'Flight Route',
            'requirement': f'Arrive at {activity.required_destination}',
            'student_work': f'Arrive at {booked_destination}',
            'met': booked_destination == activity.required_destination,
            'icon': '✓' if booked_destination == activity.required_destination else '✗',
            'weight': 'Medium'
        })
    
    # 6. Flight Details (informational)
    for flight_id, flight_data in booking_details['flights'].items():
        schedule = flight_data['schedule']
        route = schedule.flight.route
        requirements.append({
            'category': 'Flight Details',
            'requirement': f'Flight {schedule.flight.flight_number}',
            'student_work': f'{route.origin_airport.code} → {route.destination_airport.code} on {schedule.departure_time.strftime("%b %d, %Y")}',
            'met': True,
            'icon': '✓',
            'weight': 'Info',
            'optional': True
        })
    
    # Calculate score breakdown
    score_breakdown = calculate_detailed_score_breakdown(activity, booking, booking_details, seat_class_names)
    
    return {
        'requirements': requirements,
        'score_breakdown': score_breakdown,
        'summary': {
            'total_passengers': adult_count + child_count + infant_count,
            'total_flights': len(booking_details['flights']),
            'total_cost': total_price,
            'seat_classes': actual_classes
        }
    }

def calculate_detailed_score_breakdown(activity, booking, booking_details, seat_class_names):
    """Calculate detailed score breakdown for display"""
    total_points = float(activity.total_points)
    
    # Base completion points
    base_points = total_points * 0.3
    
    # Passenger points (30%)
    adult_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'adult'])
    child_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'child'])
    infant_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'infant'])
    
    passenger_match = 0
    if adult_count == activity.required_passengers:
        passenger_match += 0.5
    if child_count == activity.required_children:
        passenger_match += 0.3
    if infant_count == activity.required_infants:
        passenger_match += 0.2
    
    passenger_points = total_points * 0.3 * passenger_match
    
    # Price points (20%)
    total_price = booking_details['total_cost']
    price_points = total_points * 0.2
    if activity.required_max_price and total_price > float(activity.required_max_price):
        overage_percentage = min((total_price - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
        price_points *= (1 - overage_percentage)
    
    # Compliance points (20%)
    compliance_match = 0
    if booking.trip_type == activity.required_trip_type:
        compliance_match += 0.5
    
    # FIXED: Use seat_class_names instead of booking_details['seat_classes_used']
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower() 
        for seat_class_name in seat_class_names
    )
    if has_correct_class:
        compliance_match += 0.5
    
    compliance_points = total_points * 0.2 * compliance_match
    
    return {
        'base_points': base_points,
        'passenger_points': passenger_points,
        'price_points': price_points,
        'compliance_points': compliance_points,
        'total_earned': base_points + passenger_points + price_points + compliance_points,
        'total_possible': total_points
    }





def calculate_detailed_score_breakdown(activity, booking, booking_details, seat_class_names):
    """Calculate detailed score breakdown for display"""
    total_points = float(activity.total_points)
    
    # Base completion points
    base_points = total_points * 0.3
    
    # Passenger points (30%)
    adult_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'adult'])
    child_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'child'])
    infant_count = len([p for p in booking_details['passengers'] if p['type'].lower() == 'infant'])
    
    passenger_match = 0
    if adult_count == activity.required_passengers:
        passenger_match += 0.5
    if child_count == activity.required_children:
        passenger_match += 0.3
    if infant_count == activity.required_infants:
        passenger_match += 0.2
    
    passenger_points = total_points * 0.3 * passenger_match
    
    # Price points (20%)
    total_price = booking_details['total_cost']
    price_points = total_points * 0.2
    if activity.required_max_price and total_price > float(activity.required_max_price):
        overage_percentage = min((total_price - float(activity.required_max_price)) / float(activity.required_max_price), 1.0)
        price_points *= (1 - overage_percentage)
    
    # Compliance points (20%)
    compliance_match = 0
    if booking.trip_type == activity.required_trip_type:
        compliance_match += 0.5
    
    # FIXED: Use seat_class_names instead of booking_details['seat_classes_used']
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower() 
        for seat_class_name in seat_class_names
    )
    if has_correct_class:
        compliance_match += 0.5
    
    compliance_points = total_points * 0.2 * compliance_match
    
    return {
        'base_points': base_points,
        'passenger_points': passenger_points,
        'price_points': price_points,
        'compliance_points': compliance_points,
        'total_earned': base_points + passenger_points + price_points + compliance_points,
        'total_possible': total_points
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
    """Save a completed practice booking"""
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
        
        # Clear practice session data
        request.session.pop('is_practice_booking', None)
        request.session.pop('is_guided_practice', None)
        request.session.pop('practice_requirements', None)
        request.session.pop('selected_addons', None)  # Clear add-ons too
        
        messages.success(request, "Practice booking saved successfully!")
        return redirect('bookingapp:practice_booking_home')
        
    except Exception as e:
        print(f"Error saving practice booking: {e}")
        messages.error(request, "Error saving practice booking.")
        return redirect('bookingapp:payment_success')