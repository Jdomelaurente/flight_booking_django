from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib import messages
from .models import Section, Activity, ActivitySubmission, SectionEnrollment, ActivityPassenger
from flightapp.models import User, Student

# Helper function for session-based authentication
def get_current_user(request):
    """Get the current user from session"""
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    return None

def is_instructor(user):
    """Check if user is instructor"""
    return user and user.role == 'instructor'

# Authentication Views
def instructor_login(request):
    # If already logged in, redirect to home
    if get_current_user(request):
        return redirect('instructor_home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
            if user.password == password:
                # Manual session-based login
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['role'] = user.role
                request.session.set_expiry(86400)  # 24 hours
                
                messages.success(request, f'Welcome back {username}!')
                return redirect('instructor_home')
            else:
                messages.error(request, 'Invalid credentials')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
    
    template = loader.get_template('instructorapp/auth/login.html')
    context = {}
    return HttpResponse(template.render(context, request))

def instructor_register(request):
    # If already logged in, redirect to home
    if get_current_user(request):
        return redirect('instructor_home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = 'instructor'
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        else:
            user = User.objects.create(
                username=username,
                email=email,
                password=password,
                role=role
            )
            # Manual session-based login after registration
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['role'] = user.role
            request.session.set_expiry(86400)  # 24 hours
            
            messages.success(request, f'Account created successfully! Welcome {username}')
            return redirect('instructor_home')
    
    template = loader.get_template('instructorapp/auth/register.html')
    context = {}
    return HttpResponse(template.render(context, request))

def logout_view(request):
    # Manual logout
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('instructor_login')

# Instructor Views
def instructor_home(request):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    # Handle section creation from modal form
    if request.method == 'POST':
        section_name = request.POST.get('section_name')
        section_code = request.POST.get('section_code')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        schedule = request.POST.get('schedule')
        description = request.POST.get('description')
        
        # Basic validation
        if not section_name or not section_code or not semester or not academic_year:
            messages.error(request, 'Please fill all required fields')
        elif Section.objects.filter(section_code=section_code).exists():
            messages.error(request, 'Section code already exists')
        else:
            # Create section
            section = Section.objects.create(
                section_name=section_name,
                section_code=section_code,
                semester=semester,
                academic_year=academic_year,
                schedule=schedule,
                description=description,
                instructor=user
            )
            messages.success(request, f'Section {section.section_code} created successfully!')
            return redirect('instructor_home')
    
    sections = Section.objects.filter(instructor=user)
    activities = Activity.objects.filter(section__instructor=user)
    
    template = loader.get_template('instructorapp/instructor/home.html')
    context = {
        'sections': sections,
        'activities': activities,
        'total_students': SectionEnrollment.objects.filter(section__instructor=user).count(),
        'current_user': user,
    }
    return HttpResponse(template.render(context, request))

def instructor_section(request):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    # Handle section creation
    if request.method == 'POST':
        section_name = request.POST.get('section_name')
        section_code = request.POST.get('section_code')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        schedule = request.POST.get('schedule')
        description = request.POST.get('description')
        
        # Basic validation
        if not section_name or not section_code or not semester or not academic_year:
            messages.error(request, 'Please fill all required fields')
        elif Section.objects.filter(section_code=section_code).exists():
            messages.error(request, 'Section code already exists')
        else:
            # Create section
            section = Section.objects.create(
                section_name=section_name,
                section_code=section_code,
                semester=semester,
                academic_year=academic_year,
                schedule=schedule,
                description=description,
                instructor=user
            )
            messages.success(request, f'Section {section.section_code} created successfully!')
            return redirect('instructor_section')
    
    sections = Section.objects.filter(instructor=user)
    
    template = loader.get_template('instructorapp/instructor/section_detail.html')
    context = {
        'sections': sections,
        'current_user': user,
    }
    return HttpResponse(template.render(context, request))

def instructor_activity(request):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    activities = Activity.objects.filter(section__instructor=user)
    
    template = loader.get_template('instructorapp/instructor/activity/activity.html')
    context = {
        'activities': activities,
        'current_user': user,
    }
    return HttpResponse(template.render(context, request))

# Add these additional views for full functionality
def create_activity(request, section_id):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    section = get_object_or_404(Section, id=section_id, instructor=user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        activity_type = request.POST.get('activity_type', 'Flight Booking')
        required_trip_type = request.POST.get('required_trip_type', 'one_way')
        required_origin = request.POST.get('required_origin', '')
        required_destination = request.POST.get('required_destination', '')
        required_departure_date = request.POST.get('required_departure_date')
        required_return_date = request.POST.get('required_return_date')
        required_travel_class = request.POST.get('required_travel_class', 'economy')
        
        # Passenger counts - with proper default handling
        required_passengers = request.POST.get('required_passengers', '1')
        required_children = request.POST.get('required_children', '0')
        required_infants = request.POST.get('required_infants', '0')
        
        # Passenger information requirements
        require_passenger_details = request.POST.get('require_passenger_details') == 'on'
        
        required_max_price = request.POST.get('required_max_price')
        instructions = request.POST.get('instructions')
        total_points = request.POST.get('total_points', '100')
        due_date = request.POST.get('due_date')
        time_limit_minutes = request.POST.get('time_limit_minutes')
        
        # Basic validation
        if not title or not instructions or not due_date:
            messages.error(request, 'Please fill all required fields')
            return redirect('section_detail', section_id=section_id)
        
        try:
            # Convert passenger counts with error handling
            required_passengers_int = int(required_passengers) if required_passengers and required_passengers.strip() else 1
            required_children_int = int(required_children) if required_children and required_children.strip() else 0
            required_infants_int = int(required_infants) if required_infants and required_infants.strip() else 0
            
            # Validate passenger counts
            if required_passengers_int < 1:
                messages.error(request, 'At least one adult passenger is required')
                return redirect('section_detail', section_id=section_id)
            
            # Validate infants don't exceed adults
            if required_infants_int > required_passengers_int:
                messages.error(request, 'Number of infants cannot exceed number of adults')
                return redirect('section_detail', section_id=section_id)
            
            # Create activity
            activity = Activity.objects.create(
                title=title,
                description=description or "",
                activity_type=activity_type,
                section=section,
                required_trip_type=required_trip_type,
                required_origin=required_origin,
                required_destination=required_destination,
                required_departure_date=required_departure_date if required_departure_date else None,
                required_return_date=required_return_date if required_return_date else None,
                required_travel_class=required_travel_class,
                required_passengers=required_passengers_int,
                required_children=required_children_int,
                required_infants=required_infants_int,
                require_passenger_details=require_passenger_details,
                required_max_price=float(required_max_price) if required_max_price and required_max_price.strip() else None,
                instructions=instructions,
                total_points=float(total_points) if total_points and total_points.strip() else 100.00,
                due_date=due_date,
                time_limit_minutes=int(time_limit_minutes) if time_limit_minutes and time_limit_minutes.strip() else None
            )
            
            # Handle passenger details if required
            if require_passenger_details:
                passenger_first_names = request.POST.getlist('passenger_first_name[]')
                passenger_middle_names = request.POST.getlist('passenger_middle_name[]')
                passenger_last_names = request.POST.getlist('passenger_last_name[]')
                passenger_genders = request.POST.getlist('passenger_gender[]')
                passenger_dobs = request.POST.getlist('passenger_dob[]')
                passenger_nationalities = request.POST.getlist('passenger_nationality[]')
                
                # Create passenger objects only for valid entries
                passengers_created = 0
                for i in range(len(passenger_first_names)):
                    # Check if all required fields are filled
                    if (passenger_first_names[i].strip() and 
                        passenger_last_names[i].strip() and 
                        passenger_genders[i] and 
                        passenger_dobs[i] and 
                        passenger_nationalities[i].strip()):
                        
                        ActivityPassenger.objects.create(
                            activity=activity,
                            first_name=passenger_first_names[i].strip(),
                            middle_name=passenger_middle_names[i].strip() if passenger_middle_names[i] else None,
                            last_name=passenger_last_names[i].strip(),
                            gender=passenger_genders[i],
                            date_of_birth=passenger_dobs[i],
                            nationality=passenger_nationalities[i].strip(),
                            is_primary=(i == 0)  # First passenger is primary
                        )
                        passengers_created += 1
                
                if passengers_created == 0 and require_passenger_details:
                    messages.warning(request, 'Activity created but no passenger details were provided despite the requirement.')
            
            messages.success(request, f'Activity "{activity.title}" created successfully!')
            return redirect('section_detail', section_id=section_id)
            
        except ValueError as e:
            messages.error(request, f'Invalid number format: {str(e)}')
            return redirect('section_detail', section_id=section_id)
        except Exception as e:
            messages.error(request, f'Error creating activity: {str(e)}')
            return redirect('section_detail', section_id=section_id)
    
    # If GET request, redirect to section detail
    return redirect('section_detail', section_id=section_id)


# In your section_detail view in views.py
def section_detail(request, section_id):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    section = get_object_or_404(Section, id=section_id, instructor=user)
    enrollments = SectionEnrollment.objects.filter(section=section)
    activities = Activity.objects.filter(section=section)
    
    # Get airports from flightapp
    from flightapp.models import Airport
    airports = Airport.objects.all()
    
    # Handle student enrollment
    if request.method == 'POST' and 'enroll_student' in request.POST:
        student_number = request.POST.get('student_number')
        try:
            student = Student.objects.get(student_number=student_number)
            if not SectionEnrollment.objects.filter(section=section, student=student).exists():
                SectionEnrollment.objects.create(section=section, student=student)
                messages.success(request, f'Student {student.student_number} enrolled successfully!')
            else:
                messages.warning(request, f'Student {student.student_number} is already enrolled.')
        except Student.DoesNotExist:
            messages.error(request, f'Student with number {student_number} not found.')
        return redirect('section_detail', section_id=section_id)
    
    template = loader.get_template('instructorapp/instructor/section_detail.html')
    context = {
        'section': section,
        'enrollments': enrollments,
        'activities': activities,
        'airports': airports,  # Add airports to context
        'current_user': user,
    }
    return HttpResponse(template.render(context, request))


def edit_activity(request, activity_id):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    activity = get_object_or_404(Activity, id=activity_id, section__instructor=user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        activity_type = request.POST.get('activity_type', 'Flight Booking')
        required_trip_type = request.POST.get('required_trip_type', 'one_way')
        required_origin = request.POST.get('required_origin', '')
        required_destination = request.POST.get('required_destination', '')
        required_departure_date = request.POST.get('required_departure_date')
        required_return_date = request.POST.get('required_return_date')
        required_travel_class = request.POST.get('required_travel_class', 'economy')
        
        # Passenger counts - with proper default handling
        required_passengers = request.POST.get('required_passengers', '1')
        required_children = request.POST.get('required_children', '0')
        required_infants = request.POST.get('required_infants', '0')
        
        # Passenger information requirements
        require_passenger_details = request.POST.get('require_passenger_details') == 'on'
        
        required_max_price = request.POST.get('required_max_price')
        instructions = request.POST.get('instructions')
        total_points = request.POST.get('total_points', '100')
        due_date = request.POST.get('due_date')
        time_limit_minutes = request.POST.get('time_limit_minutes')
        
        # Basic validation
        if not title or not instructions or not due_date:
            messages.error(request, 'Please fill all required fields')
            return redirect('edit_activity', activity_id=activity_id)
        
        try:
            # Convert passenger counts with error handling
            required_passengers_int = int(required_passengers) if required_passengers else 1
            required_children_int = int(required_children) if required_children else 0
            required_infants_int = int(required_infants) if required_infants else 0
            
            # Update activity
            activity.title = title
            activity.description = description or ""
            activity.activity_type = activity_type
            activity.required_trip_type = required_trip_type
            activity.required_origin = required_origin
            activity.required_destination = required_destination
            activity.required_departure_date = required_departure_date if required_departure_date else None
            activity.required_return_date = required_return_date if required_return_date else None
            activity.required_travel_class = required_travel_class
            activity.required_passengers = required_passengers_int
            activity.required_children = required_children_int
            activity.required_infants = required_infants_int
            activity.require_passenger_details = require_passenger_details
            activity.required_max_price = float(required_max_price) if required_max_price else None
            activity.instructions = instructions
            activity.total_points = float(total_points) if total_points else 100.00
            activity.due_date = due_date
            activity.time_limit_minutes = int(time_limit_minutes) if time_limit_minutes else None
            
            activity.save()
            
            # Handle passenger details if required
            if require_passenger_details:
                # Delete existing passengers
                activity.passengers.all().delete()
                
                passenger_first_names = request.POST.getlist('passenger_first_name[]')
                passenger_middle_names = request.POST.getlist('passenger_middle_name[]')
                passenger_last_names = request.POST.getlist('passenger_last_name[]')
                passenger_genders = request.POST.getlist('passenger_gender[]')
                passenger_dobs = request.POST.getlist('passenger_dob[]')
                passenger_nationalities = request.POST.getlist('passenger_nationality[]')
                passenger_types = request.POST.getlist('passenger_type[]')
                passenger_is_primary = request.POST.getlist('passenger_is_primary[]')
                
                # Create passenger objects only for valid entries
                for i in range(len(passenger_first_names)):
                    # Check if all required fields are filled
                    if (passenger_first_names[i].strip() and 
                        passenger_last_names[i].strip() and 
                        passenger_genders[i] and 
                        passenger_dobs[i] and 
                        passenger_nationalities[i].strip()):
                        
                        ActivityPassenger.objects.create(
                            activity=activity,
                            first_name=passenger_first_names[i].strip(),
                            middle_name=passenger_middle_names[i].strip() if passenger_middle_names[i] else None,
                            last_name=passenger_last_names[i].strip(),
                            gender=passenger_genders[i],
                            date_of_birth=passenger_dobs[i],
                            nationality=passenger_nationalities[i].strip(),
                            is_primary=(i == 0)  # First passenger is primary
                        )
            
            messages.success(request, f'Activity "{activity.title}" updated successfully!')
            return redirect('section_detail', section_id=activity.section.id)
            
        except Exception as e:
            messages.error(request, f'Error updating activity: {str(e)}')
            return redirect('edit_activity', activity_id=activity_id)
    
    # Get airports from flightapp for the form
    from flightapp.models import Airport
    airports = Airport.objects.all()
    
    template = loader.get_template('instructorapp/instructor/activity/edit_activity.html')
    context = {
        'activity': activity,
        'airports': airports,
        'current_user': user,
    }
    return HttpResponse(template.render(context, request))

def delete_activity(request, activity_id):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    activity = get_object_or_404(Activity, id=activity_id, section__instructor=user)
    
    if request.method == 'POST':
        activity_title = activity.title
        section_id = activity.section.id
        activity.delete()
        messages.success(request, f'Activity "{activity_title}" deleted successfully!')
        return redirect('section_detail', section_id=section_id)
    
    # If GET request, return JSON for modal
    return JsonResponse({
        'title': activity.title,
        'section_code': activity.section.section_code,
        'activity_type': activity.activity_type,
        'due_date': activity.due_date.strftime("%B %d, %Y"),
        'submissions_count': activity.submissions.count()
    })

def activate_activity(request, activity_id):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    activity = get_object_or_404(Activity, id=activity_id, section__instructor=user)
    
    if request.method == 'POST':
        expiration_hours = int(request.POST.get('expiration_hours', 24))
        activity.activate_code(expiration_hours)
        messages.success(request, f'Activity code activated: {activity.activity_code}')
    
    return redirect('section_detail', section_id=activity.section.id)


def activity_detail(request, activity_id):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    activity = get_object_or_404(Activity, id=activity_id, section__instructor=user)
    
    # Get additional context for the template
    total_passengers = activity.get_total_passengers()
    has_passenger_details = activity.passengers.exists()
    
    template = loader.get_template('instructorapp/instructor/activity/activity_detail.html')
    context = {
        'activity': activity,
        'total_passengers': total_passengers,
        'has_passenger_details': has_passenger_details,
        'current_user': user,
    }
    return HttpResponse(template.render(context, request))

def activity_submissions(request, activity_id):
    user = get_current_user(request)
    if not user:
        return redirect('instructor_login')
    
    if not is_instructor(user):
        messages.error(request, 'Access denied. Instructor role required.')
        return redirect('instructor_login')
    
    activity = get_object_or_404(Activity, id=activity_id, section__instructor=user)
    submissions = ActivitySubmission.objects.filter(activity=activity)
    
    template = loader.get_template('instructorapp/instructor/activity/activity_submissions.html')
    context = {
        'activity': activity,
        'submissions': submissions,
        'current_user': user,
    }
    return HttpResponse(template.render(context, request))