"""
Activity Code Validation Endpoint

This endpoint validates an activity code before allowing a student to proceed with booking.
It checks:
1. Activity code exists and is active
2. Student is enrolled in the activity's section
3. Returns activity details if valid
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from fbs_instructor.models import Activity, SectionEnrollment
from app.models import Students


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_activity_code(request):
    """
    Validate an activity code for the authenticated student
    
    POST /api/bookings/validate-activity-code/
    Body: {"activity_code": "ABC12345"}
    
    Returns:
        - 200: Activity details if valid
        - 400: Invalid code or student not enrolled
    """
    activity_code = request.data.get('activity_code', '').strip().upper()
    
    if not activity_code:
        return Response({
            'success': False,
            'error': 'Activity code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find activity by code
        activity = Activity.objects.get(
            activity_code=activity_code,
            is_code_active=True
        )
    except Activity.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid or inactive activity code'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if activity is overdue
    if activity.due_date and activity.due_date < timezone.now():
        # Only block if student hasn't submitted yet
        return Response({
            'success': False,
            'error': 'The deadline for this activity has passed. You can no longer participate.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get student record
    try:
        student = Students.objects.get(user=request.user)
    except Students.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Student record not found'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if student is enrolled in the section
    is_enrolled = SectionEnrollment.objects.filter(
        student=student,
        section=activity.section,
        is_active=True
    ).exists()
    
    if not is_enrolled:
        return Response({
            'success': False,
            'error': 'You are not enrolled in the section for this activity'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # NEW: Log to InstructorLog that student started activity
    from fbs_instructor.views import log_instructor_event
    log_instructor_event(
        request,
        action_type='ACTIVITY_TAKEN',
        student=student,
        section_name=activity.section.section_name,
        activity_name=activity.title,
        details=f"Student {student.student_number} started activity '{activity.title}'."
    )

    # Return activity details
    return Response({
        'success': True,
        'activity': {
            'id': activity.id,
            'title': activity.title,
            'description': activity.description,
            'activity_code': activity.activity_code,
            'total_points': float(activity.total_points),
            'due_date': activity.due_date.isoformat() if activity.due_date else None,
            'requirements': {
                'trip_type': activity.required_trip_type,
                'origin': activity.required_origin,
                'destination': activity.required_destination,
                'travel_class': activity.required_travel_class,
                'seat_class': activity.required_seat_class if hasattr(activity, 'required_seat_class') else "",
                'passengers': activity.required_passengers,
            },
            'activity_addons': [
                {
                    "id": aa.id,
                    "addon_id": aa.addon_id if hasattr(aa, 'addon_id') else aa.addon.id,
                    "addon_name": aa.addon.name,
                    "passenger": {
                        "id": aa.passenger_id if hasattr(aa, 'passenger_id') else aa.passenger.id,
                        "first_name": aa.passenger.first_name,
                        "last_name": aa.passenger.last_name
                    }
                }
                for aa in activity.activity_addons.all()
            ],
            'section': {
                'code': activity.section.section_code,
                'name': activity.section.section_name
            }
        }
    }, status=status.HTTP_200_OK)
