from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name="main"),

    #login
    path("profile/", views.profile_view, name="profile"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),

    # flight
    path('flight/', views.flight_view, name='flight'),
    path('flights/add/', views.add_flight, name='add_flight'),
    path('flights/update/<int:id>/', views.update_flight, name='update_flight'),
    path('flights/delete/<int:id>/', views.delete_flight, name='delete_flight'),

    # route
    path('route/', views.route_view, name='route'),
    path('routes/add/', views.add_route, name='add_route'),
    path('routes/update/<int:id>/', views.update_route, name='update_route'),
    path('routes/delete/<int:id>/', views.delete_route, name='delete_route'),

    #schedule 
    path('schedule/', views.schedule_view, name='schedule'),
    path('schedules/add/', views.add_schedule, name='add_schedule'),
    path('schedules/update/<int:id>/', views.update_schedule, name='update_schedule'),
    path('schedules/delete/<int:id>/', views.delete_schedule, name='delete_schedule'),

    #seats
    path('seat/', views.seat_view, name='seat'),
    path("seats/add/", views.add_seat, name="add_seat"),
    path("seats/update/<int:seat_id>/", views.update_seat, name="update_seat"),
    path("seats/delete/<int:seat_id>/", views.delete_seat, name="delete_seat"),

    #airport
    path('airport/', views.airport_view, name='airport'),
    path("airports/add/", views.add_airport, name="add_airport"),
    path("airports/update/<int:airport_id>/", views.update_airport, name="update_airport"),
    path("airports/delete/<int:airport_id>/", views.delete_airport, name="delete_airport"),

    #airline
    path('airline/', views.airline_view, name='airline'),
    path("airlines/add/", views.add_airline, name="add_airline"),
    path("airlines/update/<int:airline_id>/", views.update_airline, name="update_airline"),
    path("airlines/delete/<int:airline_id>/", views.delete_airline, name="delete_airline"),

    # aircraft
    path('aircraft/', views.aircraft_view, name='aircraft'),
    path("aircrafts/add/", views.add_aircraft, name="add_aircraft"),
    path("aircrafts/update/<int:aircraft_id>/", views.update_aircraft, name="update_aircraft"),
    path("aircrafts/delete/<int:aircraft_id>/", views.delete_aircraft, name="delete_aircraft"),

    # seatclass
    path('seat_class/', views.seat_class_view, name='seat_class'),
    path("seat-classes/add/", views.add_seat_class, name="add_seat_class"),
    path("seat-classes/update/<int:seat_class_id>/", views.update_seat_class, name="update_seat_class"),
    path("seat-classes/delete/<int:seat_class_id>/", views.delete_seat_class, name="delete_seat_class"),

    # booking_detail
    path('booking_detail/', views.booking_detail_view, name='booking_detail'),
    path("booking-details/add/", views.add_booking_detail, name="add_booking_detail"),
    path("booking-details/update/<int:detail_id>/", views.update_booking_detail, name="update_booking_detail"),
    path("booking-details/delete/<int:detail_id>/", views.delete_booking_detail, name="delete_booking_detail"),

    # payment
    path('payment/', views.payment_view, name='payment'),
    path("payments/add/", views.add_payment, name="add_payment"),
    path("payments/update/<int:payment_id>/", views.update_payment, name="update_payment"),
    path("payments/delete/<int:payment_id>/", views.delete_payment, name="delete_payment"),

    #check_in
    path('check_in/', views.check_in_view, name='check_in'),
    path("checkins/add/", views.add_checkin, name="add_checkin"),
    path("checkins/update/<int:checkin_id>/", views.update_checkin, name="update_checkin"),
    path("checkins/delete/<int:checkin_id>/", views.delete_checkin, name="delete_checkin"),

    # student
    path('student/', views.student_view, name='student'),
    path("students/add/", views.add_student, name="add_student"),
    path("students/update/<int:student_id>/", views.update_student, name="update_student"),
    path("students/delete/<int:student_id>/", views.delete_student, name="delete_student"),

    # passenger
    path('passenger/', views.passenger_view, name='passenger'),
    path("passengers/add/", views.add_passenger, name="add_passenger"),
    path("passengers/update/<int:passenger_id>/", views.update_passenger, name="update_passenger"),
    path("passengers/delete/<int:passenger_id>/", views.delete_passenger, name="delete_passenger"),
]
