# bookingapp/urls_booking.py - FIXED VERSION
from django.urls import path
from . import views_booking

app_name = "bookingapp"

urlpatterns = [
    # ===== MAIN BOOKING FLOW =====
    path('', views_booking.home, name="main"),
    path('search/', views_booking.search_flight, name='search_flight'),
    path('schedules/', views_booking.flight_schedules, name='flight_schedules'),
    
    # Schedule Management
    path('schedules/cancel/', views_booking.cancel_selected_schedule, name="cancel_selected_schedule"),
    path('schedules/reset/', views_booking.reset_selection, name="reset_selection"),
    path('schedules/select/', views_booking.select_schedule, name='select_schedule'),
    path('schedules/review/', views_booking.review_selected_scheduled, name='review_selected_scheduled'),  # FIXED: Using review_scheduled view
    path('schedules/confirm/', views_booking.confirm_schedule, name='confirm_schedule'),
    
    # Passenger Flow
    path('passengers/proceed/', views_booking.proceed_to_passengers, name='proceed_to_passengers'),
    path('passengers/', views_booking.passenger_information, name='passenger_information'),
    path('passengers/save/', views_booking.save_passengers, name='save_passengers'),
    
    # Add-ons
    path('add-ons/', views_booking.add_ons, name='add_ons'),
    path('add-ons/save/', views_booking.save_add_ons, name='save_add_ons'),
    path('add-ons/save-single/', views_booking.save_single_addon, name='save_single_addon'),
    path('add-ons/remove/', views_booking.remove_addon, name='remove_addon'),
    path('add-ons/lounge/', views_booking.lounge_addon, name='lounge_addon'),
    path('practice/save/', views_booking.save_practice_booking, name='save_practice_booking'),
    
    # Individual add-on pages
    path('add-ons/baggage/', views_booking.baggage_addon, name='baggage_addon'),
    path('add-ons/meals/', views_booking.meals_addon, name='meals_addon'),
    path('add-ons/seats/', views_booking.seat_selection_addon, name='seat_selection_addon'),
    path('add-ons/wheelchair/', views_booking.wheelchair_addon, name='wheelchair_addon'),
    path('add-ons/insurance/', views_booking.insurance_addon, name='insurance_addon'),
    path('add-ons/quick/', views_booking.quick_addons, name='quick_addons'),

    
    # Seat Selection
    path('seats/', views_booking.select_seat, name='select_seat'),
    path('seats/confirm/', views_booking.confirm_seat, name='confirm_seat'),
    
    # Booking Summary & Confirmation
    path('booking/summary/', views_booking.booking_summary, name='booking_summary'),
    path('booking/confirm/', views_booking.confirm_booking, name='confirm_booking'),  # FIXED: Single endpoint
    
    # Payment
    path('payment/', views_booking.payment_method, name='payment_method'),
    path('payment/success/', views_booking.payment_success, name='payment_success'),
    
    # Miscellaneous
    path('book-again/', views_booking.book_again, name="book_again"),
    path('debug/print/', views_booking.print_booking_info, name='print_booking_info'),
    path('debug/activities/', views_booking.debug_student_activities, name='debug_student_activities'),
    
    # ===== AUTHENTICATION =====
    path('auth/login/', views_booking.login_view, name='login'),
    path('auth/register/', views_booking.register_view, name='register'),
    path('auth/logout/', views_booking.logout_view, name='logout'),

    path('debug-tags/', views_booking.debug_template_tags, name='debug_tags'),
]