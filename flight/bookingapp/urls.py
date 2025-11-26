# bookingapp/urls.py
from django.urls import path
from . import views

app_name = "bookingapp"

urlpatterns = [
    # Student Activity URLs
    path('student/dashboard/', views.student_home, name='student_home'),
    path('student/activity/<int:activity_id>/', views.student_activity_detail, name='student_activity_detail'),
    path('student/work/<int:submission_id>/', views.student_work_detail, name='student_work_detail'),
    path('student/activities/', views.student_activities, name='student_activities'),

    # Main Booking Flow - REORDERED URLs
    path('', views.home, name="main"),
    path('flight/search/', views.search_flight, name='search_schedule'),
    path('search-flight/', views.search_flight, name='search_flight'),
   
    path('flight/schedule/', views.flight_schedules, name='flight_schedules'),

    path("flight/schedule/cancel/", views.cancel_selected_schedule, name="cancel_selected_schedule"),
    path("flight/schedule/reset/", views.reset_selection, name="reset_selection"),





    # FIXED: Put review before select to avoid URL conflicts
    path('flight/select/review/', views.review_scheduled, name='review_selected_scheduled'),
    path('flight/select/', views.select_schedule, name='select_schedule'),
    path('flight/select/confirm/', views.confirm_schedule, name='confirm_schedule'),
    
    path('proceed-to-passengers/', views.proceed_to_passengers, name='proceed_to_passengers'),
    path('flight/select/confirm/', views.confirm_schedule, name='confirm_schedule'),
    path('flight/passenger/information/', views.passenger_information, name='passenger_information'),
    path('flight/passenger/information/save/', views.save_passengers, name='save_passengers'),

    # Add-on pages
    path('flight/add-ons/', views.add_ons, name='add_ons'),
    path('flight/save-add-ons/', views.save_add_ons, name='save_add_ons'),
    
    # Individual add-on pages
    path('flight/add-ons/baggage/', views.baggage_addon, name='baggage_addon'),
    path('flight/add-ons/meals/', views.meals_addon, name='meals_addon'),
    path('flight/add-ons/seat-selection/', views.seat_selection_addon, name='seat_selection_addon'),
    path('flight/add-ons/wheelchair/', views.wheelchair_addon, name='wheelchair_addon'),
    path('flight/add-ons/insurance/', views.insurance_addon, name='insurance_addon'),
    path('flight/add-ons/quick/', views.quick_addons, name='quick_addons'),

    # Add-on action URLs - ADD THESE
    path('flight/add-ons/save-single/', views.save_single_addon, name='save_single_addon'),
    path('flight/add-ons/remove/', views.remove_addon, name='remove_addon'),

    
    path('flight/passenger/select/seat/', views.select_seat, name='select_seat'),
    path('flight/passenger/select/seat/confirm/', views.confirm_seat, name='confirm_seat'),
    path('flight/passenger/print/passenger/session/', views.print_booking_info, name='print_booking_info'),
    path('flight/passenger/booking/summary/', views.booking_summary, name='booking_summary'),
     path('confirm-booking/', views.confirm_booking, name='confirm_booking'),
    path('flight/passenger/booking/summary/confirm/', views.confirm_booking, name='confirm_booking'),
    path('flight/passenger/booking/payment/method/', views.payment_method, name='payment_method'),
    path('flight/passenger/booking/payment/method/success/', views.payment_success, name='payment_success'),
    path("flight/book-again/", views.book_again, name="book_again"),

    # Authentication
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),

    # Debug URLs
    path('debug-activities/', views.debug_student_activities, name='debug_student_activities'),
    # path('debug-submission/<int:submission_id>/', views.debug_submission_data, name='debug_submission'),
    # path('testsubmission/<int:submission_id>/', views.test_submission_detail, name='test_submission_detail'),
    path('student/debug-scoring/<int:submission_id>/', views.debug_scoring, name='debug_scoring'),
    path('student/debug-original/<int:submission_id>/', views.check_original_scoring, name='check_original_scoring'),
    path('student/deep-debug/<int:submission_id>/', views.deep_debug_scoring, name='deep_debug_scoring'),

    # Practice booking URLs
    path('practice/', views.practice_booking_home, name='practice_home'),
    path('practice/start/', views.start_practice_booking, name='start_practice'),
    path('practice/guided/', views.guided_practice, name='guided_practice'),
    path('practice/save/', views.save_practice_booking, name='save_practice'),




    path('test/home/', views.test_home, name='test_home'),
    path('test/schedule/', views.test_schedule, name='test_schedule'),
    path('test/selected/schedule/', views.test_selected_schedule, name='test_selected_schedule'),
    path('test/passenger/', views.test_passenger, name='test_passenger'),
    path('test/addons/', views.test_addons, name='test_addon'),
    path('test/booking/summary/', views.test_booking_summary, name='test_booking_summary'),



    # debug
    path('debug/breakdown/<int:submission_id>/', views.debug_scoring_breakdown, name='debug_scoring_breakdown'),
    path('debug-score/<int:submission_id>/', views.debug_score_breakdown, name='debug_score_breakdown'),
]