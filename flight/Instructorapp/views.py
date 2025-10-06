from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.urls import reverse
from django import forms
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import redirect_to_login
from functools import wraps

# Models
from .models import Class, SectionGroup, Section, User, ExcelRowData, Booking, Passenger, MultiCityLeg

# Forms
import pandas as pd
import openpyxl
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.csrf import csrf_protect
from .forms import CustomUserCreationForm
from flightapp.models import Route, Schedule, Student
from datetime import date
from django.utils.timezone import make_aware
from django.utils import timezone

from django.core.serializers import serialize
import json
from decimal import Decimal
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.timezone import make_aware
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Booking, TaskScore, Section
from .decorators import role_required
User = get_user_model()

import random
from django.db import models

# ==================== CUSTOM DECORATOR ====================

def role_required(allowed_roles):
    """
    Decorator to check if user has required role.
    If not authenticated, redirects to login.
    If authenticated but wrong role, shows 403.
    
    Usage: @role_required(['Instructor'])
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='login')
        def wrapper(request, *args, **kwargs):
            # At this point user is guaranteed to be authenticated
            # Now check if they have the right role
            if request.user.role not in allowed_roles:
                role_text = ', '.join(allowed_roles)
                return HttpResponseForbidden(f"Access Denied: This page is only accessible to {role_text}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ==================== AUTHENTICATION VIEWS ====================
from .models import User, RegisteredUser

@csrf_protect
def registerPage(request):
    """User registration view - INSTRUCTOR ONLY"""
    if request.user.is_authenticated:
        if request.user.role == 'Instructor':
            return redirect('dashboard')
        else:
            logout(request)

    success = False
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            if user.role != 'Instructor':
                form.add_error('role', 'Only Instructors are allowed to register in this system')
                return render(request, "tutor/register.html", {
                    "form": form,
                    "errors": form.errors,
                    "success": False,
                })

            user.save()

            # ✅ Save registration log
            RegisteredUser.objects.create(
                user=user,
                username=user.username,
                email=user.email,
                role=user.role,
            )

            success = True
            messages.success(request, "Registration successful! Please login.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(
        request,
        "tutor/register.html",
        {
            "form": form,
            "errors": form.errors if form.errors else None,
            "success": success,
        },
    )

def loginPage(request):
    """User login view - INSTRUCTOR ONLY"""

    # ✅ Redirect if already logged in
    if request.user.is_authenticated:
        if request.user.role == 'Instructor':
            return redirect('dashboard')
        else:
            logout(request)

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # ✅ Check if username exists in database
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, "tutor/login.html", {
                "error": "❌ Username does not exist",
                "form": AuthenticationForm()
            })

        # ✅ Authenticate credentials
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, "tutor/login.html", {
                "error": "❌ Invalid password",
                "form": AuthenticationForm()
            })

        # ✅ Restrict login only to Instructors
        if user.role != 'Instructor':
            return render(request, "tutor/login.html", {
                "error": "⚠️ Only Instructors are allowed to login",
                "form": AuthenticationForm()
            })

        # ✅ Login success
        login(request, user)

        # Check if user was redirected by @login_required
        next_url = request.GET.get('next') or request.POST.get('next')
        return redirect(next_url or "dashboard")

    else:
        form = AuthenticationForm()

    return render(request, "tutor/login.html", {"form": form})


@login_required(login_url='login')
def logoutPage(request):
    """Logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


# ==================== STUDENT VIEWS (REMOVED - Students cannot login) ====================
# ==================== ADMIN VIEWS (REMOVED - Only Instructors allowed) ====================

# Student and Admin dashboards have been removed - ONLY INSTRUCTORS can login to this system


# ==================== INSTRUCTOR VIEWS ====================

@role_required(['Instructor'])
def dashboard(request):
    """Instructor dashboard - only accessible to instructors"""
    return render(request, 'tutor/Dashboard.html')


# ==================== CLASS MANAGEMENT ====================

@role_required(['Instructor'])
def Cclass(request):
    """List all classes for the logged-in instructor with search and pagination"""
    query = request.GET.get('q', '')
    
    # 🔒 SECURITY: Only fetch classes belonging to the logged-in instructor
    classes_list = Class.objects.filter(user=request.user).order_by('id')

    if query:
        # 🔒 SECURITY: Search is already scoped to user's classes only
        classes_list = classes_list.filter(
            Q(subject_code__icontains=query) |
            Q(subject_title__icontains=query) |
            Q(instructor__icontains=query) |
            Q(schedule__icontains=query) |
            Q(semester__icontains=query) |
            Q(academic_year__icontains=query)
        )

    paginator = Paginator(classes_list, 15)
    page_number = request.GET.get('page')
    classes = paginator.get_page(page_number)

    return render(request, 'tutor/Cclass.html', {
        'classes': classes,
        'query': query,
    })


