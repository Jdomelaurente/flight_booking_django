# bookingapp/urls.py
from django.urls import path
from . import views

app_name = "bookingapp"

urlpatterns = [
    # Student Activity URLs
    path('student/dashboard/', views.student_home, name='student_home'),
    path('student/activity/<int:activity_id>/', views.student_activity_detail, name='student_activity_detail'),
    path('student/activities/', views.student_activities, name='student_activities'),

    # Main Booking Flow
    path('', views.home, name="main"),
    path('flight/search/', views.search_flight, name='search_schedule'),
    path('flight/schedule/', views.flight_schedules, name='flight_schedules'),
    path("flight/schedule/cancel/", views.cancel_selected_schedule, name="cancel_selected_schedule"),
    path("flight/schedule/reset/", views.reset_selection, name="reset_selection"),
    path('flight/select/', views.select_schedule, name='select_schedule'),
    path('flight/select/review/', views.review_scheduled, name='review_selected_scheduled'),
    path('flight/select/confirm/', views.confirm_schedule, name='confirm_schedule'),
    path('flight/passenger/information/', views.passenger_information, name='passenger_information'),
    path('flight/passenger/information/save/', views.save_passengers, name='save_passengers'),
    path('flight/passenger/select/seat/', views.select_seat, name='select_seat'),
    path('flight/passenger/select/seat/confirm/', views.confirm_seat, name='confirm_seat'),
    path('flight/passenger/print/passenger/session/', views.print_booking_info, name='print_booking_info'),
    path('flight/passenger/booking/summary/', views.booking_summary, name='booking_summary'),
    path('flight/passenger/booking/summary/confirm/', views.confirm_booking, name='confirm_booking'),
    path('flight/passenger/booking/payment/method/', views.payment_method, name='payment_method'),
    path('flight/passenger/booking/payment/method/success/', views.payment_success, name='payment_success'),
    path("flight/book-again/", views.book_again, name="book_again"),
    # path('submission/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('student/work/<int:submission_id>/', views.student_work_detail, name='student_work_detail'),




    # Authentication
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),


    # in bookingapp/urls.py
    path('debug-activities/', views.debug_student_activities, name='debug_student_activities'),
    path('debug-submission/<int:submission_id>/', views.debug_submission_data, name='debug_submission'),
    path('testsubmission/<int:submission_id>/', views.test_submission_detail, name='test_submission_detail'),
    path('student/debug-scoring/<int:submission_id>/', views.debug_scoring, name='debug_scoring'),
    path('student/debug-original/<int:submission_id>/', views.check_original_scoring, name='check_original_scoring'),
    path('student/deep-debug/<int:submission_id>/', views.deep_debug_scoring, name='deep_debug_scoring'),


    
     # Practice booking URLs
    path('practice/', views.practice_booking_home, name='practice_home'),
    path('practice/start/', views.start_practice_booking, name='start_practice'),
    path('practice/guided/', views.guided_practice, name='guided_practice'),
    path('practice/save/', views.save_practice_booking, name='save_practice'),
]