# ============================================================================
# DJANGO IMPORTS
# ============================================================================
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json

# ============================================================================
# DJANGO REST FRAMEWORK IMPORTS
# ============================================================================
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# ============================================================================
# PYTHON STANDARD LIBRARY
# ============================================================================
import random
import string
import traceback

# ============================================================================
# CROSS-APP IMPORTS (from app.models)
# ============================================================================
from app.models import AddOn, Airline, Airport, Students, UserProfile, Booking

# ============================================================================
# LOCAL APP IMPORTS (from fbs_instructor)
# ============================================================================
from .models import (
    Activity,
    ActivityPassenger,
    Instructor,
    Section,
    SectionEnrollment,
    ActivityStudentBinding,
    ActivityAddOn,
    UserSession  # NEW: Our custom session model
)
from .serializers import LoginSerializer, UserSerializer
from .authentication import MultiSessionTokenAuthentication  # NEW: Our custom auth
from .permissions import IsInstructor  # NEW: Custom permission

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
        print(f"? Profile found: {profile.role}")
    except UserProfile.DoesNotExist:
        print(f"? No profile found for user")
        return Response({"error": "Profile not found"}, status=status.HTTP_403_FORBIDDEN)

    # 4. Create a NEW session for this login (allows multiple simultaneous logins)
    try:
        session = UserSession.objects.create(
            user=user,
            session_token=UserSession.generate_token(),
            role=profile.role,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            is_active=True
        )
        print(f"? New session created: {session.session_token[:16]}... (Role: {session.role})")
    except Exception as e:
        print(f"? Session creation failed: {str(e)}")
        traceback.print_exc()
        return Response({"error": "Failed to create session"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 5. Determine Route based on role
    dashboard_route = '/'
    if profile.role == 'instructor':
        dashboard_route = '/instructor/dashboard'
    elif profile.role == 'student':
        dashboard_route = '/student/dashboard'
    elif profile.role == 'admin':
        dashboard_route = '/admin'

    print(f"? Login successful - Redirecting to: {dashboard_route}")
    print(f"{'='*60}\n")

    # 6. Return the UNIQUE session token (NOT the old DRF token)
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
    if not username or not email or not data.get('password') or not id_number:
        return Response({"error": "Missing required fields (username, email, password, ID number)"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": f"Username '{username}' is already taken."}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": f"Email '{email}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

    if role == 'student' and Students.objects.filter(student_number=id_number).exists():
        return Response({"error": f"Student ID '{id_number}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)
    
    if role == 'instructor' and Instructor.objects.filter(instructor_id=id_number).exists():
        return Response({"error": f"Instructor ID '{id_number}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # 1. Create the User (single source of truth)
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
            return Response({"message": "Section created successfully!"}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            print("? ERROR: Section code already exists")
            return Response({"error": "Section code already exists for your account."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"? ERROR creating section: {str(e)}")
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # 3. Handling the GET (Fetching data)
    sections = Section.objects.filter(instructor=user).values(
        'id', 'section_name', 'section_code', 'semester', 'academic_year', 'schedule', 'description'
    ).order_by('-id') 
    
    print(f"? Found {sections.count()} sections for instructor")
    print(f"{'='*60}\n")
    
    return Response({
        'sections': list(sections),
        'user': {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
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
        activities = Activity.objects.filter(section=section).order_by('-created_at')
        
        activities_data = []
        for activity in activities:
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
            })
        
        return Response({
            'id': section.id,
            'section_name': section.section_name,
            'section_code': section.section_code,
            'semester': section.semester,
            'academic_year': section.academic_year,
            'schedule': section.schedule,
            'description': section.description,
            'created_at': section.created_at,
            'activities': activities_data
        }, status=status.HTTP_200_OK)
        
    except Section.DoesNotExist:
        return Response({"error": "Section not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def delete_activity(request, section_id, activity_id):
    user = request.user
    
    try:
        section = Section.objects.get(id=section_id, instructor=user)
        activity = Activity.objects.get(id=activity_id, section=section)
        activity_title = activity.title
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
            
        return Response({"message": f"Successfully enrolled {student.first_name}!"}, status=status.HTTP_201_CREATED)
    

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
        from app.models import Students  # Import your Students model
        students = Students.objects.all()
        
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
                    required_travel_class=data.get('required_travel_class', 'economy'),
                    required_passengers=required_passengers,
                    required_children=required_children,
                    required_infants=required_infants,
                    require_passenger_details=data.get('require_passenger_details', False),
                    require_passport=data.get('require_passport', False),
                    instructions=data.get('instructions'),
                    total_points=float(data.get('total_points', 100)),
                    due_date=data.get('due_date'),
                    addon_grading_enabled=data.get('require_addons', False),
                    time_limit_minutes=data.get('time_limit_minutes') or None,
                )

                passengers_data = data.get('passengers', [])
                
                for index, p_data in enumerate(passengers_data):
                    passenger = ActivityPassenger.objects.create(
                        activity=activity,
                        first_name=p_data.get('first_name', ''),
                        middle_name=p_data.get('middle_name', ''),
                        last_name=p_data.get('last_name', ''),
                        passenger_type=p_data.get('passenger_type', 'adult'),
                        gender=p_data.get('gender', ''),
                        date_of_birth=p_data.get('date_of_birth') or None,
                        nationality=p_data.get('nationality', ''),
                        passport_number=p_data.get('passport_number', ''),
                        is_primary=(index == 0)
                    )

                    selected_addons = p_data.get('selected_addons', [])
                    
                    for addon_item in selected_addons:
                        try:
                            addon_instance = AddOn.objects.get(id=addon_item['id'])
                            ActivityAddOn.objects.create(
                                activity=activity,
                                addon=addon_instance,
                                passenger=passenger,
                                is_required=addon_item.get('is_required', False),
                                quantity_per_passenger=addon_item.get('quantity', 1),
                                notes=addon_item.get('notes', ''),
                                points_value=10.00
                            )
                        except AddOn.DoesNotExist:
                            continue
                        except Exception as e:
                            print(f"Error creating ActivityAddOn: {str(e)}")
                            continue

                return Response({
                    "message": "Activity created successfully!",
                    "activity_id": activity.id
                }, status=status.HTTP_201_CREATED)

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
                "gender": get_passenger_field(p, 'gender'),
                "type": get_passenger_field(p, 'passenger_type', 'Adult').capitalize(),
                "nationality": get_passenger_field(p, 'nationality'),
                "date_of_birth": get_passenger_field(p, 'date_of_birth'),
                "passport_number": get_passenger_field(p, 'passport_number'),
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
            "required_trip_type": activity.get_required_trip_type_display() if hasattr(activity, 'get_required_trip_type_display') else activity.required_trip_type,
            "required_origin": activity.required_origin if hasattr(activity, 'required_origin') else "",
            "required_destination": activity.required_destination if hasattr(activity, 'required_destination') else "",
            "required_departure_date": activity.required_departure_date.strftime("%B %d") if activity.required_departure_date else "",
            "required_return_date": activity.required_return_date.strftime("%B %d") if activity.required_return_date else "",
            "required_travel_class": activity.get_required_travel_class_display() if hasattr(activity, 'get_required_travel_class_display') else activity.required_travel_class,
            "required_passengers": activity.required_passengers if hasattr(activity, 'required_passengers') else 0,
            "required_children": activity.required_children if hasattr(activity, 'required_children') else 0,
            "required_infants": activity.required_infants if hasattr(activity, 'required_infants') else 0,
            "instructions": activity.instructions if hasattr(activity, 'instructions') else "",
            "due_date": activity.due_date.strftime("%B %d, %Y") if activity.due_date else "",
            "activity_code": activity.activity_code if hasattr(activity, 'activity_code') else "",
            "is_code_active": activity.is_code_active if hasattr(activity, 'is_code_active') else False,
            "passengers": passengers_data
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
        
        if activity.is_code_active and activity.activity_code:
            return Response({
                "message": "Activity is already activated",
                "activity_code": activity.activity_code,
                "already_active": True
            })
        
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
        
        enrolled_students_count = Activity_Student_Bind(activity)
        
        return Response({
            "message": "Activity Activated Successfully",
            "activity_code": activity.activity_code,
            "already_active": False,
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


def Activity_Student_Bind(activity):
    from .models import ActivityStudentBinding
    
    section = activity.section
    enrolled_students = SectionEnrollment.objects.filter(section=section).select_related('student')
    students_bound = 0
    
    for enrollment in enrolled_students:
        binding, created = ActivityStudentBinding.objects.get_or_create(
            activity=activity,
            student=enrollment.student,
            defaults={
                'assigned_at': timezone.now(),
                'status': 'assigned'
            }
        )
        
        if created:
            students_bound += 1
    
    return students_bound


@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def get_activity_submissions(request, activity_id):
    """
    Get all student submissions for a specific activity.
    Shows the status of each student enrolled in the section.
    """
    try:
        # 1. Get activity and verify instructor ownership
        activity = get_object_or_404(
            Activity.objects.select_related('section'),
            id=activity_id,
            section__instructor=request.user
        )
        
        # 2. Get all students enrolled in this section
        enrollments = SectionEnrollment.objects.filter(
            section=activity.section
        ).select_related('student', 'student__user')
        
        submissions_data = []
        
        for enrollment in enrollments:
            student = enrollment.student
            
            # Find the binding for this activity
            binding = ActivityStudentBinding.objects.filter(
                activity=activity,
                student=student
            ).first()
            
            # Find any confirmed booking for this activity by this student
            # We look for ANY booking linked to this activity for this user
            booking = Booking.objects.filter(
                user=student.user,
                activity=activity
            ).order_by('-created_at').first()
            
            submission = {
                "student_id": student.id,
                "student_number": student.student_number,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "status": binding.status if binding else "not_assigned",
                "binding_id": binding.id if binding else None,
                "grade": float(binding.grade) if (binding and binding.grade is not None) else None,
                "submitted_at": binding.submitted_at.isoformat() if binding and binding.submitted_at else None,
                "booking": None
            }
            
            if booking:
                submission["booking"] = {
                    "id": booking.id,
                    "status": booking.status,
                    "is_practice": booking.is_practice,
                    "total_amount": float(booking.total_amount),
                    "trip_type": booking.get_trip_type_display(),
                    "created_at": booking.created_at.isoformat(),
                    "details": [
                        {
                            "origin": d.schedule.flight.route.origin_airport.code,
                            "destination": d.schedule.flight.route.destination_airport.code,
                            "departure": d.schedule.departure_time.isoformat(),
                            "flight_number": d.schedule.flight.flight_number,
                            "seat_class": d.seat_class.name if d.seat_class else "N/A"
                        } for d in booking.details.all()
                    ],
                    "passengers": [
                        {
                            "name": p.get_full_name(),
                            "type": p.passenger_type
                        } for p in {d.passenger_id: d.passenger for d in booking.details.all()}.values()
                    ]
                }
                
                # If there's a confirmed booking but the binding is still 'assigned' or 'in_progress',
                # we should probably treat it as 'submitted' for the instructor's view
                if submission["status"] in ["assigned", "in_progress"] and booking.status == "Confirmed":
                    submission["status"] = "submitted"
            
            submissions_data.append(submission)
            
        return Response({
            "activity_id": activity.id,
            "activity_title": activity.title,
            "submissions": submissions_data,
            "total_students": len(submissions_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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




# ==========================================
# 3. STUDENT DASHBOARD (Session-Based)
# ==========================================
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])  # NEW: Use custom auth
@permission_classes([IsAuthenticated])
def student_dashboard(request):
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
            "debug_info": {
                "user_id": user.id,
                "user_email": user.email,
                "username": user.username
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    print(f"? Student record: {student.first_name} {student.last_name} (#{student.student_number})")
    
    # 3. Get enrolled section
    enrollment = SectionEnrollment.objects.filter(student=student).select_related('section').first()
    
    if not enrollment:
        print("?? Student not enrolled in any section")
        return Response({
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
            'session_info': {
                'session_id': session_obj.id,
                'role': session_obj.role,
                'last_activity': session_obj.last_activity.isoformat()
            }
        }, status=status.HTTP_200_OK)
    
    section = enrollment.section
    print(f"? Enrolled in: {section.section_name} ({section.section_code})")
    
    # 4. Get activities - either active OR already has progress (submitted/graded)
    from django.db.models import Q
    section_activities = Activity.objects.filter(
        Q(section=section) & 
        (Q(is_code_active=True) | Q(student_bindings__student=student, student_bindings__status__in=['submitted', 'graded']))
    ).distinct().order_by('-created_at')
    
    print(f"  Total visible activities: {section_activities.count()}")
    for act in section_activities:
        reason = "active" if act.is_code_active else "completed/graded"
        print(f"    - [{act.id}] {act.title} ({reason})")
    
    # 5. Build activities data
    from .models import ActivityStudentBinding
    
    activities_data = []
    for activity in section_activities:
        binding, created = ActivityStudentBinding.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={
                'assigned_at': timezone.now(),
                'status': 'assigned'
            }
        )
        
        if created:
            print(f"  ? Created binding: {activity.title}")
        
        # Search for a confirmed booking for this activity
        booking_obj = Booking.objects.filter(
            user=user,
            activity=activity,
            status='Confirmed',
            is_practice=False
        ).first()

        activities_data.append({
            'id': activity.id,
            'title': activity.title,
            'description': activity.description or '',
            'activity_type': activity.activity_type,
            'due_date': activity.due_date.strftime('%B %d, %Y') if activity.due_date else None,
            'total_points': float(activity.total_points),
            'created_at': activity.created_at.isoformat(),
            'required_trip_type': activity.required_trip_type,
            'required_origin': activity.required_origin,
            'required_destination': activity.required_destination,
            'required_travel_class': activity.required_travel_class,
            'required_passengers': activity.required_passengers,
            'required_children': activity.required_children,
            'required_infants': activity.required_infants,
            'status': binding.status,
            'assigned_at': binding.assigned_at.isoformat(),
            'is_active': activity.is_code_active,
            'section_id': section.id,
            'section_name': section.section_name,
            'section_code': section.section_code,
            'grade': float(binding.grade) if binding.grade is not None else None,
            'submitted_at': binding.submitted_at.isoformat() if binding.submitted_at else None,
            
            # ? NEW: Add completion status and booking ID
            'completed': booking_obj is not None,
            'confirmed_booking_id': booking_obj.id if booking_obj else None
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
    
    print(f"? Returning {len(activities_data)} activities")
    print(f"{'='*60}\n")
    
    return Response({
        'user': {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'student_number': student.student_number,
            'mi': student.mi if student.mi else '',
            'phone_number': student.phone_number if student.phone_number else ''
        },
        'section': section_data,
        'activities': activities_data,
        'total_activities': len(activities_data),
        'session_info': {
            'session_id': session_obj.id,
            'role': session_obj.role,
            'last_activity': session_obj.last_activity.isoformat()
        }
    }, status=status.HTTP_200_OK)



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
    
    # 3. Get the activity
    try:
        activity = Activity.objects.select_related('section', 'section__instructor').prefetch_related('passengers').get(
            id=activity_id, 
            is_code_active=True
        )
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
    
    # 5. Get or create ActivityStudentBinding
    try:
        binding, created = ActivityStudentBinding.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={
                'assigned_at': timezone.now(),
                'status': 'assigned'
            }
        )
        
        if created:
            print(f"? Created new activity binding")
        else:
            print(f"? Using existing binding - Status: {binding.status}")
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
                'gender': getattr(passenger, 'gender', 'Male'),
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
            'description': activity.description or activity.instructions or '',  # Use description OR instructions
            'activity_type': activity.activity_type,
            'due_date': safe_date_format(activity.due_date),
            'total_points': float(activity.total_points) if activity.total_points else 0.0,
            'created_at': safe_iso_format(activity.created_at),
            
            # Flight requirements - map from database field names
            'required_trip_type': activity.required_trip_type or '',
            'required_origin': activity.required_origin or '',
            'required_destination': activity.required_destination or '',
            'required_travel_class': activity.required_travel_class or '',
            'required_passengers': activity.required_passengers or 0,
            'required_children': activity.required_children or 0,
            'required_infants': activity.required_infants or 0,
            
            # Dates
            'departure_date': safe_iso_format(getattr(activity, 'required_departure_date', None)),
            'arrival_date': safe_iso_format(getattr(activity, 'required_return_date', None)),
            
            # Section info
            'section_id': activity.section.id,
            'section_name': activity.section.section_name,
            'section_code': activity.section.section_code,
            
            # Student progress
            'status': binding.status,
            'assigned_at': safe_iso_format(binding.assigned_at),
            'submitted_at': safe_iso_format(binding.submitted_at) if binding.submitted_at else None,
            'grade': float(binding.grade) if binding.grade is not None else None,
            'feedback': binding.feedback or '',
            
            # Activity status
            'is_active': activity.is_code_active,
            
            # ? NEW: Activity code for verification
            'activity_code': activity.activity_code or '',
            
            # ? NEW: Add completion status and booking ID
            'completed': booking_obj is not None,
            'confirmed_booking_id': booking_obj.id if booking_obj else None
        }
        
        response_data = {
            'activity': activity_data,
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
        
        # Add passenger data if available
        if passengers_data:
            response_data['passengers'] = passengers_data
        
        print(f"? Returning activity details:")
        print(f"   - Title: {activity.title}")
        print(f"   - Code: {activity.activity_code}")
        print(f"   - Origin: {activity.required_origin} ? Destination: {activity.required_destination}")
        print(f"   - Passengers: {len(passengers_data)}")
        print(f"{'='*60}\n")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"? Error building response data: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Failed to build response data.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
