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
# Models
from .models import Class, SectionGroup, Section, User, ExcelRowData, Booking, Passenger

# Forms
import pandas as pd
import openpyxl
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_protect
from .forms import CustomUserCreationForm
from flightapp.models import Route, Schedule , Student
from flightapp.models import Route   # ✅ import Route from flightapp
from .models import MultiCityLeg
from django.utils.dateparse import parse_date, parse_datetime
from datetime import date
from django.utils.timezone import make_aware
User = get_user_model()
from django.utils import timezone

from django.core.serializers import serialize
import json

@csrf_protect
def registerPage(request):
    # ✅ Redirect if already logged in
    if request.user.is_authenticated:
        if request.user.role == 'Instructor':
            return redirect('dashboard')
        elif request.user.role == 'Student':
            return redirect('student_dashboard')
        elif request.user.role == 'Admin':
            return redirect('admin_dashboard')
    
    success = False
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # User with role is saved to database
            success = True
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
    # ✅ Redirect if already logged in
    if request.user.is_authenticated:
        if request.user.role == 'Instructor':
            return redirect('dashboard')
        elif request.user.role == 'Student':
            return redirect('student_dashboard')
        elif request.user.role == 'Admin':
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            return render(request, "tutor/login.html", {
                "error": "Username does not exist",
                "form": AuthenticationForm()
            })

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # ✅ Check for 'next' parameter to redirect to intended page
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            
            # Role-based redirect
            if user.role == 'Instructor':
                return redirect("dashboard")  # dashboard.html for Instructor
            elif user.role == 'Student':
                return redirect("student_dashboard")  # Student_dashboard.html
            elif user.role == 'Admin':
                return redirect("admin_dashboard")  # admin dashboard if you have one
            else:
                return redirect("dashboard")  # default fallback
        else:
            return render(request, "tutor/login.html", {
                "error": "Invalid password",
                "form": AuthenticationForm()
            })
    else:
        form = AuthenticationForm()
    return render(request, "tutor/login.html", {"form": form})

# NEW: Student dashboard view
@login_required(login_url='login')
def student_dashboard(request):
    # ✅ Ensure only students can access this
    if request.user.role != 'Student':
        return HttpResponseForbidden("Access Denied: Students only")
    
    return render(request, 'tutor/Student_dashboard.html')

@login_required(login_url='login')
def admin_dashboard(request):
    # ✅ Ensure only admins can access this
    if request.user.role != 'Admin':
        return HttpResponseForbidden("Access Denied: Admins only")
    
    return render(request, 'tutor/admin_dashboard.html')

# Logout view
@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect("login")

# Create your views here.
@login_required(login_url='login')
def dashboard(request):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    return render(request, 'tutor/Dashboard.html')

# Class List

@login_required(login_url='login')
def Cclass(request):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    query = request.GET.get('q', '')
    classes_list = Class.objects.filter(user=request.user).order_by('id')  # ✅ only user's classes

    if query:
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



# Create Class
@login_required(login_url='login')
def CreateClass(request):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    if request.method == "POST":
        subject_code = request.POST.get("subject_code")
        subject_title = request.POST.get("subject_title")
        schedule = request.POST.get("schedule")
        semester = request.POST.get("semester")
        academic_year = request.POST.get("academic_year")

        Class.objects.create(
            user=request.user,  # ✅ link to logged in user
            subject_code=subject_code,
            subject_title=subject_title,
            instructor=request.user.username,  # ✅ auto use logged in instructor
            schedule=schedule,
            semester=semester,
            academic_year=academic_year
        )

        messages.success(request, "Successfully Created!")
        return redirect("CreateClass")

    return render(request, "Create/CreateClass.html")

#Edit Class


