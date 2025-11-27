# bookingapp/urls_booking.py
from django.urls import path
from . import views_booking

app_name = "bookingapp"

urlpatterns = [
    # ===== MAIN BOOKING FLOW =====
    path('', views_booking.home, name="main"),  # FIXED: Changed from 'fbs' to ''
    path('search/', views_booking.search_flight, name='search_flight'),
    path('schedules/', views_booking.flight_schedules, name='flight_schedules'),
    path('schedule/cancel/', views_booking.cancel_selected_schedule, name="cancel_selected_schedule"),
    path('schedule/reset/', views_booking.reset_selection, name="reset_selection"),

    # Schedule Selection
    path('select/review/', views_booking.review_scheduled, name='review_selected_scheduled'),
    path('select/', views_booking.select_schedule, name='select_schedule'),
    path('select/confirm/', views_booking.confirm_schedule, name='confirm_schedule'),
    path('proceed-to-passengers/', views_booking.proceed_to_passengers, name='proceed_to_passengers'),

    # Passenger Information
    path('passenger/information/', views_booking.passenger_information, name='passenger_information'),
    path('passenger/information/save/', views_booking.save_passengers, name='save_passengers'),

    # Add-ons
    path('add-ons/', views_booking.add_ons, name='add_ons'),
    path('save-add-ons/', views_booking.save_add_ons, name='save_add_ons'),
    path('add-ons/save-single/', views_booking.save_single_addon, name='save_single_addon'),
    path('add-ons/remove/', views_booking.remove_addon, name='remove_addon'),
    
    # Individual add-on pages
    path('add-ons/baggage/', views_booking.baggage_addon, name='baggage_addon'),
    path('add-ons/meals/', views_booking.meals_addon, name='meals_addon'),
    path('add-ons/seat-selection/', views_booking.seat_selection_addon, name='seat_selection_addon'),
    path('add-ons/wheelchair/', views_booking.wheelchair_addon, name='wheelchair_addon'),
    path('add-ons/insurance/', views_booking.insurance_addon, name='insurance_addon'),
    path('add-ons/quick/', views_booking.quick_addons, name='quick_addons'),

    # Seat Selection
    path('passenger/select/seat/', views_booking.select_seat, name='select_seat'),
    path('passenger/select/seat/confirm/', views_booking.confirm_seat, name='confirm_seat'),

    # Booking Summary & Payment
    path('passenger/booking/summary/', views_booking.booking_summary, name='booking_summary'),
    path('confirm-booking/', views_booking.confirm_booking, name='confirm_booking'),
    path('passenger/booking/summary/confirm/', views_booking.confirm_booking, name='confirm_booking'),
    path('passenger/booking/payment/method/', views_booking.payment_method, name='payment_method'),
    path('passenger/booking/payment/success/', views_booking.payment_success, name='payment_success'),
    path("book-again/", views_booking.book_again, name="book_again"),
    path('passenger/print/session/', views_booking.print_booking_info, name='print_booking_info'),

    # ===== AUTHENTICATION =====
    path('auth/login/', views_booking.login_view, name='login'),
    path('auth/register/', views_booking.register_view, name='register'),
    path('auth/logout/', views_booking.logout_view, name='logout'),
]