@role_required(['Instructor'])
def CreateClass(request):
    """Create a new class"""
    if request.method == "POST":
        subject_code = request.POST.get("subject_code")
        subject_title = request.POST.get("subject_title")
        schedule = request.POST.get("schedule")
        semester = request.POST.get("semester")
        academic_year = request.POST.get("academic_year")

        # 🔒 SECURITY: Always assign the class to the logged-in instructor
        Class.objects.create(
            user=request.user,
            subject_code=subject_code,
            subject_title=subject_title,
            instructor=request.user.username,
            schedule=schedule,
            semester=semester,
            academic_year=academic_year
        )

        return redirect("Cclass")

    return render(request, "Create/CreateClass.html")


@role_required(['Instructor'])
def EditClass(request, id):
    """Edit an existing class"""
    # 🔒 SECURITY: Only fetch class if it belongs to the logged-in instructor
    cls = get_object_or_404(Class, id=id, user=request.user)

    if request.method == "POST":
        cls.subject_code = request.POST.get("subject_code")
        cls.subject_title = request.POST.get("subject_title")
        cls.instructor = request.POST.get("instructor") or request.user.get_full_name() or request.user.username
        cls.schedule = request.POST.get("schedule")
        cls.semester = request.POST.get("semester")
        cls.academic_year = request.POST.get("academic_year")
        
        # 🔒 SECURITY: Ensure user ownership doesn't change
        cls.user = request.user
        cls.save()
        
        messages.success(request, "Class updated successfully!")
        return redirect("Cclass")

    return render(request, "Cedit/editclass.html", {"cls": cls})


@role_required(['Instructor'])
def DeleteClass(request, id):
    """Delete a class"""
    # 🔒 SECURITY: Only delete class if it belongs to the logged-in instructor
    cls = get_object_or_404(Class, id=id, user=request.user)
    cls.delete()
    
    messages.success(request, "Class deleted successfully!")
    return redirect('Cclass')


# ==================== SECTION MANAGEMENT ====================


@role_required(['Instructor'])
def Section_List(request):
    """List all individual sections for the logged-in instructor"""
    # 🔒 SECURITY: Get all sections belonging ONLY to the instructor's section groups
    sections = Section.objects.filter(
        group__user=request.user
    ).select_related('group')

    colors = ["#1976d2", "#f57c00", "#388e3c", "#c2185b", "#6a1b9a", "#00838f", "#d81b60"]

    # Assign colors and ensure instructor is set
    sections_list = []
    for idx, section in enumerate(sections):
        section.card_color = colors[idx % len(colors)]
        section.instructor = section.group.instructor or request.user.username
        sections_list.append(section)

    return render(request, "tutor/Section_List.html", {"sections": sections_list})


@role_required(['Instructor'])
def Create_Section(request):
    """Create new section group with multiple sections"""
    if request.method == "POST":
        subject_code = request.POST.get("subject_code")
        num_sections = int(request.POST.get("num_sections"))

        # 🔒 SECURITY: Only fetch subject_title from instructor's own classes
        subject_title = Class.objects.filter(
            user=request.user, 
            subject_code=subject_code
        ).values_list("subject_title", flat=True).first()

        # 🔒 SECURITY: Always assign section group to the logged-in instructor
        section_group = SectionGroup.objects.create(
            user=request.user,
            subject_code=subject_code,
            subject_title=subject_title,
            instructor=request.user.username,
            num_sections=num_sections
        )

        for i in range(1, num_sections + 1):
            section_name = request.POST.get(f"section_{i}")
            section_schedule = request.POST.get(f"schedule_{i}")
            if section_name and section_schedule:
                Section.objects.create(
                    group=section_group, 
                    name=section_name, 
                    schedule=section_schedule
                )

        messages.success(request, "Section group created successfully!")
        return redirect("Section_List")

    # 🔒 SECURITY: Only show subject codes from instructor's own classes
    subject_codes = Class.objects.filter(user=request.user).values_list("subject_code", flat=True).distinct()
    classes = Class.objects.filter(user=request.user)

    context = {
        "subject_codes": subject_codes,
        "classes": classes,
        "section_range": range(1, 11),
    }
    return render(request, "Create/Create_Section.html", context)