@login_required(login_url='login')
def EditClass(request, id):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    cls = get_object_or_404(Class, id=id, user=request.user)


    if request.method == "POST":
        cls.subject_code = request.POST.get("subject_code")
        cls.subject_title = request.POST.get("subject_title")
        cls.instructor = request.POST.get("instructor") or request.user.get_full_name() or request.user.username
        cls.schedule = request.POST.get("schedule")
        cls.semester = request.POST.get("semester")
        cls.academic_year = request.POST.get("academic_year")
        cls.save()
        return redirect("Cclass")

    return render(request, "Cedit/editclass.html", {"cls": cls})

#Delete Class


@login_required(login_url='login')
def DeleteClass(request, id):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    cls = get_object_or_404(Class, id=id, user=request.user)

    cls.delete()
    return redirect('Cclass')




@login_required(login_url='login')
def Section_List(request):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    groups = SectionGroup.objects.filter(user=request.user).prefetch_related("sections")

    colors = ["#1976d2", "#f57c00", "#388e3c", "#c2185b", "#6a1b9a", "#00838f", "#d81b60"]

    # Fetch subject codes + titles (unique)
    class_map = {
        c["subject_code"]: c["subject_title"]
        for c in Class.objects.filter(user=request.user)
        .values("subject_code", "subject_title")
        .distinct()
    }

    for idx, group in enumerate(groups):
        group.card_color = colors[idx % len(colors)]
        group.subject_title = class_map.get(group.subject_code, "No Title")

        # Always ensure instructor is set
        if not getattr(group, "instructor", None):
            group.instructor = request.user.username

    return render(request, "tutor/Section_List.html", {"groups": groups})

@login_required(login_url='login')
def Create_Section(request):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    if request.method == "POST":
        subject_code = request.POST.get("subject_code")
        num_sections = int(request.POST.get("num_sections"))

        subject_title = Class.objects.filter(user=request.user, subject_code=subject_code).values_list("subject_title", flat=True).first()

        section_group = SectionGroup.objects.create(
            user=request.user,  # ✅
            subject_code=subject_code,
            subject_title=subject_title,
            instructor=request.user.username,  # ✅ auto
            num_sections=num_sections
        )

        for i in range(1, num_sections + 1):
            section_name = request.POST.get(f"section_{i}")
            section_schedule = request.POST.get(f"schedule_{i}")
            if section_name and section_schedule:
                Section.objects.create(group=section_group, name=section_name, schedule=section_schedule)

        return redirect("Section_List")

    subject_codes = Class.objects.filter(user=request.user).values_list("subject_code", flat=True).distinct()
    classes = Class.objects.filter(user=request.user)

    context = {
        "subject_codes": subject_codes,
        "classes": classes,
        "section_range": range(1, 11),
    }
    return render(request, "Create/Create_Section.html", context)





# Update Section View


@login_required(login_url='login')
def Update_section(request, pk):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    group = get_object_or_404(SectionGroup, pk=pk, user=request.user)  # ✅ Added user filter
    sections = group.sections.all()

    # Fetch both subject_code and subject_title
    classes = list(
        Class.objects.filter(user=request.user)
        .values("subject_code", "subject_title")
        .distinct()
    )
    subject_codes = [c["subject_code"] for c in classes]

    if request.method == "POST":
        subject_code = request.POST.get("subject_code")
        group.subject_code = subject_code

        # auto fetch subject title
        subject_title = next((c["subject_title"] for c in classes if c["subject_code"] == subject_code), "")
        group.subject_title = subject_title

        group.instructor = request.user.username
        group.save()

        for section in sections:
            name_key = f"section_name_{section.pk}"
            schedule_key = f"section_schedule_{section.pk}"
            if name_key in request.POST and schedule_key in request.POST:
                section.name = request.POST.get(name_key)
                section.schedule = request.POST.get(schedule_key)
                section.save()

        messages.success(request, "Section group updated successfully.")
        return redirect("Section_List")

    subject_title = next((c["subject_title"] for c in classes if c["subject_code"] == group.subject_code), "")

    return render(request, "Cedit/editsection.html", {
        "group": group,
        "sections": sections,
        "subject_codes": subject_codes,
        "subject_title": subject_title,
        "username": request.user.username,
        "classes": classes,   # ✅ now contains both code + title
    })

