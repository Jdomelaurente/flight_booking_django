from django.shortcuts import render, get_object_or_404
from instructorapp.models import Section

def item_analysis(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    return render(request, 'instructorapp/instructor/itemAnalysis/index.html', {'section': section})

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from instructorapp.models import Section, Activity, ActivitySubmission
from flightapp.models import Student
from instructorapp.utils_grading import get_booking_details, get_detailed_comparison

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from instructorapp.models import Section, Activity, ActivitySubmission
from flightapp.models import Student

def item_analysis_json(request, section_id):
    section = get_object_or_404(Section, id=section_id)

    # Get students in this section
    students = Student.objects.filter(section_enrollments__section=section).order_by('last_name', 'first_name')

    # Get activities for this section
    activities = Activity.objects.filter(section=section).order_by('title')

    analysis_results = []
    activity_stats = []

    # Variables for "All Activities" aggregate
    total_passing_all = 0
    total_failing_all = 0
    total_score_sum_all = 0.0
    total_submissions_all = 0

    for activity in activities:
        total_submissions = 0
        passing_count = 0
        failing_count = 0
        total_score_sum = 0.0

        for student in students:
            submission = ActivitySubmission.objects.filter(student_id=student.id, activity_id=activity.id).first()
            
            if submission:
                total_submissions += 1
                score = float(submission.score) if submission.score is not None else 0
                total_score_sum += score

                if score >= 0.7 * float(activity.total_points):
                    passing_count += 1
                else:
                    failing_count += 1
            else:
                score = None

            analysis_results.append({
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.last_name}",
                'activity_id': activity.id,
                'activity_title': activity.title,
                'submitted': bool(submission),
                'score': score
            })

        average_score = total_score_sum / total_submissions if total_submissions else 0

        # Update "All Activities" totals
        total_passing_all += passing_count
        total_failing_all += failing_count
        total_score_sum_all += total_score_sum
        total_submissions_all += total_submissions

        activity_stats.append({
        'activity_id': activity.id,
        'activity_title': activity.title,
        'total_students': students.count(),
        'total_submissions': total_submissions,
        'passing_count': passing_count,
        'failing_count': failing_count,
        'average_score': round(average_score, 2),
        'student_ids': [s.id for s in students] 
    })


    # Calculate aggregate average for all activities
    average_score_all = total_score_sum_all / total_submissions_all if total_submissions_all else 0

    aggregate_stats = {
        'total_students': students.count(),
        'total_submissions': total_submissions_all,
        'total_passing': total_passing_all,
        'total_failing': total_failing_all,
        'average_score': round(average_score_all, 2)
    }

    return JsonResponse({
        'section_id': section.id,
        'section_name': section.section_name,
        'activities': activity_stats,
        'student_results': analysis_results,
        'aggregate_stats': aggregate_stats  # <-- this contains the "All Activities" totals
    }, safe=False)