@role_required(['Instructor'])
def Update_section(request, pk):
    """Update an individual section (not the entire group)"""
    # 🔒 SECURITY: Get the specific section only if it belongs to the instructor
    section = get_object_or_404(Section, pk=pk, group__user=request.user)
    group = section.group

    # 🔒 SECURITY: Fetch both subject_code and subject_title only from instructor's classes
    classes = list(
        Class.objects.filter(user=request.user)
        .values("subject_code", "subject_title")
        .distinct()
    )
    subject_codes = [c["subject_code"] for c in classes]

    if request.method == "POST":
        # Update only this specific section
        section.name = request.POST.get("section_name")
        section.schedule = request.POST.get("section_schedule")
        
        # Update subject code in the group if changed
        subject_code = request.POST.get("subject_code")
        if subject_code and subject_code != group.subject_code:
            group.subject_code = subject_code
            # Auto fetch subject title from instructor's own classes
            subject_title = next(
                (c["subject_title"] for c in classes if c["subject_code"] == subject_code), 
                ""
            )
            group.subject_title = subject_title
            
            # 🔒 SECURITY: Ensure group ownership doesn't change
            group.user = request.user
            group.save()
        
        section.save()

        messages.success(request, f"Section '{section.name}' updated successfully.")
        return redirect("Section_List")

    subject_title = next(
        (c["subject_title"] for c in classes if c["subject_code"] == group.subject_code), 
        ""
    )

    return render(request, "Cedit/editsection.html", {
        "section": section,
        "group": group,
        "subject_codes": subject_codes,
        "subject_title": subject_title,
        "username": request.user.username,
        "classes": classes,
    })


@role_required(['Instructor'])
def Delete_section(request, id):
    """Delete an individual section (not the entire group)"""
    # 🔒 SECURITY: Get the specific section only if it belongs to the instructor
    section = get_object_or_404(Section, id=id, group__user=request.user)
    section_name = section.name
    group = section.group
    
    # Delete the section
    section.delete()
    
    # Optional: If this was the last section in the group, delete the group too
    if not group.sections.exists():
        group.delete()
        messages.success(request, f"Section '{section_name}' deleted successfully! The section group was also removed as it had no remaining sections.")
    else:
        # Update the num_sections count in the group
        group.num_sections = group.sections.count()
        group.save()
        messages.success(request, f"Section '{section_name}' deleted successfully!")
    
    return redirect('Section_List')


# ==================== STUDENT MANAGEMENT IN SECTIONS ==================== #

@role_required(['Instructor'])
def create_students(request, pk):
    """Add students to a section from existing student database (flightapp)"""
    # 🔒 SECURITY: Only get section if it belongs to the logged-in instructor
    section = get_object_or_404(Section, pk=pk, group__user=request.user)
    
    # Fetch all available students from flightapp.models.Student
    all_students_qs = Student.objects.all().order_by('student_number')
    
    # Convert to format expected by JavaScript (matching Django's serialize format)
    all_students = []
    for student in all_students_qs:
        all_students.append({
            'pk': student.id,
            'fields': {
                'student_number': student.student_number,
                'first_name': student.first_name,
                'middle_initial': student.middle_initial or '',
                'last_name': student.last_name,
                'email': student.email,
                'phone': student.phone or '',
            }
        })
    
    # 🔒 SECURITY: Get existing student numbers only from this instructor's section
    existing_students = ExcelRowData.objects.filter(section=section)
    existing_student_numbers = []
    for row in existing_students:
        if row.data and 'Student Number' in row.data:
            existing_student_numbers.append(row.data['Student Number'])
    
    if request.method == "POST":
        selected_students_json = request.POST.get("selected_students")
        
        if selected_students_json:
            student_ids = json.loads(selected_students_json)
            added_count = 0
            
            for student_id in student_ids:
                try:
                    student = Student.objects.get(id=student_id)
                    
                    # Check if student already added to this section
                    if student.student_number in existing_student_numbers:
                        messages.warning(request, f"{student.student_number} is already in this section")
                        continue
                    
                    # Create row data from student
                    student_data = {
                        "Student Number": student.student_number,
                        "First Name": student.first_name,
                        "Middle Initial": student.middle_initial or "",
                        "Last Name": student.last_name,
                        "Email": student.email,
                        "Phone": student.phone or "",
                    }
                    
                    # 🔒 SECURITY: Student is added to instructor's section
                    ExcelRowData.objects.create(
                        section=section,
                        data=student_data
                    )
                    added_count += 1
                    
                except Student.DoesNotExist:
                    messages.error(request, f"Student with ID {student_id} not found")
            
            if added_count > 0:
                messages.success(request, f"Successfully added {added_count} student(s) to {section.name}")
        
        return redirect("Section_Detail", pk=section.pk)
    
    return render(request, "Create/Create_students.html", {
        "section": section,
        "all_students": json.dumps(all_students),
        "existing_student_numbers": json.dumps(existing_student_numbers),
    })


