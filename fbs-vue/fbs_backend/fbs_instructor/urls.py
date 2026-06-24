from django.urls import path
from . import views
from .views import (
    Login_view,
    instructor_dashboard,
    section_details,
    register_view,
    EnrollStudentView,
    Enroll_Student_list,
    UnenrollStudentView,
    create_activity,
    update_activity,
    delete_activity,
    activity_details,
    activate_activity,
    student_activity_details,
    student_dashboard,
    submit_grade,
    release_activity_grades,
    validate_session,
    list_sessions,
    logout_view,
    get_activity_submissions,
    update_profile,
    update_section,
    bulk_enroll_students,
    clear_section_enrollments,
    admin_lms_overview,
    get_eligible_students,
    get_available_travel_classes,
    get_available_addons,
    get_instructor_logs,
    log_report_print,
    get_student_notifications,
    mark_notifications_read,
)

urlpatterns = [
    # Logs
    path('instructor/logs/', get_instructor_logs, name='get_instructor_logs'),
    path('instructor/logs/print-report/', log_report_print, name='log_report_print'),
    
    # Authentication
    path('auth/register/', register_view, name='register'),
    path('auth/login/', Login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('profile/update/', update_profile, name='update_profile'),
    path('auth/validate/', validate_session, name='validate_session'),
    path('auth/sessions/', list_sessions, name='list_sessions'),
    
    # Dashboard
    path('instructor/dashboard/', instructor_dashboard, name='instructor_dashboard'),

    # Section Management
    path('instructor/sections/<int:section_id>/', section_details, name='section_details'),
    path('instructor/sections/<int:section_id>/update/', update_section, name='update_section'),
    path('instructor/sections/<int:section_id>/enroll/', EnrollStudentView.as_view(), name='enroll-student'),
    path('instructor/sections/<int:section_id>/students/', Enroll_Student_list, name='Enroll_Student_list'),
    path('instructor/sections/<int:section_id>/enroll/<int:student_id>/', UnenrollStudentView.as_view(), name='unenroll-student'),
    path('instructor/sections/<int:section_id>/bulk-enroll/', bulk_enroll_students, name='bulk_enroll_students'),
    path('instructor/sections/<int:section_id>/clear-enrollments/', clear_section_enrollments, name='clear_section_enrollments'),
    
    # Activity Management - Create & Delete
    path('instructor/sections/<int:section_id>/activities/create/', create_activity, name='api_create_activity'),
    path('instructor/sections/<int:section_id>/activities/<int:activity_id>/update/', update_activity, name='api_update_activity'),
    path('instructor/sections/<int:section_id>/activities/<int:activity_id>/delete/', delete_activity, name='delete_activity'),
    
    # Travel/Add-on Lookups (route+date aware)
    path('instructor/available-travel-classes/', get_available_travel_classes, name='get_available_travel_classes'),
    path('instructor/available-addons/', get_available_addons, name='get_available_addons'),
    
    # Activity Details & Activation
    path('instructor/activities/<int:activity_id>/', activity_details, name='activity-details'),
    path('instructor/activities/<int:activity_id>/submissions/', get_activity_submissions, name='activity-submissions'),
    path('instructor/activity/<int:activity_id>/activate/', activate_activity, name='activate_activity'),
    path('instructor/activity/<int:activity_id>/eligible-students/', get_eligible_students, name='get_eligible_students'),
    path('instructor/activities/<int:activity_id>/submissions/<int:student_id>/grade/', submit_grade, name='submit-grade'),
    path('instructor/activities/<int:activity_id>/release-grades/', release_activity_grades, name='release-grades'),

    # ============================================
    # STUDENT URLS - ? FIXED
    # ============================================
    
    # Student Dashboard
    path('student/dashboard/data/', student_dashboard, name='student_dashboard_data'),
    
    # ? FIXED: Main student activity endpoint (matches frontend)
    path('student/activities/<int:activity_id>/details/', student_activity_details, name='student_activity_details'),
    
    # ? REMOVED: Non-existent views (commented out - create these views later if needed)
    # path('student/activities/<int:activity_id>/submit/', views.submit_activity, name='student_submit_activity'),
    # path('student/activities/<int:activity_id>/status/', views.update_activity_status, name='student_update_status'),
    # path('student/activities/<int:activity_id>/submission/', views.get_activity_submission, name='student_get_submission'),
    # path('student/activities/<int:activity_id>/draft/', views.save_draft, name='student_save_draft'),
    
    # ? KEEP: Legacy URL for backward compatibility
    path('student/activity/<int:activity_id>/', student_activity_details, name='student_activity_details_legacy'),

    # ? NEW: Practice Bookings History
    path('student/practice-bookings/', views.get_student_practice_bookings, name='student_practice_bookings'),
    
    # Existing student URLs...
    path('student/activity/start/<int:activity_id>/', views.start_activity, name='start_activity'),
    path('student/activity/fail/<int:activity_id>/', views.fail_activity, name='fail_activity'),
    
    # Notifications
    path('student/notifications/', get_student_notifications, name='get_student_notifications'),
    path('student/notifications/mark-read/', mark_notifications_read, name='mark_notifications_read'),

    # Instructor Dynamic Notifications (Persistent)
    path('instructor/notifications/read-status/', views.get_instructor_notifications_read_status, name='get_instructor_notifications_read_status'),
    path('instructor/notifications/mark-read/', views.mark_instructor_notifications_read, name='mark_instructor_notifications_read'),

    # Admin LMS Overview
    path('admin/lms-overview/', admin_lms_overview, name='admin_lms_overview'),
]