# ============================================================================
# DJANGO IMPORTS
# ============================================================================
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
import json
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# ============================================================================
# DJANGO REST FRAMEWORK IMPORTS
# ============================================================================
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser

# ============================================================================
# PYTHON STANDARD LIBRARY
# ============================================================================
import random
import string
import threading
import traceback
import csv
import io
from datetime import datetime
from decimal import Decimal

# ============================================================================
# CROSS-APP IMPORTS (from app.models)
# ============================================================================
from app.models import AddOn, Airline, Airport, PasswordResetOTP, PasswordSetupToken, Students, UserProfile, Booking, TrackLog
from django.db.models import Count, Q

from .models import (
    Activity,
    ActivityPassenger,
    Instructor,
    Section,
    SectionEnrollment,
    ActivityStudentBinding,
    ActivityAddOn,
    ActivitySegment,
    UserSession,
    InstructorLog,
    InstructorNotificationReadStatus
)
from .serializers import LoginSerializer, UserSerializer
from .authentication import MultiSessionTokenAuthentication  # NEW: Our custom auth
from .permissions import IsInstructor  # NEW: Custom permission
from flightapp.services.grading_service import grade_booking

import traceback
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


# ==========================================
# HELPER FUNCTION: Get Client IP
# ==========================================
def get_client_ip(request):
    """Get the client's IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ==========================================
# HELPER: Enhanced Logging for Instructors
# ==========================================
def log_instructor_event(request, action_type, instructor=None, student=None, section_name=None, activity_name=None, details=None, is_csv=False, login_time=None, logout_time=None, actor=None):
    """
    Utility to record logs consistently.
    If student is provided, logs for every instructor who has this student in a section.
    """
    try:
        device = request.META.get('HTTP_USER_AGENT', 'Unknown')[:255]
        ip = get_client_ip(request)
        
        # Use provided actor, or request.user if authenticated, otherwise None
        if not actor:
            actor = request.user if request.user.is_authenticated else None

        # If it's a student action (like LOGIN/LOGOUT/ACTIVITY), find all relevant instructors
        if student and not instructor:
            target_instructors = User.objects.filter(
                sections__enrollments__student=student
            ).distinct()
            
            for inst in target_instructors:
                InstructorLog.objects.create(
                    instructor=inst,
                    actor=actor,
                    student=student,
                    action_type=action_type,
                    section_name=section_name,
                    activity_name=activity_name,
                    details=details,
                    device=device,
                    ip_address=ip,
                    is_csv=is_csv,
                    login_time=login_time,
                    logout_time=logout_time
                )
        elif instructor:
            # Action specifically for one instructor
            InstructorLog.objects.create(
                instructor=instructor,
                actor=actor,
                student=student,
                action_type=action_type,
                section_name=section_name,
                activity_name=activity_name,
                details=details,
                device=device,
                ip_address=ip,
                is_csv=is_csv,
                login_time=login_time,
                logout_time=logout_time
            )
    except Exception as e:
        # Prevent logging errors from breaking the main application logic
        print(f"⚠️ ERROR in log_instructor_event ({action_type}): {str(e)}")
        import traceback
        traceback.print_exc()


# ==========================================
# HELPER: Send Schedule Email Notification
# ==========================================
def send_schedule_email_notification(instructor, section):
    """
    Sends a professional letter-style email notification to the instructor
    when a schedule is created or updated for a section.
    """
    if not instructor.email:
        print(f"? WARNING: Instructor {instructor.username} has no email. Skipping notification.")
        return False

    try:
        # 1. Prepare Content
        # Format schedule data if it's JSON
        display_schedule = "N/A"
        local_now = timezone.localtime(timezone.now())
        current_day = local_now.strftime('%A')
        
        if section.schedule:
            try:
                raw_schedule = json.loads(section.schedule)
                if isinstance(raw_schedule, list):
                    # Find today's first schedule to keep it simple
                    today_schedules = [s for s in raw_schedule if s.get('day') == current_day]
                    
                    if today_schedules:
                        # Take the first one for simplicity
                        target_sched = today_schedules[0]
                        start_time = target_sched.get('start_time')
                        if start_time:
                            time_obj = datetime.strptime(start_time, '%H:%M')
                            display_schedule = time_obj.strftime('%I:%M %p')
                    else:
                        # Fallback to the very first schedule slot if none today
                        first_sched = raw_schedule[0]
                        start_time = first_sched.get('start_time')
                        if start_time:
                            time_obj = datetime.strptime(start_time, '%H:%M')
                            display_schedule = f"{first_sched.get('day', 'N/A')} {time_obj.strftime('%I:%M %p')}"
                else:
                    display_schedule = section.schedule
            except json.JSONDecodeError:
                display_schedule = section.schedule
        
        context = {
            'instructor_name': f"{instructor.first_name} {instructor.last_name}",
            'section_name': section.section_name,
            'section_code': section.section_code,
            'display_schedule': display_schedule,
            'dashboard_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:5173') + '/instructor/dashboard',
            'current_year': local_now.year,
            'formal_date': local_now.strftime('%B %d, %Y')
        }


        # 2. Render Templates
        html_content = render_to_string('emails/instructor_schedule_notification.html', context)
        text_content = strip_tags(html_content)

        # 3. Send Email
        subject = f"Section Schedule Notification: {section.section_name} ({section.section_code})"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [instructor.email]

        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()

        print(f"? Schedule notification sent to {instructor.email} for section {section.section_name}")
        return True

    except Exception as e:
        print(f"? ERROR sending schedule notification: {str(e)}")
        traceback.print_exc()
        return False


# ==========================================
# HELPER: Send Student Schedule Notification
# ==========================================
def send_student_schedule_notification(student, section, instructor):
    """
    Sends a professional letter-style email notification to a student
    when they are enrolled in a section or a schedule is updated.
    """
    if not student.email:
        print(f"⚠️ WARNING: Student {student.student_number} has no email. Skipping notification.")
        return False

    try:
        # 1. Prepare Content
        display_schedule = "N/A"
        if settings.USE_TZ:
            local_now = timezone.localtime(timezone.now())
        else:
            local_now = timezone.now()
        current_day = local_now.strftime('%A')
        
        if section.schedule:
            try:
                raw_schedule = json.loads(section.schedule)
                if isinstance(raw_schedule, list):
                    # Find today's first schedule to keep it simple
                    today_schedules = [s for s in raw_schedule if s.get('day') == current_day]
                    
                    if today_schedules:
                        target_sched = today_schedules[0]
                        start_time = target_sched.get('start_time')
                        if start_time:
                            time_obj = datetime.strptime(start_time, '%H:%M')
                            display_schedule = time_obj.strftime('%I:%M %p')
                    else:
                        first_sched = raw_schedule[0]
                        start_time = first_sched.get('start_time')
                        if start_time:
                            time_obj = datetime.strptime(start_time, '%H:%M')
                            display_schedule = f"{first_sched.get('day', 'N/A')} {time_obj.strftime('%I:%M %p')}"
                else:
                    display_schedule = section.schedule
            except (json.JSONDecodeError, IndexError, KeyError):
                display_schedule = section.schedule
        
        context = {
            'student_name': f"{student.first_name} {student.last_name}",
            'instructor_name': f"{instructor.first_name} {instructor.last_name}",
            'section_name': section.section_name,
            'section_code': section.section_code,
            'display_schedule': display_schedule,
            'academic_year': section.academic_year,
            'dashboard_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:5173') + '/student/dashboard',
            'current_year': local_now.year,
            'formal_date': local_now.strftime('%B %d, %Y')
        }

        # 2. Render Templates
        html_content = render_to_string('emails/student_schedule_notification.html', context)
        text_content = strip_tags(html_content)

        # 3. Send Email
        subject = f"Official Enrollment & Schedule: {section.section_name} ({section.section_code})"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [student.email]

        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()

        print(f"Schedule notification sent to student {student.email} for section {section.section_name}")
        return True

    except Exception as e:
        print(f"ERROR sending student schedule notification: {str(e)}")
        # traceback.print_exc()
        return False


def send_bulk_student_schedule_notification(section, instructor):
    """Sends schedule notification to all students enrolled in the section"""
    try:
        enrollments = SectionEnrollment.objects.filter(section=section)
        count = 0
        for enrollment in enrollments:
            if send_student_schedule_notification(enrollment.student, section, instructor):
                count += 1
        print(f"Bulk schedule notification sent to {count} students in section {section.section_name}")
        return True
    except Exception as e:
        print(f"ERROR in bulk student notification: {str(e)}")
        return False


# ==========================================
# 1. LOGIN VIEW (Multi-Session Support)
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def Login_view(request):
    """
    Enhanced login with TRUE multi-device/multi-tab support
    Each login creates a unique session with its own token
    """
    print(f"\n{'='*60}")
    print(f"? LOGIN REQUEST")
    print(f"{'='*60}")
    
    # 1. Validate Input
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        print(f"? Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2. Get the specific user who is trying to login
    user = serializer.validated_data['user']
    print(f"? User authenticated: {user.username}")

    # 3. Check Role using UserProfile
    try:
        profile = UserProfile.objects.get(user=user)
        role = profile.role or ('admin' if (user.is_superuser or user.is_staff) else None)
        if role is None:
             role = 'student' # Default fallback
        print(f"✅ Profile found: {role}")
    except UserProfile.DoesNotExist:
        if user.is_superuser or user.is_staff:
            role = 'admin'
        else:
            print(f"❌ No profile found for user: {user.username}")
            return Response({"error": "Profile not found"}, status=status.HTTP_403_FORBIDDEN)

    # 4. Create a NEW session for this login (allows multiple simultaneous logins)
    try:
        session = UserSession.objects.create(
            user=user,
            session_token=UserSession.generate_token(),
            role=role,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            is_active=True
        )
        print(f"? New session created: {session.session_token[:16]}... (Role: {session.role})")
    except Exception as e:
        print(f"? Session creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": f"Failed to create session: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 5. Determine Route based on role
    dashboard_route = '/'
    if profile.role == 'instructor':
        dashboard_route = '/instructor/dashboard'
    elif profile.role == 'student':
        dashboard_route = '/student/dashboard'
    elif profile.role in ['admin', 'lms_admin', 'flight_admin', 'superadmin']:
        dashboard_route = '/admin/dashboard'

    print(f"? Login successful - Redirecting to: {dashboard_route}")
    print(f"{'='*60}\n")

    # 6. Log the action
    TrackLog.objects.create(
        user=user,
        action=f"User Login: {user.username} ({role}) logged in."
    )

    # NEW: Log to InstructorLog
    if role == 'instructor':
        log_instructor_event(
            request, 
            action_type='LOGIN', 
            instructor=user, 
            login_time=timezone.now(),
            details=f"Instructor {user.username} logged in.",
            actor=user
        )
    elif role == 'student':
        try:
            student_obj = user.student_profile
            log_instructor_event(
                request, 
                action_type='LOGIN', 
                student=student_obj, 
                login_time=timezone.now(),
                details=f"Student {student_obj.student_number} ({user.username}) logged in.",
                actor=user
            )
        except Exception as e:
            print(f"⚠️ Could not log student login: {str(e)}")

    # 7. Return the UNIQUE session token (NOT the old DRF token)
    return Response({
        "message": "Login successful",
        "token": session.session_token,  # This is unique per login
        "session_id": session.id,
        "user": UserSerializer(user).data,
        "role": profile.role,
        "dashboard_route": dashboard_route
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    data = request.data
    role = data.get('role') 
    username = data.get('username')
    email = data.get('email')
    id_number = data.get('id_number')
    
    # Validation checks
    if role == 'student':
        # Admin-created student: password is optional (will send OTP email)
        if not username or not email or not id_number:
            return Response({"error": "Missing required fields (username, email, ID number)"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if not username or not email or not data.get('password') or not id_number:
            return Response({"error": "Missing required fields (username, email, password, ID number)"}, status=status.HTTP_400_BAD_REQUEST)

    existing_user_by_username = User.objects.filter(username=username).first()
    if existing_user_by_username:
        has_student_profile = Students.objects.filter(user=existing_user_by_username).exists()
        has_instructor_profile = Instructor.objects.filter(user=existing_user_by_username).exists()
        if has_student_profile or has_instructor_profile:
            return Response({"error": f"Username '{username}' is already taken."}, status=status.HTTP_400_BAD_REQUEST)
        existing_user_by_username.delete()
    
    existing_user_by_email = User.objects.filter(email=email).first()
    if existing_user_by_email:
        has_student_profile = Students.objects.filter(user=existing_user_by_email).exists()
        has_instructor_profile = Instructor.objects.filter(user=existing_user_by_email).exists()
        if has_student_profile or has_instructor_profile:
            return Response({"error": f"Email '{email}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)
        existing_user_by_email.delete()

    if role == 'student' and Students.objects.filter(student_number=id_number).exists():
        return Response({"error": f"Student ID '{id_number}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)
    
    if role == 'instructor' and Instructor.objects.filter(instructor_id=id_number).exists():
        return Response({"error": f"Instructor ID '{id_number}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # 1. Create the User (single source of truth)
            if role == 'student':
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=None,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', '')
                )
                user.set_unusable_password()
                user.save()
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', '')
                )

            # 2. Assign Role in UserProfile (auto-created by signal)
            profile = UserProfile.objects.get(user=user)
            profile.role = role
            profile.save()

            # 3. Create role-specific record
            if role == 'student':
                Students.objects.create(
                    user=user,
                    student_number=id_number,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    email=email,
                    phone_number=data.get('phone_number', ''),
                    mi=data.get('mi', ''),
                    gender=data.get('gender', ''),
                    course=data.get('course') or 'BSHM',
                    year_level=data.get('year_level') or '1',
                    password=''
                )
            elif role == 'instructor':
                Instructor.objects.create(
                    user=user,
                    instructor_id=id_number,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    email=email,
                    middle_initial=data.get('mi', '')
                )

            # 4. Log the action
            TrackLog.objects.create(
                user=user,
                action=f"User Registration: New {role} {username} registered."
            )

            # 5. Send welcome email with setup link for student accounts
            if role == 'student':
                import uuid
                token = str(uuid.uuid4()).replace('-', '') + str(uuid.uuid4()).replace('-', '')
                PasswordSetupToken.objects.create(user=user, token=token)

                setup_url = f"{settings.FRONTEND_URL}/set-password?token={token}"

                context = {
                    'name': data.get('first_name', username),
                    'setup_url': setup_url,
                    'student_number': id_number,
                    'username': username,
                    'year': timezone.now().year
                }
                html_message = render_to_string('emails/welcome_student.html', context)
                plain_message = strip_tags(html_message)

                send_mail(
                    'Welcome to CTHM Flight Booking System - Set Up Your Password',
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )

                return Response({
                    "message": "Student account created successfully! An email has been sent to the student with instructions to set up their password.",
                    "username": user.username,
                    "role": role
                }, status=status.HTTP_201_CREATED)

            return Response({
                "message": "Registration successful!",
                "username": user.username,
                "role": role
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 2. INSTRUCTOR DASHBOARD (Session-Based)
# ==========================================
@api_view(['GET', 'POST'])
@authentication_classes([MultiSessionTokenAuthentication])  # NEW: Use custom auth
@permission_classes([IsAuthenticated, IsInstructor]) 
def instructor_dashboard(request):
    user = request.user 
    session_obj = request.session_obj  # Our UserSession object
    
    print(f"\n{'='*60}")
    print(f"??? INSTRUCTOR DASHBOARD REQUEST")
    print(f"{'='*60}")
    print(f"User: {user.username} (ID: {user.id})")
    print(f"Session Token: {session_obj.session_token[:16]}...")
    print(f"Session Role: {session_obj.role}")
    print(f"Session ID: {session_obj.id}")
    
    # 1. Verification Logic - Check session role matches
    try:
        if session_obj.role != 'instructor':
            print(f"? ERROR: Session role is '{session_obj.role}', not 'instructor'")
            return Response({
                "error": "Access denied. This session is not authorized for instructor access.",
                "session_role": session_obj.role,
                "required_role": "instructor"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Double-check with UserProfile
        if not hasattr(user, 'userprofile') or user.userprofile.role != 'instructor':
            print(f"? ERROR: User profile role mismatch")
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        
        print("? Session and profile verified as instructor")
            
    except Exception as e:
        print(f"? ERROR during verification: {str(e)}")
        traceback.print_exc()
        return Response({"error": "Profile verification failed."}, status=status.HTTP_403_FORBIDDEN)

    # 2. Handling the POST (Creating a new section)
    if request.method == 'POST':
        try:
            Section.objects.create(
                section_name=request.data.get('section_name'),
                section_code=request.data.get('section_code'),
                semester=request.data.get('semester'),
                academic_year=request.data.get('academic_year'),
                schedule=request.data.get('schedule', ''),
                description=request.data.get('description', ''),
                instructor=user
            )
            print(f"? Section created: {request.data.get('section_name')}")
            
            # Log the action
            TrackLog.objects.create(
                user=user,
                action=f"Instructor Operation: Created new section '{request.data.get('section_name')}' ({request.data.get('section_code')})."
            )

            # NEW: Log to InstructorLog
            log_instructor_event(
                request,
                action_type='SECTION_CREATED',
                instructor=user,
                section_name=request.data.get('section_name'),
                details=f"Instructor created section {request.data.get('section_name')} ({request.data.get('section_code')})"
            )
                
            return Response({"message": "Section created successfully!"}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            print("? ERROR: Section code already exists")
            return Response({"error": "Section code already exists for your account."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"? ERROR creating section: {str(e)}")
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # 3. Handling the GET (Fetching data)
    sections = Section.objects.filter(instructor=user).annotate(
        student_count=Count('enrollments', distinct=True),
        activity_count=Count('activities', distinct=True)
    ).values(
        'id', 'section_name', 'section_code', 'semester', 'academic_year', 'schedule', 'description', 'is_active', 'student_count', 'activity_count'
    ).order_by('-id')

    # Add enrolled_count alias so frontend can read it as section.enrolled_count
    sections_list = []
    for s in sections:
        s['enrolled_count'] = s['student_count']
        sections_list.append(s)
    
    print(f"? Found {sections.count()} sections for instructor")
    print(f"{'='*60}\n")
    
    return Response({
        'sections': sections_list,
        'user': {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'avatar': user.userprofile.avatar.url if user.userprofile.avatar else None
        },
        'session_info': {
            'session_id': session_obj.id,
            'role': session_obj.role,
            'last_activity': session_obj.last_activity.isoformat()
        }
    }, status=status.HTTP_200_OK)


# ==========================================
# REMAINING VIEWS (All need custom auth)
# ==========================================

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def section_details(request, section_id):
    user = request.user
    
    try:
        section = Section.objects.get(id=section_id, instructor=user)
        student_count = section.enrollments.count()
        activities = Activity.objects.filter(section=section).order_by('-created_at')
        
        activities_data = []
        for activity in activities:
            total_submissions = activity.student_bindings.filter(status__in=['submitted', 'graded']).count()
            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description or '',
                'activity_type': activity.activity_type,
                'due_date': activity.due_date,
                'total_points': float(activity.total_points),
                'created_at': activity.created_at,
                'required_trip_type': activity.required_trip_type,
                'required_origin': activity.required_origin,
                'required_destination': activity.required_destination,
                'is_code_active': getattr(activity, 'is_code_active', False),
                'total_submissions': total_submissions,
            })
        
        return Response({
            'id': section.id,
            'section_name': section.section_name,
            'section_code': section.section_code,
            'semester': section.semester,
            'academic_year': section.academic_year,
            'schedule': section.schedule,
            'description': section.description,
            'is_locked': section.is_locked,
            'is_active': section.is_active,
            'created_at': section.created_at,
            'student_count': student_count,
            'activities': activities_data
        }, status=status.HTTP_200_OK)
        
    except Section.DoesNotExist:
        return Response({"error": "Section not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH', 'PUT', 'DELETE'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def update_section(request, section_id):
    user = request.user
    section = get_object_or_404(Section, id=section_id, instructor=user)
    
    if request.method == 'DELETE':
        section_name = section.section_name
        
        # LOG Section Deletion
        log_instructor_event(
            request, 
            action_type='SECTION_DELETED',
            instructor=user,
            section_name=section_name,
            details=f"Instructor deleted section '{section_name}' and all associated data."
        )
        
        section.delete()
        return Response({"message": f"Section '{section_name}' deleted successfully!"}, status=status.HTTP_200_OK)
    
    data = request.data
    
    # Update fields if they exist in the request
    if 'section_name' in data:
        section.section_name = data['section_name']
    if 'section_code' in data:
        # Check for uniqueness if code is changed
        new_code = data['section_code']
        if new_code != section.section_code:
            if Section.objects.filter(section_code=new_code, instructor=user).exists():
                return Response({"error": "Section code already exists for your account."}, status=status.HTTP_400_BAD_REQUEST)
            section.section_code = new_code
    if 'semester' in data:
        section.semester = data['semester']
    if 'academic_year' in data:
        section.academic_year = data['academic_year']
    if 'schedule' in data:
        section.schedule = data['schedule']
    if 'description' in data:
        section.description = data['description']
    if 'is_locked' in data:
        section.is_locked = data['is_locked']
    if 'is_active' in data:
        section.is_active = data['is_active']
        
    try:
        old_schedule = section.schedule
        section.save()
        
        # Trigger notification if schedule was updated or added
        new_schedule = section.schedule
        if new_schedule and new_schedule != old_schedule:
             threading.Thread(target=send_schedule_email_notification, args=(user, section)).start()
             threading.Thread(target=send_bulk_student_schedule_notification, args=(section, user)).start()

        return Response({
            "message": "Section updated successfully!",
            "section": {
                "id": section.id,
                "section_name": section.section_name,
                "section_code": section.section_code,
                "is_locked": section.is_locked,
                "is_active": section.is_active
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def delete_activity(request, section_id, activity_id):
    user = request.user
    
    try:
        section = Section.objects.get(id=section_id, instructor=user)
        activity = Activity.objects.get(id=activity_id, section=section)
        activity_title = activity.title
        
        # LOG Activity Deletion
        log_instructor_event(
            request, 
            action_type='ACTIVITY_DELETED',
            instructor=user,
            section_name=section.section_name,
            activity_name=activity_title,
            details=f"Instructor deleted activity '{activity_title}' from section '{section.section_name}'."
        )
        
        activity.delete()
        
        return Response({
            'message': f'Activity "{activity_title}" deleted successfully!'
        }, status=status.HTTP_200_OK)
        
    except Section.DoesNotExist:
        return Response({"error": "Section not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)
    except Activity.DoesNotExist:
        return Response({"error": "Activity not found in this section."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EnrollStudentView(APIView):
    authentication_classes = [MultiSessionTokenAuthentication]
    permission_classes = [IsAuthenticated, IsInstructor]
    
    def post(self, request, section_id):
        student_num = request.data.get('student_number')
        section = get_object_or_404(Section, id=section_id, instructor=request.user)
        
        if section.is_locked:
            return Response({"error": "This section is currently locked. New enrollments are not allowed."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            student = Students.objects.get(student_number=student_num)
        except Students.DoesNotExist:
            return Response({"error": "Student number not found."}, status=status.HTTP_404_NOT_FOUND)
        
        existing_enrollment = SectionEnrollment.objects.filter(student=student).first()
        
        if existing_enrollment:
            enrolled_section = existing_enrollment.section
            return Response({
                "error": f"Student {student.first_name} {student.last_name} is already enrolled in section '{enrolled_section.section_name}' ({enrolled_section.section_code}). Students can only be enrolled in one section at a time."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        enrollment, created = SectionEnrollment.objects.get_or_create(
            section=section,
            student=student
        )
        
        if not created:
            return Response({"error": "Student is already enrolled in this section."}, status=status.HTTP_400_BAD_REQUEST)
            
        log_instructor_event(
            request,
            action_type='STUDENT_ENROLLED',
            instructor=request.user,
            student=student,
            section_name=section.section_name,
            details=f"Instructor enrolled student {student.student_number} ({student.first_name} {student.last_name}) to section '{section.section_name}'."
        )
        
        # Trigger Email Notification
        threading.Thread(target=send_student_schedule_notification, args=(student, section, request.user)).start()
        
        return Response({"message": f"Successfully enrolled {student.first_name}!"}, status=status.HTTP_201_CREATED)

class UnenrollStudentView(APIView):
    authentication_classes = [MultiSessionTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, section_id, student_id):
        # 1. Verify the section belongs to the instructor
        section = get_object_or_404(Section, id=section_id, instructor=request.user)
        
        # 2. Verify the student exists and is enrolled in this section
        student = get_object_or_404(Students, id=student_id)
        enrollment = SectionEnrollment.objects.filter(section=section, student=student).first()
        
        if not enrollment:
            return Response({"error": "Student is not enrolled in this section."}, status=status.HTTP_404_NOT_FOUND)
            
        # 3. LOG Unenrollment
        log_instructor_event(
            request,
            action_type='STUDENT_UNENROLLED',
            instructor=request.user,
            student=student,
            section_name=section.section_name,
            details=f"Instructor unenrolled student {student.student_number} ({student.first_name} {student.last_name}) from section '{section.section_name}'."
        )
        
        # 4. Delete the enrollment
        enrollment.delete()
        return Response({"message": "Student successfully unenrolled."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
@parser_classes([MultiPartParser])
def bulk_enroll_students(request, section_id):
    section = get_object_or_404(Section, id=section_id, instructor=request.user)
    
    if section.is_locked:
        return Response({"error": "This section is currently locked. New enrollments are not allowed."}, status=status.HTTP_403_FORBIDDEN)
        
    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        # Read CSV
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        # Use DictReader to handle headers automatically if possible
        # We search for student number in any column that looks like it
        reader = csv.reader(io_string)
        
        headers = next(reader, None)
        if not headers:
            return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
            
        id_index = 0
        possible_headers = ['id', 'student_number', 'student id', 'id number', 'student_id']
        found_header = False
        for i, h in enumerate(headers):
            if h.lower().strip() in possible_headers:
                id_index = i
                found_header = True
                break
        
        # If no clear header found, we'll try to process the header row too as data
        # but usually CSVs have headers. I'll stick to the found index.
        
        enrolled_count = 0
        not_found_list = []
        already_enrolled_elsewhere = []
        already_in_this_section = []
        newly_enrolled_students = []
        
        # Process the rest of the rows
        rows = list(reader)
        # If we didn't find a header, maybe the 'headers' was actually data
        if not found_header:
            rows.insert(0, headers)
            id_index = 0 # Assume first column
            
        for row in rows:
            if not row or len(row) <= id_index:
                continue
                
            student_num = row[id_index].strip()
            if not student_num:
                continue
                
            try:
                student = Students.objects.get(student_number=student_num)
                
                # Check if enrolled anywhere
                existing_enrollment = SectionEnrollment.objects.filter(student=student).first()
                if existing_enrollment:
                    if existing_enrollment.section == section:
                        already_in_this_section.append(student_num)
                    else:
                        already_enrolled_elsewhere.append({
                            "id": student_num,
                            "section": existing_enrollment.section.section_name
                        })
                    continue
                    
                # Enroll
                SectionEnrollment.objects.create(section=section, student=student)
                enrolled_count += 1
                newly_enrolled_students.append(student)
                
            except Students.DoesNotExist:
                not_found_list.append(student_num)
                
        if enrolled_count > 0:
            log_instructor_event(
                request,
                action_type='STUDENT_ENROLLED',
                instructor=request.user,
                section_name=section.section_name,
                is_csv=True,
                details=f"Instructor enrolled {enrolled_count} students to section '{section.section_name}' via CSV import."
            )
            
            # Notify newly enrolled students
            for s in newly_enrolled_students:
                threading.Thread(target=send_student_schedule_notification, args=(s, section, request.user)).start()

        return Response({
            "message": f"Successfully enrolled {enrolled_count} students.",
            "enrolled_count": enrolled_count,
            "not_found": not_found_list,
            "already_enrolled": already_enrolled_elsewhere,
            "already_in_this": already_in_this_section
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        traceback.print_exc()
        return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def clear_section_enrollments(request, section_id):
    section = get_object_or_404(Section, id=section_id, instructor=request.user)
    
    enrollments = SectionEnrollment.objects.filter(section=section)
    count = enrollments.count()
    enrollments.delete()
    
    return Response({
        "message": f"Successfully cleared {count} students from this section."
    }, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def Enroll_Student_list(request, section_id):
    section = get_object_or_404(Section, id=section_id, instructor=request.user)
    enrollments = section.enrollments.all().select_related('student')
    
    student_data = [
        {
            "id": e.student.id,
            "student_number": e.student.student_number,
            "first_name": e.student.first_name,
            "last_name": e.student.last_name,
            "email": e.student.email,
            "enrolled_at": e.enrolled_at.strftime("%Y-%m-%d")
        } for e in enrollments
    ]
    
    return Response(student_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def get_available_travel_classes(request):
    """
    Returns list of available seat class names for a given route and date.
    
    Query params:
      - origin (str): origin airport code
      - destination (str): destination airport code  
      - date (str): departure date (YYYY-MM-DD)
      - segments (str, optional): JSON array of {origin, destination, departure_date}
        for multi-city — returns intersection of available classes across all legs.
    
    Falls back to all active SeatClass names if no valid route/date is provided.
    """
    from app.models import Seat, SeatClass
    import json as _json

    origin = request.GET.get('origin', '').strip().upper()
    destination = request.GET.get('destination', '').strip().upper()
    date = request.GET.get('date', '').strip()
    return_date = request.GET.get('return_date', '').strip()
    segments_raw = request.GET.get('segments', '')

    def _classes_for_leg(orig, dest, dep_date):
        """Return set of available seat class names for a single route+date."""
        try:
            seats_qs = Seat.objects.filter(
                is_available=True,
                schedule__flight__route__origin_airport__code=orig,
                schedule__flight__route__destination_airport__code=dest,
                schedule__departure_time__date=dep_date,
            ).values_list('seat_class__name', flat=True).distinct()
            return set(name for name in seats_qs if name)
        except Exception:
            return set()

    # Priority: If specific routing info is provided, we return ONLY available classes for that route.
    # If no valid route info provided at all, we return the fallback (full list).

    # 1. Multi-city: parse segments JSON
    if segments_raw:
        try:
            segments = _json.loads(segments_raw)
            if isinstance(segments, list) and len(segments) > 0:
                result_set = None
                for seg in segments:
                    o = (seg.get('origin') or '').strip().upper()
                    d = (seg.get('destination') or '').strip().upper()
                    dt = (seg.get('departure_date') or '').strip()
                    if o and d and dt:
                        leg_classes = _classes_for_leg(o, d, dt)
                        if result_set is None:
                            result_set = leg_classes
                        else:
                            result_set = result_set.intersection(leg_classes)
                
                # If we processed valid segments, return the intersection (even if empty)
                if result_set is not None:
                    return Response({'available_travel_classes': sorted(result_set)})
        except (_json.JSONDecodeError, Exception):
            pass

    # 2. Round-trip: Check BOTH outbound and inbound legs
    if origin and destination and date and return_date:
        outbound_classes = _classes_for_leg(origin, destination, date)
        # For return leg, origin and destination are swapped
        inbound_classes = _classes_for_leg(destination, origin, return_date)
        
        # Intersection: class must be available on both legs
        available = outbound_classes.intersection(inbound_classes)
        return Response({'available_travel_classes': sorted(available)})

    # 3. Single-leg (one-way)
    if origin and destination and date:
        classes = _classes_for_leg(origin, destination, date)
        return Response({'available_travel_classes': sorted(classes)})

    # FALLBACK: Return all active seat classes ONLY if no route parameters were provided.
    all_classes = list(
        SeatClass.objects.filter(is_active=True)
        .values_list('name', flat=True)
        .distinct()
        .order_by('name')
    )
    return Response({'available_travel_classes': all_classes})
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def get_available_addons(request):
    """
    Returns list of available AddOn objects for a given route and date.
    Calculated based on the Union of add-ons available for all matching flights/airlines.
    """
    from app.models import AddOn, Schedule
    import json as _json

    origin = request.GET.get('origin', '').strip().upper()
    destination = request.GET.get('destination', '').strip().upper()
    date = request.GET.get('date', '').strip()
    segments_raw = request.GET.get('segments', '')

    def _addons_for_leg(orig, dest, dep_date):
        try:
            # Find airlines operating on this route/date
            airlines = Schedule.objects.filter(
                flight__route__origin_airport__code=orig,
                flight__route__destination_airport__code=dest,
                departure_time__date=dep_date,
            ).values_list('flight__airline', flat=True).distinct()
            
            if not airlines:
                return AddOn.objects.none()
            
            return AddOn.objects.filter(airline__in=airlines).select_related('type', 'airline')
        except Exception:
            return AddOn.objects.none()

    available_addons = AddOn.objects.none()

    if segments_raw:
        try:
            segments = _json.loads(segments_raw)
            if isinstance(segments, list) and len(segments) > 0:
                for seg in segments:
                    o = (seg.get('origin') or '').strip().upper()
                    d = (seg.get('destination') or '').strip().upper()
                    dt = (seg.get('departure_date') or '').strip()
                    if o and d and dt:
                        available_addons = available_addons | _addons_for_leg(o, d, dt)
        except (_json.JSONDecodeError, Exception):
            pass
    elif origin and destination and date:
        available_addons = _addons_for_leg(origin, destination, date)

    # Fallback: all add-ons if no route provided
    if not available_addons.exists():
        available_addons = AddOn.objects.select_related('type', 'airline').all()

    return Response({
        'available_addons': [
            {
                'id': ad.id,
                'name': ad.name,
                'price': str(ad.price),
                'description': ad.description or '',
                'airline': {'code': ad.airline.code} if ad.airline else None,
                'type': {'name': ad.type.name} if ad.type else None
            }
            for ad in available_addons.distinct()
        ]
    })


@api_view(['GET', 'POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def create_activity(request, section_id):
    instructor = request.user
    section = get_object_or_404(Section, id=section_id, instructor=instructor)

    if request.method == 'GET':
        airports = Airport.objects.all().order_by('code')
        addons = AddOn.objects.select_related('type', 'airline').all()
        
        # ? NEW: Fetch all students for randomization
        from app.models import Students, SeatClass, Schedule, Seat  # Import models
        students = Students.objects.all()
        seat_classes = SeatClass.objects.filter(is_active=True).values('name').distinct()
        
        # ? NEW: Fetch valid routes (schedules with available seats) for randomization
        # We limit to upcoming schedules to keep it relevant and fast.
        now = timezone.now()
        valid_schedules = Schedule.objects.filter(
            departure_time__gte=now,
            seats__is_available=True
        ).select_related(
            'flight__route__origin_airport',
            'flight__route__destination_airport',
            'flight__airline'
        ).values(
            'flight__route__origin_airport__code',
            'flight__route__destination_airport__code',
            'departure_time',
            'flight__airline__code'
        ).distinct()[:50] # Top 50 valid routes

        valid_routes = [
            {
                'origin': s['flight__route__origin_airport__code'],
                'destination': s['flight__route__destination_airport__code'],
                'date': s['departure_time'].date().isoformat() if s['departure_time'] else None,
                'airline': s['flight__airline__code']
            }
            for s in valid_schedules
        ]

        return Response({
            'airports': [
                {'code': a.code, 'name': a.name, 'location': a.location} 
                for a in airports
            ],
            'available_addons': [
                {
                    'id': ad.id, 
                    'name': ad.name, 
                    'price': str(ad.price), 
                    'description': ad.description or '', 
                    'airline': {'code': ad.airline.code} if ad.airline else None,
                    'type': {'name': ad.type.name} if ad.type else None
                } 
                for ad in addons
            ],
            'available_travel_classes': [sc['name'] for sc in seat_classes],
            'valid_routes': valid_routes, # ✅ Send valid routes for randomization
            # ? NEW: Send students data
            'students': [
                {
                    'first_name': s.first_name,
                    'middle_name': s.mi or '',
                    'last_name': s.last_name,
                    'gender': s.gender or ''
                }
                for s in students
            ],
            'section_schedule': section.schedule or "" 
        }, status=status.HTTP_200_OK)

    if request.method == 'POST':
        data = request.data
        
        try:
            required_passengers = int(data.get('required_passengers', 1))
            required_children = int(data.get('required_children', 0))
            required_infants = int(data.get('required_infants', 0))

            if required_passengers < 1:
                return Response({"error": "At least one adult passenger is required"}, status=400)
            if required_infants > required_passengers:
                return Response({"error": "Number of infants cannot exceed number of adults"}, status=400)

            # Map SeatClass display names to model keys (case-insensitive)
            required_travel_class_raw = data.get('required_travel_class', 'economy')
            travel_class_map = {
                'economy': 'economy',
                'premium economy': 'premium_economy',
                'premium_economy': 'premium_economy',
                'business': 'business',
                'first': 'first',
                'first class': 'first',
            }
            required_travel_class = travel_class_map.get(
                (required_travel_class_raw or 'economy').lower().strip(),
                'economy'  # default fallback
            )

            # Build Add-ons Instructions
            final_instructions = data.get('instructions') or ""
            addon_instructions_lines = []
            passengers_data = data.get('passengers', [])
            
            # Only append add-ons if addon grading is enabled
            if data.get('require_addons', False):
                for p_data in passengers_data:
                    selected_addons = p_data.get('selected_addons', [])
                    if selected_addons:
                        p_name = f"{p_data.get('first_name', '')} {p_data.get('last_name', '')}".strip()
                        if not p_name:
                            p_name = f"Passenger ({p_data.get('passenger_type', 'adult')})"
                        addon_names = []
                        for addon_item in selected_addons:
                            addon_id = addon_item.get('id')
                            qty = addon_item.get('quantity', 1)
                            if addon_id:
                                try:
                                    addon_obj = AddOn.objects.get(id=addon_id)
                                    addon_names.append(f"{qty}x {addon_obj.name}")
                                except Exception:
                                    pass
                        if addon_names:
                            addon_instructions_lines.append(f"- {p_name}: {', '.join(addon_names)}")
                            
                if addon_instructions_lines:
                    if final_instructions:
                        final_instructions += "\n\n"
                    final_instructions += "Add-ons Assigned:\n" + "\n".join(addon_instructions_lines)

            with transaction.atomic():
                activity = Activity.objects.create(
                    title=data.get('title'),
                    description=data.get('description', ""),
                    activity_type=data.get('activity_type', 'Flight Booking'),
                    section=section,
                    required_trip_type=data.get('required_trip_type', 'one_way'),
                    required_origin=data.get('required_origin'),
                    required_destination=data.get('required_destination'),
                    required_departure_date=data.get('required_departure_date') or None,
                    required_return_date=data.get('required_return_date') or None,
                    required_travel_class=required_travel_class,
                    required_seat_class=data.get('required_seat_class') or '',
                    required_passengers=required_passengers,
                    required_children=required_children,
                    required_infants=required_infants,
                    require_passenger_details=data.get('require_passenger_details', False),
                    require_passport=data.get('require_passport', False),
                    instructions=final_instructions,
                    total_points=float(data.get('total_points', 100)),
                    due_date=data.get('due_date'),
                    addon_grading_enabled=data.get('require_addons', False),
                    time_limit_minutes=data.get('time_limit_minutes') or None,
                )

                # --- Handle Multi-City Segments ---
                if data.get('required_trip_type') == 'multi_city':
                    segments_data = data.get('segments', [])
                    for index, s_data in enumerate(segments_data):
                        ActivitySegment.objects.create(
                            activity=activity,
                            origin=s_data.get('origin', ''),
                            destination=s_data.get('destination', ''),
                            departure_date=s_data.get('departure_date'),
                            order=index
                        )

                passengers_data = data.get('passengers', [])
                
                for index, p_data in enumerate(passengers_data):
                    passenger = ActivityPassenger.objects.create(
                        activity=activity,
                        first_name=p_data.get('first_name', ''),
                        middle_name=p_data.get('middle_name', ''),
                        last_name=p_data.get('last_name', ''),
                        passenger_type=p_data.get('passenger_type', 'adult'),
                        passenger_category=p_data.get('passenger_category', 'none'),
                        gender=p_data.get('gender', ''),
                        date_of_birth=p_data.get('date_of_birth') or None,
                        nationality=p_data.get('nationality', ''),
                        passport_number=p_data.get('passport_number', ''),
                        passport_expiry_date=p_data.get('passport_expiry_date') or None,
                        pwd_id_number=p_data.get('pwd_id_number', '') or None,
                        senior_id_number=p_data.get('senior_id_number', '') or None,
                        is_primary=(index == 0)
                    )

                    selected_addons = p_data.get('selected_addons', [])
                    
                    for addon_item in selected_addons:
                        try:
                            addon_id = addon_item.get('id')
                            if not addon_id:
                                continue
                            addon_instance = AddOn.objects.get(id=addon_id)
                            ActivityAddOn.objects.create(
                                activity=activity,
                                addon=addon_instance,
                                passenger=passenger,
                                is_required=addon_item.get('is_required', False),
                                quantity_per_passenger=addon_item.get('quantity', 1),
                                notes=addon_item.get('notes', ''),
                                points_value=10.00
                            )
                        except (AddOn.DoesNotExist, KeyError, ValueError):
                            continue
                        except Exception as e:
                            print(f"Error creating ActivityAddOn: {str(e)}")
                            continue

                # NEW: Log to InstructorLog
                log_instructor_event(
                    request,
                    action_type='ACTIVITY_CREATED',
                    instructor=request.user,
                    section_name=section.section_name,
                    activity_name=activity.title,
                    details=f"Instructor created activity '{activity.title}' in section '{section.section_name}'."
                )

                return Response({
                    "message": "Activity created successfully!",
                    "activity_id": activity.id
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def update_activity(request, section_id, activity_id):
    instructor = request.user
    section = get_object_or_404(Section, id=section_id, instructor=instructor)
    activity = get_object_or_404(Activity, id=activity_id, section=section)
    
    if activity.is_code_active:
        return Response({"error": "Cannot edit an activated activity."}, status=400)
        
    data = request.data
    try:
        required_passengers = int(data.get('required_passengers', 1))
        required_children = int(data.get('required_children', 0))
        required_infants = int(data.get('required_infants', 0))

        if required_passengers < 1:
            return Response({"error": "At least one adult passenger is required"}, status=400)
        if required_infants > required_passengers:
            return Response({"error": "Number of infants cannot exceed number of adults"}, status=400)

        required_travel_class_raw = data.get('required_travel_class', 'economy')
        travel_class_map = {
            'economy': 'economy',
            'premium economy': 'premium_economy',
            'premium_economy': 'premium_economy',
            'business': 'business',
            'first': 'first',
            'first class': 'first',
        }
        required_travel_class = travel_class_map.get(
            (required_travel_class_raw or 'economy').lower().strip(),
            'economy'
        )

        final_instructions = data.get('instructions') or ""
        addon_instructions_lines = []
        passengers_data = data.get('passengers', [])
        
        if data.get('require_addons', False):
            for p_data in passengers_data:
                selected_addons = p_data.get('selected_addons', [])
                if selected_addons:
                    p_name = f"{p_data.get('first_name', '')} {p_data.get('last_name', '')}".strip()
                    if not p_name:
                        p_name = f"Passenger ({p_data.get('passenger_type', 'adult')})"
                    addon_names = []
                    for addon_item in selected_addons:
                        addon_id = addon_item.get('id')
                        qty = addon_item.get('quantity', 1)
                        if addon_id:
                            try:
                                addon_obj = AddOn.objects.get(id=addon_id)
                                addon_names.append(f"{qty}x {addon_obj.name}")
                            except Exception:
                                pass
                    if addon_names:
                        addon_instructions_lines.append(f"- {p_name}: {', '.join(addon_names)}")
                        
            if addon_instructions_lines:
                if final_instructions:
                    final_instructions += "\n\n"
                final_instructions += "Add-ons Assigned:\n" + "\n".join(addon_instructions_lines)

        with transaction.atomic():
            activity.title = data.get('title')
            activity.description = data.get('description', "")
            activity.activity_type = data.get('activity_type', 'Flight Booking')
            activity.required_trip_type = data.get('required_trip_type', 'one_way')
            activity.required_origin = data.get('required_origin')
            activity.required_destination = data.get('required_destination')
            activity.required_departure_date = data.get('required_departure_date') or None
            activity.required_return_date = data.get('required_return_date') or None
            activity.required_travel_class = required_travel_class
            activity.required_seat_class = data.get('required_seat_class') or ''
            activity.required_passengers = required_passengers
            activity.required_children = required_children
            activity.required_infants = required_infants
            activity.require_passenger_details = data.get('require_passenger_details', False)
            activity.require_passport = data.get('require_passport', False)
            activity.instructions = final_instructions
            activity.total_points = float(data.get('total_points', 100))
            activity.due_date = data.get('due_date')
            activity.addon_grading_enabled = data.get('require_addons', False)
            activity.time_limit_minutes = data.get('time_limit_minutes') or None
            activity.save()

            ActivitySegment.objects.filter(activity=activity).delete()
            ActivityPassenger.objects.filter(activity=activity).delete()

            if data.get('required_trip_type') == 'multi_city':
                segments_data = data.get('segments', [])
                for index, s_data in enumerate(segments_data):
                    ActivitySegment.objects.create(
                        activity=activity,
                        origin=s_data.get('origin', ''),
                        destination=s_data.get('destination', ''),
                        departure_date=s_data.get('departure_date'),
                        order=index
                    )

            for index, p_data in enumerate(passengers_data):
                passenger = ActivityPassenger.objects.create(
                    activity=activity,
                    first_name=p_data.get('first_name', ''),
                    middle_name=p_data.get('middle_name', ''),
                    last_name=p_data.get('last_name', ''),
                    passenger_type=p_data.get('passenger_type', 'adult'),
                    passenger_category=p_data.get('passenger_category', 'none'),
                    gender=p_data.get('gender', ''),
                    date_of_birth=p_data.get('date_of_birth') or None,
                    nationality=p_data.get('nationality', ''),
                    passport_number=p_data.get('passport_number', ''),
                    passport_expiry_date=p_data.get('passport_expiry_date') or None,
                    pwd_id_number=p_data.get('pwd_id_number', '') or None,
                    senior_id_number=p_data.get('senior_id_number', '') or None,
                    is_primary=(index == 0)
                )

                selected_addons = p_data.get('selected_addons', [])
                
                for addon_item in selected_addons:
                    try:
                        addon_id = addon_item.get('id')
                        if not addon_id:
                            continue
                        addon_instance = AddOn.objects.get(id=addon_id)
                        ActivityAddOn.objects.create(
                            activity=activity,
                            addon=addon_instance,
                            passenger=passenger,
                            is_required=addon_item.get('is_required', False),
                            quantity_per_passenger=addon_item.get('quantity', 1),
                            notes=addon_item.get('notes', ''),
                            points_value=10.00
                        )
                    except Exception as e:
                        print(f"Error creating ActivityAddOn: {str(e)}")
                        continue

            log_instructor_event(
                request,
                action_type='ACTIVITY_UPDATED',
                instructor=request.user,
                section_name=section.section_name,
                activity_name=activity.title,
                details=f"Instructor updated activity '{activity.title}' in section '{section.section_name}'."
            )

            return Response({
                "message": "Activity updated successfully!",
                "activity_id": activity.id
            }, status=status.HTTP_200_OK)

    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def activity_details(request, activity_id):
    try:
        activity = get_object_or_404(
            Activity.objects.select_related('section').prefetch_related('passengers'),
            id=activity_id,
            section__instructor=request.user
        )
        
        # Helper function to safely get passenger attributes
        def get_passenger_field(passenger, field_name, default=''):
            """Safely get passenger field value"""
            return getattr(passenger, field_name, default) or default
        
        # Build passenger data with all possible fields
        passengers_data = []
        for p in activity.passengers.all():
            passenger_info = {
                "first_name": get_passenger_field(p, 'first_name'),
                "middle_name": (
                    get_passenger_field(p, 'middle_name') or 
                    get_passenger_field(p, 'middleName') or 
                    get_passenger_field(p, 'middle_initial')
                ),
                "last_name": get_passenger_field(p, 'last_name'),
                "gender": next((label for val, label in [('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'), ('male', 'Mr.'), ('female', 'Mrs.')] if get_passenger_field(p, 'gender', 'mr').lower().strip('.') == val or val == get_passenger_field(p, 'gender', 'mr').lower().strip('.')), 'Mr.'),
                "type": get_passenger_field(p, 'passenger_type', 'Adult').capitalize(),
                "nationality": get_passenger_field(p, 'nationality'),
                "date_of_birth": get_passenger_field(p, 'date_of_birth'),
                "passport_number": get_passenger_field(p, 'passport_number'),
                "passport_expiry_date": get_passenger_field(p, 'passport_expiry_date').strftime("%Y-%m-%d") if hasattr(get_passenger_field(p, 'passport_expiry_date'), 'strftime') else get_passenger_field(p, 'passport_expiry_date'),
                "pwd_id_number": get_passenger_field(p, 'pwd_id_number'),
                "senior_id_number": get_passenger_field(p, 'senior_id_number'),
                "email": get_passenger_field(p, 'email'),
                "phone": get_passenger_field(p, 'phone'),
                "seat_preference": get_passenger_field(p, 'seat_preference'),
                "special_requirements": get_passenger_field(p, 'special_requirements'),
            }
            passengers_data.append(passenger_info)
        
        data = {
            "id": activity.id,
            "title": activity.title,
            "description": activity.description,
            "section_name": activity.section.section_name if activity.section else "",
            "section_code": activity.section.section_code if activity.section else "",
            "academic_year": activity.section.academic_year if activity.section else "",
            "semester": activity.section.semester if activity.section else "",
            "schedule": activity.section.schedule if activity.section else "",
            "required_trip_type": activity.required_trip_type,
            "required_origin": activity.required_origin if hasattr(activity, 'required_origin') else "",
            "required_destination": activity.required_destination if hasattr(activity, 'required_destination') else "",
            "required_departure_date": activity.required_departure_date.strftime("%Y-%m-%d") if activity.required_departure_date else "",
            "required_return_date": activity.required_return_date.strftime("%Y-%m-%d") if activity.required_return_date else "",
            "required_travel_class": activity.required_travel_class,
            "required_seat_class": activity.required_seat_class if hasattr(activity, 'required_seat_class') else "",
            "required_passengers": activity.required_passengers if hasattr(activity, 'required_passengers') else 0,
            "required_children": activity.required_children if hasattr(activity, 'required_children') else 0,
            "required_infants": activity.required_infants if hasattr(activity, 'required_infants') else 0,
            "instructions": activity.instructions if hasattr(activity, 'instructions') else "",
            "due_date": activity.due_date.strftime("%B %d, %Y") if activity.due_date else "",
            "activity_code": activity.activity_code if hasattr(activity, 'activity_code') else "",
            "is_code_active": activity.is_code_active if hasattr(activity, 'is_code_active') else False,
            "total_points": float(activity.total_points) if activity.total_points else 100,
            "grades_released": activity.grades_released if hasattr(activity, 'grades_released') else False,
            "require_passenger_details": activity.require_passenger_details if hasattr(activity, 'require_passenger_details') else False,
            "require_passport": activity.require_passport if hasattr(activity, 'require_passport') else False,
            "require_addons": activity.addon_grading_enabled if hasattr(activity, 'addon_grading_enabled') else False,
            "time_limit_minutes": activity.time_limit_minutes if hasattr(activity, 'time_limit_minutes') else None,
            "passengers": [
                {
                    "first_name": get_passenger_field(p, 'first_name'),
                    "middle_name": (
                        get_passenger_field(p, 'middle_name') or 
                        get_passenger_field(p, 'middleName') or 
                        get_passenger_field(p, 'middle_initial')
                    ),
                    "last_name": get_passenger_field(p, 'last_name'),
                    "gender": next((label for val, label in [('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'), ('male', 'Mr.'), ('female', 'Mrs.')] if get_passenger_field(p, 'gender', 'mr').lower().strip('.') == val or val == get_passenger_field(p, 'gender', 'mr').lower().strip('.')), 'Mr.'),
                    "type": get_passenger_field(p, 'passenger_type', 'Adult').capitalize(),
                    "passenger_type": get_passenger_field(p, 'passenger_type', 'adult').lower(),
                    "nationality": get_passenger_field(p, 'nationality'),
                    "date_of_birth": get_passenger_field(p, 'date_of_birth').strftime("%Y-%m-%d") if hasattr(get_passenger_field(p, 'date_of_birth'), 'strftime') else get_passenger_field(p, 'date_of_birth'),
                    "passport_number": get_passenger_field(p, 'passport_number'),
                    "passport_expiry_date": get_passenger_field(p, 'passport_expiry_date').strftime("%Y-%m-%d") if hasattr(get_passenger_field(p, 'passport_expiry_date'), 'strftime') else get_passenger_field(p, 'passport_expiry_date'),
                    "pwd_id_number": get_passenger_field(p, 'pwd_id_number'),
                    "senior_id_number": get_passenger_field(p, 'senior_id_number'),
                    "email": get_passenger_field(p, 'email'),
                    "phone": get_passenger_field(p, 'phone'),
                    "seat_preference": get_passenger_field(p, 'seat_preference'),
                    "special_requirements": get_passenger_field(p, 'special_requirements'),
                    "passenger_category": get_passenger_field(p, 'passenger_category', 'none'),
                }
                for p in activity.passengers.all()
            ],
            "segments": [
                {
                    "origin": s.origin,
                    "destination": s.destination,
                    "departure_date": s.departure_date.strftime("%Y-%m-%d") if s.departure_date else "",
                    "order": s.order
                }
                for s in activity.segments.all()
            ] if activity.segments.exists() or activity.required_trip_type != 'round_trip' else [
                {
                    "origin": activity.required_origin,
                    "destination": activity.required_destination,
                    "departure_date": activity.required_departure_date.strftime("%Y-%m-%d") if activity.required_departure_date else "",
                    "order": 0
                },
                {
                    "origin": activity.required_destination,
                    "destination": activity.required_origin,
                    "departure_date": activity.required_return_date.strftime("%Y-%m-%d") if activity.required_return_date else "",
                    "order": 1
                }
            ],
            "activity_addons": [
                {
                    "id": aa.id,
                    "addon_id": aa.addon.id,
                    "addon_name": aa.addon.name,
                    "passenger": {
                        "id": aa.passenger.id,
                        "first_name": aa.passenger.first_name,
                        "last_name": aa.passenger.last_name
                    }
                }
                for aa in activity.activity_addons.select_related('addon', 'passenger').all()
            ]
        }
        
        return Response(data)
        
    except Activity.DoesNotExist:
        return Response(
            {"error": "Activity not found or you don't have permission to view it"},
            status=404
        )
    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=500
        )


@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def activate_activity(request, activity_id):
    try:
        activity = get_object_or_404(
            Activity,
            id=activity_id,
            section__instructor=request.user
        )
        
        # Get requested student IDs from payload
        student_ids = request.data.get('student_ids', [])
        
        # 1. Handle Code Generation (only if not already active)
        if not activity.is_code_active or not activity.activity_code:
            if not activity.activity_code:
                max_attempts = 10
                for _ in range(max_attempts):
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    if not Activity.objects.filter(activity_code=code).exclude(id=activity_id).exists():
                        activity.activity_code = code
                        break
                else:
                    return Response(
                        {"error": "Could not generate a unique activity code. Please try again."},
                        status=500
                    )
            
            activity.is_code_active = True
            
            if hasattr(activity, 'code_generated_at'):
                activity.code_generated_at = timezone.now()
            
            if hasattr(activity, 'status'):
                activity.status = 'published'
            
            activity.save()

        # 2. Bind Students
        time_limit_minutes = request.data.get('time_limit_minutes')
        enrolled_students_count = Activity_Student_Bind(
            activity, 
            student_ids=student_ids, 
            time_limit_minutes=time_limit_minutes
        )
        
        return Response({
            "message": "Activity Activated Successfully" if enrolled_students_count > 0 else "Activity updated successfully",
            "activity_code": activity.activity_code,
            "students_notified": enrolled_students_count
        })

    except Activity.DoesNotExist:
        return Response(
            {"error": "Activity not found or you don't have permission to activate it"},
            status=404
        )
    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=500
        )

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def get_eligible_students(request, activity_id):
    """
    Returns students enrolled in the section who haven't been assigned this activity yet.
    """
    try:
        activity = get_object_or_404(
            Activity,
            id=activity_id,
            section__instructor=request.user
        )
        
        section = activity.section
        # Find students in this section who ARE NOT in ActivityStudentBinding for this activity
        already_bound_ids = ActivityStudentBinding.objects.filter(
            activity=activity
        ).values_list('student_id', flat=True)
        
        eligible_enrollments = SectionEnrollment.objects.filter(
            section=section
        ).exclude(
            student_id__in=already_bound_ids
        ).select_related('student')
        
        students_data = [
            {
                "id": e.student.id,
                "student_number": e.student.student_number,
                "first_name": e.student.first_name,
                "last_name": e.student.last_name,
                "email": e.student.email
            }
            for e in eligible_enrollments
        ]
        
        return Response({
            "eligible_students": students_data,
            "total_count": len(students_data),
            "is_activity_active": activity.is_code_active
        })
        
    except Activity.DoesNotExist:
        return Response({"error": "Activity not found"}, status=404)
    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def release_activity_grades(request, activity_id):
    """
    Toggle the release status of grades for an activity.
    When released, students can see their scores.
    """
    try:
        activity = get_object_or_404(
            Activity,
            id=activity_id,
            section__instructor=request.user
        )
        
        
        # Accept a specific list of student IDs to release if provided
        # This ties into the frontend 'SHOW GRADES' logic, ensuring instructors
        # only release grades they have explicitly revealed.
        student_ids = request.data.get('student_ids', None)
        
        # Determine if we are releasing for the first time or re-releasing
        released_count = 0
        if not activity.grades_released:
            # First time: Mark activity as released and release all currently graded/submitted bindings
            activity.grades_released = True
            activity.save()
            
            # Release all existing bindings that have a grade or are submitted
            filters = Q(grade__isnull=False) | Q(status__in=['submitted', 'graded'])
            bindings_to_release = ActivityStudentBinding.objects.filter(filters, activity=activity)
            if student_ids:
                bindings_to_release = bindings_to_release.filter(student__id__in=student_ids)
                
            released_count = bindings_to_release.count()
            bindings_to_release.update(is_released=True)
            
            message = f"Grades released to {released_count} students"
            
            # LOG Grade Release
            log_instructor_event(
                request,
                action_type='GRADES_RELEASED',
                instructor=request.user,
                section_name=activity.section.section_name,
                activity_name=activity.title,
                details=f"Instructor released grades for activity '{activity.title}' to {released_count} students."
            )
        else:
            # Re-releasing: Release those unreleased but have a grade/status
            filters = Q(grade__isnull=False) | Q(status__in=['submitted', 'graded'])
            bindings_to_release = ActivityStudentBinding.objects.filter(
                filters,
                activity=activity,
                is_released=False
            )
            if student_ids:
                bindings_to_release = bindings_to_release.filter(student__id__in=student_ids)
                
            released_count = bindings_to_release.count()
            bindings_to_release.update(is_released=True)
            
            message = f"Batch release successful: {released_count} new grades released"
            
        print(f"✅ Grades for activity {activity_id}: {released_count} students released. Total release: {activity.grades_released}")
        
        return Response({
            "message": message,
            "grades_released": activity.grades_released,
            "newly_released_count": released_count
        }, status=status.HTTP_200_OK)
        
    except Activity.DoesNotExist:
        return Response(
            {"error": "Activity not found or you don't have permission"},
            status=404
        )
    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=500
        )


def calculate_submission_score(activity, booking):
    """
    Wrapper around the master grading service to maintain backward compatibility 
    in views while ensuring consistent logic.
    """
    result = grade_booking(booking, activity.id)
    if result:
        return {
            "total": result["total"],
            "breakdown": {}, # Legacy field, no longer used by new rubric
            "rubric_breakdown": result["rubric_breakdown"]
        }
    return None


def get_flight_notification_html(student, activity, section):
    """
    Generates a beautiful Boarding Pass style HTML email for activity notifications.
    Now includes the Activity Code in a professional "code" layout.
    """
    origin = (activity.required_origin or "SYS").upper()
    destination = (activity.required_destination or "TASK").upper()
    due_date = activity.due_date.strftime('%B %d, %Y') if activity.due_date else 'No due date'
    title = activity.title
    activity_code = activity.activity_code or "------"
    section_name = section.section_name
    first_name = student.first_name
    total_points = float(activity.total_points) if activity.total_points else 100
    
    # Try to get the base URL from settings, or default to a common one
    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    login_url = f"{base_url}/login"

    release_date = timezone.now().strftime('%B %d, %Y')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      .boarding-pass {{
        border: 1px solid #ffe4e6;
        border-radius: 12px;
        overflow: hidden;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        max-width: 600px;
        margin: 20px auto;
        box-shadow: 0 10px 25px -5px rgba(236, 72, 153, 0.1);
      }}
      .header {{
        background: #db2777;
        color: white;
        padding: 20px 24px;
        text-align: left;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }}
      .header-title {{
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 900;
        font-size: 12px;
        color: #fce7f3;
      }}
      .hero {{
        background-color: #ffffff;
        padding: 40px 30px 20px;
        text-align: center;
      }}
      .activity-name-badge {{
        background-color: #fdf2f8;
        color: #be185d;
        padding: 6px 16px;
        border-radius: 100px;
        font-weight: 800;
        font-size: 10px;
        display: inline-block;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
      }}
      .code-section {{
        padding: 0 30px 40px;
        text-align: center;
      }}
      .code-box {{
        background: #fff9fb;
        border: 2px dashed #fbcfe8;
        border-radius: 16px;
        padding: 30px;
        position: relative;
      }}
      .code-label {{
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        background: #db2777;
        color: white;
        font-size: 9px;
        font-weight: 900;
        padding: 4px 12px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 1px;
      }}
      .activity-code {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 42px;
        font-weight: 900;
        color: #db2777;
        letter-spacing: 8px;
        margin: 10px 0;
      }}
      .details-grid {{
        display: table;
        width: 100%;
        border-top: 1px solid #fce7f3;
        padding-top: 20px;
        margin-top: 20px;
      }}
      .detail-item {{
        display: table-cell;
        width: 50%;
        text-align: center;
      }}
      .detail-label {{
        font-size: 9px;
        text-transform: uppercase;
        color: #9d174d;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
      }}
      .detail-value {{
        font-size: 13px;
        font-weight: 700;
        color: #831843;
      }}
      .footer {{
        background-color: #fff1f2;
        padding: 24px;
        text-align: center;
        font-size: 11px;
        color: #be185d;
        border-top: 1px solid #fecdd3;
      }}
      .button {{
        display: inline-block;
        background: #db2777;
        color: white !important;
        text-decoration: none;
        padding: 12px 32px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 20px;
      }}
    </style>
    </head>
    <body>
      <div class="boarding-pass">
        <div class="header">
          <span class="header-title">Aviation Training Management</span>
          <span style="color: #fce7f3; font-weight: 900; font-size: 12px;">SYSTEM DISPATCH</span>
        </div>
        
        <div class="hero">
          <div class="activity-name-badge">{section_name}</div>
          <h1 style="margin:0; font-size: 24px; color: #831843; font-weight: 900; letter-spacing: -0.5px;">{title}</h1>
          <p style="color: #9d174d; font-size: 14px; margin-top: 8px;">Hello {first_name}, your instructor has authorized this activity.</p>
        </div>
        
        <div class="code-section">
           <div class="code-box">
              <div class="code-label">Access Passcode</div>
              <div class="activity-code">{activity_code}</div>
              <p style="color: #be185d; font-size: 10px; font-weight: 600; margin-top: 5px;">ENTER THIS CODE TO BEGIN ASSESSMENT</p>
              
              <div class="details-grid">
                <div class="detail-item" style="border-right: 1px solid #fce7f3;">
                   <div class="detail-label">Status</div>
                   <div class="detail-value" style="color: #db2777;">ACTIVE</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">Due Date</div>
                  <div class="detail-value">{due_date}</div>
                </div>
              </div>
           </div>
           
           <a href="{login_url}" class="button">Access Laboratory</a>
        </div>
        
        <div class="footer">
          This is an automated security dispatch. Ensure you have a stable connection before starting.<br>
          &copy; {timezone.now().year} Cabagan State University | Flight Booking Simulation
        </div>
      </div>
    </body>
    </html>
    """