@role_required(['Instructor'])
def section_detail(request, pk):
    """View section details with students and bookings"""
    section = get_object_or_404(Section, pk=pk, group__user=request.user)
    row_objects = ExcelRowData.objects.filter(section=section)
    
    # Search Excel rows
    query = request.GET.get("q", "").strip()
    if query:
        row_objects = [row for row in row_objects if query.lower() in str(row.data).lower()]
    
    # Build headers and rows for display
    headers = []
    rows = []
    if row_objects:
        first_row = row_objects[0].data or {}
        headers = list(first_row.keys())
        for obj in row_objects:
            rows.append({"id": obj.id, "values": list(obj.data.values())})
    
    # Fetch Bookings with scores
    bookings = Booking.objects.filter(section=section).prefetch_related(
        'passengers',
        'legs',
        'scores'
    ).order_by('-created_at')
    
    # Process route information and calculate scores
    for booking in bookings:
        # Route display
        if booking.route:
            try:
                if booking.route.isdigit():
                    route_obj = Route.objects.select_related('origin_airport', 'destination_airport').get(id=int(booking.route))
                    booking.route_display = f"{route_obj.origin_airport.code}-{route_obj.destination_airport.code}"
                else:
                    booking.route_display = booking.route
            except (Route.DoesNotExist, ValueError):
                booking.route_display = booking.route
        else:
            booking.route_display = "Route not specified"
        
        # Calculate total current score and total max score
        scores = booking.scores.all()
        booking.total_score = sum(Decimal(str(score.score)) for score in scores)
        booking.total_max_score = sum(Decimal(str(score.max_score)) for score in scores)
        
        # Format field names for display
        for score in scores:
            score.display_name = score.field_name.replace('_', ' ').title()
    
    return render(request, "tutor/Section_Detail.html", {
        "section": section,
        "headers": headers,
        "rows": rows,
        "query": query,
        "bookings": bookings,
        "now": timezone.now(),
    })

@role_required(['Instructor'])
def delete_excel_row(request, pk):
    """Delete a student from a section"""
    # 🔒 SECURITY: Get the row and verify it belongs to instructor's section
    row = get_object_or_404(ExcelRowData, pk=pk, section__group__user=request.user)
    section_id = row.section.id
    
    row.delete()
    messages.success(request, "Student removed from section successfully!")
    return redirect("Section_Detail", pk=section_id)


@role_required(['Instructor'])
def edit_student(request, pk):
    """Edit student information in a section"""
    # 🔒 SECURITY: Get the student and verify it belongs to instructor's section
    student = get_object_or_404(ExcelRowData, pk=pk, section__group__user=request.user)
    section = student.section

    # 🔒 SECURITY: Get headers from first Excel row in instructor's section
    row_objects = ExcelRowData.objects.filter(section=section)
    headers = []
    if row_objects.exists():
        headers = list(row_objects.first().data.keys())

    if request.method == "POST":
        updated_data = {}
        for header in headers:
            updated_data[header] = request.POST.get(header, "")

        student.data = updated_data
        student.save()
        
        messages.success(request, "Student information updated successfully!")
        return redirect("Section_Detail", pk=section.pk)

    return render(request, "Cedit/Edit_student.html", {
        "section": section,
        "student": student,
        "headers": headers,
    })


# ==================== FLIGHT BOOKING ====================

