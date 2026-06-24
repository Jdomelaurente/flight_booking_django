from django.utils import timezone
from app.models import Booking, BookingDetail, Students
from fbs_instructor.models import Activity, ActivityStudentBinding
import logging
import json
import math

logger = logging.getLogger(__name__)

def grade_booking(booking, activity_id):
    """
    Validates a booking against an activity's requirements and updates the student's grade.
    Now generates a semantic rubric_breakdown for UI display.
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

        # 1. Rubric Logic (Matches Frontend categories for consistency)
        # We group points into 5 major categories (20% each)
        rubric_breakdown = [
            {"label": "Accuracy of Booking", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []},
            {"label": "Technical Skill", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []},
            {"label": "Organization of Steps", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []},
            {"label": "Completeness", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []},
            {"label": "Professionalism", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []}
        ]

        # Helper to get category by keyword
        def get_cat(key):
            for cat in rubric_breakdown:
                if key.lower() in cat["label"].lower(): return cat
            return rubric_breakdown[0]

        # 2. Extract Data
        details = booking.details.all()
        all_schedules = []
        seen_schedule_ids = set()
        for d in details:
            if d.schedule_id not in seen_schedule_ids:
                all_schedules.append(d.schedule)
                seen_schedule_ids.add(d.schedule_id)
        all_schedules.sort(key=lambda s: s.departure_time)

        # --- MATCHING HELPERS ---
        def norm_str(s):
            return (str(s) or "").lower().strip()
        
        def match_exact(req, actual):
            if not req: return True
            return norm_str(req) == norm_str(actual)
            
        def normalize_addon_name(name):
            import re
            n = norm_str(name)
            n = re.sub(r'^assistance:\s*', '', n)
            n = re.sub(r'^assistance service:\s*', '', n)
            n = re.sub(r'^meal:\s*', '', n)
            n = re.sub(r'^extra baggage\s*', '', n)
            n = re.sub(r'extra baggage', 'baggage', n)
            n = re.sub(r'\s*(kg|kgs)([\s_-])', 'kg ', n)
            return n.strip()

        # 1. ACCURACY OF BOOKING (Trip Type, Origin, Destination, Class, Dates)
        acc = get_cat("Accuracy")
        acc_criteria = []
        is_tt_met = match_exact(activity.required_trip_type, booking.trip_type)
        acc_criteria.append({"label": "Trip Type", "isMet": is_tt_met})
        
        outbound_detail = details.filter(schedule=all_schedules[0]).first() if all_schedules else None
        booked_class = norm_str(outbound_detail.seat_class.name if outbound_detail and outbound_detail.seat_class else "")
        req_class = norm_str(activity.required_travel_class).replace('_', '')
        # Travel Class Uses Includes in frontend:
        is_class_met = req_class in booked_class or booked_class in req_class or not req_class
        acc_criteria.append({"label": "Travel Class", "isMet": is_class_met})

        if not all_schedules:
            acc_criteria.append({"label": "Flight Booked", "isMet": False})
        else:
            if activity.required_trip_type == 'multi_city':
                req_segs = activity.segments.all().order_by('order')
                for i, rs in enumerate(req_segs):
                    if i < len(all_schedules):
                        bs = all_schedules[i]
                        o_met = match_exact(rs.origin, bs.flight.route.origin_airport.code)
                        d_met = match_exact(rs.destination, bs.flight.route.destination_airport.code)
                        date_met = not rs.departure_date or rs.departure_date == bs.departure_time.date()
                        acc_criteria.append({"label": f"Leg {i+1} Route", "isMet": o_met and d_met})
                        acc_criteria.append({"label": f"Leg {i+1} Date", "isMet": date_met})
                    else:
                        acc_criteria.append({"label": f"Leg {i+1}", "isMet": False})
            else:
                out = all_schedules[0]
                o_met = match_exact(activity.required_origin, out.flight.route.origin_airport.code)
                d_met = match_exact(activity.required_destination, out.flight.route.destination_airport.code)
                acc_criteria.append({"label": "Origin", "isMet": o_met})
                acc_criteria.append({"label": "Destination", "isMet": d_met})
                
                req_dep_date = activity.required_departure_date
                date_met = not req_dep_date or req_dep_date == out.departure_time.date()
                acc_criteria.append({"label": "Departure Date", "isMet": date_met})
                
                if activity.required_trip_type == 'round_trip':
                    if len(all_schedules) >= 2:
                        ret = all_schedules[1]
                        ro_met = match_exact(activity.required_destination, ret.flight.route.origin_airport.code)
                        rd_met = match_exact(activity.required_origin, ret.flight.route.destination_airport.code)
                        acc_criteria.append({"label": "Return Route", "isMet": ro_met and rd_met})
                        
                        req_ret_date = activity.required_return_date
                        rdate_met = not req_ret_date or req_ret_date == ret.departure_time.date()
                        acc_criteria.append({"label": "Return Date", "isMet": rdate_met})
                    else:
                        acc_criteria.append({"label": "Return Flight", "isMet": False})

        acc["ratio"] = sum(1 for c in acc_criteria if c["isMet"]) / len(acc_criteria) if acc_criteria else 1.0
        acc["criteria"] = acc_criteria

        # 2. TECHNICAL SKILL (Passenger Data Integrity, Passport)
        tech = get_cat("Technical")
        tech_criteria = []
        
        booked_pax = []
        seen_p = set()
        for d in details:
            if d.passenger and d.passenger.id not in seen_p:
                booked_pax.append(d.passenger)
                seen_p.add(d.passenger.id)
        
        req_pax = activity.passengers.all()
        all_pax_integrity = True
        all_pax_passport = True
        
        for rp in req_pax:
            ap = next((p for p in booked_pax if norm_str(p.first_name) == norm_str(rp.first_name) and norm_str(p.last_name) == norm_str(rp.last_name)), None)
            if not ap:
                all_pax_integrity = False
                all_pax_passport = False
                continue
                
            # Strict integrity: EXACT matches just like Vue
            dob_met = ap.date_of_birth == rp.date_of_birth
            
            def get_frontend_gender(title, g):
                gf = norm_str(g)
                if not gf:
                    tf = norm_str(title).replace('.','')
                    if tf in ['mr','male']: return 'mr'
                    if tf in ['mrs','female']: return 'mrs'
                    if tf == 'ms': return 'ms'
                if gf in ['mr','male']: return 'mr'
                if gf in ['mrs','female']: return 'mrs'
                return gf
                
            gen_met = get_frontend_gender(ap.title, ap.gender) == get_frontend_gender('', rp.gender)
            nat_met = match_exact(rp.nationality, ap.nationality)
            
            # Passport exact
            if activity.require_passport:
                pass_met = match_exact(rp.passport_number, ap.passport_number)
                if not pass_met: all_pax_passport = False
                
            if not (dob_met and gen_met and nat_met):
                all_pax_integrity = False

        tech_criteria.append({"label": "Passenger Data Integrity", "isMet": all_pax_integrity})
        if activity.require_passport:
            tech_criteria.append({"label": "Document Validation", "isMet": all_pax_passport})

        tech["ratio"] = sum(1 for c in tech_criteria if c["isMet"]) / len(tech_criteria) if tech_criteria else 1.0
        tech["criteria"] = tech_criteria

        # 3. ORGANIZATION (Process Flow, Seating)
        org = get_cat("Organization")
        org_criteria = []
        org_criteria.append({"label": "Sequential Process Flow", "isMet": True}) # Assume True if booked
        
        # Seating: Every required passenger must have a seat on EVERY leg
        seating_met = True
        for rp in req_pax:
            # Need N legs = details per pax
            pax_details = [d for d in details if norm_str(d.passenger.first_name) == norm_str(rp.first_name) and norm_str(d.passenger.last_name) == norm_str(rp.last_name)]
            if len(pax_details) < len(all_schedules) or not pax_details:
                seating_met = False
                break
            for d in pax_details:
               # INFANT logic fallback
               if norm_str(rp.passenger_category) == 'infant' or norm_str(rp.passenger_type) == 'infant':
                   continue # INFANT is checked in frontend via associated adult. Relaxing it slightly here
               elif not d.seat_id:
                    seating_met = False
                    break

        org_criteria.append({"label": "Seating (All Legs)", "isMet": seating_met})
        org["ratio"] = sum(1 for c in org_criteria if c["isMet"]) / len(org_criteria) if org_criteria else 1.0
        org["criteria"] = org_criteria

        # 4. COMPLETENESS (Pax Counts, Granular Add-ons!)
        comp = get_cat("Completeness")
        comp_criteria = []
        
        pax_counts_met = (
            sum(1 for p in booked_pax if p.passenger_type.lower() in ('adult',)) == activity.required_passengers and
            sum(1 for p in booked_pax if p.passenger_type.lower() in ('child',)) == activity.required_children and
            sum(1 for p in booked_pax if p.passenger_type.lower() in ('infant',)) == activity.required_infants
        )
        comp_criteria.append({"label": "Passenger Counts", "isMet": pax_counts_met})

        req_addons = activity.activity_addons.all()
        if req_addons:
            for ra in req_addons:
                req_fn = norm_str(ra.passenger.first_name)
                req_ln = norm_str(ra.passenger.last_name)
                
                # Gather all addons for this pax
                pax_details = [d for d in details if norm_str(d.passenger.first_name) == req_fn and norm_str(d.passenger.last_name) == req_ln]
                all_actual_addons = []
                for d in pax_details:
                    all_actual_addons.extend(d.addons.all())
                
                # FIX: ActivityAddOn has no 'addon_name' field - use ra.addon.name directly
                try:
                    req_addon_name = ra.addon.name if ra.addon else 'Unknown Addon'
                except Exception:
                    req_addon_name = 'Unknown Addon'
                norm_req = normalize_addon_name(req_addon_name)
                req_id = ra.addon_id or (ra.addon.id if ra.addon else None)
                
                is_met = False
                for a in all_actual_addons:
                    if req_id and a.id == req_id:
                        is_met = True; break
                    norm_a = normalize_addon_name(a.name)
                    if norm_req == norm_a:
                        is_met = True; break
                    if len(norm_req) >= 3 and len(norm_a) >= 3 and (norm_req in norm_a or norm_a in norm_req):
                        is_met = True; break
                
                comp_criteria.append({"label": f"Add-on: {req_addon_name} ({ra.passenger.first_name})", "isMet": is_met})
        else:
            comp_criteria.append({"label": "Add-ons Compliance", "isMet": True})

        comp["ratio"] = sum(1 for c in comp_criteria if c["isMet"]) / len(comp_criteria) if comp_criteria else 1.0
        comp["criteria"] = comp_criteria

        # 5. PROFESSIONALISM (Time Management)
        prof = get_cat("Professionalism")
        prof_criteria = []
        is_time_failed = binding.is_failed_due_to_time
        prof_criteria.append({"label": "Time Management", "isMet": not is_time_failed})
        prof["ratio"] = 0.0 if is_time_failed else 1.0
        prof["criteria"] = prof_criteria

        # Final Score Calculation based on Rubric Levels
        grand_total_ratio = sum(c["ratio"] for c in rubric_breakdown) / 5.0
        
        # Update levels for UI based on frontend thresholds
        for cat in rubric_breakdown:
            r = cat["ratio"]
            if r == 1.0: cat["level"], cat["status"] = 5, "Excellent"
            elif r >= 0.8: cat["level"], cat["status"] = 4, "Very Good"
            elif r >= 0.5: cat["level"], cat["status"] = 3, "Satisfactory"
            elif r >= 0.2: cat["level"], cat["status"] = 2, "Needs Improvement"
            else: cat["level"], cat["status"] = 1, "Poor"

        total_score = float(activity.total_points)
        # Use math.floor(val + 0.5) to mimic Javascript's Math.round
        # Python's round() uses Banker's rounding which causes a 1 point discrepancy.
        earned_score = math.floor((total_score * grand_total_ratio) + 0.5)

        # Update Binding
        binding.grade = earned_score
        binding.rubric_breakdown = rubric_breakdown # Save the detailed JSON
        binding.status = 'graded' if grand_total_ratio > 0 else 'submitted'
        binding.submitted_at = timezone.now()
        binding.save()
        
        # Link booking
        booking.activity = activity
        booking.is_graded = True
        booking.save()
        
        logger.info(f"Graded booking {booking.id} Score: {earned_score}")
        
        return {
            "total": earned_score,
            "rubric_breakdown": rubric_breakdown
        }

    except Exception as e:
        logger.error(f"❌ Error grading booking {booking.id} for activity {activity_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

