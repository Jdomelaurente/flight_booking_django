import os
import django
import random
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from fbs_instructor.models import Activity
from app.models import Schedule, Seat

def generate_random_seats_test(activity, count):
    try:
        schedule_query = Schedule.objects.filter(status='Open')
        if activity.required_origin:
            schedule_query = schedule_query.filter(flight__route__origin_airport__code=activity.required_origin)
        if activity.required_destination:
            schedule_query = schedule_query.filter(flight__route__destination_airport__code=activity.required_destination)
        if activity.required_departure_date:
            schedule_query = schedule_query.filter(departure_time__date=activity.required_departure_date)
            
        schedule = schedule_query.first()
        
        if schedule:
            class_map = {
                'economy': ['Economy Class', 'Standard Seat', 'Basic Seat', 'Value Seat'],
                'premium_economy': ['Premium Economy', 'Premium Seat', 'Hot Seat'],
                'business': ['Business Class', 'Business'],
                'first': ['First Class', 'First']
            }
            target_classes = class_map.get(activity.required_travel_class.lower(), ['Economy Class'])
            
            db_seats = list(Seat.objects.filter(
                schedule=schedule,
                seat_class__name__icontains=target_classes[0]
            ).values_list('seat_number', flat=True).distinct())
            
            if not db_seats:
                q_obj = Q()
                for tc in target_classes:
                    q_obj |= Q(seat_class__name__icontains=tc)
                db_seats = list(Seat.objects.filter(
                    schedule=schedule
                ).filter(q_obj).values_list('seat_number', flat=True).distinct())
            
            print(f"DEBUG: Found {len(db_seats)} db_seats for schedule {schedule.id}")
            if db_seats and len(db_seats) >= count:
                return random.sample(db_seats, count)
        else:
            print("DEBUG: No matching schedule found for activity.")
    except Exception as e:
        print(f"DEBUG: Real seat lookup failed: {str(e)}")

    # Fallback
    print("DEBUG: Falling back to generated seats")
    rows = []
    seats_letters = ['A', 'B', 'C', 'D', 'E', 'F']
    travel_class = (activity.required_travel_class or 'economy').lower()
    
    if travel_class in ['business', 'first']:
        rows = list(range(1, 5))
        seats_letters = ['A', 'C', 'D', 'F']
    elif travel_class == 'premium_economy':
        rows = list(range(5, 10))
    else: # Economy
        rows = list(range(10, 36))
        
    all_possible_seats = [f"{row}{letter}" for row in rows for letter in seats_letters]
    
    if count > len(all_possible_seats):
        count = len(all_possible_seats)
        
    return random.sample(all_possible_seats, count)

# Test with various activities
activities = Activity.objects.all()[:5]
for act in activities:
    print(f"\nActivity: {act.title} (Class: {act.required_travel_class}, Origin: {act.required_origin}, Dest: {act.required_destination})")
    seats = generate_random_seats_test(act, 2)
    print(f"Assigned Seats: {seats}")
