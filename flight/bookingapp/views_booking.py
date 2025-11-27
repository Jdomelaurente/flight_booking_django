# bookingapp/views.py - at the top with other imports
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
from .utils import login_required, redirect_if_logged_in, calculate_activity_score
from instructorapp.models import Section, SectionEnrollment, Activity, ActivitySubmission, PracticeBooking, ActivityAddOn  # ADD Section HERE
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal
from django.db.models import Avg, Count, Sum, Q  # Add this for grade calculations

@login_required
def home(request):
    from_airports = Airport.objects.all()
    to_airports = Airport.objects.all()

    print(f"=== HOME PAGE SESSION DEBUG ===")
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
            if activity.is_due_date_passed:
                messages.error(request, "This activity has expired. The due date has passed.")
                activity = None
            else:
                # SET ACTIVITY SESSION DATA
                request.session['activity_id'] = activity.id
                request.session['activity_requirements'] = {
                    'max_price': None,  # Always set to None since budget is removed
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
            if activity.is_due_date_passed:
                messages.error(request, "This activity has expired. The due date has passed.")
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
            if activity.is_due_date_passed:
                messages.error(request, "Activity has expired. The due date has passed.")
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
        
        # VALIDATION CHECKS
        validation_errors = []
        
        # Check required fields
        if not trip_type:
            validation_errors.append("Please select a trip type.")
        
        if not origin:
            validation_errors.append("Please select origin airport.")
        
        if not destination:
            validation_errors.append("Please select destination airport.")
        
        if not departure_date:
            validation_errors.append("Please select departure date.")
        
        if trip_type == 'round_trip' and not return_date:
            validation_errors.append("Please select return date for round trip.")
        
        if adults + children + infants == 0:
            validation_errors.append("Please add at least one passenger.")
        
        # Check if origin and destination are different
        if origin and destination and origin == destination:
            validation_errors.append("Origin and destination airports cannot be the same.")
        
        # Check date validity
        if departure_date:
            try:
                depart_date_obj = datetime.strptime(departure_date, "%Y-%m-%d").date()
                today = timezone.now().date()
                
                if depart_date_obj < today:
                    validation_errors.append("Departure date cannot be in the past.")
                
                if return_date:
                    return_date_obj = datetime.strptime(return_date, "%Y-%m-%d").date()
                    if return_date_obj <= depart_date_obj:
                        validation_errors.append("Return date must be after departure date.")
                    
                    if return_date_obj < today:
                        validation_errors.append("Return date cannot be in the past.")
                        
            except ValueError:
                validation_errors.append("Invalid date format.")
        
        # If there are validation errors, return to home with errors
        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            return redirect('bookingapp:main')
        
        # If validation passes, store data in session
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

        # Show success message
        messages.success(request, "Flight search criteria saved successfully! Loading available flights...")
        
        # Render loading template instead of direct redirect
        return render(request, 'booking/loading_schedule.html')

    # If GET request, redirect to main
    return redirect('bookingapp:main')

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

    # Check if we have required session data
    if not origin_id or not destination_id or not depart_date:
        messages.error(request, "Please complete your flight search first.")
        return redirect('bookingapp:main')

    try:
        origin = Airport.objects.get(id=origin_id)
        destination = Airport.objects.get(id=destination_id)
    except Airport.DoesNotExist:
        messages.error(request, "Invalid airport selection. Please try again.")
        return redirect('bookingapp:main')

    # Departure date
    try:
        departure_obj = datetime.strptime(depart_date, "%Y-%m-%d")
        departure_date = departure_obj.strftime("%d %b %Y")
    except ValueError:
        messages.error(request, "Invalid departure date format.")
        return redirect('bookingapp:main')

    # Return date
    return_date_str = request.session.get('return_date', '')
    return_schedules = None
    if return_date_str:
        try:
            return_obj = datetime.strptime(return_date_str, "%Y-%m-%d")
            return_date = return_obj.strftime("%d %b %Y")
            return_schedules = Schedule.objects.filter(
                flight__route__origin_airport=destination,
                flight__route__destination_airport=origin,
                departure_time__date=return_obj.date()
            )
        except ValueError:
            messages.error(request, "Invalid return date format.")
            return redirect('bookingapp:main')
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

    # Add success message if schedules were found
    if schedules.exists():
        messages.success(request, f"Found {schedules.count()} available flights from {origin.code} to {destination.code}")
    else:
        messages.warning(request, f"No flights found for your selected route and date. Please try different search criteria.")

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
        messages.info(request, "Flight selection has been reset. You can choose new flights.")
    return redirect('bookingapp:flight_schedules')

@login_required
def cancel_selected_schedule(request):
    # remove selected schedules from session
    request.session.pop("depart_schedule_id", None)
    request.session.pop("return_schedule_id", None)
    messages.info(request, "Flight selection cancelled. You can choose new flights.")
    # keep trip_type so roundtrip still works
    return redirect("bookingapp:flight_schedules")

@never_cache
@login_required
def select_schedule(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        trip_type = request.session.get('trip_type', 'one_way')
        
        if not schedule_id:
            messages.error(request, "No schedule selected. Please select a flight.")
            return redirect('bookingapp:flight_schedules')
        
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
                    messages.success(request, 
                        f"✅ Departure flight selected: {schedule.flight.airline.code} {schedule.flight.flight_number} "
                        f"from {schedule.flight.route.origin_airport.code} to {schedule.flight.route.destination_airport.code} "
                        f"on {schedule.departure_time.strftime('%b %d, %Y')}"
                    )
                    return redirect('bookingapp:flight_schedules')
                else:
                    # Second selection is return
                    request.session['return_schedule_id'] = schedule_id
                    messages.success(request, 
                        f"✅ Return flight selected: {schedule.flight.airline.code} {schedule.flight.flight_number} "
                        f"from {schedule.flight.route.origin_airport.code} to {schedule.flight.route.destination_airport.code} "
                        f"on {schedule.departure_time.strftime('%b %d, %Y')}"
                    )
                    # Redirect to review both schedules
                    return redirect('bookingapp:review_selected_scheduled')
            else:
                # One-way trip - store as departure and go to review
                request.session['depart_schedule_id'] = schedule_id
                messages.success(request, 
                    f"✅ Flight selected: {schedule.flight.airline.code} {schedule.flight.flight_number} "
                    f"from {schedule.flight.route.origin_airport.code} to {schedule.flight.route.destination_airport.code} "
                    f"on {schedule.departure_time.strftime('%b %d, %Y')}"
                )
                return redirect('bookingapp:review_selected_scheduled')
            
        except Schedule.DoesNotExist:
            messages.error(request, "Selected schedule not found. Please choose another flight.")
            return redirect('bookingapp:flight_schedules')
        except Exception as e:
            messages.error(request, f"Error selecting schedule: {str(e)}")
            return redirect('bookingapp:flight_schedules')
    
    # If not POST, redirect to flight schedules
    messages.error(request, "Invalid request method.")
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
        # "number": request.POST.get("number_contact", "").strip(),
        # "email": request.POST.get("email_contact", "").strip(),
    }

    request.session['passengers'] = passengers
    request.session['contact_info'] = contact_info
    request.session.modified = True

    print("=== FINAL PASSENGERS IN SESSION ===")
    for p in passengers:
        print(f"ID: {p['id']}, Name: {p['first_name']}, Type: {p['passenger_type']}, Adult ID: {p.get('adult_id', 'N/A')}")
    print("===================================")

    # Render loading template instead of direct redirect
    return render(request, 'booking/loading_passenger.html')

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

# Add these new views to your existing views.py file
@login_required
def baggage_addon(request):
    """Page specifically for baggage add-ons"""
    print(f"=== BAGGAGE_ADDON DEBUG ===")
    print(f"GET parameters: {request.GET}")
    
    airline_id = request.GET.get('airline_id')
    schedule_id = request.GET.get('schedule_id')
    return_schedule_id = request.GET.get('return_schedule_id')
    
    print(f"Airline ID: {airline_id}")
    print(f"Schedule ID: {schedule_id}")
    print(f"Return Schedule ID: {return_schedule_id}")
    
    try:
        # Get airline
        airline = None
        if airline_id:
            try:
                airline = Airline.objects.get(id=airline_id)
                print(f"Found airline: {airline.name}")
            except Airline.DoesNotExist:
                print(f"Airline not found with ID: {airline_id}")
                messages.error(request, "Airline not found.")
                return redirect('bookingapp:add_ons')
        
        # Get schedules
        schedule = None
        if schedule_id:
            try:
                schedule = Schedule.objects.get(id=schedule_id)
                print(f"Found schedule: {schedule.flight.flight_number}")
            except Schedule.DoesNotExist:
                print(f"Schedule not found with ID: {schedule_id}")
                messages.error(request, "Schedule not found.")
                return redirect('bookingapp:add_ons')
        
        return_schedule = None
        if return_schedule_id:
            try:
                return_schedule = Schedule.objects.get(id=return_schedule_id)
                print(f"Found return schedule: {return_schedule.flight.flight_number}")
            except Schedule.DoesNotExist:
                print(f"Return schedule not found with ID: {return_schedule_id}")
                # Don't redirect for return schedule - it might be optional
        
        # Get passengers from session
        passengers = request.session.get('passengers', [])
        print(f"Passengers in session: {len(passengers)}")
        
        if not passengers:
            messages.error(request, "Please enter passenger information first.")
            return redirect('bookingapp:passenger_information')
        
        # Get baggage-specific add-ons
        baggage_addons = AddOn.objects.filter(
            airline=airline,
            type__name__icontains='baggage',
            included=False
        ).select_related('type').order_by('price')
        
        print(f"Found {baggage_addons.count()} baggage add-ons")
        
        # Get previously selected add-ons from session
        selected_addons = request.session.get('selected_addons', {})
        print(f"Selected add-ons: {selected_addons}")
        
        # Prepare passenger data with their selected add-ons
        passenger_data = []
        for passenger in passengers:
            passenger_id = str(passenger['id'])
            passenger_addons = selected_addons.get(passenger_id, [])
            
            # Get addon objects for this passenger
            addon_objects = []
            for addon_id in passenger_addons:
                try:
                    addon = AddOn.objects.get(id=addon_id)
                    addon_objects.append(addon)
                except AddOn.DoesNotExist:
                    continue
            
            passenger_data.append({
                'id': passenger_id,
                'first_name': passenger['first_name'],
                'last_name': passenger['last_name'],
                'passenger_type': passenger['passenger_type'],
                'selected_addons': addon_objects
            })
        total_price = 0
        for passenger in passenger_data:
            for addon in passenger['selected_addons']:
                total_price += addon.price
        context = {
            'addons': baggage_addons,
            'airline': airline,
            'schedule': schedule,
            'return_schedule': return_schedule,
            'passengers': passenger_data,  # Use processed passenger data
            'selected_addons': selected_addons,
            'addon_type': 'Baggage',
            'depart_schedule': schedule,
            'total_price': total_price,
        }
        
        return render(request, 'booking/addons/baggage.html', context)
        
    except Exception as e:
        print(f"Error loading baggage options: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, "Error loading baggage options.")
        return redirect('bookingapp:add_ons')

@login_required
def meals_addon(request):
    """Page specifically for meal add-ons"""
    airline_id = request.GET.get('airline_id')
    schedule_id = request.GET.get('schedule_id')
    return_schedule_id = request.GET.get('return_schedule_id')
    
    try:
        airline = Airline.objects.get(id=airline_id) if airline_id else None
        schedule = Schedule.objects.get(id=schedule_id) if schedule_id else None
        return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None
        
        # Get passengers from session
        passengers = request.session.get('passengers', [])
        
        # Get meal-specific add-ons
        meal_addons = AddOn.objects.filter(
            airline=airline,
            type__name__icontains='meal',
            included=False
        )
        
        # Get previously selected add-ons from session
        selected_addons = request.session.get('selected_addons', {})
        
        context = {
            'addons': meal_addons,
            'airline': airline,
            'schedule': schedule,
            'return_schedule': return_schedule,
            'passengers': passengers,
            'selected_addons': selected_addons,
            'addon_type': 'Meals',
            'depart_schedule': schedule,  # For template compatibility
        }
        return render(request, 'booking/addons/meals.html', context)
        
    except Exception as e:
        print(f"Error loading meal options: {e}")
        messages.error(request, "Error loading meal options.")
        return redirect('bookingapp:add_ons')

@login_required
def seat_selection_addon(request):
    """Redirect to main seat selection page"""
    airline_id = request.GET.get('airline_id')
    schedule_id = request.GET.get('schedule_id')
    return_schedule_id = request.GET.get('return_schedule_id')
    
    redirect_url = f"{reverse('bookingapp:select_seat')}?from_addons=true&airline_id={airline_id}&schedule_id={schedule_id}"
    if return_schedule_id:
        redirect_url += f"&return_schedule_id={return_schedule_id}"
        
    return redirect(redirect_url)

@login_required
def lounge_addon(request):
    """Page specifically for lounge access add-ons"""
    airline_id = request.GET.get('airline_id')
    schedule_id = request.GET.get('schedule_id')
    return_schedule_id = request.GET.get('return_schedule_id')
    
    try:
        airline = Airline.objects.get(id=airline_id) if airline_id else None
        schedule = Schedule.objects.get(id=schedule_id) if schedule_id else None
        return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None
        
        # Get passengers from session
        passengers = request.session.get('passengers', [])
        
        # Get lounge access add-ons
        lounge_addons = AddOn.objects.filter(
            airline=airline,
            type__name__icontains='lounge',
            included=False
        )
        
        # Get previously selected add-ons from session
        selected_addons = request.session.get('selected_addons', {})
        
        context = {
            'addons': lounge_addons,
            'airline': airline,
            'schedule': schedule,
            'return_schedule': return_schedule,
            'passengers': passengers,
            'selected_addons': selected_addons,
            'addon_type': 'Lounge Access',
            'depart_schedule': schedule,  # For template compatibility
        }
        return render(request, 'booking/addons/lounge.html', context)
        
    except Exception as e:
        print(f"Error loading lounge options: {e}")
        messages.error(request, "Error loading lounge options.")
        return redirect('bookingapp:add_ons')

@login_required
def insurance_addon(request):
    """Page specifically for travel insurance"""
    airline_id = request.GET.get('airline_id')
    schedule_id = request.GET.get('schedule_id')
    return_schedule_id = request.GET.get('return_schedule_id')
    
    try:
        airline = Airline.objects.get(id=airline_id) if airline_id else None
        schedule = Schedule.objects.get(id=schedule_id) if schedule_id else None
        return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None
        
        # Get passengers from session
        passengers = request.session.get('passengers', [])
        
        # Get insurance add-ons
        insurance_addons = AddOn.objects.filter(
            airline=airline,
            type__name__icontains='insurance',
            included=False
        )
        
        # Get previously selected add-ons from session
        selected_addons = request.session.get('selected_addons', {})
        
        context = {
            'addons': insurance_addons,
            'airline': airline,
            'schedule': schedule,
            'return_schedule': return_schedule,
            'passengers': passengers,
            'selected_addons': selected_addons,
            'addon_type': 'Travel Insurance',
            'depart_schedule': schedule,  # For template compatibility
        }
        return render(request, 'booking/addons/insurance.html', context)
        
    except Exception as e:
        print(f"Error loading insurance options: {e}")
        messages.error(request, "Error loading insurance options.")
        return redirect('bookingapp:add_ons')
@login_required
def wheelchair_addon(request):
    """Page specifically for wheelchair service add-ons"""
    airline_id = request.GET.get('airline_id')
    schedule_id = request.GET.get('schedule_id')
    return_schedule_id = request.GET.get('return_schedule_id')
    
    try:
        airline = Airline.objects.get(id=airline_id) if airline_id else None
        schedule = Schedule.objects.get(id=schedule_id) if schedule_id else None
        return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None
        
        # Get passengers from session
        passengers = request.session.get('passengers', [])
        
        # Get wheelchair service add-ons
        wheelchair_addons = AddOn.objects.filter(
            airline=airline,
            type__name__icontains='wheelchair',
            included=False
        )
        
        # Get previously selected add-ons from session
        selected_addons = request.session.get('selected_addons', {})
        
        context = {
            'addons': wheelchair_addons,
            'airline': airline,
            'schedule': schedule,
            'return_schedule': return_schedule,
            'passengers': passengers,
            'selected_addons': selected_addons,
            'addon_type': 'Wheelchair Service',
            'depart_schedule': schedule,
        }
        return render(request, 'booking/addons/wheelchair.html', context)
        
    except Exception as e:
        print(f"Error loading wheelchair options: {e}")
        messages.error(request, "Error loading wheelchair service options.")
        return redirect('bookingapp:add_ons')    

@login_required
def quick_addons(request):
    """Quick selection page for all add-ons"""
    airline_id = request.GET.get('airline_id')
    schedule_id = request.GET.get('schedule_id')
    return_schedule_id = request.GET.get('return_schedule_id')
    
    try:
        airline = Airline.objects.get(id=airline_id) if airline_id else None
        schedule = Schedule.objects.get(id=schedule_id) if schedule_id else None
        return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None
        
        # Get passengers from session
        passengers = request.session.get('passengers', [])
        
        # Get all available add-ons for this airline
        available_addons = AddOn.objects.filter(
            airline=airline,
            included=False
        ).select_related('type').order_by('type__name', 'name')
        
        # Group add-ons by type for better organization
        addons_by_type = {}
        for addon in available_addons:
            type_name = addon.type.name if addon.type else "Other"
            if type_name not in addons_by_type:
                addons_by_type[type_name] = []
            addons_by_type[type_name].append(addon)
        
        # Get previously selected add-ons from session
        selected_addons = request.session.get('selected_addons', {})
        
        context = {
            'depart_schedule': schedule,
            'return_schedule': return_schedule,
            'passengers': passengers,
            'addons_by_type': addons_by_type,
            'selected_addons': selected_addons,
            'airline': airline,
        }
        return render(request, 'booking/addons/quick_selection.html', context)
        
    except Exception as e:
        print(f"Error loading quick add-ons: {e}")
        messages.error(request, "Error loading add-ons.")
        return redirect('bookingapp:add_ons')

@login_required
def save_single_addon(request):
    """Save add-on selections from individual add-on pages - handles both selection and deselection"""
    if request.method != 'POST':
        return redirect('bookingapp:add_ons')
    
    try:
        passengers = request.session.get('passengers', [])
        selected_addons = request.session.get('selected_addons', {})
        
        # Process add-on selections for each passenger
        for passenger in passengers:
            passenger_id = str(passenger['id'])
            
            # Get selected add-ons for this passenger from the form
            # This will be an empty list if nothing is checked
            passenger_addons = request.POST.getlist(f'addons_{passenger_id}')
            
            # Update the selected add-ons for this passenger
            # This REPLACES the entire list, so unchecked items are removed
            selected_addons[passenger_id] = passenger_addons
        
        # Save to session
        request.session['selected_addons'] = selected_addons
        request.session.modified = True
        
        print(f"=== SAVED SINGLE ADD-ON DEBUG ===")
        print(f"Selected add-ons after save: {selected_addons}")
        
        messages.success(request, "Baggage selections updated successfully!")
        
        # Redirect back to the baggage page with the same parameters
        airline_id = request.POST.get('airline_id')
        schedule_id = request.POST.get('schedule_id')
        return_schedule_id = request.POST.get('return_schedule_id')
        
        redirect_url = f"{reverse('bookingapp:baggage_addon')}?airline_id={airline_id}&schedule_id={schedule_id}"
        if return_schedule_id:
            redirect_url += f"&return_schedule_id={return_schedule_id}"
            
        return redirect(redirect_url)
        
    except Exception as e:
        print(f"Error saving add-ons: {e}")
        messages.error(request, "Error saving baggage selections.")
        return redirect('bookingapp:add_ons')

@login_required
def remove_addon(request):
    """Remove a specific add-on from a passenger"""
    if request.method == 'POST':
        try:
            passenger_id = request.POST.get('passenger_id')
            addon_id = request.POST.get('addon_id')
            
            selected_addons = request.session.get('selected_addons', {})
            
            if passenger_id in selected_addons and addon_id in selected_addons[passenger_id]:
                selected_addons[passenger_id].remove(addon_id)
                request.session['selected_addons'] = selected_addons
                request.session.modified = True
                
                messages.success(request, "Add-on removed successfully!")
            
        except Exception as e:
            print(f"Error removing add-on: {e}")
            messages.error(request, "Error removing add-on.")
    
    return redirect('bookingapp:add_ons')    

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

    # Check if coming from add-ons page
    from_addons = request.GET.get('from_addons') == 'true'
    skip_addons = request.GET.get('skip_addons') == 'true'
    
    # If skipping add-ons, clear any selected add-ons
    if skip_addons:
        request.session['selected_addons'] = {}
        request.session.modified = True
        messages.info(request, "Add-ons skipped. You can add them later if needed.")

    depart_schedule = Schedule.objects.get(id=depart_id)
    return_schedule = Schedule.objects.filter(id=return_id).first() if return_id else None

    # Fetch all seats, not just available ones
    depart_seats = depart_schedule.seats.all().order_by("seat_number")
    return_seats = return_schedule.seats.all().order_by("seat_number") if return_schedule else None

    passengers = request.session.get("passengers", [])
    selected_seats = request.session.get("selected_seats", {})  # { passenger_id: {"depart": "A1", "return": "B1"} }

    context = {
        'depart_schedule': depart_schedule,
        'return_schedule': return_schedule,
        "depart_seats": depart_seats,
        "return_seats": return_seats,
        "passengers": passengers,
        "selected_seats": selected_seats,
        "from_addons": from_addons,  # Pass this to template to show different messaging
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
    print(f"=== SESSION DATA DEBUG ===")
    print(f"Session keys: {list(request.session.keys())}")
    print(f"Selected add-ons in session: {request.session.get('selected_addons')}")
    print(f"Passengers in session: {request.session.get('passengers')}")
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

    print(f"=== ADD-ONS DEBUG IN BOOKING SUMMARY ===")
    print(f"Selected add-ons from session: {selected_addons}")

    # Calculate add-ons cost - CORRECTED LOGIC
    if selected_addons:
        for passenger_id, addon_ids in selected_addons.items():
            if addon_ids:  # Only process if there are add-ons for this passenger
                addons_details[passenger_id] = []
                for addon_id in addon_ids:
                    try:
                        addon = AddOn.objects.get(id=addon_id)
                        addons_details[passenger_id].append({
                            'id': addon.id,
                            'name': addon.name,
                            'description': addon.description,
                            'price': addon.price,
                            'type': addon.type.name if addon.type else 'General'
                        })
                        addons_total += addon.price
                        print(f"✅ Added add-on: {addon.name} (ID: {addon_id}) - Price: {addon.price} for passenger {passenger_id}")
                    except AddOn.DoesNotExist:
                        print(f"❌ Add-on with ID {addon_id} not found - skipping")
                        continue
    else:
        print("❌ No selected add-ons found in session")

    print(f"Total add-ons cost calculated: {addons_total}")
    print(f"Add-ons details: {addons_details}")
    print("=========================================")

    # Get included add-ons for both schedules based on seat classes
    depart_included_addons = []
    return_included_addons = []
    
    if depart_schedule:
        # Get unique seat classes from selected seats for departure
        depart_seat_classes = set()
        for passenger in passengers:
            pid = str(passenger.get("id"))
            seat_info = seats.get(pid, {})
            depart_seat_number = seat_info.get("depart")
            
            if depart_seat_number and depart_schedule:
                try:
                    seat_obj = Seat.objects.get(
                        schedule=depart_schedule, 
                        seat_number=depart_seat_number
                    )
                    if seat_obj.seat_class:
                        depart_seat_classes.add(seat_obj.seat_class)
                except Seat.DoesNotExist:
                    pass
        
        # Get included add-ons for these seat classes
        if depart_seat_classes:
            depart_included_addons = AddOn.objects.filter(
                seat_class__in=depart_seat_classes,
                included=True  # This is the key filter for included add-ons
            ).select_related('type', 'seat_class', 'airline').distinct()
    
    if return_schedule:
        # Get unique seat classes from selected seats for return flight
        return_seat_classes = set()
        for passenger in passengers:
            pid = str(passenger.get("id"))
            seat_info = seats.get(pid, {})
            return_seat_number = seat_info.get("return")
            
            if return_seat_number and return_schedule:
                try:
                    seat_obj = Seat.objects.get(
                        schedule=return_schedule, 
                        seat_number=return_seat_number
                    )
                    if seat_obj.seat_class:
                        return_seat_classes.add(seat_obj.seat_class)
                except Seat.DoesNotExist:
                    pass
        
        # Get included add-ons for these seat classes
        if return_seat_classes:
            return_included_addons = AddOn.objects.filter(
                seat_class__in=return_seat_classes,
                included=True  # This is the key filter for included add-ons
            ).select_related('type', 'seat_class', 'airline').distinct()

    # DEBUG PRINT START
    print("=== INCLUDED ADD-ONS DEBUG ===")
    print("Departure seat classes:", [sc.name for sc in depart_seat_classes] if depart_schedule else "No departure schedule")
    print("Departure included add-ons:", [f"{addon.name} ({addon.seat_class.name})" for addon in depart_included_addons])
    print("Return seat classes:", [sc.name for sc in return_seat_classes] if return_schedule else "No return schedule")
    print("Return included add-ons:", [f"{addon.name} ({addon.seat_class.name})" for addon in return_included_addons])
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

        # Get seat class for this passenger
        depart_seat_class = None
        return_seat_class = None
        
        if depart_schedule and seat_info.get("depart"):
            try:
                depart_seat_obj = Seat.objects.get(
                    schedule=depart_schedule, 
                    seat_number=seat_info.get("depart")
                )
                depart_seat_class = depart_seat_obj.seat_class
            except Seat.DoesNotExist:
                pass
        
        if return_schedule and seat_info.get("return"):
            try:
                return_seat_obj = Seat.objects.get(
                    schedule=return_schedule, 
                    seat_number=seat_info.get("return")
                )
                return_seat_class = return_seat_obj.seat_class
            except Seat.DoesNotExist:
                pass

        # Get included add-ons specific to this passenger's seat classes
        passenger_depart_included = []
        passenger_return_included = []
        
        if depart_seat_class:
            passenger_depart_included = AddOn.objects.filter(
                seat_class=depart_seat_class,
                included=True
            ).select_related('type', 'seat_class', 'airline')
        
        if return_seat_class:
            passenger_return_included = AddOn.objects.filter(
                seat_class=return_seat_class,
                included=True
            ).select_related('type', 'seat_class', 'airline')

        # DEBUG: Check what add-ons this passenger has
        passenger_addons = addons_details.get(str(passenger['id']), [])
        print(f"Passenger {pid} ({passenger['first_name']}) has {len(passenger_addons)} selected add-ons")

        passenger_data.append({
            "full_name": f"{passenger['first_name']} {passenger.get('mi', '')} {passenger['last_name']}",
            "depart_seat": seat_info.get("depart", "Not selected"),
            "return_seat": seat_info.get("return", "Not selected"),
            "depart_seat_class": depart_seat_class,
            "return_seat_class": return_seat_class,
            "gender": passenger['gender'],
            "dob": f"{passenger['dob_month']}/{passenger['dob_day']}/{passenger['dob_year']}",
            "passport": passenger.get('passport', ''),
            "nationality": passenger.get('nationality', ''),
            'passenger_type': passenger.get('passenger_type', ''),
            'id': passenger['id'],
            'selected_addons': passenger_addons,  # This should now have the correct data
            'depart_included_addons': passenger_depart_included,
            'return_included_addons': passenger_return_included,
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
    print(f"  - Add-ons Total: {addons_total}")  # DEBUG


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
        "addons_details": addons_details,  # This should now have the correct data
        "addons_total": addons_total,
        "grand_total": grand_total,
        "depart_included_addons": depart_included_addons,
        "return_included_addons": return_included_addons,
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

    # VALIDATION CHECKS
    validation_errors = []
    
    # Validate required data
    if not depart_schedule_id:
        validation_errors.append("Please select a departure flight.")
    
    if not student_id:
        validation_errors.append("Student session expired. Please login again.")
    
    if not passengers:
        validation_errors.append("Passenger information is missing.")
    
    # Check if all passengers have seats for departure
    if depart_schedule_id:
        for passenger in passengers:
            pid = str(passenger.get("id"))
            seat_info = seats.get(pid, {})
            if not seat_info.get("depart"):
                validation_errors.append(f"Please select a departure seat for {passenger.get('first_name', 'passenger')}.")
                break
    
    # Check if return seats are selected for round trip
    if return_schedule_id:
        for passenger in passengers:
            pid = str(passenger.get("id"))
            seat_info = seats.get(pid, {})
            if not seat_info.get("return"):
                validation_errors.append(f"Please select a return seat for {passenger.get('first_name', 'passenger')}.")
                break

    # If validation errors, return to summary with errors
    if validation_errors:
        for error in validation_errors:
            messages.error(request, error)
        return redirect('bookingapp:booking_summary')

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
        print(f"Total passengers from session: {len(passengers)}")
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

        # Store booking details for add-on linking
        booking_details_map = {}  # { passenger_id: { 'depart': booking_detail, 'return': booking_detail } }

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

            # Initialize booking details map for this passenger
            booking_details_map[pid] = {}

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
                    depart_booking_detail = BookingDetail.objects.create(
                        booking=booking,
                        passenger=passenger_obj,
                        schedule=depart_schedule,
                        seat=outbound_seat_obj,
                        seat_class=outbound_seat_obj.seat_class,
                        price=0.00 if p.get('passenger_type', '').lower() == 'infant' else depart_schedule.price
                    )

                    # Store for add-on linking
                    booking_details_map[pid]['depart'] = depart_booking_detail

                    print(f"✅ Created depart booking for {p['first_name']} ({p.get('passenger_type')}) - Seat: {depart_seat_number}")        

                except Seat.DoesNotExist:
                    print(f"❌ Seat {depart_seat_number} not found or unavailable for depart schedule")
                    messages.error(request, f"Seat {depart_seat_number} is no longer available. Please select different seats.")
                    return redirect('bookingapp:booking_summary')

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
                    
                    # Create booking detail for return
                    return_booking_detail = BookingDetail.objects.create(
                        booking=booking,
                        passenger=passenger_obj,
                        schedule=return_schedule,
                        seat=return_seat_obj,
                        seat_class=return_seat_obj.seat_class,
                        price=0.00 if p.get('passenger_type', '').lower() == 'infant' else return_schedule.price
                    )

                    # Store for add-on linking
                    booking_details_map[pid]['return'] = return_booking_detail

                    print(f"✅ Created return booking for {p['first_name']} ({p.get('passenger_type')}) - Seat: {return_seat_number}")
                    
                except Seat.DoesNotExist:
                    print(f"❌ Seat {return_seat_number} not found or unavailable for return schedule")
                    messages.error(request, f"Seat {return_seat_number} is no longer available. Please select different seats.")
                    return redirect('bookingapp:booking_summary')

        # 🔥 PROCESS ADD-ONS FOR EACH PASSENGER
        print("=== PROCESSING ADD-ONS ===")
        addons_processed = 0
        
        for passenger_id, addon_ids in selected_addons.items():
            print(f"Processing add-ons for passenger {passenger_id}: {addon_ids}")
            
            if passenger_id in booking_details_map:
                passenger_details = booking_details_map[passenger_id]
                
                for addon_id in addon_ids:
                    try:
                        addon = AddOn.objects.get(id=addon_id)
                        
                        # Link add-on to ALL booking details for this passenger
                        for flight_type, booking_detail in passenger_details.items():
                            booking_detail.addons.add(addon)
                            
                            print(f"✅ Linked add-on '{addon.name}' ({addon.type}) to {flight_type} flight for passenger {passenger_id}")
                            addons_processed += 1
                            
                    except AddOn.DoesNotExist:
                        print(f"⚠️ Add-on with ID {addon_id} not found - skipping")
                        continue
        
        print(f"✅ Successfully processed {addons_processed} add-on links")

        # DEBUG: Count actual booking details created
        total_booking_details = booking.details.count()
        
        print(f"📊 BOOKING CREATION SUMMARY:")
        print(f"  - Total BookingDetail objects created: {total_booking_details}")
        print(f"  - Expected passengers: {len(passengers)}")
        
        print("✅ Booking created successfully! ID:", booking.id)
        
        # CRITICAL FIX: Save booking ID to session and ensure it persists
        request.session['current_booking_id'] = booking.id
        request.session.modified = True  # Force session save
        
        print(f"✅ Session updated - current_booking_id: {request.session.get('current_booking_id')}")

        # Show success message
        messages.success(request, "Booking confirmed successfully! Proceeding to payment...")
        
        # Render loading template for booking processing
        return render(request, 'booking/loading_booking.html')

    except Exception as e:
        print(f"❌ Unexpected error in confirm_booking: {str(e)}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('bookingapp:booking_summary')

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
    is_practice_booking = request.session.get('is_practice_booking', False)
    
    print(f"=== PAYMENT_SUCCESS DEBUG ===")
    print(f"Booking ID from session: {booking_id}")
    print(f"Activity ID from session: {activity_id}")
    print(f"Is Practice Booking: {is_practice_booking}")

    # Check if this is a practice booking
    if is_practice_booking:
        print("🎯 This is a practice booking - saving practice record")
        return save_practice_booking(request)
    
    if not booking_id:
        print("❌ No booking_id in session")
        messages.error(request, "No booking found. Please start over.")
        return redirect('studentapp:student_home')
    
    # Handle regular booking without activity (practice or regular booking)
    if not activity_id:
        print("🎯 Regular booking without activity - showing success page")
        try:
            booking = Booking.objects.get(id=booking_id)
            student = Student.objects.get(id=request.session.get('student_id'))
            
            print(f"✅ Found booking: {booking.id} for student: {student.first_name}")
            
            # Save as practice booking if it was marked as practice
            if request.session.get('is_practice_booking'):
                print("💾 Saving as practice booking")
                practice_booking = PracticeBooking.objects.create(
                    student=student,
                    booking=booking,
                    practice_type='free_practice',
                    scenario_description='Free practice booking',
                    is_completed=True
                )
                print(f"✅ Practice booking saved: {practice_booking.id}")
            
            # Clear session data but keep student login
            keys_to_clear = [
                "passengers", "selected_seats", "confirm_depart_schedule",
                "confirm_return_schedule", "current_booking_id", "trip_type",
                "origin", "destination", "departure_date", "return_date",
                "passenger_count", "contact_info", "adults", "children", "infants",
                "selected_addons", "is_practice_booking", "is_guided_practice", 
                "practice_requirements"
            ]
            
            student_id = request.session.get('student_id')
            for key in keys_to_clear:
                request.session.pop(key, None)
            
            request.session['student_id'] = student_id
            request.session.modified = True
            
            print("🧹 Cleared booking session data")
            
            # Render success page for regular/practice booking
            messages.success(request, "Booking completed successfully!")
            return render(request, "booking/payment_success.html", {
                'booking': booking,
                'student': student,
                'is_practice_booking': True,
                'practice_booking': practice_booking if request.session.get('is_practice_booking') else None
            })
            
        except Booking.DoesNotExist:
            print(f"❌ Booking {booking_id} not found")
            messages.error(request, "Booking not found.")
            return redirect('studentapp:student_home')
        except Student.DoesNotExist:
            print(f"❌ Student not found")
            messages.error(request, "Student not found.")
            return redirect('bookingapp:login')
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            messages.error(request, "Error processing booking.")
            return redirect('studentapp:student_home')
    
    # Handle activity submission (existing code)
    try:
        booking = Booking.objects.get(id=booking_id)
        activity = Activity.objects.get(id=activity_id)
        student = Student.objects.get(id=request.session.get('student_id'))
        
        print(f"✅ Found objects - Booking: {booking.id}, Activity: {activity.title}, Student: {student.first_name}")
        
        # ... rest of your existing activity submission code ...
        # Get origin and destination airports from the booking
        origin_airport = None
        destination_airport = None
        
        # Get the first booking detail to extract route information
        first_booking_detail = booking.details.first()
        if first_booking_detail:
            route = first_booking_detail.schedule.flight.route
            origin_airport = route.origin_airport
            destination_airport = route.destination_airport
            print(f"🌍 Airport info - Origin: {origin_airport.code}, Destination: {destination_airport.code}")
        
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
            
            try:
                # Calculate score before creating submission
                score = calculate_activity_score(booking, activity)
                print(f"📊 Calculated score: {score}/{activity.total_points}")
                
                # Create activity submission WITH airport data
                submission_data = {
                    'activity': activity,
                    'student': student,
                    'booking': booking,
                    'status': 'submitted',
                    'required_trip_type': activity.required_trip_type,
                    'required_travel_class': activity.required_travel_class,
                    'required_passengers': activity.required_passengers,
                    'required_children': activity.required_children,
                    'required_infants': activity.required_infants,
                    'require_passenger_details': activity.require_passenger_details,
                    'score': score,
                    'submitted_at': timezone.now()
                }
                
                # ADD AIRPORT DATA if available - FIXED: Use Airport objects, not strings
                if hasattr(activity, 'required_origin') and activity.required_origin:
                    try:
                        origin_airport = Airport.objects.get(code=activity.required_origin)
                        submission_data['required_origin_airport'] = origin_airport
                        print(f"✅ Set origin airport: {origin_airport.code}")
                    except Airport.DoesNotExist:
                        print(f"❌ Origin airport not found: {activity.required_origin}")
                
                if hasattr(activity, 'required_destination') and activity.required_destination:
                    try:
                        destination_airport = Airport.objects.get(code=activity.required_destination)
                        submission_data['required_destination_airport'] = destination_airport
                        print(f"✅ Set destination airport: {destination_airport.code}")
                    except Airport.DoesNotExist:
                        print(f"❌ Destination airport not found: {activity.required_destination}")
                
                # Create the submission
                submission = ActivitySubmission.objects.create(**submission_data)
                
                # Calculate add-on scores
                addon_score, max_addon_points = submission.calculate_addon_score()
                submission.addon_score = addon_score
                submission.max_addon_points = max_addon_points
                submission.save()
                
                print(f"✅ SUCCESS: Created submission: {submission.id}")
                print(f"   Submission details - Activity: {submission.activity.title}, Student: {submission.student.first_name}, Booking: {submission.booking.id}, Score: {submission.score}")
                print(f"   Add-on Score: {submission.addon_score}/{submission.max_addon_points}")
                print(f"   Origin Airport: {submission.required_origin_airport.code if submission.required_origin_airport else 'None'}")
                print(f"   Destination Airport: {submission.required_destination_airport.code if submission.required_destination_airport else 'None'}")
                
                messages.success(request, f"Activity '{activity.title}' submitted successfully! Score: {score}/{activity.total_points}")
                
            except Exception as create_error:
                print(f"❌ ERROR creating submission: {create_error}")
                import traceback
                traceback.print_exc()
                
                # Create minimal submission without score if creation fails
                minimal_submission_data = {
                    'activity': activity,
                    'student': student,
                    'booking': booking,
                    'status': 'submitted',
                    'required_trip_type': activity.required_trip_type,
                    'required_travel_class': activity.required_travel_class,
                    'required_passengers': activity.required_passengers,
                    'required_children': activity.required_children,
                    'required_infants': activity.required_infants,
                    'require_passenger_details': activity.require_passenger_details,
                    'score': Decimal('0.0'),
                    'submitted_at': timezone.now()
                }
                
                # Add airport data to minimal submission too
                if hasattr(activity, 'required_origin') and activity.required_origin:
                    try:
                        origin_airport = Airport.objects.get(code=activity.required_origin)
                        minimal_submission_data['required_origin_airport'] = origin_airport
                    except Airport.DoesNotExist:
                        pass
                
                if hasattr(activity, 'required_destination') and activity.required_destination:
                    try:
                        destination_airport = Airport.objects.get(code=activity.required_destination)
                        minimal_submission_data['required_destination_airport'] = destination_airport
                    except Airport.DoesNotExist:
                        pass
                
                submission = ActivitySubmission.objects.create(**minimal_submission_data)
                messages.warning(request, f"Activity submitted but scoring failed. Please contact instructor.")
        
        # NOW clear the session data after successful submission creation
        request.session.pop('activity_id', None)
        request.session.pop('activity_requirements', None)
        request.session.pop('current_booking_id', None)
        request.session.modified = True
        print("🧹 Cleared activity and booking data from session")
        
        # Render success page for activity submission
        return render(request, "booking/payment_success.html", {
            'booking': booking,
            'student': student,
            'activity': activity,
            'submission': submission if 'submission' in locals() else existing_submission,
            'is_activity_submission': True
        })
        
    except Booking.DoesNotExist:
        print(f"❌ Booking {booking_id} not found")
        messages.error(request, "Booking not found.")
        return redirect('studentapp:student_home')
    except Activity.DoesNotExist:
        print(f"❌ Activity {activity_id} not found")  
        messages.error(request, "Activity not found.")
        return redirect('studentapp:student_home')
    except Student.DoesNotExist:
        print(f"❌ Student not found")
        messages.error(request, "Student not found.")
        return redirect('bookingapp:login')
    except Exception as e:
        print(f"❌ Unexpected error in payment_success: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, "Error processing submission. Please contact support.")
        return redirect('studentapp:student_home')


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