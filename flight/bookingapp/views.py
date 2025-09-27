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


""" get all inputs from home  """
@login_required
def search_flight(request):
    if request.method == 'POST':
        trip_type = request.POST.get('trip_type')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_date = request.POST.get('departure_date')
        return_date = request.POST.get('return_date')
        passenger_count = request.POST.get('passenger')

        if not trip_type and not origin and not destination and not departure_date and not return_date and not passenger_count:
            return redirect('bookingapp:main')

        if trip_type:
            request.session['trip_type'] = trip_type
            print(f" trip type:  {trip_type}")
        if origin:    
            request.session['origin'] =  int(origin)
            print(f" origin {origin}")
        if destination:
            request.session['destination'] = int(destination)
            print(f" destination {destination}")
        if departure_date:    
            request.session['departure_date'] = departure_date
            print( f" departure_date {departure_date}")
        if return_date:    
            request.session['return_date'] = return_date
           
            print( f" return_date {return_date}")
        if passenger_count:    
            request.session['passenger_count'] = int(passenger_count)
            print(f" passenger_count {passenger_count}")

        request.session['seat'] = None
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
        "pasenger_count": passenger_count,
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
            # clear_search = [
            #     'trip_type', 'origin', 'destination',
            #     'departure_date', 'return_date',
            
            #     'depart_schedule_id', 'return_schedule_id'
            # ]
            # for key in clear_search:
            #     print(f"pop {key}")
            #     request.session.pop(key, None)
            # print(request.session['confirm_depart_schedule'])    
            # print(request.session['confirm_return_schedule'])    
            # print(request.session['seat'])    
            # print(request.session['passenger_count'])    
            return redirect('bookingapp:passenger_information')
        else:
            return redirect('bookingapp:flight_schedules')




""" Enter a passenger information """
@login_required
def passenger_information(request):
    """ get session passenger_count """
    passenger_count = request.session.get('passenger_count')
    if not passenger_count:
            return redirect('bookingapp:home')  # change 'home' if your URL name is different

    print("Passenger count in session:", passenger_count)

    student = None
    if request.session.get("student_id"):
        student = Student.objects.get(id=request.session["student_id"])

    template = loader.get_template('booking/passenger.html')
    context = {
        'passenger_range': range(1, passenger_count + 1),
        'student': student,
    }
    return HttpResponse(template.render(context, request))



@login_required
def save_passengers(request):
    passenger_count = request.session.get('passenger_count', 1)
    if request.method == 'POST':
        passengers = []

        """ store all the passenger """
        for i in range(1, passenger_count+1):
            passenger_data = {
                "gender": request.POST.get(f"gender_{i}"),
                "first_name": request.POST.get(f"first_name_{i}"),
                "last_name": request.POST.get(f"last_name_{i}"),
                "mi": request.POST.get(f"mi_{i}"),
                "dob_day": request.POST.get(f"dob_day_{i}"),
                "dob_month": request.POST.get(f"dob_month_{i}"),
                "dob_year": request.POST.get(f"dob_year_{i}"),
                "passport": request.POST.get(f"passport_{i}"),
                "nationality": request.POST.get(f"nationality_{i}"),
            }
            
            passengers.append(passenger_data)

        
        """ store contact booker """
        contact_info = {
            "first_name": request.POST.get("f_name_contact"),
            "last_name": request.POST.get("l_name_contact"),
            "mi": request.POST.get("m_name_contact"),
            "number": request.POST.get("number_contact"),
            "email": request.POST.get("email_contact"),
        }

        request.session['passengers'] = passengers
        request.session['contact_info'] = contact_info

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

