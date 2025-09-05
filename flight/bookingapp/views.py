from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from flightapp.models import Schedule, Route,  Airport
# Create your views here.

def home(request):
    from_airports = Route.objects.select_related("origin_airport").all()
    to_airports = Route.objects.select_related("destination_airport").all()

    templates= loader.get_template('booking/home.html')
    context = {
        "from_airports" :from_airports,
        "to_airports" : to_airports,

    }
    return HttpResponse(templates.render(context, request))


def flight_schedule(request):
    schedules = []
    origin_airport = None
    destination_airport = None
    depart_date = None

    if request.method == "POST":
        from_id = request.POST.get("from")
        to_id = request.POST.get("to")
        depart_date_str = request.POST.get("depart")

        # Save selections in session
        request.session['origin_airport_id'] = from_id
        request.session['destination_airport_id'] = to_id
        request.session['depart_date'] = depart_date_str

    else:  # GET request: try to load from session
        from_id = request.session.get('origin_airport_id')
        to_id = request.session.get('destination_airport_id')
        depart_date_str = request.session.get('depart_date')

    # Get airport objects for display
    try:
        origin_airport = Airport.objects.get(id=from_id) if from_id else None
        destination_airport = Airport.objects.get(id=to_id) if to_id else None
    except Airport.DoesNotExist:
        origin_airport = None
        destination_airport = None

    # Parse departure date
    try:
        depart_date = datetime.strptime(depart_date_str, "%Y-%m-%d").date() if depart_date_str else None
    except (TypeError, ValueError):
        depart_date = None

    # Filter routes using IDs
    if from_id and to_id:
        routes = Route.objects.filter(
            origin_airport_id=from_id,
            destination_airport_id=to_id
        )

        # Filter schedules
        if depart_date:
            schedules = Schedule.objects.filter(
                flight__route__in=routes,
                departure_time__date=depart_date
            ).select_related(
                "flight", "flight__airline",
                "flight__route__origin_airport",
                "flight__route__destination_airport"
            )

    template = loader.get_template("booking/flight_schedule.html")
    context = {
        "schedules": schedules,
        "origin_airport": origin_airport,
        "destination_airport": destination_airport,
        "depart_date": depart_date
    }
    return HttpResponse(template.render(context, request))


def select_schedule(request):
    if request.method == "POST":
        schedule_id = request.POST.get("schedule_id")
        request.session['selected_schedule_id'] = schedule_id
        return redirect('passenger')




def passenger(request):
    schedule = None
    schedule_id = request.session.get('selected_schedule_id')
    
    if schedule_id:
        try:
            schedule = Schedule.objects.select_related(
                "flight",
                "flight__airline",
                "flight__route__origin_airport",
                "flight__route__destination_airport"
            ).get(id=schedule_id)
        except Schedule.DoesNotExist:
            schedule = None
    templates= loader.get_template('booking/passenger.html')
    context = {
        'schedule': schedule,
    }
    return HttpResponse(templates.render(context, request))

def seat(request):
    templates= loader.get_template('booking/seat.html')
    context = {

    }
    return HttpResponse(templates.render(context, request))

def booking_summary(request):
    templates= loader.get_template('booking/booking_summary.html')
    context = {

    }
    return HttpResponse(templates.render(context, request))

def payment(request):
    templates= loader.get_template('booking/payment.html')
    context = {

    }
    return HttpResponse(templates.render(context, request))


def success(request):
    templates= loader.get_template('booking/success.html')
    context = {

    }
    return HttpResponse(templates.render(context, request))
