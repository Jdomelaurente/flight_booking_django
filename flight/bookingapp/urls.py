from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="main"),
    path('flight_schedule', views.flight_schedule, name="flight_schedule"),
    path('select_schedule', views.select_schedule, name="select_schedule"),
    path('passenger', views.passenger, name="passenger"),
    path('book_seat', views.seat, name="bookseat"),
    path('booking_summary', views.booking_summary, name="booking_summary"),
    path('payment', views.payment, name="payment"),
    path('success', views.success, name="success"),

]