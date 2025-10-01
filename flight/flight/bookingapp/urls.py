from django.urls import path
from . import views

app_name = "bookingapp"

urlpatterns = [
    path('', views.home, name="main"),
    path('flight/search/', views.search_flight, name='search_schedule'),

    path('flight/schedule/', views.flight_schedules, name='flight_schedules'),
    path("flight/schedule/cancel/", views.cancel_selected_schedule, name="cancel_selected_schedule"),
    path("flight/schedule/reset/", views.reset_selection, name="reset_selection"),
    path('flight/select/', views.select_schedule, name='select_schedule'),


    path('flight/select/review', views.review_scheduled, name='review_selected_scheduled'),
    path('flight/select/confirm', views.confirm_schedule, name='confirm_schedule'),

    path('flight/passenger/information', views.passenger_information, name='passenger_information'),
    path('flight/passenger/information/save', views.save_passengers, name='save_passengers'),

    path('flight/passenger/select/seat', views.select_seat, name='select_seat'),
    path('flight/passenger/select/seat/confirm', views.confirm_seat, name='confirm_seat'),

    # """ check session """
    path('flight/passenger/print/passenger/session', views.print_booking_info, name='print_booking_info'),


    path('flight/passenger/booking/summary', views.booking_summary, name='booking_summary'),

    path('flight/passenger/booking/summary/confirm', views.confirm_booking, name='confirm_booking'),

    path('flight/passenger/booking/payment/method', views.payment_method, name='payment_method'),
    path('flight/passenger/booking/payment/method/success', views.payment_success, name='payment_success'),

    path("flight/book-again/", views.book_again, name="book_again"),



    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),



]