# instructorapp/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import (
    Section, SectionEnrollment, Activity, ActivityPassenger, 
    ActivitySubmission, ActivityAddOn, StudentSelectedAddOn, PracticeBooking
)


class SectionEnrollmentInline(admin.TabularInline):
    model = SectionEnrollment
    extra = 0
    readonly_fields = ['enrolled_at']
    fields = ['student', 'is_active', 'enrolled_at']
    raw_id_fields = ['student']
    can_delete = True


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = [
        'section_code', 
        'section_name', 
        'semester', 
        'academic_year', 
        'instructor', 
        'enrolled_students_count',
        'activities_count',
        'created_at'
    ]
    list_filter = [
        'semester', 
        'academic_year', 
        'instructor',
        'created_at'
    ]
    search_fields = [
        'section_code', 
        'section_name', 
        'instructor__username',
        'instructor__first_name',
        'instructor__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'enrolled_students_count_display', 'activities_count_display']
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'section_name',
                'section_code',
                'semester',
                'academic_year',
                'instructor'
            ]
        }),
        ('Schedule & Description', {
            'fields': [
                'schedule',
                'description'
            ]
        }),
        ('Statistics', {
            'fields': [
                'enrolled_students_count_display',
                'activities_count_display'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'updated_at'
            ],
            'classes': ['collapse']
        })
    ]
    inlines = [SectionEnrollmentInline]
    
    def enrolled_students_count_display(self, obj):
        return obj.enrolled_students_count()
    enrolled_students_count_display.short_description = 'Enrolled Students'
    
    def activities_count_display(self, obj):
        return obj.activities.count()
    activities_count_display.short_description = 'Activities Count'
    
    def activities_count(self, obj):
        return obj.activities.count()
    activities_count.short_description = 'Activities'


@admin.register(SectionEnrollment)
class SectionEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'section',
        'student',
        'is_active',
        'enrolled_at'
    ]
    list_filter = [
        'section__semester',
        'section__academic_year',
        'is_active',
        'enrolled_at'
    ]
    search_fields = [
        'section__section_code',
        'section__section_name',
        'student__student_number',
        'student__user__first_name',
        'student__user__last_name'
    ]
    readonly_fields = ['enrolled_at']
    list_editable = ['is_active']
    raw_id_fields = ['section', 'student']


class ActivityAddOnInline(admin.TabularInline):
    model = ActivityAddOn
    extra = 1
    fields = [
        'addon',
        'passenger',
        'is_required',
        'quantity_per_passenger',
        'points_value',
        'notes'
    ]
    raw_id_fields = ['addon', 'passenger']


class ActivityPassengerInline(admin.TabularInline):
    model = ActivityPassenger
    extra = 0
    fields = [
        'first_name',
        'middle_name',
        'last_name',
        'passenger_type',
        'gender',
        'date_of_birth',
        'passport_number',
        'nationality',
        'is_primary'
    ]
    readonly_fields = ['created_at', 'updated_at']


