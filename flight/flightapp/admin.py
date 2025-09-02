from django.contrib import admin
from .models import (
    MyUser,
    Airline,
    Aircraft,
    Airport,
    Route,
    Flight,
    Schedule,
    SeatClass,
    Seat,
    Booking,
    BookingDetail,
    Payment,
    CheckInDetail,
    PassengerInfo,
    Student,
    TrackLog,
)

# Register models
admin.site.register(MyUser)
admin.site.register(Airline)
admin.site.register(Aircraft)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Flight)
admin.site.register(Schedule)
admin.site.register(SeatClass)
admin.site.register(Seat)
admin.site.register(Booking)
admin.site.register(BookingDetail)
admin.site.register(Payment)
admin.site.register(CheckInDetail)
admin.site.register(PassengerInfo)
admin.site.register(Student)
admin.site.register(TrackLog)