@role_required(['Instructor'])
def book_flight(request, section_id):
    """
    Book a flight for a section.
    Accessible by: INSTRUCTORS ONLY (their own sections)
    """
    # 🔒 SECURITY: Only get section if it belongs to the logged-in instructor
    section = get_object_or_404(Section, id=section_id, group__user=request.user)

    # Fetch all routes
    routes = Route.objects.select_related("origin_airport", "destination_airport").all()

    # Fetch all schedules with related flight + routes
    schedules = Schedule.objects.select_related(
        "flight__route__origin_airport", 
        "flight__route__destination_airport"
    ).all()

    if request.method == "POST":
        trip_type = request.POST.get("trip_type", "one_way")
        route_id = request.POST.get("route")
        departure_date = request.POST.get("departure_date")
        return_date = request.POST.get("return_date") or None
        duration = request.POST.get("duration") or None
        travel_class = request.POST.get("travel_class", "economy")
        adults = int(request.POST.get("adults", 1))
        children = int(request.POST.get("children", 0))
        infants_on_lap = int(request.POST.get("infants_on_lap", 0))
        seat_preference = request.POST.get("seat_preference", "")

        if not departure_date:
            messages.error(request, "Departure date is required.")
            return render(request, "Create/Create_Instruction.html", {
                "section": section,
                "routes": routes,
                "schedules": schedules,
            })

        # Handle multi-city booking
        multi_city_data = []
        if trip_type == "multi_city":
            i = 1
            while f"from_{i}" in request.POST:
                origin = request.POST.get(f"from_{i}")
                dest = request.POST.get(f"to_{i}")
                date = request.POST.get(f"date_{i}")
                leg_duration = request.POST.get(f"duration_{i}") or None
                
                if origin and dest and date:
                    multi_city_data.append({
                        "origin": origin,
                        "destination": dest,
                        "date": parse_date(date),
                        "duration": make_aware(parse_datetime(leg_duration)) if leg_duration else None,
                    })
                i += 1

        # Store the original route format for display
        original_route = route_id
        
        # Handle round trip route parsing - keep original format for storage
        if trip_type == "round_trip" and route_id and "|" in route_id:
            # Keep the full route for display (e.g., "BXU-CEB|CEB-BXU")
            outbound_route_id, return_route_id = route_id.split("|")
        
        # 🔒 SECURITY: Create the booking for instructor's section
        booking = Booking.objects.create(
            section=section,
            trip_type=trip_type,
            route=original_route,
            departure_date=parse_date(departure_date),
            return_date=parse_date(return_date) if return_date else None,
            duration=make_aware(parse_datetime(duration)) if duration else None,
            adults=adults,
            children=children,
            infants_on_lap=infants_on_lap,
            travel_class=travel_class,
            seat_preference=seat_preference,
        )

        # Handle multi-city legs
        if multi_city_data:
            for leg in multi_city_data:
                MultiCityLeg.objects.create(
                    booking=booking,
                    origin=leg["origin"],
                    destination=leg["destination"],
                    departure_date=leg["date"],
                    duration=leg["duration"],
                )

        # Handle passengers
        passenger_count = int(request.POST.get("passenger_count", 1))
        for p in range(1, passenger_count + 1):
            first_name = request.POST.get(f"first_name_{p}", "").strip()
            last_name = request.POST.get(f"last_name_{p}", "").strip()
            middle_initial = request.POST.get(f"mi_{p}", "").strip() or None

            if not first_name or not last_name:
                continue

            # Parse date of birth
            dob_year = request.POST.get(f'year_{p}')
            dob_month = request.POST.get(f'month_{p}')
            dob_day = request.POST.get(f'day_{p}')
            dob = None
            if dob_year and dob_month and dob_day:
                try:
                    dob = parse_date(f"{dob_year}-{dob_month.zfill(2)}-{dob_day.zfill(2)}")
                except:
                    dob = None

            nationality = request.POST.get(f"nationality_{p}", "").strip()
            passport = request.POST.get(f"passport_{p}", "").strip()

            if first_name and last_name and dob and nationality and passport:
                Passenger.objects.create(
                    booking=booking,
                    title=request.POST.get(f"title_{p}", "N/A"),
                    first_name=first_name,
                    middle_initial=middle_initial,
                    last_name=last_name,
                    dob=dob,
                    nationality=nationality,
                    passport=passport,
                    has_declaration=bool(request.POST.get(f"declaration_{p}")),
                    is_pwd=bool(request.POST.get(f"pwd_{p}")),
                )

        messages.success(request, "Flight booking created successfully!")
        return redirect("Section_Detail", pk=section.id)

    return render(request, "Create/Create_Instruction.html", {
        "section": section,
        "routes": routes,
        "schedules": schedules,
    })

