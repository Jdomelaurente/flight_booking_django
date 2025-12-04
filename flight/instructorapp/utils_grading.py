from django.shortcuts import redirect
from functools import wraps
from decimal import Decimal
from django.utils import timezone
from flightapp.models import Airport

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('student_id'):  # check if logged in
            return redirect('bookingapp:login')
        return view_func(request, *args, **kwargs)
    return wrapper

def redirect_if_logged_in(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('student_id'):  # already logged in
            return redirect('studentapp:student_home')  # send them to home
        return view_func(request, *args, **kwargs)
    return wrapper


def calculate_activity_score(booking, activity):
    """
    Calculate score based on how well the booking matches activity requirements
    WITH CONSISTENT WEIGHTS
    """
    total_points = float(activity.total_points)

    print(f"=== SCORING DEBUG ===")
    print(f"Activity: {activity.title}")
    print(f"Total points available: {total_points}")

    # VERIFIED WEIGHTS - MUST MATCH TEMPLATE DISPLAY
    base_weight = 0.10              # 10% - Completion
    passenger_info_weight = 0.40    # 40% - Passenger information quality 
    flight_route_weight = 0.10      # 10% - Flight route compliance
    trip_type_weight = 0.10         # 10% - Trip type compliance
    travel_class_weight = 0.10      # 10% - Travel class compliance
    passenger_count_weight = 0.15   # 15% - Passenger count compliance
    addon_weight = 0.05             # 5% - Add-ons

    # VERIFY WEIGHTS SUM TO 100%
    total_weight = (base_weight + passenger_info_weight + flight_route_weight + 
                   trip_type_weight + travel_class_weight + passenger_count_weight + addon_weight)
    print(f"WEIGHT VERIFICATION: {total_weight} (should be 1.0)")

    # Initialize scores
    points_earned = 0.0
    score_components = {}
    warnings = []

    # 1. Base points for completing the booking
    base_points = total_points * base_weight
    points_earned += base_points
    score_components['base'] = base_points
    print(f"1. Base points: {base_points}")

    # 2. Passenger Information Quality (now returns (score, warning_message))
    passenger_info_score, passenger_info_warning = evaluate_passenger_information_quality(booking, activity)
    if passenger_info_warning:
        warnings.append(passenger_info_warning)
        score_components['passenger_info_warning'] = passenger_info_warning

    passenger_info_points = total_points * passenger_info_weight * passenger_info_score
    points_earned += passenger_info_points
    score_components['passenger_info'] = passenger_info_points
    print(f"2. Passenger info: {passenger_info_points} (quality: {passenger_info_score})")

    # 3. Flight Route Compliance (10%)
    flight_route_score = evaluate_flight_route_compliance(booking, activity)
    flight_route_points = total_points * flight_route_weight * flight_route_score
    points_earned += flight_route_points
    score_components['flight_route'] = flight_route_points
    print(f"3. Flight route: {flight_route_points} (score: {flight_route_score})")

    # 4. Trip Type Compliance
    trip_type_match = booking.trip_type == activity.required_trip_type
    trip_type_points = total_points * trip_type_weight * (1.0 if trip_type_match else 0.0)
    points_earned += trip_type_points
    score_components['trip_type'] = trip_type_points
    print(f"4. Trip type: {trip_type_points} (match: {trip_type_match})")

    # 5. Travel Class Compliance
    has_correct_class = False
    for detail in booking.details.order_by('id'):
        if detail.seat_class and detail.seat_class.name.lower() == activity.required_travel_class.lower():
            has_correct_class = True
            break

    travel_class_points = total_points * travel_class_weight * (1.0 if has_correct_class else 0.0)
    points_earned += travel_class_points
    score_components['travel_class'] = travel_class_points
    print(f"5. Travel class: {travel_class_points} (correct: {has_correct_class})")

    # 6. Passenger Count Compliance (weighted)
    adult_count = sum(1 for detail in booking.details.order_by('id') if detail.passenger.passenger_type.lower() == 'adult')
    child_count = sum(1 for detail in booking.details.order_by('id') if detail.passenger.passenger_type.lower() == 'child')
    infant_count = sum(1 for detail in booking.details.order_by('id') if detail.passenger.passenger_type.lower() == 'infant')

    print(f"Passenger counts - Adults: {adult_count}/{activity.required_passengers}, "
          f"Children: {child_count}/{activity.required_children}, "
          f"Infants: {infant_count}/{activity.required_infants}")

    # Calculate passenger count score with proper ratios
    adult_ratio = min(adult_count / activity.required_passengers, 1.0) if activity.required_passengers > 0 else 1.0
    child_ratio = min(child_count / activity.required_children, 1.0) if activity.required_children > 0 else 1.0
    infant_ratio = min(infant_count / activity.required_infants, 1.0) if activity.required_infants > 0 else 1.0

    total_required = activity.required_passengers + activity.required_children + activity.required_infants
    if total_required > 0:
        passenger_count_score = (
            (adult_ratio * activity.required_passengers) +
            (child_ratio * activity.required_children) + 
            (infant_ratio * activity.required_infants)
        ) / total_required
    else:
        passenger_count_score = 1.0

    passenger_count_points = total_points * passenger_count_weight * passenger_count_score
    points_earned += passenger_count_points
    score_components['passenger_count'] = passenger_count_points
    print(f"6. Passenger count: {passenger_count_points} (score: {passenger_count_score})")

    # 7. Add-ons
    addon_points = 0.0
    if hasattr(activity, 'activity_addons') and activity.activity_addons.exists() and activity.addon_grading_enabled:
        required_addons = activity.activity_addons.filter(is_required=True)
        total_required_addons = required_addons.count()

        if total_required_addons > 0:
            # Get student's selected add-ons
            student_addons = set()
            for detail in booking.details.order_by('id'):
                for addon in detail.addons.all():
                    student_addons.add(addon.id)

            matched_required = sum(1 for req_addon in required_addons if req_addon.addon.id in student_addons)
            addon_score_ratio = matched_required / total_required_addons if total_required_addons > 0 else 1.0
            addon_points = total_points * addon_weight * addon_score_ratio
            print(f"7. Add-ons: {addon_points} (matched {matched_required}/{total_required_addons})")
        else:
            addon_points = total_points * addon_weight
            print(f"7. Add-ons: {addon_points} (no required add-ons)")
    else:
        addon_points = total_points * addon_weight
        print(f"7. Add-ons: {addon_points} (add-on grading disabled)")

    points_earned += addon_points
    score_components['addons'] = addon_points

    # Ensure score doesn't exceed total points
    final_score = min(points_earned, total_points)

    # Final breakdown
    print(f"=== FINAL SCORE BREAKDOWN ===")
    print(f"Base: {score_components['base']:.2f}")
    print(f"Passenger Info: {score_components['passenger_info']:.2f}")
    if 'passenger_info_warning' in score_components:
        print(f"Passenger info warning: {score_components['passenger_info_warning']}")
    print(f"Flight Route: {score_components['flight_route']:.2f}")
    print(f"Trip Type: {score_components['trip_type']:.2f}")
    print(f"Travel Class: {score_components['travel_class']:.2f}")
    print(f"Passenger Count: {score_components['passenger_count']:.2f}")
    print(f"Add-ons: {score_components['addons']:.2f}")
    print(f"TOTAL: {final_score:.2f}/{total_points}")
    print("=============================")

    result = {
        'score': Decimal(str(round(final_score, 2))),
        'raw_total': final_score,
        'score_components': score_components,
        'warnings': warnings
    }

    return result


def evaluate_passenger_information_quality(booking, activity):
    """
    Evaluate the quality and completeness of passenger information
    Returns (score_between_0_and_1, warning_message_or_empty_string)

    Note: booking.details MUST be ordered ASC by id before calling this function,
    but this function also uses .order_by('id') for safety.
    """
    print("=== PASSENGER INFORMATION EVALUATION ===")

    booking_details = list(booking.details.order_by('id').select_related('passenger'))
    total_passengers = len(booking_details)

    # FIRST: Check if we have the right number of passengers
    required_total = activity.required_passengers + activity.required_children + activity.required_infants
    warning_message = ""

    if total_passengers != required_total:
        print(f"❌ Passenger count mismatch: required {required_total}, got {total_passengers}")
        # Heavier penalty for missing passengers compared to extra (configurable)
        count_penalty = 0.3
        if total_passengers < required_total and required_total > 1:
            # Missing passengers when more than 1 expected -> explicit warning
            missing = required_total - total_passengers
            warning_message = f"Kulang ang gi-book nga passengers: {total_passengers}/{required_total} (kulang {missing}) - Minusan og points."
            print(f"⚠️ {warning_message}")
        elif total_passengers > required_total:
            extra = total_passengers - required_total
            warning_message = f"Naay extra passengers: {total_passengers}/{required_total} (extra {extra}) - Posibleng penalty."
            print(f"⚠️ {warning_message}")
    else:
        count_penalty = 0.0
        print(f"✅ Correct passenger count: {total_passengers}")

    if total_passengers == 0:
        # no passengers, zero score and warning if required_total > 0
        if required_total > 0:
            warning_message = f"Kulang ang gi-book nga passengers: 0/{required_total} - Minusan og points."
        return 0.0, warning_message

    total_score = 0.0

    # Count passenger types to verify requirements
    adult_count = 0
    child_count = 0
    infant_count = 0

    # Get predefined passengers for this activity
    predefined_passengers = list(activity.passengers.all())
    has_predefined_passengers = bool(predefined_passengers)

    print(f"Predefined passengers: {has_predefined_passengers} ({len(predefined_passengers)} passengers)")

    for i, detail in enumerate(booking_details):
        passenger = detail.passenger
        passenger_type = (passenger.passenger_type or '').lower()

        # Count passenger types
        if passenger_type == 'adult':
            adult_count += 1
        elif passenger_type == 'child':
            child_count += 1
        elif passenger_type == 'infant':
            infant_count += 1

        passenger_score = 0.0
        passenger_deductions = []

        print(f"Evaluating passenger {i+1}: {passenger.first_name} {passenger.last_name} ({passenger_type})")

        # 1. Name completeness (40% of passenger score)
        name_score = 0.0
        if passenger.first_name and passenger.first_name.strip():
            name_score += 0.5
        else:
            passenger_deductions.append("Missing first name")

        if passenger.last_name and passenger.last_name.strip():
            name_score += 0.5
        else:
            passenger_deductions.append("Missing last name")

        passenger_score += name_score * 0.4

        # 2. Date of birth validity (30% of passenger score)
        dob_score = 0.0
        if passenger.date_of_birth:
            today = timezone.now().date()
            age = today.year - passenger.date_of_birth.year - (
                (today.month, today.day) < (passenger.date_of_birth.month, passenger.date_of_birth.day)
            )

            if 0 <= age <= 120:  # Reasonable age range
                dob_score = 1.0
            else:
                dob_score = 0.5
                passenger_deductions.append(f"Unrealistic age: {age} years")
        else:
            passenger_deductions.append("Missing date of birth")

        passenger_score += dob_score * 0.3

        # 3. Gender information (20% of passenger score)
        gender_score = 1.0 if passenger.gender and passenger.gender.strip() else 0.0
        if not gender_score:
            passenger_deductions.append("Missing gender")
        passenger_score += gender_score * 0.2

        # 4. Passport information (10% of passenger score)
        passport_score = 1.0
        passport_deductions = []

        # Predefined passport logic if present
        predefined_passport = None
        if has_predefined_passengers and i < len(predefined_passengers):
            predefined_passenger = predefined_passengers[i]
            predefined_passport = (
                predefined_passenger.passport_number.strip()
                if predefined_passenger.passport_number
                else None
            )

            print(f"  Predefined passenger: {predefined_passenger.first_name} {predefined_passenger.last_name}")
            print(f"  Predefined passport: {predefined_passport}")

        if predefined_passport and predefined_passport.lower() not in ["none", ""]:
            # Predefined requires exact match
            if passenger.passport_number and passenger.passport_number.strip():
                if passenger.passport_number.strip() == predefined_passport:
                    passport_score = 1.0
                    print(f"  ✅ Passport matches predefined: {passenger.passport_number}")
                else:
                    passport_score = 0.0
                    passport_deductions.append(f"Passport mismatch (expected {predefined_passport})")
            else:
                passport_score = 0.0
                passport_deductions.append("Missing passport (expected predefined)")
        else:
            # Normal rules
            if activity.require_passport:
                if passenger.passport_number and len(passenger.passport_number.strip()) >= 5:
                    passport_score = 1.0
                    print(f"  ✅ Valid passport: {passenger.passport_number}")
                else:
                    passport_score = 0.0
                    passport_deductions.append("Missing required passport")
            else:
                origin_airport = Airport.objects.filter(code=activity.required_origin).first()
                dest_airport = Airport.objects.filter(code=activity.required_destination).first()

                if origin_airport and dest_airport:
                    if (origin_airport.airport_type == 'international' or
                        dest_airport.airport_type == 'international'):
                        if passenger.passport_number and passenger.passport_number.strip():
                            passport_score = 1.0
                        else:
                            passport_score = 0.0
                            passport_deductions.append("Missing passport for international flight")
                # If no special requirements, full points
                passport_score = 1.0

        passenger_score += passport_score * 0.1
        if passport_deductions:
            passenger_deductions.extend(passport_deductions)

        # Store individual passenger score
        total_score += passenger_score

        print(f"  Passenger score: {passenger_score:.2f}")
        if passenger_deductions:
            print(f"  Deductions: {', '.join(passenger_deductions)}")
        print()

    # Calculate average score across all passengers
    average_score = total_score / total_passengers

    # SECOND: Check if passenger types match requirements
    type_penalty = 0.0
    if adult_count != activity.required_passengers:
        type_penalty += 0.1
        print(f"❌ Adult count mismatch: required {activity.required_passengers}, got {adult_count}")
    if child_count != activity.required_children:
        type_penalty += 0.1
        print(f"❌ Child count mismatch: required {activity.required_children}, got {child_count}")
    if infant_count != activity.required_infants:
        type_penalty += 0.1
        print(f"❌ Infant count mismatch: required {activity.required_infants}, got {infant_count}")

    # Apply penalties and clamp
    final_score = average_score * (1 - count_penalty - type_penalty)
    final_score = max(0.0, min(final_score, 1.0))

    print(f"Raw passenger information quality: {average_score:.2f}")
    print(f"Count penalty: {count_penalty:.2f}")
    print(f"Type penalty: {type_penalty:.2f}")
    print(f"Final passenger information quality: {final_score:.2f}")
    print("=======================================")

    return final_score, warning_message


def evaluate_flight_route_compliance(booking, activity):
    """Evaluate if the flight route matches activity requirements"""
    score = 1.0  # Start with perfect score

    # Get the first booking detail to check route (ensure ordering doesn't affect)
    first_detail = booking.details.order_by('id').first()
    if not first_detail:
        return 0.0

    route = first_detail.schedule.flight.route

    # Check origin
    if hasattr(activity, 'required_origin') and activity.required_origin:
        if route.origin_airport.code != activity.required_origin:
            score -= 0.5  # Lose 50% for wrong origin
            print(f"❌ Origin mismatch: required {activity.required_origin}, got {route.origin_airport.code}")
        else:
            print(f"✅ Origin match: {activity.required_origin}")

    # Check destination  
    if hasattr(activity, 'required_destination') and activity.required_destination:
        if route.destination_airport.code != activity.required_destination:
            score -= 0.5  # Lose 50% for wrong destination
            print(f"❌ Destination mismatch: required {activity.required_destination}, got {route.destination_airport.code}")
        else:
            print(f"✅ Destination match: {activity.required_destination}")

    return max(score, 0.0)  # Ensure score doesn't go below 0


def evaluate_correct_passenger_details(activity, booking_details, penalty_extra_multiplier=0.5):
    """
    Compare booking_details (as returned by get_booking_details) against
    ActivityPassenger records (activity.passengers.all()).

    Returns a dict:
    {
      'details': [ ... ],
      'matched_points': float,
      'penalty_points': float,
      'possible_points': float,
      'accuracy_score': float (0..1),
      'warnings': [ ... ]
    }

    penalty_extra_multiplier: fraction of one passenger's possible points to deduct per missing/extra passenger.
    """
    print("=== EVALUATE CORRECT PASSENGER DETAILS ===")

    expected_qs = list(activity.passengers.all())  # ActivityPassenger instances in order
    student_passengers = list(booking_details.get('passengers', []))  # list of dicts

    # If get_booking_details included passenger_id, sort to be safe
    try:
        student_passengers = sorted(student_passengers, key=lambda p: int(p.get('passenger_id', 0)))
    except Exception:
        # fallback: keep current order
        pass

    # Field weights (points)
    field_weights = {
        'first_name': 1,
        'middle_name': 1,
        'last_name': 1,
        'passenger_type': 1,
        'gender': 1,
        'date_of_birth': 1,
        'nationality': 1,
        'passport': 3,
    }
    passenger_possible = sum(field_weights.values())  # e.g., 12

    details = []
    matched_points = 0.0
    penalty_points = 0.0
    warnings = []

    expected_count = len(expected_qs)
    student_count = len(student_passengers)

    print(f"Expected passengers: {expected_count}, Student passengers: {student_count}")

    # Compare expected vs student by index (order matters)
    for idx, expected in enumerate(expected_qs):
        # Build expected dict
        expected_dict = {
            'first_name': expected.first_name or '',
            'middle_name': expected.middle_name or '',
            'last_name': expected.last_name or '',
            'passenger_type': expected.passenger_type or '',
            'gender': expected.gender or '',
            'date_of_birth': str(expected.date_of_birth) if expected.date_of_birth else '',
            'nationality': expected.nationality or '',
            'passport': expected.passport_number or '',
        }

        # Student dict (may be missing)
        student = student_passengers[idx] if idx < student_count else {}
        student_dict = {
            'first_name': student.get('first_name', '') if student else '',
            'middle_name': student.get('middle_name', '') if student else '',
            'last_name': student.get('last_name', '') if student else '',
            'passenger_type': student.get('type', '') if student else '',
            'gender': student.get('gender', '') if student else '',
            'date_of_birth': str(student.get('date_of_birth') or '') if student else '',
            'nationality': student.get('nationality', '') if student else '',
            'passport': student.get('passport', '') if student else '',
        }

        field_results = {}
        passenger_score = 0.0

        for field, pts in field_weights.items():
            expected_val = str(expected_dict.get(field) or '').strip().lower()
            student_val = str(student_dict.get(field) or '').strip().lower()

            is_correct = (expected_val == student_val and expected_val != '')
            # Special handling: date_of_birth may be comparable even if formats differ
            if field == 'date_of_birth':
                is_correct = (expected_val == student_val and expected_val != '')

            if is_correct:
                passenger_score += pts
                field_results[field] = {'student': student_dict.get(field), 'expected': expected_dict.get(field), 'is_correct': True, 'points': pts}
            else:
                field_results[field] = {'student': student_dict.get(field), 'expected': expected_dict.get(field), 'is_correct': False, 'points': 0}

        matched_points += passenger_score

        details.append({
            'index': idx,
            'expected': expected_dict,
            'student': student_dict,
            'field_results': field_results,
            'score': passenger_score,
            'possible': passenger_possible
        })

        print(f"Passenger {idx+1} score: {passenger_score}/{passenger_possible}")

    # Missing student passengers -> penalty
    if student_count < expected_count:
        missing = expected_count - student_count
        penalty_for_missing = missing * passenger_possible * penalty_extra_multiplier
        penalty_points += penalty_for_missing
        msg = f"Penalty for {missing} missing passenger(s): {penalty_for_missing} points."
        warnings.append(msg)
        print(msg)

    # Extra student passengers -> penalty (already existed)
    if student_count > expected_count:
        extra = student_count - expected_count
        penalty_for_extra = extra * passenger_possible * penalty_extra_multiplier
        penalty_points += penalty_for_extra
        msg = f"Penalty for {extra} extra passenger(s): {penalty_for_extra} points."
        warnings.append(msg)
        print(msg)

    possible_points = expected_count * passenger_possible
    effective_points = max(0.0, matched_points - penalty_points)

    accuracy_score = (effective_points / possible_points) if possible_points > 0 else 0.0
    accuracy_score = max(0.0, min(accuracy_score, 1.0))

    print(f"Matched points: {matched_points}, Penalty: {penalty_points}, Possible: {possible_points}, Accuracy score: {accuracy_score:.3f}")

    return {
        'details': details,
        'matched_points': float(matched_points),
        'penalty_points': float(penalty_points),
        'possible_points': float(possible_points),
        'accuracy_score': float(accuracy_score),
        'warnings': warnings
    }


def get_booking_details(booking):
    """Get detailed information about what was actually booked"""
    print(f"=== GET_BOOKING_DETAILS DEBUG ===")
    print(f"Booking ID: {booking.id}")

    booking_details = booking.details.order_by('id').select_related(
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
            'passenger_id': detail.passenger.id,  # new field to preserve ordering downstream
            'first_name': detail.passenger.first_name,
            'middle_name': detail.passenger.middle_name,
            'last_name': detail.passenger.last_name,
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

        # Prevent duplicates — compare by first+last (safe because ActivityPassenger ordering is controlled)
        identifier = f"{passenger_info['first_name']}_{passenger_info['last_name']}"
        if not any(f"{p.get('first_name')}_{p.get('last_name')}" == identifier for p in details['passengers']):
            details['passengers'].append(passenger_info)

    print(f"Final passengers count: {len(details['passengers'])}")
    print(f"Final flights count: {len(details['flights'])}")
    print("=== END GET_BOOKING_DETAILS ===")

    return details


def get_detailed_comparison(activity, booking, booking_details, submission=None):
    """
    Compare activity requirements and student booking; returns a rich dict including
    passenger accuracy details and score_breakdown. This function now integrates
    evaluate_correct_passenger_details() so accuracy impacts scoring.
    """
    # Initialize counts
    adult_count = 0
    child_count = 0
    infant_count = 0
    total_price = booking_details.get('total_cost', 0)

    # Count passenger types from booking_details
    for passenger in booking_details.get('passengers', []):
        passenger_type = passenger.get('type', '').lower()
        if passenger_type == 'adult':
            adult_count += 1
        elif passenger_type == 'child':
            child_count += 1
        elif passenger_type == 'infant':
            infant_count += 1

    # Check travel class compliance
    seat_classes_used = booking_details.get('seat_classes_used', [])
    seat_class_names = [seat_class.name.lower() for seat_class in seat_classes_used if seat_class]
    has_correct_class = any(
        seat_class_name == activity.required_travel_class.lower()
        for seat_class_name in seat_class_names
    )

    actual_classes = ", ".join([seat_class.name for seat_class in seat_classes_used]) if seat_classes_used else "Not specified"

    # Trip type submitted
    submitted_trip_type = getattr(booking, 'trip_type', 'Not specified')

    # Extract booked origin/destination from flight groups if available
    origin_match = True
    destination_match = True
    booked_origin = None
    booked_destination = None

    if booking_details.get('flights'):
        first_flight = next(iter(booking_details['flights'].values()), None)
        if first_flight:
            booked_origin = first_flight['schedule'].flight.route.origin_airport
            booked_destination = first_flight['schedule'].flight.route.destination_airport

            if hasattr(activity, 'required_origin') and activity.required_origin:
                origin_match = booked_origin.code == activity.required_origin
            if hasattr(activity, 'required_destination') and activity.required_destination:
                destination_match = booked_destination.code == activity.required_destination

    # Evaluate passenger information quality (completeness) -> unpack (score, warning)
    passenger_info_quality_score, passenger_info_warning = evaluate_passenger_information_quality(booking, activity)

    # Evaluate correctness vs expected activity passengers
    passenger_accuracy = evaluate_correct_passenger_details(activity, booking_details)
    passenger_accuracy_score = passenger_accuracy.get('accuracy_score', 0.0)
    passenger_accuracy_warnings = passenger_accuracy.get('warnings', [])

    # Combine quality + accuracy into a single passenger info score (so we don't change top-level weights)
    passenger_info_score = (passenger_info_quality_score + passenger_accuracy_score) / 2.0

    # Build passenger comparison summary
    passenger_comparison = {
        'required_adults': activity.required_passengers,
        'submitted_adults': adult_count,
        'required_children': activity.required_children,
        'submitted_children': child_count,
        'required_infants': activity.required_infants,
        'submitted_infants': infant_count,
        'adults_match': adult_count == activity.required_passengers,
        'children_match': child_count == activity.required_children,
        'infants_match': infant_count == activity.required_infants,
        'information_quality_score': passenger_info_quality_score,
        'information_quality_percentage': passenger_info_quality_score * 100,
        # include accuracy details
        'accuracy_score': passenger_accuracy_score,
        'accuracy_percentage': passenger_accuracy_score * 100,
        'accuracy_details': passenger_accuracy.get('details', []),
        'warnings': ([passenger_info_warning] if passenger_info_warning else []) + passenger_accuracy_warnings
    }

    # Price comparison (kept simple)
    price_comparison = {
        'submitted_total': total_price,
        'within_budget': True,
        'overage': 0,
    }

    # Flight comparison details
    flight_comparison = {
        'required_trip_type': activity.required_trip_type,
        'submitted_trip_type': submitted_trip_type,
        'trip_type_match': submitted_trip_type == activity.required_trip_type,
        'required_travel_class': activity.required_travel_class,
        'actual_travel_classes': actual_classes,
        'has_correct_class': has_correct_class,
        'required_origin': getattr(activity, 'required_origin', None),
        'required_destination': getattr(activity, 'required_destination', None),
        'booked_origin': booked_origin.code if booked_origin else 'Not specified',
        'booked_destination': booked_destination.code if booked_destination else 'Not specified',
        'origin_match': origin_match,
        'destination_match': destination_match,
    }

    # Score breakdown using your verified weights
    total_points = float(activity.total_points)

    base_weight = 0.10              # 10% - Completion
    passenger_info_weight = 0.40    # 40% - Passenger information quality 
    flight_route_weight = 0.10      # 10% - Flight route compliance
    trip_type_weight = 0.10         # 10% - Trip type compliance
    travel_class_weight = 0.10      # 10% - Travel class compliance
    passenger_count_weight = 0.15   # 15% - Passenger count compliance
    addon_weight = 0.05             # 5% - Add-ons

    # Base points
    base_points = total_points * base_weight

    # Passenger info points — now use combined passenger_info_score
    passenger_info_points = total_points * passenger_info_weight * passenger_info_score

    # Flight route points
    flight_route_score = 1.0 if (origin_match and destination_match) else 0.0
    flight_route_points = total_points * flight_route_weight * flight_route_score

    # Trip type
    trip_type_match = 1.0 if booking.trip_type == activity.required_trip_type else 0.0
    trip_type_points = total_points * trip_type_weight * trip_type_match

    # Travel class
    travel_class_match = 1.0 if has_correct_class else 0.0
    travel_class_points = total_points * travel_class_weight * travel_class_match

    # Passenger count points (original weighted match)
    passenger_match = 0
    if adult_count == activity.required_passengers:
        passenger_match += 0.5
    if child_count == activity.required_children:
        passenger_match += 0.3
    if infant_count == activity.required_infants:
        passenger_match += 0.2
    passenger_points = total_points * passenger_count_weight * passenger_match

    # Add-on points
    addon_points = float(submission.addon_score) if submission and getattr(submission, 'addon_score', None) else 0.0

    # Total earned
    total_earned = (
        base_points +
        passenger_info_points +
        flight_route_points +
        trip_type_points +
        travel_class_points +
        passenger_points +
        addon_points
    )

    # Build score_breakdown
    score_breakdown = {
        'base_points': float(base_points),
        'passenger_info_points': float(passenger_info_points),
        'flight_route_points': float(flight_route_points),
        'trip_type_points': float(trip_type_points),
        'travel_class_points': float(travel_class_points),
        'passenger_points': float(passenger_points),
        'addon_points': float(addon_points),
        'total_earned': float(total_earned),
        'total_possible': float(total_points),
        # extras for template/diagnostics
        'matched_passenger_points': passenger_accuracy.get('matched_points', 0.0),
        'passenger_accuracy_penalty': passenger_accuracy.get('penalty_points', 0.0),
        'passenger_accuracy_possible': passenger_accuracy.get('possible_points', 0.0),
        'passenger_accuracy_score': passenger_accuracy.get('accuracy_score', 0.0),
    }

    # Build requirements, deductions, recommendations as before (kept intact)
    requirements = []
    deductions = []
    recommendations = []

    # Trip Type requirement
    requirements.append({
        'category': 'Trip Type',
        'requirement': f'{activity.required_trip_type.title()} Trip',
        'student_work': f'{booking.trip_type.title()} Trip',
        'met': booking.trip_type == activity.required_trip_type,
        'icon': '✓' if booking.trip_type == activity.required_trip_type else '✗',
        'weight': 'High'
    })

    # Passenger counts
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

    requirements.append({
        'category': 'Travel Class',
        'requirement': f'{activity.required_travel_class.title()} Class',
        'student_work': actual_classes,
        'met': has_correct_class,
        'icon': '✓' if has_correct_class else '✗',
        'weight': 'High'
    })

    # Passenger Information
    requirements.append({
        'category': 'Passenger Information',
        'requirement': 'Complete passenger details',
        'student_work': f'{passenger_info_quality_score * 100:.1f}% complete',
        'met': passenger_info_quality_score >= 0.8,
        'icon': '✓' if passenger_info_quality_score >= 0.8 else '⚠',
        'weight': 'Medium',
        'details': 'Includes names, dates of birth, gender, and passport as required'
    })

    # Origin / destination requirements
    if hasattr(activity, 'required_origin') and activity.required_origin:
        requirements.append({
            'category': 'Flight Route',
            'requirement': f'Depart from {activity.required_origin}',
            'student_work': f'Depart from {booked_origin.code if booked_origin else "Not specified"}',
            'met': origin_match,
            'icon': '✓' if origin_match else '✗',
            'weight': 'Medium'
        })
    if hasattr(activity, 'required_destination') and activity.required_destination:
        requirements.append({
            'category': 'Flight Route',
            'requirement': f'Arrive at {activity.required_destination}',
            'student_work': f'Arrive at {booked_destination.code if booked_destination else "Not specified"}',
            'met': destination_match,
            'icon': '✓' if destination_match else '✗',
            'weight': 'Medium'
        })

    if passenger_info_quality_score < 0.8:
        recommendations.append("Ensure all passenger details are complete including names, dates of birth, gender, and contact information")

    if passenger_info_quality_score < 0.5:
        deductions.append({
            'category': 'Passenger Information',
            'issue': 'Incomplete passenger details',
            'details': f'Passenger information quality score: {passenger_info_quality_score * 100:.1f}%',
            'points_lost': f'Up to {total_points * passenger_info_weight * (1 - passenger_info_quality_score):.1f} points',
            'type': 'passenger_info'
        })

    return {
        'passenger_comparison': passenger_comparison,
        'price_comparison': price_comparison,
        'flight_comparison': flight_comparison,
        'requirements': requirements,
        'deductions': deductions,
        'recommendations': recommendations,
        'score_breakdown': score_breakdown,
    }


# Add missing function that's referenced in calculate_activity_score
def evaluate_passport_compliance(booking, activity):
    """Evaluate passport compliance for all passengers"""
    booking_details = booking.details.order_by('id')
    total_passengers = len(booking_details)

    if total_passengers == 0:
        return 0.0

    compliant_passengers = 0
    for detail in booking_details:
        passenger = detail.passenger
        if passenger.passport_number and passenger.passport_number.strip():
            compliant_passengers += 1

    return compliant_passengers / total_passengers
