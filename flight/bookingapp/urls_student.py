# bookingapp/urls_student.py
from django.urls import path
from . import views_student

app_name = "studentapp"

urlpatterns = [
    # ===== STUDENT DASHBOARD & ACTIVITIES =====
    path('', views_student.student_home, name='student_home'),
    path('activities/', views_student.student_activities, name='student_activities'),
    path('activity/<int:activity_id>/', views_student.student_activity_detail, name='student_activity_detail'),
    path('work/<int:submission_id>/', views_student.student_work_detail, name='student_work_detail'),
    path('section/<int:section_id>/grade-report/<int:student_id>/', 
         views_student.student_section_grade_report, 
         name='student_section_grade_report'),
    
    # ===== PRACTICE BOOKING =====
    path('practice/', views_student.practice_booking_home, name='practice_home'),
    path('practice/start/', views_student.start_practice_booking, name='start_practice'),
    path('practice/guided/', views_student.guided_practice, name='guided_practice'),
    path('practice/save/', views_student.save_practice_booking, name='save_practice'),

    # ===== DEBUG & SCORING =====
    path('debug/activities/', views_student.debug_student_activities, name='debug_student_activities'),
    path('debug/scoring/<int:submission_id>/', views_student.debug_scoring, name='debug_scoring'),
    path('debug/original/<int:submission_id>/', views_student.check_original_scoring, name='check_original_scoring'),
    path('debug/deep/<int:submission_id>/', views_student.deep_debug_scoring, name='deep_debug_scoring'),
    path('debug/breakdown/<int:submission_id>/', views_student.debug_scoring_breakdown, name='debug_scoring_breakdown'),
    path('debug/score/<int:submission_id>/', views_student.debug_score_breakdown, name='debug_score_breakdown'),
]