class ActivitySubmissionInline(admin.TabularInline):
    model = ActivitySubmission
    extra = 0
    readonly_fields = ['submitted_at', 'status', 'score_display']
    fields = [
        'student',
        'status',
        'score_display',
        'submitted_at'
    ]
    raw_id_fields = ['student', 'booking']
    can_delete = False
    
    def score_display(self, obj):
        if obj.score is not None:
            return f"{obj.score}/100"
        return "Not Graded"
    score_display.short_description = 'Score'


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'section',
        'activity_type',
        'status',
        'is_code_active',
        'total_points',
        'due_date',
        'submissions_count',
        'graded_count',
        'created_at'
    ]
    list_filter = [
        'status',
        'activity_type',
        'is_code_active',
        'section__semester',
        'section__academic_year',
        'created_at',
        'due_date'
    ]
    search_fields = [
        'title',
        'activity_code',
        'section__section_code',
        'section__section_name',
        'description'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'activity_code',
        'code_generated_at',
        'submissions_count_display',
        'graded_count_display',
        'average_score_display',
        'get_total_passengers_display',
        'time_until_due_display',
        'submission_status_display'
    ]
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'title',
                'description',
                'activity_type',
                'section',
                'status'
            ]
        }),
        ('Flight Requirements', {
            'fields': [
                'required_trip_type',
                'required_origin',
                'required_destination',
                'required_departure_date',
                'required_return_date',
                'required_travel_class'
            ]
        }),
        ('Passenger Requirements', {
            'fields': [
                'required_passengers',
                'required_children',
                'required_infants',
                'get_total_passengers_display',
                'require_passenger_details',
                'require_passport'
            ]
        }),
        ('Instructions & Grading', {
            'fields': [
                'instructions',
                'total_points',
                'addon_grading_enabled',
                'required_addon_points'
            ]
        }),
        ('Timing', {
            'fields': [
                'due_date',
                'time_limit_minutes',
                'time_until_due_display',
                'submission_status_display'
            ]
        }),
        ('Activity Code System', {
            'fields': [
                'activity_code',
                'is_code_active',
                'code_generated_at',
            ],
            'classes': ['collapse']
        }),
        ('Statistics', {
            'fields': [
                'submissions_count_display',
                'graded_count_display',
                'average_score_display'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'updated_at'
            ],
            'classes': ['collapse']
        })
    ]
    inlines = [ActivityAddOnInline, ActivityPassengerInline, ActivitySubmissionInline]
    actions = ['activate_codes', 'deactivate_codes', 'close_activities', 'publish_activities']
    
    def submissions_count(self, obj):
        return obj.submissions.count()
    submissions_count.short_description = 'Submissions'
    
    def graded_count(self, obj):
        return obj.submissions.filter(status='graded').count()
    graded_count.short_description = 'Graded'
    
    def submissions_count_display(self, obj):
        return obj.submissions.count()
    submissions_count_display.short_description = 'Total Submissions'
    
    def graded_count_display(self, obj):
        return obj.submissions.filter(status='graded').count()
    graded_count_display.short_description = 'Graded Submissions'
    
    def average_score_display(self, obj):
        avg_score = obj.submissions.filter(score__isnull=False).aggregate(Avg('score'))['score__avg']
        if avg_score is not None:
            return f"{avg_score:.2f}/100"
        return "No grades yet"
    average_score_display.short_description = 'Average Score'
    
    def get_total_passengers_display(self, obj):
        return obj.get_total_passengers()
    get_total_passengers_display.short_description = 'Total Required Passengers'
    
    def time_until_due_display(self, obj):
        time_remaining = obj.time_until_due
        if time_remaining:
            days = time_remaining.days
            hours = time_remaining.seconds // 3600
            return f"{days}d {hours}h"
        return "Expired"
    time_until_due_display.short_description = 'Time Until Due'
    
    def submission_status_display(self, obj):
        status = obj.submission_status
        color_map = {
            'expired': 'red',
            'active': 'green',
            'inactive': 'orange'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            color_map.get(status, 'black'),
            status.upper()
        )
    submission_status_display.short_description = 'Submission Status'
    
    def activate_codes(self, request, queryset):
        for activity in queryset:
            if activity.status != 'closed':
                activity.activate_code()
                self.message_user(
                    request, 
                    f"Activated code for {activity.title}: {activity.activity_code}"
                )
    activate_codes.short_description = "Activate codes for selected activities"
    
    def deactivate_codes(self, request, queryset):
        updated = queryset.update(is_code_active=False)
        self.message_user(request, f"Deactivated codes for {updated} activities")
    deactivate_codes.short_description = "Deactivate codes for selected activities"
    
    def close_activities(self, request, queryset):
        updated = queryset.update(status='closed', is_code_active=False)
        self.message_user(request, f"Closed {updated} activities")
    close_activities.short_description = "Close selected activities"
    
    def publish_activities(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f"Published {updated} activities")
    publish_activities.short_description = "Publish selected activities"


@admin.register(ActivityPassenger)
class ActivityPassengerAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'activity',
        'passenger_type',
        'gender',
        'date_of_birth',
        'nationality',
        'is_primary',
        'created_at'
    ]
    list_filter = [
        'passenger_type',
        'gender',
        'is_primary',
        'activity__section',
        'created_at'
    ]
    search_fields = [
        'first_name',
        'last_name',
        'activity__title',
        'nationality',
        'passport_number'
    ]
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['activity']