#Student Grade student_grade
@role_required(['Instructor'])
def Section_Task(request):
    """
    Display sections and bookings (tasks) for grade viewing.
    Shows only sections belonging to the logged-in user.
    """
    # 🔒 SECURITY: Fetch only sections belonging to the logged-in instructor
    user_sections = Section.objects.filter(group__user=request.user).order_by('name')
    
    # Get selected section from GET parameter
    selected_section_id = request.GET.get('section', '')
    selected_section = None
    tasks_data = []
    
    if selected_section_id and user_sections.exists():
        try:
            # 🔒 SECURITY: Ensure the selected section belongs to the logged-in instructor
            selected_section = Section.objects.get(pk=selected_section_id, group__user=request.user)
            
            # 🔒 SECURITY: Fetch all bookings (tasks) only from this instructor's section
            bookings = Booking.objects.filter(section=selected_section).prefetch_related(
                'passengers',
                'legs'
            ).order_by('-created_at')
            
            # Extract booking data for display as tasks
            task_counter = 1
            for booking in bookings:
                # Process route for display
                route_display = "Route not specified"
                if booking.route:
                    try:
                        if booking.route.isdigit():
                            route_obj = Route.objects.select_related(
                                'origin_airport', 
                                'destination_airport'
                            ).get(id=int(booking.route))
                            route_display = f"{route_obj.origin_airport.code} → {route_obj.destination_airport.code}"
                        else:
                            # Handle multi-city or round trip routes
                            route_display = booking.route.replace('|', ' ↔ ').replace('-', ' → ')
                    except (Route.DoesNotExist, ValueError):
                        route_display = booking.route
                
                # Build task description
                description = f"Flight booking for {booking.adults} adult(s)"
                if booking.children > 0:
                    description += f", {booking.children} child(ren)"
                if booking.infants_on_lap > 0:
                    description += f", {booking.infants_on_lap} infant(s)"
                description += f" • {booking.travel_class.title()} class • {booking.trip_type.replace('_', ' ').title()}"
                
                # Determine status
                status = "Upcoming"
                if booking.departure_date:
                    if booking.departure_date < timezone.now().date():
                        status = "Completed"
                    elif booking.departure_date == timezone.now().date():
                        status = "Today"
                
                tasks_data.append({
                    'id': booking.id,
                    'task_number': task_counter,
                    'title': f"Flight Booking - {route_display}",
                    'description': description,
                    'due_date': booking.departure_date,
                    'created_at': booking.created_at,
                    'status': status,
                })
                task_counter += 1
            
        except Section.DoesNotExist:
            pass
    
    return render(request, "Student/Section_task.html", {
        'user_sections': user_sections,
        'selected_section': selected_section,
        'tasks_data': tasks_data,
        'selected_section_id': selected_section_id,
    })



@role_required(['Instructor'])
def Edit_instruction(request, pk):
    """Edit instruction/booking with scoring system"""
    booking = get_object_or_404(Booking, pk=pk, section__group__user=request.user)
    section = booking.section
    
    # Get existing scores
    existing_scores = {score.field_name: score for score in booking.scores.all()}
    
    if request.method == "POST":
        # Update basic booking fields
        booking.trip_type = request.POST.get("trip_type", booking.trip_type)
        booking.route = request.POST.get("route", booking.route)
        booking.departure_date = parse_date(request.POST.get("departure_date")) or booking.departure_date
        booking.return_date = parse_date(request.POST.get("return_date")) if request.POST.get("return_date") else None
        booking.duration = make_aware(parse_datetime(request.POST.get("duration"))) if request.POST.get("duration") else None
        booking.adults = int(request.POST.get("adults", booking.adults))
        booking.children = int(request.POST.get("children", booking.children))
        booking.infants_on_lap = int(request.POST.get("infants_on_lap", booking.infants_on_lap))
        booking.travel_class = request.POST.get("travel_class", booking.travel_class)
        booking.seat_preference = request.POST.get("seat_preference", booking.seat_preference)
        
        # Process scores - only max_score, actual score starts at 0
        score_fields = [
            'trip_type', 'route', 'departure_date', 'return_date', 'duration',
            'adults', 'children', 'infants_on_lap', 'travel_class', 'seat_preference',
            'passenger_info'  # Single field for all passenger information
        ]
        
        # Delete scores that are no longer needed (max_score not provided or 0)
        for field in score_fields:
            max_score_value = request.POST.get(f"max_score_{field}")
            if not max_score_value or Decimal(max_score_value) == 0:
                if field in existing_scores:
                    existing_scores[field].delete()
        
        # Update or create scores with provided max_score values
        for field in score_fields:
            max_score_value = request.POST.get(f"max_score_{field}")
            
            if max_score_value and Decimal(max_score_value) > 0:
                max_score_decimal = Decimal(max_score_value)
                
                # Update or create score with 0 initial score
                if field in existing_scores:
                    score_obj = existing_scores[field]
                    score_obj.max_score = max_score_decimal
                    score_obj.score = Decimal('0.00')
                    score_obj.save()
                else:
                    TaskScore.objects.create(
                        booking=booking,
                        field_name=field,
                        score=Decimal('0.00'),
                        max_score=max_score_decimal
                    )
        
        # Calculate total max score from all saved scores
        all_scores = TaskScore.objects.filter(booking=booking)
        total_max = sum(score.max_score for score in all_scores)
        
        # Keep total_score at 0 until students complete the task
        booking.total_score = Decimal('0.00')
        
        # Check if task should be activated
        activate_task = request.POST.get("activate_task") == "true"
        
        if activate_task:
            # Generate task code if not exists
            if not booking.task_code:
                booking.task_code = booking.generate_unique_code()
            booking.is_active = True
            messages.success(request, f"Task activated successfully! Task Code: {booking.task_code} | Max Score: {total_max}")
        else:
            booking.is_active = False
            messages.success(request, f"Task updated successfully (not activated yet). Max Score: {total_max}")
        
        booking.save()
        
        return redirect("Section_Detail", pk=section.pk)
    
    return render(request, "Cedit/Edit_instruction.html", {
        "booking": booking,
        "section": section,
        "existing_scores": existing_scores,
    })

