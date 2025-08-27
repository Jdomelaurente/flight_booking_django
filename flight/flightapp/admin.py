from django.contrib import admin
from .models import (
    MyUser, Airport, Airline, Aircraft, Route, Flight, Schedule,
    SeatClass, Seat, Student, BookingDetail, Payment, CheckInDetail
)

admin.site.register([
    MyUser, Airport, Airline, Aircraft, Route, Flight, Schedule,
    SeatClass, Seat, Student, BookingDetail, Payment, CheckInDetail
])
