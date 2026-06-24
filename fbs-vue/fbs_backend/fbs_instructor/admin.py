from django.contrib import admin
from .models import (
    Section, Instructor, SectionEnrollment, 
    Activity, ActivityPassenger, ActivityAddOn
)

# --- INLINES ---

class SectionEnrollmentInline(admin.TabularInline):
    model = SectionEnrollment
    extra = 1

class ActivityAddOnInline(admin.TabularInline):
    model = ActivityAddOn
    extra = 1
    # Matches ActivityAddOn fields
    fields = ('passenger', 'addon', 'is_required', 'quantity_per_passenger', 'points_value')

class ActivityPassengerInline(admin.StackedInline):
    model = ActivityPassenger
    extra = 0
    # Organizes passenger details into a readable layout
    fieldsets = (
        (None, {
            'fields': (('first_name', 'middle_name', 'last_name'), ('passenger_type', 'gender', 'date_of_birth'))
        }),
        ('Travel Details', {
            'fields': (('passport_number', 'nationality', 'is_primary'),)
        }),
    )

# --- ADMIN CLASSES ---

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('instructor_id', 'get_full_name', 'email', 'phone', 'user')
    search_fields = ('instructor_id', 'first_name', 'last_name', 'email')
    fieldsets = (
        ('Account Info', {'fields': ('user', 'instructor_id')}),
        ('Personal Info', {'fields': ('first_name', 'middle_initial', 'last_name', 'email', 'phone')}),
    )

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        'section_code', 
        'section_name', 
        'instructor', 
        'semester', 
        'academic_year',
        'schedule',      
        'created_at'
    )
    list_filter = ('semester', 'academic_year', 'instructor')
    search_fields = ('section_code', 'section_name', 'instructor__username')
    inlines = [SectionEnrollmentInline]

@admin.register(SectionEnrollment)
class SectionEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('get_student_id', 'get_student_name', 'section', 'enrolled_at', 'is_active')
    list_filter = ('section', 'is_active')
    search_fields = ('student__student_number', 'student__last_name', 'section__section_code')

    def get_student_id(self, obj):
        return obj.student.student_number
    get_student_id.short_description = 'Student ID'

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    get_student_name.short_description = 'Student Name'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'activity_type', 'status', 'due_date', 'activity_code', 'is_code_active')
    list_filter = ('activity_type', 'status', 'section')
    search_fields = ('title', 'activity_code', 'instructions')
    readonly_fields = ('activity_code', 'code_generated_at')
    inlines = [ActivityPassengerInline]
    
    fieldsets = (
        ('General Information', {
            'fields': ('title', 'description', 'instructions', 'section', 'status')
        }),
        ('Booking Requirements', {
            'fields': (
                ('required_trip_type', 'required_travel_class'),
                ('required_origin', 'required_destination'),
                ('required_departure_date', 'required_return_date'),
                ('required_passengers', 'required_children', 'required_infants'),
                ('require_passenger_details', 'require_passport')
            )
        }),
        ('Grading & Deadlines', {
            'fields': (
                ('total_points', 'due_date', 'time_limit_minutes'), 
                ('addon_grading_enabled', 'required_addon_points')
            )
        }),
        ('Access Code', {
            'classes': ('collapse',),
            'fields': ('is_code_active', 'activity_code', 'code_generated_at'),
        }),
    )

@admin.register(ActivityPassenger)
class ActivityPassengerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'passenger_type', 'activity', 'nationality', 'is_primary')
    list_filter = ('passenger_type', 'gender', 'nationality')
    search_fields = ('first_name', 'last_name', 'passport_number', 'activity__title')
    inlines = [ActivityAddOnInline]

@admin.register(ActivityAddOn)
class ActivityAddOnAdmin(admin.ModelAdmin):
    list_display = ('addon', 'passenger', 'get_activity', 'is_required', 'points_value')
    list_filter = ('is_required', 'addon')

    def get_activity(self, obj):
        return obj.activity.title
    get_activity.short_description = 'Activity'