# Individual Grade view
@role_required(['Instructor'])
def Student_Grade(request):
    """
    Display students for a specific task (booking) in a section.
    Accessible by: INSTRUCTORS ONLY (their own sections)
    """
    # Get task_id, section_id, and task_number from GET parameters
    task_id = request.GET.get('task', '')
    section_id = request.GET.get('section', '')
    task_number = request.GET.get('task_number', '1')
    
    if not task_id or not section_id:
        messages.error(request, "Invalid request: Missing task or section parameter")
        return redirect('Section_Task')
    
    try:
        # 🔒 SECURITY: Get the section and verify it belongs to the logged-in instructor
        section = Section.objects.get(pk=section_id, group__user=request.user)
        
        # 🔒 SECURITY: Get the booking (task) with passengers and verify it belongs to this instructor's section
        booking = Booking.objects.prefetch_related('passengers', 'legs', 'scores').get(
            pk=task_id, 
            section=section
        )
        
        # Calculate total max score for this task
        task_scores = TaskScore.objects.filter(booking=booking)
        total_max_score = sum(score.max_score for score in task_scores)
        
        # Build task name using the task number
        task_name = f"Task {task_number}"
        
        # Process route for display - convert ID to airport codes
        route_display = "Route not specified"
        route_code = booking.route
        
        if booking.route:
            try:
                # Check if route is a numeric ID
                if booking.route.isdigit():
                    route_obj = Route.objects.select_related(
                        'origin_airport', 
                        'destination_airport'
                    ).get(id=int(booking.route))
                    route_code = f"{route_obj.origin_airport.code}-{route_obj.destination_airport.code}"
                    route_display = f"{route_obj.origin_airport.code} → {route_obj.destination_airport.code}"
                else:
                    # Route already in text format (e.g., "BXU-CEB" or "BXU-CEB|CEB-BXU")
                    route_code = booking.route
                    route_display = booking.route.replace('|', ' ↔ ').replace('-', ' → ')
            except (Route.DoesNotExist, ValueError):
                route_code = booking.route
                route_display = booking.route
        
        # Update booking object with processed route for template
        booking.route_code = route_code
        booking.route_display_text = route_display
        
        # Build task description
        task_description = f"{route_display} • {booking.trip_type.replace('_', ' ').title()}"
        task_details = f"Flight booking for {booking.adults} adult(s)"
        if booking.children > 0:
            task_details += f", {booking.children} child(ren)"
        if booking.infants_on_lap > 0:
            task_details += f", {booking.infants_on_lap} infant(s)"
        task_details += f" • {booking.travel_class.title()} class"
        
        # 🔒 SECURITY: Get all students only from this instructor's section
        row_objects = ExcelRowData.objects.filter(section=section)
        
        # Get all student bookings for this task (students who submitted this task)
        student_bookings = Booking.objects.filter(
            section=section,
            task_code=booking.task_code
        ).exclude(id=booking.id).prefetch_related('passengers', 'scores')
        
        # Create a dictionary mapping student numbers to their bookings
        student_booking_dict = {}
        for student_booking in student_bookings:
            passengers = student_booking.passengers.all()
            if passengers.exists():
                first_passenger = passengers.first()
                # Extract student number - adjust based on your model
                student_num = getattr(first_passenger, 'student_number', None)
                if student_num:
                    student_booking_dict[student_num] = student_booking
        
        # Build students data with their scores for this specific task
        students_data = []
        for obj in row_objects:
            if obj.data:
                student_number = obj.data.get('Student Number', 'N/A')
                
                # Check if this student has submitted the task
                if student_number in student_booking_dict:
                    student_booking = student_booking_dict[student_number]
                    
                    # Get the student's total score for this task
                    student_score = student_booking.total_score if student_booking.total_score else Decimal('0.00')
                    
                    # Calculate percentage
                    if total_max_score > 0:
                        percentage = round((float(student_score) / float(total_max_score)) * 100, 2)
                    else:
                        percentage = 0
                else:
                    # Student hasn't submitted this task yet
                    student_score = None
                    percentage = 0
                
                students_data.append({
                    'id': obj.id,
                    'student_number': student_number,
                    'first_name': obj.data.get('First Name', ''),
                    'middle_initial': obj.data.get('Middle Initial', ''),
                    'last_name': obj.data.get('Last Name', ''),
                    'email': obj.data.get('Email', ''),
                    'score': student_score,
                    'percentage': percentage,
                })
        
        return render(request, "Grades/Student_Grade.html", {
            'section': section,
            'booking': booking,  # This includes passengers and processed route
            'task_name': task_name,
            'task_description': task_description,
            'task_details': task_details,
            'task_due_date': booking.departure_date,
            'students_data': students_data,
            'total_max_score': total_max_score,
        })
        
    except Section.DoesNotExist:
        messages.error(request, "Access Denied: Section not found or you don't have permission")
        return redirect('Section_Task')
    except Booking.DoesNotExist:
        messages.error(request, "Task not found or you don't have permission to access it")
        return redirect('Section_Task')