def _send_activity_notification_worker(activity, enrolled_students, section):
    """Background worker to send emails without blocking the main request"""
    for student in enrolled_students:
        if student.email:
            subject = f"Activity Access Code: {activity.activity_code} | {activity.title}"
            message = (
                f"Hello {student.first_name},\n\n"
                f"A new activity '{activity.title}' has been released for your section: {section.section_name}.\n\n"
                f"ACTIVITY CODE: {activity.activity_code}\n\n"
                f"Please log in to your dashboard to complete the task.\n"
                f"Due Date: {activity.due_date.strftime('%B %d, %Y') if activity.due_date else 'No due date'}\n\n"
                f"--- This is an automated notification ---"
            )
            html_message = get_flight_notification_html(student, activity, section)
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL or 'fbs@example.com',
                    [student.email],
                    fail_silently=True,
                    html_message=html_message
                )
            except Exception as e:
                print(f"Error sending activation email to {student.email}: {str(e)}")

def generate_random_seats(activity, count):
    """
    Generate unique random seat labels.
    Attempts to pull real seat_numbers from the simulator database (app.Seat).
    Falls back to row-based generation if no matching flight/seats are found.
    """
    import random
    from app.models import Seat, Schedule, SeatClass
    from django.db.models import Q
    
    # 1. Try to find real seats in the simulator
    try:
        # Match schedule by activity requirements
        schedule_query = Schedule.objects.filter(status='Open')
        
        if activity.required_origin:
            schedule_query = schedule_query.filter(flight__route__origin_airport__code=activity.required_origin)
        if activity.required_destination:
            schedule_query = schedule_query.filter(flight__route__destination_airport__code=activity.required_destination)
        if activity.required_departure_date:
            schedule_query = schedule_query.filter(departure_time__date=activity.required_departure_date)
            
        schedule = schedule_query.first()
        
        if schedule:
            # Map activity travel class to database SeatClass name
            class_map = {
                'economy': ['Economy Class', 'Standard Seat', 'Basic Seat', 'Value Seat'],
                'premium_economy': ['Premium Economy', 'Premium Seat', 'Hot Seat'],
                'business': ['Business Class', 'Business'],
                'first': ['First Class', 'First']
            }
            target_classes = class_map.get(activity.required_travel_class.lower(), ['Economy Class'])
            
            # Fetch available seats for this schedule and class
            db_seats = list(Seat.objects.filter(
                schedule=schedule,
                seat_class__name__icontains=target_classes[0] # Try primary match
            ).values_list('seat_number', flat=True).distinct())
            
            # If nothing found with primary, try all variations
            if not db_seats:
                q_obj = Q()
                for tc in target_classes:
                    q_obj |= Q(seat_class__name__icontains=tc)
                db_seats = list(Seat.objects.filter(
                    schedule=schedule
                ).filter(q_obj).values_list('seat_number', flat=True).distinct())
            
            if db_seats and len(db_seats) >= count:
                return random.sample(db_seats, count)
    except Exception as e:
        print(f"DEBUG: Real seat lookup failed: {str(e)}")

    # 2. Fallback: Generate labels based on travels class (Legacy/Simulation fallback)
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

