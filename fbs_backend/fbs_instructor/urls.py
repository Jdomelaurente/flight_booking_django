from django.urls import path
from . import views
from .views import (
    Login_view,
    instructor_dashboard,
    section_details,
    register_view,
    EnrollStudentView,
    Enroll_Student_list,
    create_activity,
    delete_activity,
    activity_details,
    activate_activity,
    student_dashboard,
    get_activity_submissions,
    student_activity_details,  # ADDED
    validate_session,          # ADDED
    list_sessions,             # ADDED
    logout_view,
    update_profile,
)

urlpatterns = [
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
    path('instructor/sections/<int:section_id>/enroll/', EnrollStudentView.as_view(), name='enroll-student'),
    path('instructor/sections/<int:section_id>/students/', Enroll_Student_list, name='Enroll_Student_list'),
    
    # Activity Management - Create & Delete
    path('instructor/sections/<int:section_id>/activities/create/', create_activity, name='api_create_activity'),
    path('instructor/sections/<int:section_id>/activities/<int:activity_id>/delete/', delete_activity, name='delete_activity'),
    
    # Activity Details & Activation
    path('instructor/activities/<int:activity_id>/', activity_details, name='activity-details'),
    path('instructor/activities/<int:activity_id>/submissions/', get_activity_submissions, name='activity-submissions'),
    path('instructor/activity/<int:activity_id>/activate/', activate_activity, name='activate_activity'),

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


    
]