@role_required(['Instructor'])
def Score_details(request, pk):
    """
    Display detailed score comparison between student submission and task requirements.
    pk = student's ExcelRowData id
    """
    # Get parameters from URL
    task_id = request.GET.get('task', '')
    section_id = request.GET.get('section', '')
    task_number = request.GET.get('task_number', '1')
    
    if not task_id or not section_id:
        messages.error(request, "Invalid request: Missing task or section parameter")
        return redirect('Section_Task')
    
    try:
        # 🔒 SECURITY: Get the section and verify it belongs to the logged-in instructor
        section = Section.objects.get(pk=section_id, group__user=request.user)
        
        # 🔒 SECURITY: Get the task booking (instructor's template) with all related data
        task_booking = Booking.objects.prefetch_related('passengers', 'scores').get(
            pk=task_id,
            section=section
        )
        
        # Get student data from ExcelRowData
        student_row = ExcelRowData.objects.get(pk=pk, section=section)
        student_data = student_row.data
        student_number = student_data.get('Student Number', 'N/A')
        student_name = f"{student_data.get('First Name', '')} {student_data.get('Last Name', '')}"
        
        # 🔒 SECURITY: Get student's submission for this specific task
        # First get all student bookings for this task
        student_bookings = Booking.objects.prefetch_related('passengers', 'scores').filter(
            section=section,
            task_code=task_booking.task_code
        ).exclude(id=task_booking.id)  # Exclude the instructor's template
        
        # Then find the one matching this student
        student_booking = None
        for booking in student_bookings:
            passengers = booking.passengers.all()
            if passengers.exists():
                first_passenger = passengers.first()
                passenger_student_num = getattr(first_passenger, 'student_number', None)
                if passenger_student_num == student_number:
                    student_booking = booking
                    break
        
        # Calculate scores
        task_scores = TaskScore.objects.filter(booking=task_booking)
        total_max_score = sum(score.max_score for score in task_scores)
        student_total_score = student_booking.total_score if student_booking else Decimal('0.00')
        
        # Build task name and description
        task_name = f"Task {task_number}"
        
        # Process route display
        route_display = "Route not specified"
        if task_booking.route:
            try:
                if task_booking.route.isdigit():
                    route_obj = Route.objects.select_related(
                        'origin_airport', 
                        'destination_airport'
                    ).get(id=int(task_booking.route))
                    route_display = f"{route_obj.origin_airport.code} → {route_obj.destination_airport.code}"
                else:
                    route_display = task_booking.route.replace('|', ' ↔ ').replace('-', ' → ')
            except (Route.DoesNotExist, ValueError):
                route_display = task_booking.route
        
        return render(request, "Grades/Score_details.html", {
            'section': section,
            'task_booking': task_booking,
            'student_booking': student_booking,
            'student_name': student_name,
            'student_number': student_number,
            'student_data': student_data,
            'total_max_score': total_max_score,
            'student_total_score': student_total_score,
            'task_name': task_name,
            'task_number': task_number,
            'route_display': route_display,
        })
        
    except Section.DoesNotExist:
        messages.error(request, "Access Denied: Section not found or you don't have permission")
        return redirect('Section_Task')
    except ExcelRowData.DoesNotExist:
        messages.error(request, "Student not found")
        return redirect('Section_Task')
    except Booking.DoesNotExist:
        messages.error(request, "Task not found")
        return redirect('Section_Task')