@admin.register(ActivityAddOn)
class ActivityAddOnAdmin(admin.ModelAdmin):
    list_display = [
        'activity',
        'addon',
        'passenger',
        'is_required',
        'quantity_per_passenger',
        'points_value',
        'created_at'
    ]
    list_filter = [
        'is_required',
        'activity__section',
        'created_at'
    ]
    search_fields = [
        'activity__title',
        'addon__name',
        'passenger__first_name',
        'passenger__last_name',
        'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['activity', 'addon', 'passenger']
    list_editable = ['is_required', 'points_value', 'quantity_per_passenger']


class StudentSelectedAddOnInline(admin.TabularInline):
    model = StudentSelectedAddOn
    extra = 0
    readonly_fields = ['points_earned', 'created_at']
    fields = ['activity_addon', 'addon', 'booking_detail', 'quantity_selected', 'points_earned']
    raw_id_fields = ['activity_addon', 'addon', 'booking_detail']
    can_delete = False


@admin.register(ActivitySubmission)
class ActivitySubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'activity',
        'student',
        'status',
        'score_display',
        'addon_score_display',
        'total_score_display',
        'submitted_at',
        'is_late_display'
    ]
    list_filter = [
        'status',
        'activity__section',
        'submitted_at',
        'activity__due_date'
    ]
    search_fields = [
        'activity__title',
        'student__student_number',
        'student__user__first_name',
        'student__user__last_name',
        'feedback'
    ]
    readonly_fields = [
        'submitted_at',
        'is_late_display',
        'addon_completion_percentage_display',
        'base_score_display',
        'total_score_with_addons_display'
    ]
    raw_id_fields = ['activity', 'student', 'booking']
    list_editable = ['status']
    fieldsets = [
        ('Submission Information', {
            'fields': [
                'activity',
                'student',
                'booking',
                'status',
                'submitted_at',
                'is_late_display'
            ]
        }),
        ('Grading', {
            'fields': [
                'score',
                'addon_score',
                'max_addon_points',
                'base_score_display',
                'total_score_with_addons_display',
                'addon_completion_percentage_display',
                'feedback',
                'addon_feedback'
            ]
        }),
        ('Activity Requirements (Reference)', {
            'fields': [
                'required_trip_type',
                'required_travel_class',
                'required_passengers',
                'required_children',
                'required_infants',
                'require_passenger_details',
                'required_origin_airport',
                'required_destination_airport'
            ],
            'classes': ['collapse']
        })
    ]
    inlines = [StudentSelectedAddOnInline]
    actions = ['mark_as_graded', 'mark_as_submitted', 'calculate_addon_scores']
    
    def score_display(self, obj):
        if obj.score is not None:
            return f"{obj.score:.2f}"
        return "Not Graded"
    score_display.short_description = 'Base Score'
    
    def addon_score_display(self, obj):
        return f"{obj.addon_score:.2f}/{obj.max_addon_points:.2f}"
    addon_score_display.short_description = 'Add-on Score'
    
    def total_score_display(self, obj):
        total = obj.total_score_with_addons
        return f"{total:.2f}/100"
    total_score_display.short_description = 'Total Score'
    
    def is_late_display(self, obj):
        if obj.is_late_submission:
            return format_html('<span style="color: red;">⚠ Late</span>')
        return format_html('<span style="color: green;">✓ On Time</span>')
    is_late_display.short_description = 'Late Status'
    
    def base_score_display(self, obj):
        return f"{obj.base_score:.2f}"
    base_score_display.short_description = 'Base Score (without add-ons)'
    
    def total_score_with_addons_display(self, obj):
        total = obj.total_score_with_addons
        return f"{total:.2f}/100"
    total_score_with_addons_display.short_description = 'Total Score (with add-ons)'
    
    def addon_completion_percentage_display(self, obj):
        percentage = obj.addon_completion_percentage
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            percentage
        )
    addon_completion_percentage_display.short_description = 'Add-on Completion'
    
    def mark_as_graded(self, request, queryset):
        updated = queryset.update(status='graded')
        self.message_user(request, f"Marked {updated} submissions as graded")
    mark_as_graded.short_description = "Mark selected submissions as graded"
    
    def mark_as_submitted(self, request, queryset):
        updated = queryset.update(status='submitted')
        self.message_user(request, f"Marked {updated} submissions as submitted")
    mark_as_submitted.short_description = "Mark selected submissions as submitted"
    
    def calculate_addon_scores(self, request, queryset):
        for submission in queryset:
            try:
                addon_score, max_addon_points = submission.calculate_addon_score()
                submission.addon_score = addon_score
                submission.max_addon_points = max_addon_points
                submission.save()
                self.message_user(
                    request, 
                    f"Updated add-on scores for {submission.student.student_number}: {addon_score}/{max_addon_points}"
                )
            except Exception as e:
                self.message_user(
                    request, 
                    f"Error calculating add-on scores for {submission.student.student_number}: {str(e)}",
                    level='ERROR'
                )
    calculate_addon_scores.short_description = "Recalculate add-on scores"


@admin.register(StudentSelectedAddOn)
class StudentSelectedAddOnAdmin(admin.ModelAdmin):
    list_display = [
        'submission',
        'activity_addon',
        'addon',
        'quantity_selected',
        'points_earned',
        'created_at'
    ]
    list_filter = [
        'submission__activity',
        'created_at'
    ]
    search_fields = [
        'submission__student__student_number',
        'submission__student__user__first_name',
        'submission__student__user__last_name',
        'addon__name',
        'activity_addon__activity__title'
    ]
    readonly_fields = ['points_earned', 'created_at']
    raw_id_fields = ['submission', 'activity_addon', 'addon', 'booking_detail']


@admin.register(PracticeBooking)
class PracticeBookingAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'practice_type',
        'is_completed',
        'created_at'
    ]
    list_filter = [
        'practice_type',
        'is_completed',
        'created_at'
    ]
    search_fields = [
        'student__student_number',
        'student__user__first_name',
        'student__user__last_name',
        'scenario_description'
    ]
    readonly_fields = ['created_at']
    raw_id_fields = ['student', 'booking']
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'student',
                'booking',
                'practice_type',
                'is_completed'
            ]
        }),
        ('Practice Details', {
            'fields': [
                'scenario_description',
                'practice_requirements'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at'
            ]
        })
    ]


# Optional: Custom admin site configuration
class InstructorAppAdminSite(admin.AdminSite):
    site_header = "Flight Booking Instructor Administration"
    site_title = "Instructor App Admin"
    index_title = "Welcome to Instructor App Administration"

# You can register this custom admin site in your urls.py if needed
# instructor_admin_site = InstructorAppAdminSite(name='instructor_admin')