# ✅ Delete SectionGroup

@login_required(login_url='login')
def Delete_section(request, id):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    group = get_object_or_404(SectionGroup, id=id, user=request.user)

    group.delete()
    return redirect('Section_List')




@login_required(login_url='login')
def create_students(request, pk):
    # ✅ Ensure only instructors can access this
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    section = get_object_or_404(Section, pk=pk)
    
    # ✅ Verify section belongs to current instructor
    if section.group.user != request.user:
        return HttpResponseForbidden("Access Denied: You don't have permission to modify this section")
    
    # Fetch all available students from the other app - ✅ Filter only Student role users
    all_students_qs = Student.objects.filter(user__role='Student').order_by('student_number')
    
    # Convert QuerySet to JSON-serializable format
    all_students = json.loads(serialize('json', all_students_qs))
    
    # Get existing student numbers in this section
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
                    student = Student.objects.get(id=student_id, user__role='Student')  # ✅ Double-check role
                    
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
        "all_students": all_students,
        "existing_student_numbers": existing_student_numbers,
    })

@login_required(login_url='login')
def section_detail(request, pk):
    # ✅ Allow both Instructors and Students to view, but with different permissions
    section = get_object_or_404(Section, pk=pk)
    
    # ✅ Verify access permissions
    if request.user.role == 'Instructor':
        # Instructor can only view their own sections
        if section.group.user != request.user:
            return HttpResponseForbidden("Access Denied: You don't have permission to view this section")
    elif request.user.role == 'Student':
        # Student can only view sections they're enrolled in
        student_numbers = ExcelRowData.objects.filter(section=section).values_list('data__Student Number', flat=True)
        
        # Check if current user's student record exists in this section
        try:
            student_profile = Student.objects.get(user=request.user)
            if student_profile.student_number not in student_numbers:
                return HttpResponseForbidden("Access Denied: You are not enrolled in this section")
        except Student.DoesNotExist:
            return HttpResponseForbidden("Access Denied: Student profile not found")
    else:
        # Admins might have full access, or restrict based on your requirements
        if request.user.role != 'Admin':
            return HttpResponseForbidden("Access Denied")
    
    row_objects = ExcelRowData.objects.filter(section=section)
    
    # Search Excel rows
    query = request.GET.get("q", "").strip()
    if query:
        row_objects = [row for row in row_objects if query.lower() in str(row.data).lower()]
    
    headers = []
    rows = []
    if row_objects:
        first_row = row_objects[0].data or {}
        headers = list(first_row.keys())
        for obj in row_objects:
            rows.append({"id": obj.id, "values": list(obj.data.values())})
    
    # Fetch Bookings with related data
    bookings = Booking.objects.filter(section=section).prefetch_related(
        'passengers',
        'legs'
    ).order_by('-created_at')
    
    # Process route information for each booking
    for booking in bookings:
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
    
    return render(request, "tutor/Section_Detail.html", {
        "section": section,
        "headers": headers,
        "rows": rows,
        "query": query,
        "bookings": bookings,
        "now": timezone.now(),
    })



@login_required(login_url='login')
def delete_excel_row(request, pk):
    # ✅ Ensure only instructors can delete
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    row = get_object_or_404(ExcelRowData, pk=pk)
    section_id = row.section.id
    
    # ✅ Verify section belongs to current instructor
    if row.section.group.user != request.user:
        return HttpResponseForbidden("Access Denied: You don't have permission to modify this section")
    
    row.delete()
    messages.success(request, "Row deleted successfully!")
    # redirect to the Section_Detail view by name, not to the template file
    return redirect("Section_Detail", pk=section_id)



