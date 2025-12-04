
# instructorapp/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from decimal import Decimal
from instructorapp.models import ActivitySubmission
from instructorapp.utils_grading import get_booking_details, get_detailed_comparison
from django.shortcuts import render

@require_GET
def grade_all_submissions(request, activity_id):
    submissions = ActivitySubmission.objects.filter(activity_id=activity_id)
    all_results = []

    def safe_float(v, default=0.0):
        try:
            return float(v)
        except Exception:
            return default

    for submission in submissions:
        result = {
            "activity_id": activity_id,
            "submission_id": submission.id,
            "student_id": submission.student_id,
            "student_name": f"{submission.student.first_name} {submission.student.last_name}"
                            if hasattr(submission, 'student') else "",
            "submitted_at": submission.submitted_at.isoformat() if getattr(submission, 'submitted_at', None) else None,
            "points": {},
            "details": {},
            "comparison": {},
            "passenger_details": [],
            "correct_passenger_details": [],
            "final_score": 0.0,
            "compliance_percentage": 0.0,
        }

        booking = getattr(submission, 'booking', None)
        if not booking:
            result["details"]["error"] = "No booking attached to submission."
            submission.score = 0.0
            submission.save()
            all_results.append(result)
            continue

        try:
            booking_details = get_booking_details(booking)
            comparison = get_detailed_comparison(
                activity=submission.activity,
                booking=booking,
                booking_details=booking_details,
                submission=submission
            )
        except Exception as e:
            result["details"]["error"] = f"Error computing score: {str(e)}"
            submission.score = 0.0
            submission.save()
            all_results.append(result)
            continue

        result['comparison'] = comparison

        # STUDENT passenger details (as provided in booking)
        result['passenger_details'] = sorted([
            {
                "full_name": " ".join(filter(None, [
                    p.get("first_name", ""),
                    p.get("middle_name", ""),
                    p.get("last_name", "")
                ])),
                "type": p.get("type", ""),
                "date_of_birth": str(p.get("date_of_birth") or ""),
                "gender": p.get("gender", ""),
                "passport": p.get("passport", ""),
                "nationality": p.get("nationality", ""),
                "flights": [
                    {
                        "route": f.get("route", ""),
                        "date": str(f.get("date") or ""),
                        "seat_class": getattr(f.get("seat_class"), 'name', f.get("seat_class")),
                        "seat_number": f.get("seat_number", ""),
                        "price": float(f.get("price") or 0.0),
                    } for f in p.get("flights", [])
                ],
            } for p in booking_details.get("passengers", [])
        ], key=lambda x: x["full_name"])  # <── FIX: ASCENDING by full_name



        # Build correct_passenger_details (field-by-field) from comparison['passenger_comparison']['accuracy_details']
        accuracy_details = comparison.get('passenger_comparison', {}).get('accuracy_details', [])
        correct_pass_list = []
        for det in accuracy_details:
            # each det from utils.evaluate_correct_passenger_details() contains 'expected', 'student', 'field_results', 'score', 'possible'
            field_results = det.get('field_results', {})
            # Transform into frontend-friendly structure
            front_fields = {}
            for field, fr in field_results.items():
                front_fields[field] = {
                    "student": fr.get('student'),
                    "correct": fr.get('expected'),
                    "is_correct": fr.get('is_correct'),
                    "points": fr.get('points')
                }

            # --- ADD FULL NAME (student + expected) ---
            # Combine FIRST + MIDDLE + LAST into one field
            first = field_results.get("first_name", {}).get("student", "")
            middle = field_results.get("middle_name", {}).get("student", "")
            last = field_results.get("last_name", {}).get("student", "")

            correct_first = field_results.get("first_name", {}).get("expected", "")
            correct_middle = field_results.get("middle_name", {}).get("expected", "")
            correct_last = field_results.get("last_name", {}).get("expected", "")

            front_fields["full_name"] = {
                "student": " ".join(filter(None, [first, middle, last])),
                "correct": " ".join(filter(None, [correct_first, correct_middle, correct_last])),
                "is_correct":
                    field_results.get("first_name", {}).get("is_correct") and
                    field_results.get("middle_name", {}).get("is_correct") and
                    field_results.get("last_name", {}).get("is_correct"),
                "points": (
                    (field_results.get("first_name", {}).get("points") or 0) +
                    (field_results.get("middle_name", {}).get("points") or 0) +
                    (field_results.get("last_name", {}).get("points") or 0)
                )
            }

            correct_pass_list.append({
                "index": det.get('index'),
                "fields": front_fields,
                "score": det.get('score'),
                "possible": det.get('possible')
            })

        result['correct_passenger_details'] = sorted(correct_pass_list, key=lambda x: x["index"])

        # Compute final score from comparison['score_breakdown']
        score_breakdown = comparison.get('score_breakdown', {})
        total_earned = safe_float(score_breakdown.get('total_earned'))
        if not total_earned:
            # fallback sum
            total_earned = sum(v for k, v in score_breakdown.items() if k.endswith('_points') and isinstance(v, (int, float)))

        # Save final score on submission
        result["final_score"] = total_earned
        submission.score = round(total_earned, 2)
        submission.save()

        # Compliance percentage
        total_possible = safe_float(score_breakdown.get('total_possible', 100))
        result['compliance_percentage'] = min(total_earned / total_possible * 100, 100.0) if total_possible > 0 else 0.0

        all_results.append(result)

    return JsonResponse({"submissions": all_results}, safe=True)

def item_analysis(request):
    return render(request, 'instructorapp/instructor/itemAnalysis/index.html')