def Activity_Student_Bind(activity, student_ids=None, time_limit_minutes=None):
    from .models import ActivityStudentBinding
    
    section = activity.section
    enrolled_students_query = SectionEnrollment.objects.filter(section=section).select_related('student', 'student__user')
    
    # Filter by specific student IDs if provided
    if student_ids:
        enrolled_students_query = enrolled_students_query.filter(student_id__in=student_ids)
    
    students_bound = 0
    bound_students_list = []
    
    # Process bindings synchronously (fast database operations)
    for enrollment in enrolled_students_query:
        student = enrollment.student
        
        # User requested: Students can now choose any seats.
        # Remove automatic seat assignment during release.
        assigned_seats = []
            
        # Use provided limit OR activity's default
        final_time_limit = time_limit_minutes if time_limit_minutes is not None else activity.time_limit_minutes

        binding, created = ActivityStudentBinding.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={
                'assigned_at': timezone.now(),
                'status': 'assigned',
                'assigned_seats': assigned_seats,
                'time_limit_minutes': final_time_limit
            }
        )
        
        # If binding already existed
        if not created:
            if time_limit_minutes is not None:
                binding.time_limit_minutes = time_limit_minutes
            # Ensure we clear seats if re-binding
            binding.assigned_seats = []
            binding.save()
        if created:
            students_bound += 1
            bound_students_list.append(student)

            # Create in-app notification
            from .models import StudentNotification
            StudentNotification.objects.create(
                student=student,
                activity=activity,
                title="New Activity Available",
                message=f"An activity '{activity.title}' has been assigned to you."
            )
            
    # Dispatch emails in the background (slow network operations)
    if bound_students_list:
        # Pass necessary data to the thread
        # Note: We pass the queryset or list to ensure the thread can access the data
        email_thread = threading.Thread(
            target=_send_activity_notification_worker, 
            args=(activity, bound_students_list, section)
        )
        email_thread.daemon = True # Ensure it doesn't block server shutdown
        email_thread.start()
    
    return students_bound


