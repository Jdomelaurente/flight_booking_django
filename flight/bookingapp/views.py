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



# Create your views here.
@login_required
def home(request):
    from_airports = Airport.objects.all()
    to_airports = Airport.objects.all()

    templates= loader.get_template('booking/home.html')
    context = {
        "origins" :from_airports,
        "destinations" : to_airports,
    }
    return HttpResponse(templates.render(context, request))


@login_required
def search_flight(request):
    if request.method == 'POST':
        trip_type = request.POST.get('trip_type')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_date = request.POST.get('departure_date')
        return_date = request.POST.get('return_date')
        adults = int(request.POST.get('adults', 1))
        children = int(request.POST.get('children', 0))
        infants = int(request.POST.get('infants', 0))
        
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

        # Print all session data to console
        # print("=== Current Session Data ===")
        # for key, value in request.session.items():
        #     print(f"{key}: {value}")
        # print("============================")

        return redirect("bookingapp:flight_schedules")

@never_cache
@login_required
def flight_schedules(request):
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
    adults = request.session.get('adults', 1)
    children = request.session.get('children', 0)
    infants = request.session.get('infants', 0)

    total_passengers = adults + children + infants
    if total_passengers == 0:
        return redirect('bookingapp:home')

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

        # For infants, link to the selected adult - FIX THE MAPPING
        if passenger_data["passenger_type"].lower() == "infant":
            adult_selection = request.POST.get(f"infant_adult_{i+1}")
            # Convert the adult selection (1-based) to passenger ID (0-based)
            # Adult selection "1" should map to passenger ID "0"
            # Adult selection "2" should map to passenger ID "1"  
            if adult_selection:
                adult_id = str(int(adult_selection) - 1)  # Convert 1-based to 0-based
                passenger_data["adult_id"] = adult_id
                print(f"Infant {i+1} linked to adult selection: {adult_selection} -> passenger ID: {adult_id}")
            else:
                passenger_data["adult_id"] = "0"  # Default to first adult
                print(f"Infant {i+1} defaulted to adult ID: 0")

        passengers.append(passenger_data)
        print(f"Passenger {i}: {passenger_data['first_name']} ({passenger_data['passenger_type']}) - ID: {passenger_data['id']}")

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
            "nationality": passenger.get('nationality', '')
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
def confirm_booking(request):
    passengers = request.session.get('passengers', [])
    seats = request.session.get('selected_seats', {})
    depart_schedule_id = request.session.get('confirm_depart_schedule')
    return_schedule_id = request.session.get('confirm_return_schedule')
    student_id = request.session.get('student_id')

    if not (depart_schedule_id and student_id):
        messages.error(request, "Booking data is missing.")
        return redirect('bookingapp:select_seat')

    depart_schedule = Schedule.objects.get(id=depart_schedule_id)
    return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None
    student = Student.objects.get(id=student_id)

    try:
       with transaction.atomic():
            # 1️⃣ Create Booking
            booking = Booking.objects.create(
                student=student,
                trip_type=request.session.get('trip_type', 'one_way'),
                status="Pending"
            )

            # DEBUG: Print what we're working with
            print("=== CONFIRM_BOOKING DEBUG ===")
            print("Passengers:", [(p['first_name'], p['id']) for p in passengers])
            print("Seats:", seats)
            print("=============================")

            # 2️⃣ Create PassengerInfo and BookingDetail
            for p in passengers:  # ✅ CHANGE: Don't use enumerate
                pid = str(p.get("id"))  # ✅ CHANGE: Get passenger ID
                seat_info = seats.get(pid, {})  # ✅ CHANGE: Use passenger ID to get seats
                depart_seat_number = seat_info.get("depart")
                return_seat_number = seat_info.get("return")

                print(f"Processing {p['first_name']} (ID: {pid}): {seat_info}")

                dob = date(int(p['dob_year']), int(p['dob_month']), int(p['dob_day']))
                passenger_obj = PassengerInfo.objects.create(
                    first_name=p['first_name'],
                    middle_name=p.get('mi', ''),
                    last_name=p['last_name'],
                    gender=p['gender'],
                    date_of_birth=dob,
                    passport_number=p.get('passport', ''),
                    email=student.email,
                    phone=student.phone
                )

                if depart_seat_number:
                    try:
                        outbound_seat_obj = Seat.objects.get(schedule=depart_schedule, seat_number=depart_seat_number)
                        BookingDetail.objects.create(
                            booking=booking,
                            passenger=passenger_obj,
                            schedule=depart_schedule,
                            seat=outbound_seat_obj,
                            seat_class=outbound_seat_obj.seat_class
                        )
                        print(f"✅ Created depart booking for {p['first_name']} - Seat: {depart_seat_number}")
                    except Seat.DoesNotExist:
                        print(f"❌ Seat {depart_seat_number} not found for depart schedule")
                        raise ValueError(f"Seat {depart_seat_number} not found for depart flight")

                if return_schedule and return_seat_number:
                    try:
                        return_seat_obj = Seat.objects.get(schedule=return_schedule, seat_number=return_seat_number)
                        BookingDetail.objects.create(
                            booking=booking,
                            passenger=passenger_obj,
                            schedule=return_schedule,
                            seat=return_seat_obj,
                            seat_class=return_seat_obj.seat_class
                        )
                        print(f"✅ Created return booking for {p['first_name']} - Seat: {return_seat_number}")
                    except Seat.DoesNotExist:
                        print(f"❌ Seat {return_seat_number} not found for return schedule")
                        raise ValueError(f"Seat {return_seat_number} not found for return flight")

            print("✅ Booking created successfully!")
            request.session['current_booking_id'] = booking.id

    except Exception as e:
        print(f"❌ Error in confirm_booking: {str(e)}")
        messages.error(request, f"Error creating booking: {str(e)}")
        return redirect('bookingapp:select_seat')

    return redirect('bookingapp:payment_method')


