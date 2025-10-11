from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from flightapp.models import Schedule, Route,  Airport,Seat, PassengerInfo
from flightapp.models import Booking, BookingDetail, Payment, PassengerInfo, Student
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from datetime import date
from django.views.decorators.cache import never_cache
from .utils import login_required, redirect_if_logged_in
from instructorapp.models import Activity, ActivitySubmission, SectionEnrollment
from django.contrib import messages
from django.shortcuts import get_object_or_404

def calculate_activity_score(booking, activity):
    """
    Calculate score based on how well the booking matches activity requirements
    """
    total_points = activity.total_points
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
            overage_percentage = min((total_amount - activity.required_max_price) / activity.required_max_price, 1.0)
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
        detail.seat_class.lower() == activity.required_travel_class.lower() 
        for detail in booking_details
    )
    if has_correct_class:
        compliance_match += 0.5
    else:
        deduction_reasons.append(f"Travel class mismatch")
    
    points_earned += compliance_points * compliance_match
    print(f"Compliance match: {compliance_match * 100}% -> {compliance_points * compliance_match} points")
    
    # Ensure score doesn't exceed total points
    final_score = min(points_earned, total_points)
    
    print(f"Final score: {final_score}/{total_points}")
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
        activity = get_object_or_404(Activity, id=activity_id, is_code_active=True, status='published')
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
            'passengers': passengers,  # Add this line
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
        
        # Get all activities from enrolled sections - REMOVE invalid select_related fields
        all_activities = Activity.objects.filter(
            section__in=[enrollment.section for enrollment in enrolled_sections]
        ).select_related('section')  # Only select_related on valid fields
        
        # Get submitted activities
        submitted_activities = ActivitySubmission.objects.filter(
            student=student
        ).select_related('activity')
        
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



@login_required
def home(request):
    from_airports = Airport.objects.all()
    to_airports = Airport.objects.all()

    print("=== HOME PAGE SESSION DEBUG ===")
    print(f"Session activity_id: {request.session.get('activity_id')}")
    print(f"GET params - activity_id: {request.GET.get('activity_id')}, activity_code: {request.GET.get('activity_code')}")
    
    # Check for activity code from modal OR activity_id from URL
    activity_code = request.GET.get('activity_code')
    activity_id = request.GET.get('activity_id')
    activity = None
    
    # Clear any previous activity data if we're starting fresh
    if 'clear_activity' in request.GET:
        request.session.pop('activity_id', None)
        request.session.pop('activity_requirements', None)
        print("🧹 Cleared previous activity data")
    
    # If we have activity_id from GET parameters, set it in session
    if activity_id:
        try:
            activity = Activity.objects.get(
                id=activity_id, 
                is_code_active=True, 
                status='published'
            )
            # SET ACTIVITY SESSION DATA
            request.session['activity_id'] = activity.id
            request.session['activity_requirements'] = {
                'max_price': float(activity.required_max_price) if activity.required_max_price else None,
                'travel_class': activity.required_travel_class,
                'require_passenger_details': activity.require_passenger_details,
            }
            print(f"🎯 ACTIVITY SESSION SET: {activity.title} (ID: {activity.id})")
            messages.success(request, f"Activity '{activity.title}' loaded successfully!")
        except Activity.DoesNotExist:
            print(f"❌ Activity not found: {activity_id}")
            messages.error(request, "Activity not found or no longer available.")
    
    # If we only have activity_code (from home page modal)
    elif activity_code:
        try:
            activity = Activity.objects.get(
                activity_code=activity_code.upper().strip(),
                is_code_active=True, 
                status='published'
            )
            # SET ACTIVITY SESSION DATA
            request.session['activity_id'] = activity.id
            request.session['activity_requirements'] = {
                'max_price': float(activity.required_max_price) if activity.required_max_price else None,
                'travel_class': activity.required_travel_class,
                'require_passenger_details': activity.require_passenger_details,
            }
            print(f"🎯 ACTIVITY SESSION SET via code: {activity.title} (ID: {activity.id})")
            messages.success(request, f"Activity '{activity.title}' loaded successfully!")
        except Activity.DoesNotExist:
            print(f"❌ Activity code not found: {activity_code}")
            messages.error(request, "Invalid activity code. Please check with your instructor.")
    
    # Check if we have activity from session
    elif request.session.get('activity_id'):
        try:
            activity = Activity.objects.get(
                id=request.session.get('activity_id'), 
                is_code_active=True, 
                status='published'
            )
            print(f"🎯 ACTIVITY FROM SESSION: {activity.title} (ID: {activity.id})")
        except Activity.DoesNotExist:
            print(f"❌ Session activity not found: {request.session.get('activity_id')}")
            request.session.pop('activity_id', None)
            request.session.pop('activity_requirements', None)
    
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

    template = loader.get_template('booking/home.html')
    context = {
        "origins": from_airports,
        "destinations": to_airports,
        "activity": activity,
    }
    return HttpResponse(template.render(context, request))


@login_required
def search_flight(request):
    # Preserve activity_id if it exists
    activity_id = request.session.get('activity_id')
    
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
    depart_date =request.session.get('departure_date')
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

    # Departure schedules
    schedules = Schedule.objects.filter(
        flight__route__origin_airport=origin,
        flight__route__destination_airport=destination,
        departure_time__date=departure_obj.date()
    )


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


