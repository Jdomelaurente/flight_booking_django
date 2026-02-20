from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminLoginView,
    AirlineTaxViewSet, 
    AirlineViewSet, 
    AirportViewSet, 
    AircraftViewSet,
    BookingDetailViewSet,
    BookingTaxViewSet,
    BookingViewSet,
    CheckInDetailViewSet,
    DashboardViewSet,
    PassengerInfoViewSet,
    PassengerTypeTaxRateViewSet, 
    SeatClassViewSet, 
    AddOnTypeViewSet,
    RouteViewSet,
    FlightViewSet,
    ScheduleViewSet,
    SeatViewSet,
    SeatRequirementViewSet,
    AirportFeeViewSet,
    TaxTypeViewSet,
    StudentsViewSet,
    InstructorsViewSet,
    PaymentViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()

# ... (rest of the router registrations)
router.register(r'seat-requirements', SeatRequirementViewSet, basename='seatrequirement')
router.register(r'students', StudentsViewSet, basename='student')
router.register(r'instructors', InstructorsViewSet, basename='instructor')

# ==========================================
# DASHBOARD
# ==========================================
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

# ==========================================
# MANAGE FLIGHT
# ==========================================
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'flights', FlightViewSet, basename='flight')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'seats', SeatViewSet, basename='seat')
# ==========================================
# ASSETS
# ==========================================
router.register(r'airlines', AirlineViewSet, basename='airline')
router.register(r'airports', AirportViewSet, basename='airport')
router.register(r'aircraft', AircraftViewSet, basename='aircraft')
router.register(r'seat-classes', SeatClassViewSet, basename='seatclass')
router.register(r'add-ons', AddOnTypeViewSet, basename='addon')

# ==========================================
# BOOKING
# ==========================================
router.register(r'booking-details', BookingDetailViewSet, basename='bookingdetail')

# ==========================================
# PASSENGER
# ==========================================
router.register(r'passengers', PassengerInfoViewSet, basename='passenger')
router.register(r'checkins', CheckInDetailViewSet, basename='checkin')

# ==========================================
# MANAGE TAX
# ==========================================
router.register(r'airport-fees', AirportFeeViewSet, basename='airportfee')
router.register(r'tax-types', TaxTypeViewSet, basename='taxtype')
router.register(r'airline-taxes', AirlineTaxViewSet, basename='airlinetax')
router.register(r'passenger-tax-rates', PassengerTypeTaxRateViewSet, basename='passengertaxrate')
router.register(r'booking-taxes', BookingTaxViewSet, basename='bookingtax')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    # Manual path for login
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    
    # Include all the router-generated CRUD URLs
    path('', include(router.urls)),
]