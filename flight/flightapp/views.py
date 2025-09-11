from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404, redirect
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render

import hashlib
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from collections import defaultdict
from django.utils.timezone import localtime
from django.shortcuts import render
from .models import Schedule
from datetime import datetime
from django.utils import timezone
from datetime import datetime


from .models import Flight
from .models import Route
from .models import Schedule
from .models import Seat
from .models import Airport
from .models import Airline
from .models import Aircraft
from .models import SeatClass
from .models import Booking
from .models import BookingDetail
from .models import Payment
from .models import CheckInDetail
from .models import Student
from .models import PassengerInfo
from .models import  TrackLog

# ------------------------------------ Users ----------------------------------------------------------

# main
def main(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render())

def admin_dashboard(request):
    return render(request, "dashboard.html")

def instructor_dashboard(request):
    return render(request, "instructor_dashboard.html")


# profile
def profile_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")  # redirect if not logged in

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username:
            user.username = username

        if password:
            user.set_password(password)  # hash the new password

        user.save()
        return redirect("profile")  # reload the profile page

    return render(request, "profile.html", {"user": user})

# Hash
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# REGISTER
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        role = request.POST.get("role")

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        User.objects.create(
            username=username,
            email=email,
            password=hash_password(password),
            role=role
        )
        messages.success(request, "Account created. Please login.")
        return redirect("login")

    return render(request, "register.html")

# LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = hash_password(request.POST.get("password"))

        try:
            user = User.objects.get(username=username, password=password)
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            request.session["role"] = user.role  # store role in session

            # redirect based on role
            if user.role == "admin":
                return redirect("admin_dashboard")
            elif user.role == "instructor":
                return redirect("instructor_dashboard")
            elif user.role == "student":
                return redirect("student_dashboard")
            else:
                return redirect("login")  # fallback
        except User.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html")




# LOGOUT
def logout_view(request):
    request.session.flush()
    return redirect("login")

# ------------------------------------Dashboard ----------------------------------------------------------

def dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = User.objects.get(id=user_id)
    if user.role == "admin":
        return redirect("admin_dashboard")
    elif user.role == "instructor":
        return redirect("instructor_dashboard")
    return redirect("login")


# dashboard
from django.utils import timezone
from datetime import datetime

def admin_dashboard(request):
    date_filter = request.GET.get("date")
    schedules = Schedule.objects.all()
    current_time = timezone.now()

    if date_filter:
        try:
            selected_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            schedules = schedules.filter(departure_time__date=selected_date)
        except ValueError:
            selected_date = None
    else:
        selected_date = None

    schedule_data = []

    # Initialize counters
    total_open = 0
    total_closed = 0
    total_on_flight = 0
    total_arrived = 0

    for s in schedules:
        # Future flights → use DB status (Open/Closed)
        if current_time < s.departure_time:
            status = s.status  # Open / Closed
            if status == "Open":
                total_open += 1
            else:
                total_closed += 1
        # Ongoing flight
        elif s.departure_time <= current_time < s.arrival_time:
            status = "On Flight"
            total_on_flight += 1
        # Completed flight
        else:
            status = "Arrived"
            total_arrived += 1

        schedule_data.append({'schedule': s, 'status': status})

    # 🔹 Fetch bookings (latest first)
    bookings = Booking.objects.select_related("student", "schedule", "seat").order_by("-created_at")

    return render(request, "dashboard.html", {
        "schedule_data": schedule_data,
        "selected_date": selected_date,
        "username": request.user.username,
        "total_open": total_open,
        "total_closed": total_closed,
        "total_on_flight": total_on_flight,
        "total_arrived": total_arrived,
          # ✅ pass to template
    })


# ------------------------------------ ASSETS ----------------------------------------------------------

# ---------------------------
# Seat Class
# ---------------------------

# List
def seat_class_view(request):
    seat_classes = SeatClass.objects.all()
    return render(request, "asset/seat_class/seat_class.html", {"seat_classes": seat_classes})
    

