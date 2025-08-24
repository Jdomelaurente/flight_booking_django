from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404, redirect
from datetime import datetime
from django.utils import timezone

import hashlib
from .models import MyUser
from django.contrib import messages

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

# main
def main(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render())

# profile
def profile_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")  # redirect if not logged in

    user = MyUser.objects.get(id=user_id)

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
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if MyUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        MyUser.objects.create(username=username, password=hash_password(password))
        messages.success(request, "Account created. Please login.")
        return redirect("login")

    return render(request, "register.html")

# LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = hash_password(request.POST.get("password"))

        try:
            user = MyUser.objects.get(username=username, password=password)
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            return redirect("dashboard")
        except MyUser.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html")

# DASHBOARD
def dashboard_view(request):
    if "user_id" not in request.session:
        return redirect("login")
    return render(request, "dashboard.html", {"username": request.session["username"]})

# LOGOUT
def logout_view(request):
    request.session.flush()
    return redirect("login")

# ---------------------------
# Flight
# ---------------------------

# flightlist
def flight_view(request):
    flights = Flight.objects.all()
    return render(request, 'manage_flight/flight/flight.html', {'flight': flights})

#  add flight
def add_flight(request):
    if request.method == "POST":
        flight_number = request.POST.get("flight_number")
        airline_id = request.POST.get("airline")
        aircraft_id = request.POST.get("aircraft")
        route_id = request.POST.get("route")

        airline = Airline.objects.get(id=airline_id)
        aircraft = Aircraft.objects.get(id=aircraft_id)
        route = Route.objects.get(id=route_id)

        Flight.objects.create(
            flight_number=flight_number,
            airline=airline,
            aircraft=aircraft,
            route=route,
        )
        return redirect("flight")  # adjust to your flight list route

    airlines = Airline.objects.all()
    aircrafts = Aircraft.objects.all()
    routes = Route.objects.all()
    return render(request, "manage_flight/flight/add_flight.html", {
        "airlines": airlines,
        "aircrafts": aircrafts,
        "routes": routes,
    })

# update flight 
def update_flight(request, id):
    flight = get_object_or_404(Flight, id=id)

    if request.method == "POST":
        flight.flight_number = request.POST.get("flight_number")
        flight.airline = request.POST.get("airline")
        flight.aircraft = request.POST.get("aircraft")
        flight.route = request.POST.get("route")
        flight.save()
        return redirect('flight')  # Redirect back to list

    return render(request, 'manage_flight/flight/update_flight.html', {'flight': flight})

# delete flight
def delete_flight(request, id):
    flight = get_object_or_404(Flight, id=id)
    flight.delete()
    return redirect('flight') 

# ---------------------------
# Route
# ---------------------------

def route_view(request):
    routes = Route.objects.all()
    return render(request, "manage_flight/route/route.html", {"routes": routes})

# ---------------------------
# Add Route
# ---------------------------
def add_route(request):
    airports = Airport.objects.all()
    airlines = Airline.objects.all()
    aircrafts = Aircraft.objects.all()

    if request.method == "POST":
        departure_id = request.POST["departure_airport"]
        arrival_id = request.POST["arrival_airport"]
        airline_id = request.POST["airline"]
        aircraft_id = request.POST["aircraft"]
        distance = request.POST["distance"]
        duration = request.POST["duration"]

        departure_airport = get_object_or_404(Airport, id=departure_id)
        arrival_airport = get_object_or_404(Airport, id=arrival_id)
        airline = get_object_or_404(Airline, id=airline_id)
        aircraft = get_object_or_404(Aircraft, id=aircraft_id)

        Route.objects.create(
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            airline=airline,
            aircraft=aircraft,
            distance=distance,
            duration=duration,
        )
        return redirect("route")

    return render(
        request,
        "manage_flight/route/add_route.html",
        {"airports": airports, "airlines": airlines, "aircrafts": aircrafts},
    )