@csrf_exempt
@login_required
def confirm_seat(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."})

    seat_number = request.POST.get("seat_number")
    passenger_id = request.POST.get("passenger_id")
    trip = request.POST.get("trip")  # 'depart' or 'return'

    if not all([seat_number, passenger_id, trip]):
        return JsonResponse({"success": False, "message": "Missing required data."})

    # Store in session only; no database locking yet
    selected_seats = request.session.get('selected_seats', {})
    if passenger_id not in selected_seats:
        selected_seats[passenger_id] = {}
    selected_seats[passenger_id][trip] = seat_number
    request.session['selected_seats'] = selected_seats
    request.session.modified = True

    return JsonResponse({
        "success": True,
        "seat": seat_number,
        "passenger_id": passenger_id,
        "trip": trip
    })



from decimal import Decimal
@login_required
def booking_summary(request):
    # Get selected schedules
    depart_schedule_id = request.session.get('confirm_depart_schedule')
    return_schedule_id = request.session.get('confirm_return_schedule')

    if not depart_schedule_id and not return_schedule_id:
        return redirect("bookingapp:main")

    depart_schedule = Schedule.objects.filter(id=depart_schedule_id).first() if depart_schedule_id else None
    return_schedule = Schedule.objects.filter(id=return_schedule_id).first() if return_schedule_id else None

    # Get passengers and selected seats
    passengers = request.session.get('passengers', [])
    seats = request.session.get('selected_seats', {})  # { "0": {"depart": "A1", "return": "B1"} }

    # Combine passenger info with seat assignment
    passenger_data = []
    for idx, passenger in enumerate(passengers):
        seat_info = seats.get(str(idx), {})
        passenger_data.append({
            "full_name": f"{passenger['first_name']} {passenger.get('mi', '')} {passenger['last_name']}",
            "depart_seat": seat_info.get("depart", "Not selected"),
            "return_seat": seat_info.get("return", "Not selected"),
            "gender": passenger['gender'],
            "dob": f"{passenger['dob_month']}/{passenger['dob_day']}/{passenger['dob_year']}",
            "passport": passenger.get('passport', ''),
            "nationality": passenger.get('nationality', '')
        })

    # Get contact info
    contact_info = request.session.get('contact_info', {})

    num_passengers = len(passengers)

    # Handle one-way or round-trip
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
@login_required
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
                outbound_schedule=depart_schedule,
                return_schedule=return_schedule,
                status="Pending"
            )

            # 2️⃣ Create PassengerInfo and BookingDetail
            for idx, p in enumerate(passengers):
                seat_info = seats.get(str(idx), {})
                depart_seat_number = seat_info.get("depart")
                return_seat_number = seat_info.get("return")

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

                # Assign seats in BookingDetail, but **do not mark unavailable yet**
                depart_seat_obj = Seat.objects.get(schedule=depart_schedule, seat_number=depart_seat_number)
                BookingDetail.objects.create(
                    booking=booking,
                    flight=depart_schedule.flight,
                    seat=depart_seat_obj,
                    seat_class=depart_seat_obj.seat_class
                )

                if return_schedule and return_seat_number:
                    return_seat_obj = Seat.objects.get(schedule=return_schedule, seat_number=return_seat_number)
                    BookingDetail.objects.create(
                        booking=booking,
                        flight=return_schedule.flight,
                        seat=return_seat_obj,
                        seat_class=return_seat_obj.seat_class
                    )

            request.session['current_booking_id'] = booking.id

    except Exception as e:
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

    booking = Booking.objects.get(id=booking_id)
    total_amount = booking.outbound_schedule.price
    if booking.return_schedule:
        total_amount += booking.return_schedule.price
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

                    booking.status = "Paid"
                    booking.save()

                    # Lock and mark seats
                    for detail in booking.details.select_for_update():
                        seat = detail.seat
                        if seat and seat.is_available:
                            seat.is_available = False
                            seat.save()
                        elif seat and not seat.is_available:
                            raise ValueError(f"Seat {seat.seat_number} is already taken.")

                    # Clear session except login
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

                    return redirect("bookingapp:payment_success")

            except ValueError as e:
                # ⚠ Seat is already taken → redirect to select seat page
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

@redirect_if_logged_in
def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('bookingapp:login')