# Add
def add_seat_class(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price_multiplier = request.POST.get("price_multiplier")
        description = request.POST.get("description")  # optional

        SeatClass.objects.create(
            name=name,
            price_multiplier=price_multiplier
        )
        return redirect("seat_class")
    return render(request, "asset/seat_class/add_seat_class.html")

# Update
def update_seat_class(request, seat_class_id):
    seat_class = get_object_or_404(SeatClass, pk=seat_class_id)
    if request.method == "POST":
        seat_class.name = request.POST.get("name")
        seat_class.price_multiplier = request.POST.get("price_multiplier")
        seat_class.save()
        return redirect("seat_class")
    return render(request, "asset/seat_class/update_seat_class.html", {"seat_class": seat_class})


# Delete
def delete_seat_class(request, seat_class_id):
    seat_class = get_object_or_404(SeatClass, pk=seat_class_id)
    seat_class.delete()
    return redirect("seat_class")


# ---------------------------
# Aircraft
# ---------------------------

# List
def aircraft_view(request):
    aircrafts = Aircraft.objects.all()
    return render(request, 'asset/aircraft/aircraft.html', {"aircrafts": aircrafts})

# Add
def add_aircraft(request):
    if request.method == "POST":
        model = request.POST.get("model")
        capacity = request.POST.get("capacity")
        airline_id = request.POST.get("airline")  # comes from dropdown
        airline = Airline.objects.get(id=airline_id)

        Aircraft.objects.create(
            model=model,
            capacity=capacity,
            airline=airline
        )
        return redirect("aircraft")

    airlines = Airline.objects.all()  # for dropdown
    return render(request, "asset/aircraft/add_aircraft.html", {"airlines": airlines})

# Update
def update_aircraft(request, aircraft_id):
    aircraft = get_object_or_404(Aircraft, id=aircraft_id)
    airlines = Airline.objects.all()

    if request.method == "POST":
        aircraft.model = request.POST["model"]
        aircraft.capacity = request.POST["capacity"]
        aircraft.type = request.POST["type"]
        airline_id = request.POST["airline"]
        aircraft.airline = get_object_or_404(Airline, id=airline_id)

        aircraft.save()
        return redirect("aircraft")

    return render(
        request,
        "asset/aircraft/update_aircraft.html",
        {"aircraft": aircraft, "airlines": airlines}
    )

# Delete
def delete_aircraft(request, aircraft_id):
    aircraft = get_object_or_404(Aircraft, id=aircraft_id)
    aircraft.delete()
    return redirect("aircraft")


# ---------------------------
# Airlines
# ---------------------------

# List
def airline_view(request):
    airlines = Airline.objects.all()
    return render(request, "asset/airline/airline.html", {"airlines": airlines})

# Add
def add_airline(request):
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        Airline.objects.create(name=name, code=code)
        return redirect("airline")
    return render(request, "asset/airline/add_airline.html")

# Update
def update_airline(request, airline_id):
    airline = get_object_or_404(Airline, id=airline_id)
    if request.method == "POST":
        airline.name = request.POST.get("name")
        airline.code = request.POST.get("code")
        airline.save()
        return redirect("airline")
    return render(request, "asset/airline/update_airline.html", {"airline": airline})

# Delete
def delete_airline(request, airline_id):
    airline = get_object_or_404(Airline, id=airline_id)
    airline.delete()
    return redirect("airline")

# ---------------------------
# Airport
# ---------------------------

# List
def airport_view(request):
    airports = Airport.objects.all()
    return render(request, "asset/airport/airport.html", {"airports": airports})


from django.db import IntegrityError
# Add
def add_airport(request):
    error_message = None

    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        location = request.POST.get("location")

        # Check for duplicate airport code
        if Airport.objects.filter(code=code).exists():
            error_message = f"Airport with code {code} already exists."
        else:
            try:
                Airport.objects.create(
                    name=name,
                    code=code,
                    location=location,
                )
                return redirect("airport")
            except IntegrityError:
                error_message = "Something went wrong while saving."

    return render(request, "asset/airport/add_airport.html", {"error_message": error_message})


# Update
def update_airport(request, airport_id):
    airport = get_object_or_404(Airport, pk=airport_id)

    if request.method == "POST":
        airport.name = request.POST.get("name")
        airport.code = request.POST.get("code")
        airport.location = request.POST.get("location")
        airport.save()
        return redirect("airport")

    return render(request, "asset/airport/update_airport.html", {"airport": airport})

# Delete
def delete_airport(request, airport_id):
    airport = get_object_or_404(Airport, pk=airport_id)
    airport.delete()
    return redirect("airport")

# ------------------------------------------ Manage Flight ----------------------------------------

# ---------------------------
# Flight
# ---------------------------

# List
def flight_view(request):
    flights = Flight.objects.all()
    return render(request, "manage_flight/flight/flight.html", {"flights": flights})


# Add 
def add_flight(request):
    if request.method == "POST":
        flight_number = request.POST.get("flight_number")
        airline_id = request.POST.get("airline")
        aircraft_id = request.POST.get("aircraft")
        route_id = request.POST.get("route")  # ✅ Only route, no origin/destination

        airline = Airline.objects.get(id=airline_id)
        aircraft = Aircraft.objects.get(id=aircraft_id)
        route = Route.objects.get(id=route_id)

        Flight.objects.create(
            flight_number=flight_number,
            airline=airline,
            aircraft=aircraft,
            route=route,   # ✅ this links to both origin + destination
        )
        return redirect("flight")

    airlines = Airline.objects.all()
    routes = Route.objects.all()
    return render(request, "manage_flight/flight/add_flight.html", {"airlines": airlines, "routes": routes})


# AJAX endpoint to load aircraft based on airline
def load_aircrafts(request):
    airline_id = request.GET.get("airline")
    aircrafts = Aircraft.objects.filter(airline_id=airline_id).values("id", "model")
    return JsonResponse(list(aircrafts), safe=False)

# Update
def update_flight(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    airlines = Airline.objects.all()
    aircrafts = Aircraft.objects.all()
    routes = Route.objects.all()

    if request.method == "POST":
        flight.flight_number = request.POST.get("flight_number")
        flight.airline = get_object_or_404(Airline, pk=request.POST.get("airline"))
        flight.aircraft = get_object_or_404(Aircraft, pk=request.POST.get("aircraft"))
        flight.route = get_object_or_404(Route, pk=request.POST.get("route"))
        flight.save()
        return redirect("flight")

    return render(request, "manage_flight/flight/update_flight.html", {
        "flight": flight,
        "airlines": airlines,
        "aircrafts": aircrafts,
        "routes": routes
    })

# Delete flight
def delete_flight(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    flight.delete()
    return redirect("flight")


# ---------------------------
# Route
# ---------------------------

# List
def route_view(request):
    routes = Route.objects.all()
    return render(request, "manage_flight/route/route.html", {"routes": routes})

# Add 
def add_route(request):
    airports = Airport.objects.all()
    if request.method == "POST":
        origin_id = request.POST.get("origin_airport")
        destination_id = request.POST.get("destination_airport")
        origin = get_object_or_404(Airport, pk=origin_id)
        destination = get_object_or_404(Airport, pk=destination_id)
        Route.objects.create(origin_airport=origin, destination_airport=destination)
        return redirect("route")
    return render(request, "manage_flight/route/add_route.html", {"airports": airports})

# Update 
def update_route(request, route_id):
    route = get_object_or_404(Route, pk=route_id)
    airports = Airport.objects.all()
    if request.method == "POST":
        route.origin_airport = get_object_or_404(Airport, pk=request.POST.get("origin_airport"))
        route.destination_airport = get_object_or_404(Airport, pk=request.POST.get("destination_airport"))
        route.save()
        return redirect("route")
    return render(request, "manage_flight/route/update_route.html", {"route": route, "airports": airports})

# Delete 
def delete_route(request, route_id):
    route = get_object_or_404(Route, pk=route_id)
    route.delete()
    return redirect("route")


from django.utils import timezone

# ---------------------------
# Schedule
# ---------------------------


def schedule_view(request):
    schedules = Schedule.objects.all()

    schedule_data = []
    total_open = total_closed = total_on_flight = total_arrived = 0

    for s in schedules:
        s.update_status()  # 🔹 model decides correct status

        if s.status == "Open":
            total_open += 1
        elif s.status == "Closed":
            total_closed += 1
        elif s.status == "On Flight":
            total_on_flight += 1
        elif s.status == "Arrived":
            total_arrived += 1

        schedule_data.append({
            "schedule": s,
            "status": s.status
        })

    context = {
        "schedule_data": schedule_data,
        "total_open": total_open,
        "total_closed": total_closed,
        "total_on_flight": total_on_flight,
        "total_arrived": total_arrived,
    }
    return render(request, "manage_flight/schedule/schedule.html", context)



# Add schedule
def add_schedule(request):
    flights = Flight.objects.all()

    if request.method == "POST":
        flight_id = request.POST.get("flight")
        departure_time = request.POST.get("departure_time")
        arrival_time = request.POST.get("arrival_time")
        price = request.POST.get("price")  # if you want to include price

        flight = Flight.objects.get(id=flight_id)

        # Schedule save() will auto-generate seats
        Schedule.objects.create(
            flight=flight,
            departure_time=departure_time,
            arrival_time=arrival_time,
            price=price
        )

        return redirect("schedule")

    return render(
        request, 
        "manage_flight/schedule/add_schedule.html", 
        {"flights": flights}
    )



# Update schedule
def update_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    flights = Flight.objects.all()
    if request.method == "POST":
        schedule.flight = get_object_or_404(Flight, pk=request.POST.get("flight"))
        schedule.departure_time = request.POST.get("departure_time")
        schedule.arrival_time = request.POST.get("arrival_time")
        schedule.save()
        return redirect("schedule")
    return render(request, "manage_flight/schedule/update_schedule.html", {"schedule": schedule, "flights": flights})


# Delete schedule
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    schedule.delete()
    return redirect("schedule")


# -----------------------------
# Seat
# -----------------------------

# List


def seat_view(request):
    seats = Seat.objects.all()
    flights = Flight.objects.all()

    flight_id = request.GET.get("flight")
    if flight_id:
        seats = seats.filter(schedule__flight__id=flight_id)

    return render(request, "manage_flight/seat/seat.html", {"seats": seats, "flights": flights})


# Add
def add_seat(request):
    schedules = Schedule.objects.all()
    seat_classes = SeatClass.objects.all()
    
    if request.method == "POST":
        schedule_id = request.POST.get("schedule")
        seat_class_id = request.POST.get("seat_class")
        seat_number = request.POST.get("seat_number")
        is_available = "is_available" in request.POST

        schedule = get_object_or_404(Schedule, id=schedule_id)
        seat_class = get_object_or_404(SeatClass, id=seat_class_id)

        Seat.objects.create(
            schedule=schedule,
            seat_class=seat_class,
            seat_number=seat_number,
            is_available=is_available
        )
        return redirect("seat")
    
    return render(request, "manage_flight/seat/add_seat.html", {"schedules": schedules, "seat_classes": seat_classes})

# Update 
def update_seat(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    schedules = Schedule.objects.all()
    seat_classes = SeatClass.objects.all()
    
    if request.method == "POST":
        schedule_id = request.POST.get("schedule")
        seat_class_id = request.POST.get("seat_class")
        seat_number = request.POST.get("seat_number")
        is_available = "is_available" in request.POST

        seat.schedule = get_object_or_404(Schedule, id=schedule_id)
        seat.seat_class = get_object_or_404(SeatClass, id=seat_class_id)
        seat.seat_number = seat_number
        seat.is_available = is_available
        seat.save()
        return redirect("seat")
    
    return render(request, "manage_flight/seat/update_seat.html", {
        "seat": seat,
        "schedules": schedules,
        "seat_classes": seat_classes
    })

# Delete
def delete_seat(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    seat.delete()
    return redirect("seat")

# ---------------------------------------Booking Info-----------------------------------------------

# ---------------------------
# Booking
# ---------------------------

# List 
def booking_view(request):
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, "booking_info/booking/booking.html", {"bookings": bookings})

# Add
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Schedule, Seat, Booking

def add_booking(request):
    students = Student.objects.all()
    schedules = Schedule.objects.all()
    seats = Seat.objects.filter(is_available=True)

    if request.method == "POST":
        student_id = request.POST.get("student")
        trip_type = request.POST.get("trip_type")
        status = request.POST.get("status", "pending")

        if not student_id:
            messages.error(request, "Student is required.")
            return redirect("add_booking")

        student = get_object_or_404(Student, id=student_id)

        # ------------------------------
        # Handle booking types
        # ------------------------------
        if trip_type == "one_way":
            outbound_id = request.POST.get("outbound_schedule")
            if not outbound_id:
                messages.error(request, "Outbound schedule is required.")
                return redirect("add_booking")

            outbound_schedule = get_object_or_404(Schedule, id=outbound_id)
            outbound_seat_id = request.POST.get("outbound_seat") or None
            outbound_seat = Seat.objects.get(id=outbound_seat_id) if outbound_seat_id else None

            booking = Booking.objects.create(
                student=student,
                trip_type="one_way",
                outbound_schedule=outbound_schedule,
                outbound_seat=outbound_seat,
                status=status
            )

            # Mark seat unavailable
            if outbound_seat:
                outbound_seat.is_available = False
                outbound_seat.save()

        elif trip_type == "round_trip":
            outbound_id = request.POST.get("outbound_schedule")
            return_id = request.POST.get("return_schedule")

            if not outbound_id or not return_id:
                messages.error(request, "Both outbound and return schedules are required.")
                return redirect("add_booking")

            outbound_schedule = get_object_or_404(Schedule, id=outbound_id)
            return_schedule = get_object_or_404(Schedule, id=return_id)

            outbound_seat_id = request.POST.get("outbound_seat") or None
            return_seat_id = request.POST.get("return_seat") or None

            outbound_seat = Seat.objects.get(id=outbound_seat_id) if outbound_seat_id else None
            return_seat = Seat.objects.get(id=return_seat_id) if return_seat_id else None

            booking = Booking.objects.create(
                student=student,
                trip_type="round_trip",
                outbound_schedule=outbound_schedule,
                outbound_seat=outbound_seat,
                return_schedule=return_schedule,
                return_seat=return_seat,
                status=status
            )

            # Mark both seats unavailable
            if outbound_seat:
                outbound_seat.is_available = False
                outbound_seat.save()
            if return_seat:
                return_seat.is_available = False
                return_seat.save()

        elif trip_type == "multi_city":
            segment_num = 1
            while True:
                schedule_id = request.POST.get(f"multi_schedule_{segment_num}")
                if not schedule_id:
                    break

                schedule = get_object_or_404(Schedule, id=schedule_id)
                seat_id = request.POST.get(f"multi_seat_{segment_num}") or None
                seat = Seat.objects.get(id=seat_id) if seat_id else None

                booking = Booking.objects.create(
                    student=student,
                    trip_type="multi_city",
                    outbound_schedule=schedule,   # reuse outbound for segment
                    outbound_seat=seat,
                    status=status
                )

                # Mark seat unavailable
                if seat:
                    seat.is_available = False
                    seat.save()

                segment_num += 1

        messages.success(request, "Booking successfully created.")
        return redirect("booking")

    return render(request, "booking_info/booking/add_booking.html", {
        "students": students,
        "schedules": schedules,
        "seats": seats,
    })


# 🔹 API endpoint to fetch seats for a schedule
def get_seats_for_schedule(request, schedule_id):
    seats = Seat.objects.filter(schedule_id=schedule_id).select_related("seat_class")
    data = [
        {
            "id": seat.id,
            "label": f"{seat.seat_number} - {seat.seat_class.name} - {'Available' if seat.is_available else 'Booked'}",
            "is_available": seat.is_available
        }
        for seat in seats
    ]
    return JsonResponse(data, safe=False)

from django.http import JsonResponse
from .models import Schedule

def get_return_schedules(request, outbound_id):
    try:
        outbound = Schedule.objects.get(id=outbound_id)
        outbound_route = outbound.flight.route  # or outbound.flight.routes.first() if multiple
    except Schedule.DoesNotExist:
        return JsonResponse([], safe=False)

    # Find schedules with matching reverse route
    return_schedules = Schedule.objects.filter(
        flight__route__origin_airport=outbound_route.destination_airport,
        flight__route__destination_airport=outbound_route.origin_airport,
        status="Open"
    )

    data = [
        {
            "id": s.id,
            "flight_number": s.flight.flight_number,
            "origin": s.flight.route.origin_airport.code,
            "destination": s.flight.route.destination_airport.code,
            "departure_time": s.departure_time.strftime("%Y-%m-%d %H:%M")
        }
        for s in return_schedules
    ]
    return JsonResponse(data, safe=False)

# Update
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    students = Student.objects.all()
    schedules = Schedule.objects.all()
    seats = Seat.objects.filter(is_available=True) | Seat.objects.filter(id=booking.seat.id if booking.seat else None)

    if request.method == "POST":
        student_id = request.POST.get("student")
        schedule_id = request.POST.get("schedule")
        seat_id = request.POST.get("seat")
        status = request.POST.get("status")

        # Free previous seat if changed
        if booking.seat and (not seat_id or int(seat_id) != booking.seat.id):
            booking.seat.is_available = True
            booking.seat.save()

        booking.student = get_object_or_404(Student, id=student_id)
        booking.schedule = get_object_or_404(Schedule, id=schedule_id)
        booking.seat = get_object_or_404(Seat, id=seat_id) if seat_id else None
        booking.status = status
        booking.save()

        # Mark new seat as unavailable
        if booking.seat:
            booking.seat.is_available = False
            booking.seat.save()

        return redirect("booking")
    
    return render(request, "booking_info/booking/update_booking.html", {
        "booking": booking,
        "students": students,
        "schedules": schedules,
        "seats": seats,
    })

# Delete 
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.seat:
        booking.seat.is_available = True
        booking.seat.save()
    booking.delete()
    return redirect("booking")

# ---------------------------
# Payment
# ---------------------------

# List
def payment_view(request):
    payments = Payment.objects.all()
    return render(request, "booking_info/payment/payment.html", {"payments": payments})

# Add
def add_payment(request):
    bookings = Booking.objects.all()  # to select a booking for payment
    if request.method == "POST":
        booking_id = request.POST.get("booking")
        amount = request.POST.get("amount")
        method = request.POST.get("method")
        status = request.POST.get("status")
        transaction_id = request.POST.get("transaction_id", "")

        booking = get_object_or_404(Booking, id=booking_id)

        Payment.objects.create(
            booking=booking,
            amount=amount,
            method=method,
            status=status,
            transaction_id=transaction_id
        )
        messages.success(request, "Payment added successfully!")
        return redirect("payment")

    return render(request, "booking_info/payment/add_payment.html", {"bookings": bookings})

# Update
def update_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    bookings = Booking.objects.all()
    if request.method == "POST":
        booking_id = request.POST.get("booking")
        payment.amount = request.POST.get("amount")
        payment.method = request.POST.get("method")
        payment.status = request.POST.get("status")
        payment.transaction_id = request.POST.get("transaction_id", "")
        payment.booking = get_object_or_404(Booking, id=booking_id)
        payment.save()
        messages.success(request, "Payment updated successfully!")
        return redirect("payment")

    return render(request, "booking_info/payment/update_payment.html", {"payment": payment, "bookings": bookings})

# Delete 
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.delete()
    messages.success(request, "Payment deleted successfully!")
    return redirect("payment")

# ---------------------------
# Booking_detail
# ---------------------------

# List 
def booking_detail_view(request):
    details = BookingDetail.objects.all()
    return render(request, "booking_info/booking_detail/booking_detail.html", {"details": details})

# Add
def add_booking_detail(request):
    bookings = Booking.objects.all()
    flights = Flight.objects.all()
    seats = Seat.objects.filter(is_available=True)  # ✅ only show available seats
    seat_classes = SeatClass.objects.all()

    if request.method == "POST":
        booking_id = request.POST.get("booking")
        flight_id = request.POST.get("flight")
        seat_id = request.POST.get("seat")
        seat_class_id = request.POST.get("seat_class")

        booking = get_object_or_404(Booking, id=booking_id)
        flight = get_object_or_404(Flight, id=flight_id)
        seat = get_object_or_404(Seat, id=seat_id) if seat_id else None
        seat_class = get_object_or_404(SeatClass, id=seat_class_id) if seat_class_id else None

        # ✅ Create booking detail
        BookingDetail.objects.create(
            booking=booking,
            flight=flight,
            seat=seat,
            seat_class=seat_class
        )

        # ✅ Mark seat as unavailable
        if seat:
            seat.is_available = False
            seat.save()

        messages.success(request, "Booking detail added successfully!")
        return redirect("booking_detail")

    return render(request, "booking_info/booking_detail/add_booking_detail.html", {
        "bookings": bookings,
        "flights": flights,
        "seats": seats,
        "seat_classes": seat_classes
    })



# Update
def update_booking_detail(request, detail_id):
    detail = get_object_or_404(BookingDetail, id=detail_id)
    bookings = Booking.objects.all()
    flights = Flight.objects.all()
    seats = Seat.objects.filter(is_available=True) | Seat.objects.filter(id=detail.seat_id)
    seat_classes = SeatClass.objects.all()

    if request.method == "POST":
        detail.booking = get_object_or_404(Booking, id=request.POST.get("booking"))
        detail.flight = get_object_or_404(Flight, id=request.POST.get("flight"))

        # ✅ Seat logic
        old_seat = detail.seat
        new_seat_id = request.POST.get("seat")
        new_seat = get_object_or_404(Seat, id=new_seat_id) if new_seat_id else None

        if old_seat and old_seat != new_seat:
            old_seat.is_available = True
            old_seat.save()

        if new_seat and new_seat.is_available:
            new_seat.is_available = False
            new_seat.save()
            detail.seat = new_seat

        # ✅ Seat class
        seat_class_id = request.POST.get("seat_class")
        detail.seat_class = get_object_or_404(SeatClass, id=seat_class_id) if seat_class_id else None

        detail.save()
        messages.success(request, "Booking detail updated successfully!")
        return redirect("booking_detail")

    return render(request, "booking_info/booking_detail/update_booking_detail.html", {
        "detail": detail,
        "bookings": bookings,
        "flights": flights,
        "seats": seats,
        "seat_classes": seat_classes
    })
    

# Delete
def delete_booking_detail(request, detail_id):
    detail = get_object_or_404(BookingDetail, id=detail_id)

    # ✅ Restore seat availability
    if detail.seat:
        detail.seat.is_available = True
        detail.seat.save()

    detail.delete()
    messages.success(request, "Booking detail deleted successfully!")
    return redirect("booking_detail")


# ---------------------------------------Passenger Info---------------------------------------------

# ---------------------------
# Passenger
# ---------------------------

# List 
def passenger_view(request):
    passengers = PassengerInfo.objects.all()
    return render(request, "passenger_info/passenger/passenger.html", {"passengers": passengers})

# Add 
def add_passenger(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        middle_name = request.POST.get("middle_name")
        gender = request.POST.get("gender")
        date_of_birth = request.POST.get("date_of_birth")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        passport_number = request.POST.get("passport_number")

        PassengerInfo.objects.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            gender=gender,
            date_of_birth=date_of_birth,
            phone=phone,
            email=email,
            passport_number=passport_number
        )
        messages.success(request, "Passenger added successfully!")
        return redirect("passenger")

    return render(request, "passenger_info/passenger/add_passenger.html")

# Update
def update_passenger(request, passenger_id):
    passenger = get_object_or_404(PassengerInfo, id=passenger_id)

    if request.method == "POST":
        passenger.first_name = request.POST.get("first_name")
        passenger.last_name = request.POST.get("last_name")
        passenger.middle_name = request.POST.get("middle_name")
        passenger.gender = request.POST.get("gender")
        passenger.date_of_birth = request.POST.get("date_of_birth")
        passenger.phone = request.POST.get("phone")
        passenger.email = request.POST.get("email")
        passenger.passport_number = request.POST.get("passport_number")
        passenger.save()

        messages.success(request, "Passenger updated successfully!")
        return redirect("passenger")

    return render(request, "passenger_info/passenger/update_passenger.html", {"passenger": passenger})

# Delete 
def delete_passenger(request, passsenger_id):
    passenger = get_object_or_404(PassengerInfo, id=passsenger_id)
    passenger.delete()
    messages.success(request, "Passenger deleted successfully!")
    return redirect("passenger")

# -----------------------------
# Students
# -----------------------------

# List 
def check_in_view(request):
    checkins = CheckInDetail.objects.select_related("booking_detail__booking").all()
    return render(request, "passenger_info/check_in/check_in.html", {"checkins": checkins})

# Add Check-In
def add_checkin(request):
    booking_details = BookingDetail.objects.all()

    if request.method == "POST":
        booking_detail_id = request.POST.get("booking_detail")
        boarding_pass = request.POST.get("boarding_pass")
        baggage_count = request.POST.get("baggage_count") or 0
        baggage_weight = request.POST.get("baggage_weight") or 0.0

        CheckInDetail.objects.create(
            booking_detail_id=booking_detail_id,
            boarding_pass=boarding_pass,
            baggage_count=baggage_count,
            baggage_weight=baggage_weight
        )
        messages.success(request, "Check-in added successfully!")
        return redirect("check_in")

    return render(request, "passenger_info/check_in/add_check_in.html", {"booking_details": booking_details})

# Update
def update_checkin(request, checkin_id):
    checkin = get_object_or_404(CheckInDetail, id=checkin_id)
    booking_details = BookingDetail.objects.all()

    if request.method == "POST":
        checkin.booking_detail_id = request.POST.get("booking_detail")
        checkin.boarding_pass = request.POST.get("boarding_pass")
        checkin.baggage_count = request.POST.get("baggage_count") or 0
        checkin.baggage_weight = request.POST.get("baggage_weight") or 0.0
        checkin.save()

        messages.success(request, "Check-in updated successfully!")
        return redirect("check_in")

    return render(request, "passenger_info/check_in/update_check_in.html", {"checkin": checkin, "booking_details": booking_details})

# Delete 
def delete_checkin(request, checkin_id):
    checkin = get_object_or_404(CheckInDetail, id=checkin_id)
    checkin.delete()
    messages.success(request, "Check-in deleted successfully!")
    return redirect("check_in")

# ---------------------------------------Student Info-----------------------------------------------

# -----------------------------
# Students
# -----------------------------

# List Students
def student_view(request):
    students = Student.objects.all().order_by('student_number')
    return render(request, "student_info/student/student.html", {"students": students})

# Add
def add_student(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")  # get raw password
        phone = request.POST.get("phone")
        student_number = request.POST.get("student_number")

        if not password:
            messages.error(request, "Password is required.")
            return redirect("add_student")

        # Hash the password before saving
        hashed_password = make_password(password)

        Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,  # save hashed password
            phone=phone,
            student_number=student_number
        )
        messages.success(request, "Student added successfully.")
        return redirect("student")
    
    return render(request, "student_info/student/add_student.html")


# Update
def update_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == "POST":
        student.first_name = request.POST.get("first_name")
        student.last_name = request.POST.get("last_name")
        student.email = request.POST.get("email")
        student.phone = request.POST.get("phone")
        student.student_number = request.POST.get("student_number")
        password = request.POST.get("password")
        if password:
            student.password = password  # TODO: hash password
        student.save()
        messages.success(request, "Student updated successfully.")
        return redirect("student")
    
    return render(request, "student_info/student/update_student.html", {"student": student})

# Delete
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully.")
    return redirect("student")

# -----------------------------
# Tracklog
# -----------------------------

# List TrackLogs
def tracklog_view(request):
    tracklogs = TrackLog.objects.select_related("student").all()
    return render(request, "student_info/track_log/tracklog.html", {"tracklogs": tracklogs})

# Add TrackLog
def add_tracklog(request):
    students = Student.objects.all()

    if request.method == "POST":
        student_id = request.POST.get("student")
        action = request.POST.get("action")

        TrackLog.objects.create(
            student_id=student_id,
            action=action,
        )
        messages.success(request, "TrackLog added successfully!")
        return redirect("tracklog")

    return render(request, "student_info/track_log/add_tracklog.html", {"students": students})

# Update TrackLog
def update_tracklog(request, tracklog_id):
    tracklog = get_object_or_404(TrackLog, id=tracklog_id)
    students = Student.objects.all()

    if request.method == "POST":
        tracklog.student_id = request.POST.get("student")
        tracklog.action = request.POST.get("action")
        tracklog.save()

        messages.success(request, "TrackLog updated successfully!")
        return redirect("tracklog")

    return render(request, "student_info/track_log/update_tracklog.html", {"tracklog": tracklog, "students": students})

# Delete TrackLog
def delete_tracklog(request, tracklog_id):
    tracklog = get_object_or_404(TrackLog, id=tracklog_id)
    tracklog.delete()
    messages.success(request, "TrackLog deleted successfully!")
    return redirect("tracklog")