# update route
def update_route(request, id):
    route = get_object_or_404(Route, id=id)

    if request.method == "POST":
        route.origin = request.POST.get("origin")
        route.destination = request.POST.get("destination")
        route.distance = request.POST.get("distance")
        route.duration = request.POST.get("duration")
        route.airline = request.POST.get("airline")
        route.aircraft = request.POST.get("aircraft")
        route.save()
        return redirect('route')

    return render(request, 'manage_flight/route/update_route.html', {"route": route})

# delete route
def delete_route(request, id):
    route = get_object_or_404(Route, id=id)
    route.delete()
    return redirect('route')

# ---------------------------
# Schedule
# ---------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from .models import Flight, Schedule
from datetime import datetime

def schedule_view(request):
    schedules = Schedule.objects.all()
    current_time = timezone.localtime(timezone.now())

    schedule_data = []
    for s in schedules:
        if current_time < s.departure_time:
            status = "Standby"
        elif s.departure_time <= current_time < s.arrival_time:
            status = "On Flight"
        else:
            status = "Arrived"

        schedule_data.append({
            "schedule": s,
            "status": status
        })

    return render(request, "manage_flight/schedule/schedule.html", {
        "schedule_data": schedule_data,
        "current_time": current_time
    })



# ---------------------------
# Add schedule
# ---------------------------
def add_schedule(request):
    flights = Flight.objects.all()
    if request.method == "POST":
        flight_id = request.POST["flight_id"]
        departure_time_str = request.POST["departure_time"]
        arrival_time_str = request.POST["arrival_time"]

        # Convert to datetime (Flask logic)
        departure_time = datetime.strptime(departure_time_str, "%Y-%m-%dT%H:%M")
        arrival_time = datetime.strptime(arrival_time_str, "%Y-%m-%dT%H:%M")

        # Make timezone-aware
        departure_time = timezone.make_aware(departure_time)
        arrival_time = timezone.make_aware(arrival_time)

        Schedule.objects.create(
            flight_id=flight_id,
            departure_time=departure_time,
            arrival_time=arrival_time
        )
        messages.success(request, "Flight schedule added successfully!")
        return redirect("schedule")

    return render(request, "manage_flight/schedule/add_schedule.html", {"flights": flights})


