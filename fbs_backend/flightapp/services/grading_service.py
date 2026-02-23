from django.utils import timezone
from app.models import Booking, BookingDetail, Students
from fbs_instructor.models import Activity, ActivityStudentBinding
import logging

logger = logging.getLogger(__name__)

def grade_booking(booking, activity_id):
    """
    Validates a booking against an activity's requirements and updates the student's grade.
    """
    try:
        if not activity_id:
            return

        activity = Activity.objects.get(id=activity_id)
        student = None
        
        # Try to find the student record for this user
        try:
            student = Students.objects.get(user=booking.user)
        except Students.DoesNotExist:
            logger.warning(f"User {booking.user.username} has no Student profile but tried to grade activity {activity_id}")
            return

        # Get the binding
        binding, created = ActivityStudentBinding.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={'status': 'submitted'}
        )

        # 1. Weights for Granular Scoring (Percentage of total_points)
        weights = {
            'trip_type': 0.10,
            'pax_counts': 0.30, # 10% each for A, C, I
            'origin': 0.20,
            'destination': 0.20,
            'seat_class': 0.20
        }
        
        earned_percentages = 0.0

        # Initialize score and feedback
        score = 0.0
        total_score = float(activity.total_points)
        feedback = []

        # 1. Check Trip Type
        if activity.required_trip_type and booking.trip_type != activity.required_trip_type:
            feedback.append(f"[X] Incorrect Trip Type: Requires {activity.get_required_trip_type_display()}, got {booking.get_trip_type_display()}")
        else:
            feedback.append("[OK] Correct Trip Type")
            earned_percentages += weights['trip_type']

        # 2. Check Passenger Counts
        details = booking.details.all()
        unique_passengers = {}
        for d in details:
            if d.passenger_id not in unique_passengers:
                unique_passengers[d.passenger_id] = d.passenger
        
        adults = sum(1 for p in unique_passengers.values() if p.passenger_type == "Adult")
        children = sum(1 for p in unique_passengers.values() if p.passenger_type == "Child")
        infants = sum(1 for p in unique_passengers.values() if p.passenger_type == "Infant")

        pax_correct = True
        if adults != activity.required_passengers:
            feedback.append(f"[X] Incorrect Adult Count: Requires {activity.required_passengers}, got {adults}")
            pax_correct = False
        else:
            earned_percentages += weights['pax_counts'] / 3

        if children != activity.required_children:
            feedback.append(f"[X] Incorrect Child Count: Requires {activity.required_children}, got {children}")
            pax_correct = False
        else:
            earned_percentages += weights['pax_counts'] / 3

        if infants != activity.required_infants:
            feedback.append(f"[X] Incorrect Infant Count: Requires {activity.required_infants}, got {infants}")
            pax_correct = False
        else:
            earned_percentages += weights['pax_counts'] / 3
        
        if pax_correct:
            feedback.append(f"[OK] Correct Passenger Counts ({adults}A, {children}C, {infants}I)")

        # 3, 4, 5. Flight Origin, Destination, Class
        # For multiple passengers, we usually check the first outbound detail
        # But we should be careful to pick the correct outbound vs return schedules
        all_schedules = []
        seen_schedule_ids = set()
        for d in details:
            if d.schedule_id not in seen_schedule_ids:
                all_schedules.append(d.schedule)
                seen_schedule_ids.add(d.schedule_id)
        
        # Sort schedules by departure time
        all_schedules.sort(key=lambda s: s.departure_time)
        
        if not all_schedules:
            feedback.append("[X] No flight schedules found in booking")
        else:
            outbound_schedule = all_schedules[0]
            
            # --- Check Origin ---
            booked_origin = outbound_schedule.flight.route.origin_airport
            req_origin = activity.required_origin.upper() if activity.required_origin else None
            if req_origin:
                if req_origin != booked_origin.code and req_origin not in booked_origin.city.upper():
                    feedback.append(f"[X] Incorrect Origin: Requires {activity.required_origin}, got {booked_origin.city} ({booked_origin.code})")
                else:
                    feedback.append("[OK] Correct Origin")
                    earned_percentages += weights['origin']

            # --- Check Destination ---
            booked_dest = outbound_schedule.flight.route.destination_airport
            req_dest = activity.required_destination.upper() if activity.required_destination else None
            if req_dest:
                if req_dest != booked_dest.code and req_dest not in booked_dest.city.upper():
                    feedback.append(f"[X] Incorrect Destination: Requires {activity.required_destination}, got {booked_dest.city} ({booked_dest.code})")
                else:
                    feedback.append("[OK] Correct Destination")
                    earned_percentages += weights['destination']

            # --- Check Seat Class ---
            if activity.required_travel_class:
                # Get the seat class from the detail matching the outbound schedule
                outbound_detail = details.filter(schedule=outbound_schedule).first()
                booked_class = outbound_detail.seat_class.name if outbound_detail and outbound_detail.seat_class else "Unknown"
                req_class = activity.required_travel_class.lower().replace('_', ' ')
                b_class = booked_class.lower()
                
                if req_class not in b_class:
                     feedback.append(f"[X] Incorrect Seat Class: Requires {activity.get_required_travel_class_display()}, got {booked_class}")
                else:
                     feedback.append("[OK] Correct Seat Class")
                     earned_percentages += weights['seat_class']

        # 6. Check Arrival/Return leg for Round Trip
        if activity.required_trip_type == 'round_trip':
            if len(all_schedules) < 2:
                feedback.append("[X] Missing Return Flight: Round trip requires a return booking")
            else:
                outbound = all_schedules[0]
                return_leg = all_schedules[1]
                # Simple check: Return destination should be outbound origin
                if return_leg.flight.route.destination_airport.code != outbound.flight.route.origin_airport.code:
                    feedback.append("[X] Incorrect Return Route: Return flight must end at origin")
                else:
                    feedback.append("[OK] Valid Return Route")

        # Calculate Final Score
        score = round(total_score * earned_percentages, 2)
        
        if earned_percentages >= 1.0:
            binding.status = 'graded'
            feedback.insert(0, f"PERFECT SCORE! All requirements met. ({score}/{total_score})")
        elif earned_percentages > 0:
            binding.status = 'graded' # Mark as graded even if partial
            feedback.insert(0, f"Partial Score: Some requirements met. ({score}/{total_score})")
        else:
            binding.status = 'submitted'
            feedback.insert(0, f"Requirements not met. ({score}/{total_score})")
            
        # Update Binding
        binding.grade = score
        binding.feedback = "\n".join(feedback)
        binding.submitted_at = timezone.now()
        binding.save()
        
        # Update Booking to link
        booking.activity = activity
        booking.is_graded = True
        booking.save()
        
        logger.info(f"Graded booking {booking.id} for activity {activity.title}. Score: {score}")

    except Exception as e:
        logger.error(f"Error grading booking: {str(e)}")
        import traceback
        traceback.print_exc() 