@login_required(login_url='login')
def edit_student(request, pk):
    # ✅ Ensure only instructors can edit
    if request.user.role != 'Instructor':
        return HttpResponseForbidden("Access Denied: Instructors only")
    
    student = get_object_or_404(ExcelRowData, pk=pk)
    section = student.section
    
    # ✅ Verify section belongs to current instructor
    if section.group.user != request.user:
        return HttpResponseForbidden("Access Denied: You don't have permission to modify this section")

    # Get headers from first Excel row for consistency
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
        messages.success(request, "Student updated successfully!")
        return redirect("Section_Detail", pk=section.pk)

    return render(request, "Cedit/Edit_student.html", {
        "section": section,
        "student": student,
        "headers": headers,
    })



@login_required(login_url='login')
def book_flight(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    
    # ✅ Verify access permissions
    if request.user.role == 'Instructor':
        # Instructor can only book for their own sections
        if section.group.user != request.user:
            return HttpResponseForbidden("Access Denied: You don't have permission to book for this section")
    elif request.user.role == 'Student':
        # Student can only book for sections they're enrolled in
        student_numbers = ExcelRowData.objects.filter(section=section).values_list('data__Student Number', flat=True)
        
        try:
            student_profile = Student.objects.get(user=request.user)
            if student_profile.student_number not in student_numbers:
                return HttpResponseForbidden("Access Denied: You are not enrolled in this section")
        except Student.DoesNotExist:
            return HttpResponseForbidden("Access Denied: Student profile not found")
    else:
        # Restrict non-instructor/student roles if needed
        if request.user.role != 'Admin':
            return HttpResponseForbidden("Access Denied")

    # ✅ fetch all routes
    routes = Route.objects.select_related("origin_airport", "destination_airport").all()

    # ✅ fetch all schedules with related flight + routes
    schedules = Schedule.objects.select_related("flight__route__origin_airport", "flight__route__destination_airport").all()

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
            return render(request, "Create/Create_Instruction.html", {
                "section": section,
                "routes": routes,
                "schedules": schedules,
                "error": "Departure date is required."
            })

        # ✅ Handle multi-city booking
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
                        "duration": make_aware(parse_datetime(leg_duration)) if leg_duration else None,  # Fix timezone
                    })
                i += 1

        # ✅ Store the original route format for display
        original_route = route_id
        
        # ✅ Handle round trip route parsing - but keep original format for storage
        if trip_type == "round_trip" and route_id and "|" in route_id:
            # Keep the full route for display (e.g., "BXU-CEB|CEB-BXU")
            # You can split for processing if needed, but store the complete route
            outbound_route_id, return_route_id = route_id.split("|")
            # For round trip, you might want to store the complete route or just outbound
            # Keeping original format for better display
        
        # ✅ Create the main booking
        booking = Booking.objects.create(
            section=section,
            trip_type=trip_type,
            route=original_route,  # Store the original route format (like BXU-CEB or BXU-CEB|CEB-BXU)
            departure_date=parse_date(departure_date),
            return_date=parse_date(return_date) if return_date else None,
            duration=make_aware(parse_datetime(duration)) if duration else None,  # Fix timezone warning
            adults=adults,
            children=children,
            infants_on_lap=infants_on_lap,
            travel_class=travel_class,
            seat_preference=seat_preference,
        )

        # ✅ Handle multi-city legs
        if multi_city_data:
            for leg in multi_city_data:
                MultiCityLeg.objects.create(
                    booking=booking,
                    origin=leg["origin"],
                    destination=leg["destination"],
                    departure_date=leg["date"],
                    duration=leg["duration"],
                )

        # ✅ Handle passengers
        passenger_count = int(request.POST.get("passenger_count", 1))
        for p in range(1, passenger_count + 1):
            first_name = request.POST.get(f"first_name_{p}", "").strip()
            last_name = request.POST.get(f"last_name_{p}", "").strip()
            middle_initial = request.POST.get(f"mi_{p}", "").strip() or None

            if not first_name or not last_name:
                continue

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

        return redirect("Section_Detail", pk=section.id)

    return render(request, "Create/Create_Instruction.html", {
        "section": section,
        "routes": routes,
        "schedules": schedules,
    })