@login_required
def select_schedule(request):
    if request.method == "POST":
        schedule_id = request.POST.get("schedule")            # departure
        return_schedule_id = request.POST.get("return_schedule")  # return

        # store schedules if found
        if schedule_id:
            depart_schedule = Schedule.objects.filter(id=schedule_id).first()
            if depart_schedule:
                request.session["depart_schedule_id"] = depart_schedule.id

        if return_schedule_id:
            return_schedule = Schedule.objects.filter(id=return_schedule_id).first()
            if return_schedule:
                request.session["return_schedule_id"] = return_schedule.id

        trip_type = request.session.get("trip_type")

        # handle roundtrip logic
        if trip_type in ["roundtrip", "round_trip"]:
            if not return_schedule_id:  
                # only depart is selected, go back to schedule page
                return redirect("bookingapp:flight_schedules")
            else:
                # both depart + return are chosen → go to review
                return redirect("bookingapp:review_selected_scheduled")

        # handle one-way logic
        else:
            # after selecting departure → go straight to review
            return redirect("bookingapp:review_selected_scheduled")




""" review selected schedule  """
@never_cache   
@login_required
def review_scheduled(request):

    depart_id = request.session.get('depart_schedule_id')
    return_id = request.session.get('return_schedule_id')
    print(depart_id)
    print(return_id)

    if not depart_id:
        return redirect("bookingapp:flight_schedules")
    depart_schedule =Schedule.objects.filter(id= depart_id).first()
    return_schedule =Schedule.objects.filter(id= return_id).first() if return_id else None

    template =loader.get_template('booking/selected_scheduled.html')
    context={
        'depart_schedule':depart_schedule,
        'return_schedule':return_schedule,
    }
    return HttpResponse(template.render(context, request))

@login_required
def confirm_schedule(request):
    if request.method == 'POST':
        depart_id = request.POST.get('depart_schedule')
        return_id = request.POST.get('return_schedule')

        if depart_id:
            depart_schedule = Schedule.objects.filter(id=depart_id).first()
        else:
            depart_schedule = None

        if return_id:
            return_schedule = Schedule.objects.filter(id=return_id).first()
        else:
            return_schedule = None

        if depart_schedule:
            request.session['confirm_depart_schedule'] = depart_schedule.id
        if return_schedule:
            request.session['confirm_return_schedule'] = return_schedule.id

        print("confirm_depart_schedule:", request.session.get('confirm_depart_schedule'))
        print("confirm_return_schedule:", request.session.get('confirm_return_schedule'))


        if depart_schedule:  
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

    return redirect('bookingapp:select_seat')






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

    passengers = request.session.get('passengers', [])
    seats = request.session.get('selected_seats', {})

    # DEBUG PRINT START
    print("=== SESSION PASSENGERS & SELECTED SEATS ===")
    for passenger in passengers:
        pid = str(passenger["id"])
        seat_info = seats.get(pid, {})
        print(f"{passenger['first_name']} ({passenger['passenger_type']}): {seat_info}")
    print("Full selected_seats dict:", seats)
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
            'passenger_type' : passenger.get('passenger_type', '')
        })

        
    contact_info = request.session.get('contact_info', {})

    num_passengers = len(passengers)
    price_per_passenger = 0
    if depart_schedule:
        price_per_passenger += depart_schedule.price
    if return_schedule:
        price_per_passenger += return_schedule.price

    subtotal = price_per_passenger * num_passengers
    taxes = 20 * num_passengers
    insurance = 515 * num_passengers
    total_price = subtotal + taxes + insurance

    template = loader.get_template("booking/booking_summary.html")
    context = {
        "depart_schedule": depart_schedule,
        "return_schedule": return_schedule,
        "passengers": passenger_data,
        "contact_info": contact_info,
        "price_per_passenger": price_per_passenger,
        "num_passengers": num_passengers,
        "subtotal": subtotal,
        "taxes": taxes,
        "insurance": insurance,
        "total": total_price,
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
    
    # Debug: Check if this is an activity booking
    if activity_id:
        try:
            activity = Activity.objects.get(id=activity_id)
            print(f"🎯 ACTIVITY BOOKING DETECTED: {activity.title}")
        except Activity.DoesNotExist:
            print("❌ Activity not found")
    else:
        print("ℹ️ Regular booking (no activity)")

    try:
        booking = Booking.objects.get(id=booking_id)
        
        print(f"✅ Found booking: {booking.id}")
        
        # Check if booking details exist
        if not booking.details.exists():
            messages.error(request, "No booking details found. Please create a new booking.")
            return redirect("bookingapp:main")

        # Calculate total amount properly - only charge adults and children
        non_infant_details = booking.details.filter(passenger__passenger_type__in=['Adult', 'Child'])
        subtotal = sum(detail.price for detail in non_infant_details)
        taxes = Decimal(20) * non_infant_details.count()
        insurance = Decimal(500) * non_infant_details.count()
        total_amount = subtotal + taxes + insurance

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
                        # We need them for payment_success to create the ActivitySubmission
                        keys_to_clear = [
                            "passengers", "selected_seats", "confirm_depart_schedule",
                            "confirm_return_schedule", "trip_type",
                            "origin", "destination", "departure_date", "return_date",
                            "passenger_count", "contact_info", "adults", "children", "infants"
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
                    messages.error(request, f"Payment failed: {str(e)}")
                    return redirect("bookingapp:payment_method")

        return render(request, "booking/payment.html", {
            "booking": booking,
            "payment_methods": Payment.PAYMENT_METHODS,
            "total_amount": total_amount
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
        "contact_info"
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