# ---------------------------
# Edit schedule
# ---------------------------
def update_schedule(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    flights = Flight.objects.all()

    if request.method == "POST":
        schedule.flight_id = request.POST["flight_id"]

        departure_time_str = request.POST["departure_time"]
        arrival_time_str = request.POST["arrival_time"]

        # Convert like in Flask
        departure_time = datetime.strptime(departure_time_str, "%Y-%m-%dT%H:%M")
        arrival_time = datetime.strptime(arrival_time_str, "%Y-%m-%dT%H:%M")

        schedule.departure_time = timezone.make_aware(departure_time)
        schedule.arrival_time = timezone.make_aware(arrival_time)

        schedule.save()
        messages.success(request, "Flight schedule updated successfully!")
        return redirect("schedule")

    return render(request, "manage_flight/schedule/update_schedule.html", {
        "schedule": schedule,
        "flights": flights
    })


# ---------------------------
# Delete schedule
# ---------------------------
def delete_schedule(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    schedule.delete()
    messages.error(request, "Flight schedule deleted.")
    return redirect("schedule")

# ---------------------------
# Seat
# ---------------------------

def seat_view(request):
    seats = Seat.objects.all()
    return render(request, 'manage_flight/seat/seat.html', {"seats": seats})

# Add seat
def add_seat(request):
    if request.method == "POST":
        schedule_id = request.POST["schedule"]
        seat_number = request.POST["seat_number"]
        seat_class_id = request.POST["seat_class"]   # Now we use ID, not text
        available = request.POST.get("available") == "on"
        price = request.POST["price"]

        schedule = Schedule.objects.get(id=schedule_id)
        seat_class = SeatClass.objects.get(id=seat_class_id)  # ✅ fetch instance

        Seat.objects.create(
            schedule=schedule,
            seat_number=seat_number,
            seat_class=seat_class,   # ✅ correct
            available=available,
            price=price
        )
        return redirect("seat")

    schedules = Schedule.objects.all()
    seat_classes = SeatClass.objects.all()   # ✅ add this
    return render(request, "manage_flight/seat/add_seat.html", {
        "schedules": schedules,
        "seat_classes": seat_classes
    })


# Update seat
def update_seat(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)

    if request.method == "POST":
        seat.schedule_id = request.POST["schedule"]
        seat.seat_number = request.POST["seat_number"]
        seat.seat_class = request.POST["seat_class"]
        seat.available = request.POST.get("available") == "on"
        seat.price = request.POST["price"]
        seat.save()
        return redirect("seat")

    schedules = Schedule.objects.all()
    return render(request, "manage_flight/seat/update_seat.html", {"seat": seat, "schedules": schedules})

# Delete seat
def delete_seat(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    seat.delete()
    return redirect("seat")

# ---------------------------
# Airport
# ---------------------------

# ---------------------------
# Airport List
# ---------------------------
def airport_view(request):
    airports = Airport.objects.all()
    return render(request, "asset/airport/airport.html", {"airports": airports})

# ---------------------------
# Add Airport
# ---------------------------
def add_airport(request):
    if request.method == "POST":
        code = request.POST["code"]
        name = request.POST["name"]
        city = request.POST["city"]
        country = request.POST["country"]

        Airport.objects.create(code=code, name=name, city=city, country=country)
        return redirect("airport")

    return render(request, "asset/airport/add_airport.html")

# Update airport
def update_airport(request, airport_id):
    airport = get_object_or_404(Airport, id=airport_id)

    if request.method == "POST":
        airport.code = request.POST["code"]
        airport.name = request.POST["name"]
        airport.city = request.POST["city"]
        airport.country = request.POST["country"]
        airport.save()
        return redirect("airport")

    return render(request, "asset/airport/update_airport.html", {"airport": airport})

# Delete airport
def delete_airport(request, airport_id):
    airport = get_object_or_404(Airport, id=airport_id)
    airport.delete()
    return redirect("airport")

# ---------------------------
# Airline
# ---------------------------

def airline_view(request):
    airlines = Airline.objects.all()
    return render(request, 'asset/airline/airline.html', {"airlines": airlines})

# Add Airline
def add_airline(request):
    if request.method == "POST":
        code = request.POST["code"]
        name = request.POST["name"]

        Airline.objects.create(code=code, name=name)
        return redirect("airline")

    return render(request, "asset/airline/add_airline.html")

# Update Airline
def update_airline(request, airline_id):
    airline = get_object_or_404(Airline, id=airline_id)

    if request.method == "POST":
        airline.code = request.POST["code"]
        airline.name = request.POST["name"]
        airline.save()
        return redirect("airline")

    return render(request, "asset/airline/update_airline.html", {"airline": airline})

# Delete Airline
def delete_airline(request, airline_id):
    airline = get_object_or_404(Airline, id=airline_id)
    airline.delete()
    return redirect("airline")

# ---------------------------
# Aircraft
# ---------------------------


# ---------------------------
# Aircraft List
# ---------------------------
def aircraft_view(request):
    aircrafts = Aircraft.objects.all()
    return render(request, 'asset/aircraft/aircraft.html', {"aircrafts": aircrafts})

# ---------------------------
# Add Aircraft
# ---------------------------
def add_aircraft(request):
    airlines = Airline.objects.all()  # so you can choose airline in dropdown

    if request.method == "POST":
        model = request.POST["model"]
        capacity = request.POST["capacity"]
        type = request.POST["type"]
        airline_id = request.POST["airline"]

        airline = get_object_or_404(Airline, id=airline_id)

        Aircraft.objects.create(
            model=model,
            capacity=capacity,
            type=type,
            airline=airline
        )
        return redirect("aircraft")

    return render(request, "asset/aircraft/add_aircraft.html", {"airlines": airlines})

# ---------------------------
# Update Aircraft
# ---------------------------
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

# ---------------------------
# Delete Aircraft
# ---------------------------
def delete_aircraft(request, aircraft_id):
    aircraft = get_object_or_404(Aircraft, id=aircraft_id)
    aircraft.delete()
    return redirect("aircraft")

# ---------------------------
# Seat_class
# ---------------------------

def seat_class_view(request):
    seat_classes = SeatClass.objects.all()
    return render(request, 'asset/seat_class/seat_class.html', {"seat_classes": seat_classes})


# Add Seat Class
def add_seat_class(request):
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]
        price_multiplier = request.POST["price_multiplier"]

        SeatClass.objects.create(
            name=name,
            description=description,
            price_multiplier=price_multiplier
        )
        return redirect("seat_class")

    return render(request, "asset/seat_class/add_seat_class.html")

# Update Seat Class
def update_seat_class(request, seat_class_id):
    seat_class = get_object_or_404(SeatClass, id=seat_class_id)

    if request.method == "POST":
        seat_class.name = request.POST["name"]
        seat_class.description = request.POST["description"]
        seat_class.price_multiplier = request.POST["price_multiplier"]
        seat_class.save()
        return redirect("seat_class")

    return render(request, "asset/seat_class/update_seat_class.html", {"seat_class": seat_class})

# Delete Seat Class
def delete_seat_class(request, seat_class_id):
    seat_class = get_object_or_404(SeatClass, id=seat_class_id)
    seat_class.delete()
    return redirect("seat_class")

# ---------------------------
# Booking
# ---------------------------

def booking_view(request):
    bookings = Booking.objects.all()
    return render(request, 'booking/booking/booking.html', {"bookings": bookings})


# Add booking
import random
import string

def generate_reference():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def add_booking(request):
    if request.method == "POST":
        student_id = request.POST["student"]
        status = request.POST["status"]

        student = Student.objects.get(id=student_id)

        Booking.objects.create(
            student=student,
            reference=generate_reference(),  # auto-generate unique reference
            status=status
        )
        return redirect("booking")

    students = Student.objects.all()
    return render(request, "booking/booking/add_booking.html", {"students": students})



# Update booking
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST":
        booking.student = request.POST["student"]
        booking.booking_date = request.POST["booking_date"]
        booking.status = request.POST["status"]
        booking.save()
        return redirect("booking")
    return render(request, "booking/booking/update_booking.html", {"booking": booking})

# Delete booking
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect("booking")

# ---------------------------
# Booking_detail
# ---------------------------

def booking_detail_view(request):
    details = BookingDetail.objects.all()
    return render(request, 'booking/booking_detail/booking_detail.html', {"details": details})

# Add
def add_booking_detail(request):
    if request.method == "POST":
        booking_id = request.POST["booking"]
        flight_id = request.POST["flight"]
        seat_class_id = request.POST["seat_class"]
        quantity = request.POST["quantity"]

        BookingDetail.objects.create(
            booking_id=booking_id,
            flight_id=flight_id,
            seat_class_id=seat_class_id,
            quantity=quantity
        )
        return redirect("booking_detail")

    bookings = Booking.objects.all()
    flights = Flight.objects.all()
    seat_classes = SeatClass.objects.all()
    return render(request, "booking/booking_detail/add_booking_detail.html", {
        "bookings": bookings,
        "flights": flights,
        "seat_classes": seat_classes
    })

# Update
def update_booking_detail(request, detail_id):
    detail = get_object_or_404(BookingDetail, id=detail_id)
    if request.method == "POST":
        detail.booking_id = request.POST["booking"]
        detail.flight_id = request.POST["flight"]
        detail.seat_class_id = request.POST["seat_class"]
        detail.quantity = request.POST["quantity"]
        detail.save()
        return redirect("booking_detail")

    bookings = Booking.objects.all()
    flights = Flight.objects.all()
    seat_classes = SeatClass.objects.all()
    return render(request, "booking/booking_detail/update_booking_detail.html", {
        "detail": detail,
        "bookings": bookings,
        "flights": flights,
        "seat_classes": seat_classes
    })

# Delete
def delete_booking_detail(request, detail_id):
    detail = get_object_or_404(BookingDetail, id=detail_id)
    detail.delete()
    return redirect("booking_detail")

# ---------------------------
# Payment
# ---------------------------
def payment_view(request):
    payments = Payment.objects.all()
    return render(request, 'booking/payment/payment.html', {"payments": payments})

# Add
def add_payment(request):
    if request.method == "POST":
        booking_id = request.POST["booking"]
        amount = request.POST["amount"]
        method = request.POST["method"]
        transaction_id = request.POST["transaction_id"]
        status = request.POST["status"]

        Payment.objects.create(
            booking_id=booking_id,
            amount=amount,
            method=method,
            transaction_id=transaction_id,
            status=status
        )
        return redirect("payment")

    bookings = Booking.objects.all()
    return render(request, "booking/payment/add_payment.html", {"bookings": bookings})

# Update
def update_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == "POST":
        payment.booking_id = request.POST["booking"]
        payment.amount = request.POST["amount"]
        payment.method = request.POST["method"]
        payment.transaction_id = request.POST["transaction_id"]
        payment.status = request.POST["status"]
        payment.save()
        return redirect("payment")

    bookings = Booking.objects.all()
    return render(request, "booking/payment/update_payment.html", {"payment": payment, "bookings": bookings})

# Delete
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.delete()
    return redirect("payment")

# ---------------------------
# Check_in
# ---------------------------
def check_in_view(request):
    checkins = CheckInDetail.objects.all()
    return render(request, "passenger/check_in/check_in.html", {"checkins": checkins})

# Add
def add_checkin(request):
    if request.method == "POST":
        booking_id = request.POST["booking"]
        boarding_pass = request.POST["boarding_pass"]
        baggage_count = request.POST["baggage_count"]
        baggage_weight = request.POST["baggage_weight"]

        CheckInDetail.objects.create(
            booking_id=booking_id,
            boarding_pass=boarding_pass,
            baggage_count=baggage_count,
            baggage_weight=baggage_weight
        )
        return redirect("check_in")

    bookings = Booking.objects.all()
    return render(request, "passenger/check_in/add_check_in.html", {"bookings": bookings})

# Update
def update_checkin(request, checkin_id):
    checkin = get_object_or_404(CheckInDetail, id=checkin_id)
    if request.method == "POST":
        checkin.booking_id = request.POST["booking"]
        checkin.boarding_pass = request.POST["boarding_pass"]
        checkin.baggage_count = request.POST["baggage_count"]
        checkin.baggage_weight = request.POST["baggage_weight"]
        checkin.save()
        return redirect("check_in")

    bookings = Booking.objects.all()
    return render(request, "passenger/check_in/update_check_in.html", {"checkin": checkin, "bookings": bookings})

# Delete
def delete_checkin(request, checkin_id):
    checkin = get_object_or_404(CheckInDetail, id=checkin_id)
    checkin.delete()
    return redirect("check_in")

# ---------------------------
# Student
# ---------------------------
def student_view(request):
    students = Student.objects.all()
    return render(request, "passenger/student/student.html", {"students": students})

# Add
def add_student(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        phone_number = request.POST.get("phone_number", "")
        date_of_birth = request.POST.get("date_of_birth", None)
        address = request.POST.get("address", "")

        Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            date_of_birth=date_of_birth if date_of_birth else None,
            address=address
        )
        return redirect("student")

    return render(request, "passenger/student/add_student.html")

# Update
def update_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        student.username = request.POST["username"]
        student.email = request.POST["email"]
        student.name = request.POST["name"]
        student.phone = request.POST["phone"]
        student.save()
        return redirect("student")

    return render(request, "passenger/student/update_student.html", {"student": student})

# Delete
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect("student")