@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def get_activity_submissions(request, activity_id):
    """
    Get all student submissions for a specific activity.
    Optimized for high performance with bulk fetching and pre-fetching.
    """
    try:
        # 1. Get activity with all design data prefetched
        activity = get_object_or_404(
            Activity.objects.select_related('section').prefetch_related(
                'passengers', 'segments', 'activity_addons', 'activity_addons__addon', 'activity_addons__passenger'
            ),
            id=activity_id,
            section__instructor=request.user
        )
        
        # 2. Get all students enrolled in this section
        enrollments = SectionEnrollment.objects.filter(
            section=activity.section,
            is_active=True
        ).select_related('student', 'student__user')
        
        # 3. Bulk fetch data for all enrolled students
        student_user_ids = [e.student.user_id for e in enrollments if e.student.user_id]
        student_ids = [e.student_id for e in enrollments]
        
        # Map bindings by student_id
        bindings_map = {
            b.student_id: b 
            for b in ActivityStudentBinding.objects.filter(activity=activity, student_id__in=student_ids)
        }
        
        # Map latest confirmed booking by user_id
        # We prefetch details for all bookings to speed up analysis calls
        all_bookings = Booking.objects.filter(
            user_id__in=student_user_ids, 
            activity=activity
        ).prefetch_related(
            'details', 'details__schedule', 'details__schedule__flight', 
            'details__schedule__flight__route', 'details__schedule__flight__route__origin_airport',
            'details__schedule__flight__route__destination_airport', 'details__seat_class', 
            'details__seat', 'details__passenger', 'details__addons'
        ).order_by('user_id', '-created_at')
        
        bookings_map = {}
        for b in all_bookings:
            if b.user_id not in bookings_map:
                bookings_map[b.user_id] = b
        
        submissions_data = []
        
        for enrollment in enrollments:
            try:
                student = enrollment.student
                binding = bindings_map.get(student.id)
                
                # Map confirmed booking by user_id
                booking = bookings_map.get(student.user_id)
                
                score_data = None
                if binding:
                    # 1. Timeout Check: If time is up and no booking, auto-fail
                    if binding.status in ['assigned', 'in_progress'] and not booking:
                        if binding.expires_at and timezone.now() > binding.expires_at:
                            binding.status = 'graded'
                            binding.grade = 0.0
                            binding.is_failed_due_to_time = True
                            binding.feedback = "Time limit exceeded. Activity automatically failed."
                            binding.submitted_at = timezone.now()
                            binding.save()

                    # 2. Dynamic Grading: If student has a booking but grade is missing or status is submitted
                    # (Ensure we have the most up-to-date rubric_breakdown for the table)
                    if booking:
                        score_data = calculate_submission_score(activity, booking)
                        if score_data and (binding.grade is None or binding.status == 'submitted'):
                            binding.grade = score_data['total']
                            binding.rubric_breakdown = score_data['rubric_breakdown']
                            binding.status = 'graded'
                            binding.save()

                submission = {
                    "student_id": student.id,
                    "student_number": student.student_number,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "email": student.email,
                    "status": binding.status if binding else "not_assigned",
                    "binding_id": binding.id if binding else None,
                    "grade": float(binding.grade) if (binding and binding.grade is not None) else None,
                    "rubric_breakdown": binding.rubric_breakdown if (binding and hasattr(binding, 'rubric_breakdown')) else None,
                    "assigned_seats": binding.assigned_seats if (binding and hasattr(binding, 'assigned_seats')) else [],
                    "is_released": binding.is_released if binding else False,
                    "is_failed_due_to_time": binding.is_failed_due_to_time if (binding and hasattr(binding, 'is_failed_due_to_time')) else False,
                    "submitted_at": binding.submitted_at.isoformat() if binding and binding.submitted_at else None,
                    "booking": None
                }
                
                if booking:
                    # Optimized booking serialization using prefetched data
                    details_list = list(booking.details.all())
                    submission["booking"] = {
                        "id": booking.id,
                        "status": booking.status,
                        "is_practice": booking.is_practice,
                        "total_amount": float(booking.total_amount or 0.0),
                        "trip_type": booking.get_trip_type_display(),
                        "created_at": booking.created_at.isoformat() if booking.created_at else None,
                        "details": [
                            {
                                "origin": d.schedule.flight.route.origin_airport.code if d.schedule.flight.route.origin_airport else "???",
                                "destination": d.schedule.flight.route.destination_airport.code if d.schedule.flight.route.destination_airport else "???",
                                "departure": d.schedule.departure_time.isoformat() if d.schedule.departure_time else None,
                                "flight_number": d.schedule.flight.flight_number,
                                "seat_class": d.seat_class.name if d.seat_class else "N/A",
                                "seat_number": d.seat.seat_number if d.seat else "N/A"
                            } for d in details_list
                        ],
                        "passengers": [
                            {
                                "name": p.get_full_name() if p else "Unknown",
                                "type": p.passenger_type if p else "Adult"
                            } for p in {d.passenger_id: d.passenger for d in details_list if d.passenger_id}.values()
                        ]
                    }
                    
                    if submission["status"] in ["assigned", "in_progress"] and booking.status == "Confirmed":
                        submission["status"] = "submitted"

                    # Calculate analysis (using optimized score function which will use prefetched details)
                    # Use score_data from above if available, otherwise calculate it
                    if not score_data:
                        score_data = calculate_submission_score(activity, booking)
                    
                    if score_data:
                        submission["analysis"] = score_data.get("breakdown", {})
                        
                        if binding and binding.grade is None:
                            # Auto-set grade if not available
                            binding.grade = score_data["total"]
                            binding.rubric_breakdown = score_data["rubric_breakdown"]
                            binding.status = 'graded' if booking.status == "Confirmed" else 'submitted'
                            binding.is_released = False  # Wait for instructor to release grades
                            if booking.submitted_at:
                                binding.submitted_at = booking.submitted_at
                            elif not binding.submitted_at:
                                binding.submitted_at = timezone.now()
                            binding.save()
                            submission["status"] = binding.status
                            submission["is_released"] = False
                        
                        # CRITICAL FIX: Always push the freshly computed grade + rubric_breakdown
                        # into the response dict, regardless of whether we had to save the binding.
                        # This ensures the API never returns stale/null data from the pre-fetched
                        # binding object, which was causing 0/zero display in the submissions table.
                        submission["grade"] = float(score_data["total"]) if score_data["total"] is not None else None
                        submission["rubric_breakdown"] = score_data["rubric_breakdown"]
                        submission["status"] = "graded" if booking.status == "Confirmed" else submission["status"]
                    else:
                        submission["analysis"] = {}
                        print(f"⚠️ Warning: Grading failed for booking {booking.id}")
                
                submissions_data.append(submission)
            except Exception as e:
                print(f"❌ Error processing submission for student {enrollment.student.student_number}: {str(e)}")
                traceback.print_exc()
                # Still add a basic record so the student shows up in the table
                submissions_data.append({
                    "student_id": enrollment.student.id,
                    "student_number": enrollment.student.student_number,
                    "first_name": enrollment.student.first_name,
                    "last_name": enrollment.student.last_name,
                    "email": enrollment.student.email,
                    "status": "error",
                    "error_detail": str(e),
                    "booking": None
                })
            
        # Sort submissions by grade descending (highest score first)
        submissions_data.sort(key=lambda x: x['grade'] if x['grade'] is not None else -1, reverse=True)
            
        return Response({
            "activity_id": activity.id,
            "activity_title": activity.title,
            "total_points": float(activity.total_points) if activity.total_points else 100,
            "grades_released": activity.grades_released,
            "submissions": submissions_data,
            "total_students": len(submissions_data)
        }, status=status.HTTP_200_OK)
        
    except Http404:
        return Response({"error": "Activity not found or you don't have permission to view it."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        traceback.print_exc()
        return Response({
            "error": str(e),
            "detail": "An error occurred while processing activity submissions. Check server logs."
        }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# USER PROFILE MANAGEMENT
# ==========================================
@api_view(['GET', 'PATCH'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        data = serializer.data
        # Add avatar URL manually since it's on the profile
        if hasattr(user, 'userprofile') and user.userprofile.avatar:
            data['avatar'] = request.build_absolute_uri(user.userprofile.avatar.url)
        else:
            data['avatar'] = None
        return Response(data)

    elif request.method == 'PATCH':
        # Use our new serializer
        from .serializers import UserProfileUpdateSerializer
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Return updated data with full avatar URL
            response_data = serializer.data
            if hasattr(user, 'userprofile') and user.userprofile.avatar:
                response_data['avatar'] = request.build_absolute_uri(user.userprofile.avatar.url)
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# LOGOUT VIEW
# ==========================================
@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout - Deactivate the current session only
    """
    try:
        session_obj = request.session_obj
        session_obj.deactivate()
        
        # NEW: Log to InstructorLog
        now = timezone.now()
        # Find the latest LOGIN record for this user that hasn't been logged out
        latest_log = InstructorLog.objects.filter(
            actor=request.user, 
            action_type='LOGIN', 
            logout_time__isnull=True
        ).first()
        
        if latest_log:
            latest_log.logout_time = now
            latest_log.save()
        else:
            # If no login record (e.g. started before logging was added), create a LOGOUT record
            # We don't have a login record to update, so just create a simple one
            log_instructor_event(
                request, 
                action_type='LOGOUT', 
                instructor=request.user if hasattr(request.user, 'instructor_profile') else None,
                student=getattr(request.user, 'student_profile', None),
                logout_time=now,
                details=f"User {request.user.username} logged out."
            )

        print(f"? Session {session_obj.id} deactivated for user {request.user.username}")
        
        return Response({
            "message": "Logged out successfully"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"? Error during logout: {str(e)}")
        return Response({
            "error": "Logout failed"
        }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# SESSION VALIDATION
# ==========================================
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def validate_session(request):
    """
    Validate current session
    """
    try:
        user = request.user
        session_obj = request.session_obj
        profile = user.userprofile
        
        return Response({
            "valid": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": profile.role
            },
            "session": {
                "id": session_obj.id,
                "role": session_obj.role,
                "created_at": session_obj.created_at.isoformat(),
                "last_activity": session_obj.last_activity.isoformat()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"? Session validation error: {str(e)}")
        return Response({
            "valid": False,
            "error": "Session invalid"
        }, status=status.HTTP_401_UNAUTHORIZED)


# ==========================================
# SESSION MANAGEMENT - List all user sessions
# ==========================================
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    """
    List all active sessions for the current user
    """
    try:
        sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-last_activity')
        
        sessions_data = [
            {
                "id": s.id,
                "role": s.role,
                "created_at": s.created_at.isoformat(),
                "last_activity": s.last_activity.isoformat(),
                "ip_address": s.ip_address,
                "is_current": s.id == request.session_obj.id
            }
            for s in sessions
        ]
        
        return Response({
            "sessions": sessions_data,
            "total": len(sessions_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def start_activity(request, activity_id):
    """
    Start the activity timer for the current student.
    Sets started_at and expires_at if not already set.
    """
    user = request.user
    
    try:
        activity = Activity.objects.get(id=activity_id)
        # Verify student enrollment/binding
        binding = ActivityStudentBinding.objects.get(activity=activity, student__user=user)
        
        if not binding.started_at:
            now = timezone.now()
            binding.started_at = now
            binding.status = 'in_progress'
            
            # Use binding's limit (which falls back to activity's limit)
            limit = binding.time_limit_minutes
            if limit:
                binding.expires_at = now + timezone.timedelta(minutes=limit)
            
            binding.save()
            print(f"?? Timer started for {user.username} on Activity {activity.id}. Expires at: {binding.expires_at}")
        
        return Response({
            "message": "Activity started",
            "started_at": binding.started_at,
            "expires_at": binding.expires_at,
            "time_limit_minutes": binding.time_limit_minutes
        })
        
    except (Activity.DoesNotExist, ActivityStudentBinding.DoesNotExist):
        return Response({"error": "Activity or binding not found"}, status=404)
    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def fail_activity(request, activity_id):
    """
    Explicitly fail an activity for the student (e.g. when time is up).
    Sets grade to 0 and is_failed_due_to_time to True.
    """
    from .models import ActivityStudentBinding, Activity
    from app.models import Students
    
    try:
        user = request.user
        
        # Get the student record
        student = None
        if hasattr(user, 'student_profile'):
            student = user.student_profile
        else:
            student = Students.objects.get(user=user)
            
        if not student:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            binding = ActivityStudentBinding.objects.get(
                activity_id=activity_id,
                student=student
            )
        except ActivityStudentBinding.DoesNotExist:
            return Response({"error": "Activity assignment not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Update binding status to failed
        # We set status to 'graded' so it shows the 0 grade, but set is_failed_due_to_time=True
        binding.status = 'graded'
        binding.grade = 0.0
        binding.is_failed_due_to_time = True
        binding.feedback = "Time limit exceeded. Activity automatically failed."
        binding.submitted_at = timezone.now()
        binding.save()
        
        # Log to InstructorLog that student failed due to timeout
        log_instructor_event(
            request,
            action_type='ACTIVITY_FAILED_TIMEOUT',
            student=student,
            section_name=binding.activity.section.section_name,
            activity_name=binding.activity.title,
            details=f"Student {student.student_number} failed activity '{binding.activity.title}' due to time limit reached."
        )
        
        return Response({
            "success": True,
            "message": "Activity marked as failed due to time limit.",
            "grade": 0.0,
            "status": "graded"
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# 3. STUDENT DASHBOARD (Session-Based)
# ==========================================
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    try:
        user = request.user
        session_obj = request.session_obj  # Our UserSession object
        
        print(f"\n{'='*60}")
        print(f"? STUDENT DASHBOARD REQUEST")
        print(f"{'='*60}")
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Session Token: {session_obj.session_token[:16]}...")
        print(f"Session Role: {session_obj.role}")
        print(f"Session ID: {session_obj.id}")
        
        # 1. Verify session role
        try:
            if session_obj.role != 'student':
                print(f"? ERROR: Session role is '{session_obj.role}', not 'student'")
                return Response({
                    "error": "Access denied. This session is not authorized for student access.",
                    "session_role": session_obj.role,
                    "required_role": "student"
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Double-check with UserProfile
            if not hasattr(user, 'userprofile') or user.userprofile.role != 'student':
                print(f"? ERROR: User profile role mismatch")
                return Response({"error": "Access denied. Student access only."}, status=status.HTTP_403_FORBIDDEN)
            
            print("? Session and profile verified as student")
                
        except Exception as e:
            print(f"? ERROR during verification: {str(e)}")
            traceback.print_exc()
            return Response({"error": "Profile verification failed."}, status=status.HTTP_403_FORBIDDEN)

        # 2. Get Students record
        student = None
        
        # Try multiple methods
        if hasattr(user, 'student_profile'):
            student = user.student_profile
            print(f"? Method 1: Found student via related_name")
        
        if not student:
            try:
                student = Students.objects.get(user=user)
                print(f"? Method 2: Found student via user FK")
            except Students.DoesNotExist:
                print("?? Method 2: No Students record with user FK")
            except Exception as e:
                print(f"?? Method 2 error: {str(e)}")
        
        if not student:
            try:
                student = Students.objects.get(email=user.email)
                print(f"? Method 3: Found student via email match")
            except Students.DoesNotExist:
                print("?? Method 3: No Students record with matching email")
            except Exception as e:
                print(f"?? Method 3 error: {str(e)}")
        
        if not student:
            print("? FATAL: Could not find Students record!")
            return Response({
                "error": "Student record not found. Please contact your administrator.",
                "not_enrolled": True,
                "debug_info": {
                    "user_id": user.id,
                    "user_email": user.email,
                    "username": user.username
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"? Student record: {student.first_name} {student.last_name} (#{student.student_number})")
        
        # 3. Get enrolled section
        enrollment = SectionEnrollment.objects.filter(student=student, is_active=True).select_related('section').first()
        
        # Check if enrollment exists AND section is active
        if not enrollment or not enrollment.section.is_active:
            print("?? Student not enrolled in any session or section is disabled")
            return Response({
                'error': 'You are not enrolled in any section. Please contact your administrator.',
                'not_enrolled': True,
                'user': {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'student_number': student.student_number,
                    'mi': student.mi if student.mi else '',
                    'phone_number': student.phone_number if student.phone_number else ''
                },
                'section': None,
                'activities': [],
                'total_activities': 0,
            }, status=status.HTTP_403_FORBIDDEN)
        
        section = enrollment.section
        print(f"? Enrolled in: {section.section_name} ({section.section_code})")
        
        # 4. Get activities - Only Published or Closed activities (Hide Drafts)
        # (We will identify bindings in the loop)
        section_activities = Activity.objects.filter(
            section=section
        ).exclude(status='draft').order_by('-created_at')
        
        print(f"  Total visible activities: {section_activities.count()}")
        for act in section_activities:
            print(f"    - [{act.id}] {act.title}")
        
        # 5. Build activities data
        from .models import ActivityStudentBinding
        
        activities_data = []
        for activity in section_activities:
            binding = ActivityStudentBinding.objects.filter(
                activity=activity,
                student=student
            ).first()
            
            # If no binding, it means the student has not been assigned or has not entered the code
            if not binding:
                activities_data.append({
                    'id': activity.id,
                    'title': activity.title,
                    'description': activity.description or '',
                    'instructions': activity.instructions or '',
                    'activity_type': activity.activity_type,
                    'due_date': activity.due_date.strftime('%B %d, %Y') if activity.due_date else None,
                    'total_points': float(activity.total_points),
                    'created_at': activity.created_at.isoformat(),
                    'required_trip_type': activity.required_trip_type,
                    'required_origin': activity.required_origin,
                    'required_destination': activity.required_destination,
                    'required_travel_class': activity.required_travel_class,
                    'status': 'unassigned',
                    'assigned_at': None,
                    'is_active': activity.is_code_active,
                    'grade': None,
                    'completed': False,
                    'confirmed_booking_id': None
                })
                continue
            
            # Search for a confirmed booking for this activity
            booking_obj = Booking.objects.filter(
                user=user,
                activity=activity,
                status='Confirmed',
                is_practice=False
            ).first()

            if booking_obj and (binding.grade is None or binding.status in ['assigned', 'in_progress', 'submitted']):
                score_data = calculate_submission_score(activity, booking_obj)
                if score_data:
                    binding.grade = score_data['total']
                    binding.rubric_breakdown = score_data['rubric_breakdown']
                    binding.status = 'graded'
                    binding.is_released = False  # Wait for instructor to release grades
                    if booking_obj.submitted_at:
                        binding.submitted_at = booking_obj.submitted_at
                    binding.save()
                    print(f"  ? Auto-graded dashboard activity {activity.id}: {score_data['total']}")
                else:
                    print(f"  ⚠️ Warning: calculate_submission_score returned None for activity {activity.id}")

            # ? NEW: Time Limit Check (Auto-fail if expired)
            if binding.status in ['assigned', 'in_progress'] and not booking_obj:
                if binding.expires_at and timezone.now() > binding.expires_at:
                    binding.status = 'graded' # Mark as graded so it counts as done
                    binding.grade = 0.0
                    binding.is_failed_due_to_time = True
                    binding.feedback = "Time limit reached. Activity failed."
                    binding.save()
                    print(f"  ⚠️ Activity {activity.id} failed due to time limit for {user.username}")

            # ? Manual Grade Release Check (Include failed entries immediately)
            effective_grade = float(binding.grade) if (binding.grade is not None and (binding.is_released or activity.grades_released or binding.is_failed_due_to_time)) else None

            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description or '',
                'instructions': activity.instructions or '',
                'activity_type': activity.activity_type,
                'due_date': activity.due_date.strftime('%B %d, %Y') if activity.due_date else None,
                'total_points': float(activity.total_points),
                'created_at': activity.created_at.isoformat(),
                'required_trip_type': activity.required_trip_type,
                'required_origin': activity.required_origin,
                'required_destination': activity.required_destination,
                'required_travel_class': activity.required_travel_class,
                'required_seat_class': activity.required_seat_class if hasattr(activity, 'required_seat_class') else "",
                'required_passengers': activity.required_passengers,
                'required_children': activity.required_children,
                'required_infants': activity.required_infants,
                'status': binding.status,
                'assigned_at': binding.assigned_at.isoformat(),
                'is_active': activity.is_code_active,
                'section_id': section.id,
                'section_name': section.section_name,
                'section_code': section.section_code,
                'grade': effective_grade,
                'feedback': binding.feedback if (binding.is_released or activity.grades_released or binding.is_failed_due_to_time) else '',
                'submitted_at': binding.submitted_at.isoformat() if binding.submitted_at else None,
                'time_limit_minutes': binding.time_limit_minutes,
                'started_at': binding.started_at.isoformat() if binding.started_at else None,
                'expires_at': binding.expires_at.isoformat() if binding.expires_at else None,
                'is_failed_due_to_time': binding.is_failed_due_to_time,
                
                'completed': (booking_obj is not None) or (binding and binding.status in ['submitted', 'graded']),
                'confirmed_booking_id': booking_obj.id if booking_obj else None,
                'grades_released': activity.grades_released or (binding.is_released if binding else False),
            })
        
        section_data = {
            'id': section.id,
            'section_name': section.section_name,
            'section_code': section.section_code,
            'semester': section.semester,
            'academic_year': section.academic_year,
            'schedule': section.schedule,
            'description': section.description,
            'enrolled_at': enrollment.enrolled_at.strftime('%Y-%m-%d'),
            'activities_count': len(activities_data)
        }

        # Fetch classmates (all enrolled students)
        classmates_query = SectionEnrollment.objects.filter(section=section, is_active=True).select_related('student')
        classmates_data = []
        
        from .models import ActivityStudentBinding
        student_ids = [cls.student.id for cls in classmates_query]
        bindings = ActivityStudentBinding.objects.filter(
            student_id__in=student_ids,
            activity__section=section,
            status='graded',
            grade__isnull=False
        )
        
        student_stats = {}
        for b in bindings:
            if b.student_id not in student_stats:
                student_stats[b.student_id] = {'total_grade': 0.0, 'count': 0}
            student_stats[b.student_id]['total_grade'] += float(b.grade)
            student_stats[b.student_id]['count'] += 1

        section_leaderboard = []

        for cls in classmates_query:
            classmates_data.append({
                'first_name': cls.student.first_name,
                'last_name': cls.student.last_name,
                'student_number': cls.student.student_number,
                'email': cls.student.email,
                'gender': cls.student.gender
            })
            
            sid = cls.student.id
            count = student_stats.get(sid, {}).get('count', 0)
            total = student_stats.get(sid, {}).get('total_grade', 0.0)
            avg_grade = (total / count) if count > 0 else 0.0
            
            section_leaderboard.append({
                'id': user.id if sid == student.id else sid, # Use matching user ID for isMe logic
                'student_id': sid,
                'first_name': cls.student.first_name,
                'last_name': cls.student.last_name,
                'avg_grade': round(avg_grade, 2),
                'graded_count': count
            })
            
        instructor_obj = section.instructor
        instructor_data = {
            'first_name': instructor_obj.first_name,
            'last_name': instructor_obj.last_name,
            'email': instructor_obj.email
        }
        
        print(f"? Returning {len(activities_data)} activities and {len(classmates_data)} classmates")
        print(f"{'='*60}\n")
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'student_number': student.student_number,
                'mi': student.mi if student.mi else '',
                'phone_number': student.phone_number if student.phone_number else ''
            },
            'section': section_data,
            'instructor': instructor_data,
            'classmates': classmates_data,
            'section_leaderboard': section_leaderboard,
            'activities': activities_data,
            'total_activities': len(activities_data),
            'session_info': {
                'session_id': session_obj.id,
                'role': session_obj.role,
                'last_activity': session_obj.last_activity.isoformat()
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"\n{'!'*60}")
        print(f"❌ FATAL ERROR IN STUDENT DASHBOARD")
        print(f"{'!'*60}")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            "error": "An internal server error occurred while loading your dashboard.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def student_activity_details(request, activity_id):
    """
    Get detailed information about a specific activity for the authenticated student
    ? UPDATED VERSION - Now includes activity_code for verification
    """
    user = request.user
    session_obj = request.session_obj
    
    print(f"\n{'='*60}")
    print(f"? STUDENT ACTIVITY DETAILS REQUEST")
    print(f"{'='*60}")
    print(f"User: {user.username} (ID: {user.id})")
    print(f"Activity ID: {activity_id}")
    print(f"Session Role: {session_obj.role}")
    
    # 1. Verify session role
    try:
        if session_obj.role != 'student':
            print(f"? ERROR: Session role is '{session_obj.role}', not 'student'")
            return Response({
                "error": "Access denied. This session is not authorized for student access.",
                "session_role": session_obj.role,
                "required_role": "student"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Double-check with UserProfile
        if not hasattr(user, 'userprofile') or user.userprofile.role != 'student':
            print(f"? ERROR: User profile role mismatch")
            return Response({
                "error": "Access denied. Student access only."
            }, status=status.HTTP_403_FORBIDDEN)
        
        print("? Session and profile verified as student")
            
    except Exception as e:
        print(f"? ERROR during verification: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Profile verification failed."
        }, status=status.HTTP_403_FORBIDDEN)

    # 2. Get Students record
    student = None
    
    if hasattr(user, 'student_profile'):
        student = user.student_profile
        print(f"? Found student via related_name")
    
    if not student:
        try:
            student = Students.objects.get(user=user)
            print(f"? Found student via user FK")
        except Students.DoesNotExist:
            print("?? No Students record with user FK")
        except Exception as e:
            print(f"?? Error: {str(e)}")
    
    if not student:
        try:
            student = Students.objects.get(email=user.email)
            print(f"? Found student via email match")
        except Students.DoesNotExist:
            print("?? No Students record with matching email")
        except Exception as e:
            print(f"?? Error: {str(e)}")
    
    if not student:
        print("? FATAL: Could not find Students record!")
        return Response({
            "error": "Student record not found. Please contact your administrator.",
            "debug_info": {
                "user_id": user.id,
                "user_email": user.email,
                "username": user.username
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    print(f"? Student record: {student.first_name} {student.last_name} (#{student.student_number})")
    
    # 3. Get the activity - Exclude drafts for students
    try:
        activity = Activity.objects.select_related('section', 'section__instructor').prefetch_related(
            'passengers', 'segments', 'activity_addons', 'activity_addons__addon', 'activity_addons__passenger'
        ).get(
            id=activity_id
        )
        
        if activity.status == 'draft':
            print(f"? Activity {activity_id} is still in DRAFT mode")
            return Response({
                "error": "This activity has not been activated by the instructor yet."
            }, status=status.HTTP_403_FORBIDDEN)

        print(f"? Activity found: {activity.title}")
        print(f"? Activity code: {activity.activity_code}")
    except Activity.DoesNotExist:
        print(f"? Activity {activity_id} not found or inactive")
        return Response({
            "error": "Activity not found or is no longer active."
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"? Error fetching activity: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Failed to retrieve activity details.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 4. Verify student has access to this activity (enrolled in section)
    try:
        enrollment = SectionEnrollment.objects.filter(
            student=student,
            section=activity.section
        ).first()
        
        if not enrollment:
            print(f"? Student not enrolled in section: {activity.section.section_code}")
            return Response({
                "error": "Access denied. You are not enrolled in the section for this activity.",
                "section_code": activity.section.section_code
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"? Student enrolled in section: {activity.section.section_code}")
    except Exception as e:
        print(f"? Error checking enrollment: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Failed to verify enrollment.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 5. Verify selective activation (check if binding exists)
    try:
        binding = ActivityStudentBinding.objects.filter(
            activity=activity,
            student=student
        ).first()
        
        if binding:
            print(f"? Found activity binding - Status: {binding.status}")
                
            # ? NEW: Automatic Grading Trigger for Student View
            # Optimized with select_related and prefetch_related for scoring and serialization
            booking_obj = Booking.objects.filter(
                user=user, activity=activity, status='Confirmed', is_practice=False
            ).select_related(
                'user'
            ).prefetch_related(
                'details__schedule__flight__airline',
                'details__schedule__flight__route__origin_airport',
                'details__schedule__flight__route__destination_airport',
                'details__seat_class',
                'details__passenger',
                'details__addons'
            ).first()

            submission_score_data = None # Cache for analysis
            if booking_obj:
                submission_score_data = calculate_submission_score(activity, booking_obj)
                
                if submission_score_data and (binding.grade is None or binding.status in ['assigned', 'in_progress', 'submitted']):
                    binding.grade = submission_score_data['total']
                    binding.rubric_breakdown = submission_score_data['rubric_breakdown']
                    binding.status = 'graded'
                    binding.is_released = False # Wait for instructor to release grades
                    if booking_obj.submitted_at:
                        binding.submitted_at = booking_obj.submitted_at
                    binding.save()
                    print(f"? Auto-graded student {user.username}: {submission_score_data['total']}")

            # ? NEW: Time limit check in details
            is_timed_out = False
            if binding.status in ['assigned', 'in_progress'] and binding.expires_at and timezone.now() > binding.expires_at:
                is_timed_out = True
                if not booking_obj:
                    binding.status = 'graded'
                    binding.grade = 0.0
                    binding.is_failed_due_to_time = True
                    binding.feedback = "Time limit reached."
                    binding.save()
        else:
            print(f"? No binding found for student {user.username} - Activity viewable due to enrollment")
            booking_obj = None
            is_timed_out = False
            submission_score_data = None
            
    except Exception as e:
        print(f"? Error with ActivityStudentBinding: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Failed to create or retrieve activity binding.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 6. Get instructor information
    instructor_data = None
    try:
        if activity.section and activity.section.instructor:
            instructor = activity.section.instructor
            instructor_data = {
                'id': instructor.id,
                'first_name': instructor.first_name,
                'last_name': instructor.last_name,
                'email': instructor.email,
                'employee_id': instructor.employee_id if hasattr(instructor, 'employee_id') else None
            }
            print(f"? Instructor: {instructor.first_name} {instructor.last_name}")
        else:
            print("?? No instructor assigned to this section")
    except Exception as e:
        print(f"?? Error fetching instructor: {str(e)}")
        # Continue without instructor data
    
    # 7. Get passenger information from ActivityPassenger model
    passengers_data = []
    try:
        # Get passengers from the activity
        activity_passengers = activity.passengers.all() if hasattr(activity, 'passengers') else []
        
        for passenger in activity_passengers:
            passenger_dict = {
                'type': passenger.passenger_type.capitalize() if hasattr(passenger, 'passenger_type') else 'Adult',
                'gender': 'Mr.' if getattr(passenger, 'gender', 'mr').lower() == 'mr' else 'Mrs.' if getattr(passenger, 'gender', 'mr').lower() == 'mrs' else 'Ms.',
                'first_name': getattr(passenger, 'first_name', ''),
                'last_name': getattr(passenger, 'last_name', ''),
                'middle_initial': getattr(passenger, 'middle_name', '') or getattr(passenger, 'middle_initial', ''),
                'nationality': getattr(passenger, 'nationality', 'Philippines'),
                'passport': getattr(passenger, 'passport_number', ''),
                'seat_preference': getattr(passenger, 'seat_preference', 'Window'),
                'has_reservation': getattr(passenger, 'has_reservation', False),
                'is_pwd': getattr(passenger, 'is_pwd', False)
            }
            
            # Handle date of birth
            if hasattr(passenger, 'date_of_birth') and passenger.date_of_birth:
                dob = passenger.date_of_birth
                passenger_dict['birth_day'] = str(dob.day).zfill(2)
                passenger_dict['birth_month'] = dob.strftime('%B')
                passenger_dict['birth_year'] = str(dob.year)
            else:
                passenger_dict['birth_day'] = '01'
                passenger_dict['birth_month'] = 'January'
                passenger_dict['birth_year'] = '1990'
            
            passengers_data.append(passenger_dict)
        
        print(f"? Found {len(passengers_data)} passengers from ActivityPassenger model")
        
    except Exception as e:
        print(f"?? Error fetching passengers: {str(e)}")
        traceback.print_exc()
        # Continue without passenger data
    
    # 8. Build response data
    try:
        # Helper functions for safe date formatting
        def safe_date_format(date_obj, format_string='%B %d, %Y'):
            """Safely format date, return None if date is None"""
            if date_obj:
                try:
                    return date_obj.strftime(format_string)
                except:
                    return str(date_obj)
            return None
        
        def safe_iso_format(date_obj):
            """Safely convert to ISO format, return None if date is None"""
            if date_obj:
                try:
                    return date_obj.isoformat()
                except:
                    return str(date_obj)
            return None

        # Helper function to safely get passenger attributes
        def get_p_field(passenger, field_name, default=''):
            """Safely get passenger field value"""
            val = getattr(passenger, field_name, default)
            return val if val is not None else default

        def _normalize_gender_raw(g):
            """Normalize gender value to 'MR', 'MRS', or 'MS' matching booking form codes."""
            val = (g or '').upper().strip().replace('.', '')
            if val in ('MR', 'MALE', 'M'):
                return 'MR'
            if val in ('MRS', 'FEMALE', 'F'):
                return 'MRS'
            if val in ('MS',):
                return 'MS'
            return val or 'MR'


        # Search for a confirmed booking for this activity
        booking_obj = Booking.objects.filter(
            user=user,
            activity=activity,
            status='Confirmed',
            is_practice=False
        ).first()

        # Build activity data with PROPER field mapping
        activity_data = {
            'id': activity.id,
            'title': activity.title,
            'description': activity.description or '',
            'instructions': activity.instructions or '',
            'activity_type': activity.activity_type,
            'due_date': safe_date_format(activity.due_date),
            'total_points': float(activity.total_points) if activity.total_points else 0.0,
            'created_at': safe_iso_format(activity.created_at),
            
            # Flight requirements
            'required_trip_type': activity.required_trip_type or '',
            'required_origin': activity.required_origin or '',
            'required_destination': activity.required_destination or '',
            'required_travel_class': activity.required_travel_class or '',
            'required_seat_class': activity.required_seat_class if hasattr(activity, 'required_seat_class') else "",
            'required_passengers': activity.required_passengers or 0,
            'required_children': activity.required_children or 0,
            'required_infants': activity.required_infants or 0,
            
            # Dates
            'departure_date': safe_iso_format(getattr(activity, 'required_departure_date', None)),
            'arrival_date': safe_iso_format(getattr(activity, 'required_return_date', None)),
            'required_departure_date': safe_date_format(activity.required_departure_date, "%Y-%m-%d"),
            'required_return_date': safe_date_format(activity.required_return_date, "%Y-%m-%d"),
            
            # Standardized Passengers
            'passengers': [
                {
                    'first_name': get_p_field(p, 'first_name'),
                    'last_name': get_p_field(p, 'last_name'),
                    'middle_initial': get_p_field(p, 'middle_name') or get_p_field(p, 'middle_initial'),
                    'gender': _normalize_gender_raw(get_p_field(p, 'gender', 'mr')),
                    'passenger_type': get_p_field(p, 'passenger_type', 'adult').lower(),
                    'type': get_p_field(p, 'passenger_type', 'Adult').capitalize(),
                    'date_of_birth': safe_date_format(p.date_of_birth, "%Y-%m-%d"),
                    'nationality': get_p_field(p, 'nationality'),
                    'passport_number': get_p_field(p, 'passport_number') or get_p_field(p, 'passport'),
                    'passport_expiry_date': safe_date_format(p.passport_expiry_date, "%Y-%m-%d"),
                    'pwd_id_number': get_p_field(p, 'pwd_id_number'),
                    'senior_id_number': get_p_field(p, 'senior_id_number'),
                    'seat_preference': get_p_field(p, 'seat_preference', 'Window'),
                    'passenger_category': get_p_field(p, 'passenger_category', 'none'),
                }
                for p in activity.passengers.all()
            ],
            
            # Section info
            'section_id': activity.section.id,
            'section_name': activity.section.section_name,
            'section_code': activity.section.section_code,
            
            # Student progress
            'status': binding.status if binding else 'unassigned',
            'assigned_at': safe_iso_format(binding.assigned_at) if binding else None,
            'submitted_at': safe_iso_format(binding.submitted_at) if (binding and binding.submitted_at) else None,
            'grade': float(binding.grade) if (binding and binding.grade is not None and (binding.is_released or activity.grades_released or binding.is_failed_due_to_time)) else None,
            'feedback': binding.feedback if (binding and (binding.is_released or activity.grades_released or binding.is_failed_due_to_time)) else '',
            'rubric_breakdown': (binding.rubric_breakdown if binding else None) or (submission_score_data['rubric_breakdown'] if submission_score_data else None) if (activity.grades_released or (binding and binding.is_released)) else None,
            'analysis': submission_score_data if (booking_obj and (activity.grades_released or (binding and binding.is_released))) else None,
            'grades_released': activity.grades_released or (binding.is_released if binding else False),
            'assigned_seats': binding.assigned_seats if binding else [],
            
            # Activity status info
            'is_active': activity.is_code_active,
            'activity_code': activity.activity_code or '',
            'is_failed_due_to_time': binding.is_failed_due_to_time if binding else False,
            
            'segments': [
                {
                    'origin': s.origin,
                    'destination': s.destination,
                    'departure_date': safe_date_format(s.departure_date, "%Y-%m-%d"),
                    'order': s.order
                }
                for s in sorted(activity.segments.all(), key=lambda x: x.order)
            ] if activity.segments.all() or activity.required_trip_type != 'round_trip' else [
                {
                    'origin': activity.required_origin,
                    'destination': activity.required_destination,
                    'departure_date': safe_date_format(activity.required_departure_date, "%Y-%m-%d"),
                    'order': 0
                },
                {
                    'origin': activity.required_destination,
                    'destination': activity.required_origin,
                    'departure_date': safe_date_format(activity.required_return_date, "%Y-%m-%d"),
                    'order': 1
                }
            ],
            "activity_addons": [
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
            'completed': (booking_obj is not None) or (binding and binding.status in ['submitted', 'graded']),
            'confirmed_booking_id': booking_obj.id if booking_obj else None,
            'time_limit_minutes': binding.time_limit_minutes if binding else activity.time_limit_minutes,
            'started_at': binding.started_at.isoformat() if (binding and binding.started_at) else None,
            'expires_at': binding.expires_at.isoformat() if (binding and binding.expires_at) else None,
            'is_failed_due_to_time': binding.is_failed_due_to_time if binding else False,
            'is_timed_out': is_timed_out
        }
        
        # Import serializer locally to include full booking data in-place
        from flightapp.serializers import BookingSerializer
        
        response_data = {
            'activity': activity_data,
            'booking': BookingSerializer(booking_obj).data if booking_obj else None,
            'student': {
                'id': student.id,
                'student_number': student.student_number,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email
            },
            'session_info': {
                'session_id': session_obj.id,
                'role': session_obj.role,
                'last_activity': safe_iso_format(session_obj.last_activity)
            }
        }
        
        # Add instructor data if available
        if instructor_data:
            response_data['instructor'] = instructor_data
        
        # Add root passengers data for backward compatibility (standardized)
        response_data['passengers'] = [
            {
                'type': get_p_field(p, 'passenger_type', 'Adult').capitalize(),
                'gender': next((label for val, label in [('mr', 'Mr.'), ('mrs', 'Mrs.'), ('male', 'Mr.'), ('female', 'Mrs.')] if val in get_p_field(p, 'gender', 'mr').lower()), 'Mr.'),
                'first_name': get_p_field(p, 'first_name'),
                'last_name': get_p_field(p, 'last_name'),
                'middle_initial': get_p_field(p, 'middle_name') or get_p_field(p, 'middle_initial'),
                'nationality': get_p_field(p, 'nationality'),
                'passport': get_p_field(p, 'passport_number') or get_p_field(p, 'passport'),
                'passport_number': get_p_field(p, 'passport_number') or get_p_field(p, 'passport'),
                'seat_preference': get_p_field(p, 'seat_preference', 'Window'),
                'has_reservation': getattr(p, 'has_reservation', False),
                'is_pwd': getattr(p, 'passenger_category', '') == 'pwd',
                'passenger_category': get_p_field(p, 'passenger_category', 'none'),
                # Birth details
                'birth_day': str(p.date_of_birth.day).zfill(2) if hasattr(p.date_of_birth, 'day') else '01',
                'birth_month': p.date_of_birth.strftime('%B') if hasattr(p.date_of_birth, 'strftime') else 'January',
                'birth_year': str(p.date_of_birth.year) if hasattr(p.date_of_birth, 'year') else '1990',
                'date_of_birth': safe_date_format(p.date_of_birth, "%Y-%m-%d"),
            }
            for p in activity.passengers.all()
        ]
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"? Error building response data: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Failed to build response data.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def submit_grade(request, activity_id, student_id):
    """
    Submit or update a grade for a student's activity submission.
    """
    try:
        # 1. Verify instructor owns this activity
        activity = get_object_or_404(
            Activity,
            id=activity_id,
            section__instructor=request.user
        )
        
        # 2. Get the binding
        binding = get_object_or_404(
            ActivityStudentBinding,
            activity=activity,
            student_id=student_id
        )
        
        # 3. Update grade and status
        grade_value = request.data.get('grade')
        feedback_value = request.data.get('feedback', '')
        
        if grade_value is None:
            return Response({"error": "Grade is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        binding.grade = grade_value
        binding.feedback = feedback_value
        
        # Save the exact rubric breakdown components from the frontend
        rubric_breakdown = request.data.get('rubric_breakdown')
        if rubric_breakdown is not None:
            binding.rubric_breakdown = rubric_breakdown
            
        binding.status = 'graded'
        binding.is_released = False  # Wait for explicit release
        binding.save()
        
        return Response({
            "message": "Grade submitted successfully",
            "grade": float(binding.grade),
            "status": binding.status
        }, status=status.HTTP_200_OK)
    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ============================================================
# NEW: GET PRACTICE BOOKINGS (STUDENT)
# ============================================================
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def get_student_practice_bookings(request):
    """
    Get all practice bookings for the authenticated student.
    Returns status mapped to success/fail/pending.
    """
    try:
        # Get user's practice bookings, newest first
        bookings = Booking.objects.filter(
            user=request.user, 
            is_practice=True
        ).prefetch_related(
            'details',
            'details__schedule__flight__route__origin_airport',
            'details__schedule__flight__route__destination_airport'
        ).order_by('-created_at')
        
        practice_bookings_data = []
        
        for booking in bookings:
            # Map booking status to our UI categories
            ui_status = 'pending'
            if booking.status in ['Confirmed', 'Completed', 'checkin', 'boarding']:
                ui_status = 'success'
            elif booking.status in ['Cancelled', 'Failed']:
                ui_status = 'fail'
            
            # Extract first route info as a summary
            first_detail = booking.details.first()
            route_summary = "Unknown Route"
            departure_date = None
            
            if first_detail and first_detail.schedule and first_detail.schedule.flight:
                origin = first_detail.schedule.flight.route.origin_airport.code
                dest = first_detail.schedule.flight.route.destination_airport.code
                route_summary = f"{origin} ✈ {dest}"
                departure_date = first_detail.schedule.departure_time.isoformat()
                
                if booking.trip_type == 'round_trip':
                    route_summary = f"{origin} ⇄ {dest}"
                elif booking.trip_type == 'multi_city':
                    route_summary += " (Multi-City)"

            practice_bookings_data.append({
                "id": booking.id,
                "status": booking.status,
                "ui_status": ui_status,
                "total_amount": float(booking.total_amount),
                "trip_type": booking.get_trip_type_display(),
                "created_at": booking.created_at.isoformat(),
                "activity_code_used": booking.activity_code_used,
                "route_summary": route_summary,
                "departure_date": departure_date,
                "passenger_count": booking.details.count()
            })
            
        return Response({
            "practice_bookings": practice_bookings_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": f"Failed to load practice bookings: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==========================================
# ADMIN: LMS OVERVIEW STATS
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_lms_overview(request):
    """
    Admin-only LMS analytics endpoint.
    Returns aggregated stats for the dashboard overview page.
    """
    from django.db.models import Count, Avg, Q
    from django.db.models.functions import TruncWeek, TruncMonth
    from datetime import timedelta

    try:
        # ── 1. Activity Status Breakdown (all bindings) ──
        status_breakdown = (
            ActivityStudentBinding.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        status_map = {s['status']: s['count'] for s in status_breakdown}
        total_bindings = sum(status_map.values())

        # ── 2. Completion Rate per Section ──
        sections = Section.objects.all().prefetch_related('enrollments')
        section_stats = []
        for sec in sections:
            bindings = ActivityStudentBinding.objects.filter(activity__section=sec)
            total = bindings.count()
            completed = bindings.filter(status='completed').count()
            avg_grade = bindings.filter(grade__isnull=False).aggregate(avg=Avg('grade'))['avg']
            section_stats.append({
                'name': f"{sec.section_name} ({sec.section_code})",
                'total': total,
                'completed': completed,
                'rate': round((completed / total * 100), 1) if total > 0 else 0,
                'avg_grade': round(float(avg_grade), 1) if avg_grade else None,
                'enrolled': sec.enrollments.count(),
            })
        # Sort by completion rate descending
        section_stats.sort(key=lambda x: x['rate'], reverse=True)

        # ── 3. Submission Timeline (Dynamic Filtering) ──
        period = request.query_params.get('period', 'weekly')
        if period == 'weekly':
            # Last 8 weeks
            start_date = timezone.now() - timedelta(weeks=8)
            trunc_func = TruncWeek('submitted_at')
            date_format = '%b %d'
        elif period == 'monthly':
            # Last 6 months
            start_date = timezone.now() - timedelta(days=180)
            trunc_func = TruncMonth('submitted_at')
            date_format = '%b %Y'
        else:
            # Last 12 months (yearly view)
            start_date = timezone.now() - timedelta(days=365)
            trunc_func = TruncMonth('submitted_at')
            date_format = '%b'

        weekly = (
            ActivityStudentBinding.objects
            .filter(submitted_at__gte=start_date, submitted_at__isnull=False)
            .annotate(date_group=trunc_func)
            .values('date_group')
            .annotate(count=Count('id'))
            .order_by('date_group')
        )
        timeline = [
            {'week': w['date_group'].strftime(date_format), 'count': w['count']}
            for w in weekly
        ]

        # ── 4. Top Performing Students (highest avg grade) ──
        from app.models import Students
        top_students = (
            ActivityStudentBinding.objects
            .filter(grade__isnull=False)
            .values('student__first_name', 'student__last_name', 'student__student_number')
            .annotate(avg_grade=Avg('grade'), completed=Count('id', filter=Q(status='completed')))
            .order_by('-avg_grade')[:8]
        )
        top_list = [
            {
                'name': f"{s['student__first_name']} {s['student__last_name']}",
                'student_number': s['student__student_number'],
                'avg_grade': round(float(s['avg_grade']), 1),
                'completed': s['completed'],
            }
            for s in top_students
        ]

        # ── 5. Teacher Performance (Managerial) ──
        instructors = Instructor.objects.all().select_related('user')
        teacher_stats = []
        for instructor_obj in instructors:
            teacher = instructor_obj.user
            if not teacher:
                continue
            
            # Get sections for this teacher
            teacher_sections = Section.objects.filter(instructor=teacher)
            t_sections_count = teacher_sections.count()
            
            # Get all bindings for activities in these sections
            t_bindings = ActivityStudentBinding.objects.filter(activity__section__in=teacher_sections)
            t_total_tasks = t_bindings.count()
            t_completed_tasks = t_bindings.filter(status='completed').count()
            
            # Get total students across sections
            t_student_count = SectionEnrollment.objects.filter(section__in=teacher_sections).values('student').distinct().count()

            teacher_stats.append({
                'name': f"{teacher.first_name} {teacher.last_name}" if (teacher.first_name or teacher.last_name) else (instructor_obj.first_name + " " + instructor_obj.last_name if instructor_obj.first_name else teacher.username),
                'sections': t_sections_count,
                'students': t_student_count,
                'tasks': t_total_tasks,
                'completed': t_completed_tasks,
                'rate': round((t_completed_tasks / t_total_tasks * 100), 1) if t_total_tasks > 0 else 0
            })

        # ── 6. Totals ──
        totals = {
            'students': Students.objects.count(),
            'instructors': Instructor.objects.count(),
            'sections': Section.objects.count(),
            'activities': Activity.objects.count(),
            'bindings': total_bindings,
        }

        # ── 7. Students at Risk (Predictive Analysis) ──
        from django.db.models import F
        at_risk = []
        risk_query = (
            ActivityStudentBinding.objects
            .values('student__first_name', 'student__last_name', 'student__student_number')
            .annotate(
                avg_grade=Avg('grade'),
                total=Count('id'),
                completed_count=Count('id', filter=Q(status='completed'))
            )
        )
        
        for s in risk_query:
            reason = None
            if s['avg_grade'] and s['avg_grade'] < 75:
                reason = "Low Average Grade"
            elif s['total'] > 0 and (s['completed_count'] / s['total']) < 0.3:
                reason = "Low Engagement"
                
            if reason:
                at_risk.append({
                    'name': f"{s['student__first_name']} {s['student__last_name']}",
                    'student_number': s['student__student_number'],
                    'avg_grade': round(float(s['avg_grade']), 1) if s['avg_grade'] else 0,
                    'reason': reason,
                    'missing': s['total'] - s['completed_count']
                })
        
        # Sort by lowest grade and limit
        at_risk.sort(key=lambda x: x['avg_grade'])
        at_risk = at_risk[:10]

        # ── 8. Difficulty Map (Problematic Lessons) ──
        # Find activities with lowest average grades or high failure rates
        difficult_lessons = (
            ActivityStudentBinding.objects
            .values('activity__title')
            .annotate(
                avg_grade=Avg('grade'),
                total=Count('id'),
                completed_count=Count('id', filter=Q(status='completed')),
                failed_count=Count('id', filter=Q(is_failed_due_to_time=True))
            )
            .order_by('avg_grade')[:10]
        )
        
        difficulty_map = []
        for d in difficult_lessons:
            # Calculate failure rate or low score rate
            avg = float(d['avg_grade']) if d['avg_grade'] else 0
            if avg < 85 or (d['failed_count'] / d['total'] if d['total'] > 0 else 0) > 0.2:
                difficulty_map.append({
                    'title': d['activity__title'],
                    'avg_grade': round(avg, 1),
                    'failure_rate': round((d['failed_count'] / d['total'] * 100), 1) if d['total'] > 0 else 0,
                    'total_students': d['total']
                })

        return Response({
            'totals': totals,
            'status_breakdown': status_map,
            'section_stats': section_stats,
            'timeline': timeline,
            'top_students': top_list,
            'at_risk_students': at_risk,
            'teacher_stats': teacher_stats,
            'difficulty_map': difficulty_map,
        }, status=200)

    except Exception as e:
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def get_instructor_logs(request):
    """
    Fetch all logs for the current instructor.
    """
    logs = InstructorLog.objects.filter(instructor=request.user).order_by('-timestamp')
    
    data = []
    for log in logs:
        data.append({
            'id': log.id,
            'actor_name': f"{log.actor.first_name} {log.actor.last_name}" if log.actor else 'System',
            'actor_role': log.actor.userprofile.role if log.actor and hasattr(log.actor, 'userprofile') else 'N/A',
            'student_number': log.student.student_number if log.student else None,
            'action_type': log.action_type,
            'section_name': log.section_name,
            'activity_name': log.activity_name,
            'details': log.details,
            'device': log.device,
            'ip_address': log.ip_address,
            'is_csv': log.is_csv,
            'login_time': log.login_time.isoformat() if log.login_time else None,
            'logout_time': log.logout_time.isoformat() if log.logout_time else None,
            'timestamp': log.timestamp.isoformat()
        })
        
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def log_report_print(request):
    """
    Log when an instructor prints a report for an activity or section.
    """
    activity_id = request.data.get('activity_id')
    section_id = request.data.get('section_id')
    report_type = request.data.get('report_type', 'Grade Report')
    
    section_name = None
    activity_name = None
    
    if activity_id:
        try:
            activity = Activity.objects.get(id=activity_id, section__instructor=request.user)
            activity_name = activity.title
            section_name = activity.section.section_name
        except Activity.DoesNotExist:
            pass
    elif section_id:
        try:
            section = Section.objects.get(id=section_id, instructor=request.user)
            section_name = section.section_name
        except Section.DoesNotExist:
            pass
            
    log_instructor_event(
        request,
        action_type='REPORT_PRINTED',
        instructor=request.user,
        section_name=section_name,
        activity_name=activity_name,
        details=f"Instructor printed {report_type} for {activity_name or section_name or 'unspecified context'}."
    )
    
    return Response({"message": "Print action logged successfully."}, status=status.HTTP_200_OK)


# ============================================
# STUDENT NOTIFICATIONS
# ============================================

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def get_student_notifications(request):
    """
    Get all notifications for the authenticated student.
    Returns unread count and latest 20 notifications.
    """
    from .models import StudentNotification
    from app.models import Students
    
    try:
        # Get the student record
        student = None
        if hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
        else:
            student = Students.objects.get(user=request.user)
            
        if not student:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Get notifications
        notifications = StudentNotification.objects.filter(student=student)
        unread_count = notifications.filter(is_read=False).count()
        latest = notifications.order_by('-created_at')[:20]
        
        # Serialize
        data = []
        for notif in latest:
            data.append({
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'is_read': notif.is_read,
                'created_at': notif.created_at,
                'activity_id': notif.activity.id,
                'activity_code': notif.activity.activity_code,
            })
            
        return Response({
            'unread_count': unread_count,
            'notifications': data
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def mark_notifications_read(request):
    """
    Mark specific notifications or all notifications as read for the student.
    """
    from .models import StudentNotification
    from app.models import Students
    
    try:
        student = None
        if hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
        else:
            student = Students.objects.get(user=request.user)
            
        if not student:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        notification_ids = request.data.get('notification_ids', [])
        
        if notification_ids:
            # Mark specific as read
            StudentNotification.objects.filter(
                student=student, 
                id__in=notification_ids
            ).update(is_read=True)
        else:
            # Mark ALL as read
            StudentNotification.objects.filter(
                student=student, 
                is_read=False
            ).update(is_read=True)
            
        return Response({"status": "success"})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================
# INSTRUCTOR NOTIFICATIONS (DB PERSISTENCE)
# ============================================

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def get_instructor_notifications_read_status(request):
    """
    Get all notification IDs that this instructor has already read.
    """
    read_statuses = InstructorNotificationReadStatus.objects.filter(instructor=request.user)
    read_ids = list(read_statuses.values_list('notification_id', flat=True))
    
    return Response({
        "read_notification_ids": read_ids
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def mark_instructor_notifications_read(request):
    """
    Mark one or more notification IDs as read for this instructor.
    """
    notification_ids = request.data.get('notification_ids', [])
    if not isinstance(notification_ids, list):
        notification_ids = [notification_ids]
        
    created_count = 0
    for nid in notification_ids:
        if nid:
            obj, created = InstructorNotificationReadStatus.objects.get_or_create(
                instructor=request.user,
                notification_id=nid
            )
            if created:
                created_count += 1
                
    return Response({
        "message": f"Successfully marked {created_count} notifications as read.",
        "status": "success"
    }, status=status.HTTP_200_OK)