from decimal import Decimal
from django.contrib import messages



@login_required
def payment_method(request):
    booking_id = request.session.get('current_booking_id')
    if not booking_id:
        messages.error(request, "No booking found. Please start again.")
        return redirect("bookingapp:home")

    booking = get_object_or_404(Booking, id=booking_id)


    # ✅ Calculate total amount from BookingDetails
    total_amount = sum(detail.price for detail in booking.details.all())
    total_amount += Decimal(20) + Decimal(500)  # taxes + insurance

    if request.method == "POST":
        method = request.POST.get("payment_method")
        if method:
            try:
                with transaction.atomic():
                    # Create Payment
                    Payment.objects.create(
                        booking=booking,
                        amount=total_amount,
                        method=method,
                        status="Completed",  # mock payment
                        transaction_id=f"MOCK{booking.id:05d}"
                    )

                    # Mark booking as Paid
                    booking.status = "Paid"
                    booking.save()

                    # Lock and mark seats as unavailable
                    for detail in booking.details.select_for_update():
                        seat = detail.seat
                        if seat:
                            if seat.is_available:
                                seat.is_available = False
                                seat.save()
                            else:
                                raise ValueError(f"Seat {seat.seat_number} is already taken.")

                    # Clear session except login/student_id
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
                    request.session.modified = True

                    return redirect("bookingapp:payment_success")

            except ValueError as e:
                messages.error(request, str(e))
                return redirect("bookingapp:select_seat")

    return render(request, "booking/payment.html", {
        "booking": booking,
        "payment_methods": Payment.PAYMENT_METHODS,
        "total_amount": total_amount
    })




@login_required
def payment_success(request):
    # Keep student login only
    student_id = request.session.get('student_id')
    request.session.flush()
    request.session['student_id'] = student_id

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

        # Create student
        student = Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password=make_password(password),
            student_number=f"STU{Student.objects.count() + 1:04d}"
        )

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

        try:
            student = Student.objects.get(email=email)
            if check_password(password, student.password):
                request.session['student_id'] = student.id
                messages.success(request, f"Welcome {student.first_name}!")
                return redirect('bookingapp:main')
            else:
                messages.error(request, "Incorrect password.")
        except Student.DoesNotExist:
            messages.error(request, "Email not registered.")


    template = loader.get_template("booking/auth/login.html")
    context = {
    }

    return HttpResponse(template.render(context, request))


def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('bookingapp:login')
