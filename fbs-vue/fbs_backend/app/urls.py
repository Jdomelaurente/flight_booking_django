from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.admin_auth_views import AdminLoginView
from .api.asset_views import (
    AirlineTaxViewSet, AirlineViewSet, AirportViewSet, 
    AircraftViewSet, SeatClassViewSet, AddOnTypeViewSet,
    TaxTypeViewSet, AirportFeeViewSet, PassengerTypeTaxRateViewSet
)
from .api.booking_views import (
    BookingDetailViewSet, BookingTaxViewSet, BookingViewSet, PaymentViewSet
)
from .api.checkin_views import CheckInDetailViewSet
from .api.dashboard_views import DashboardViewSet
from .api.passenger_views import PassengerInfoViewSet
from .api.flight_views import (
    RouteViewSet, FlightViewSet, ScheduleViewSet, 
    SeatViewSet, SeatRequirementViewSet
)
from .api.student_views import StudentsViewSet
from .api.instructor_views import InstructorsViewSet
from .api.extra_services_views import (
    CountryViewSet, SeatClassFeatureViewSet, InsuranceProviderViewSet,
    InsuranceBenefitViewSet, InsuranceCoverageTypeViewSet, TravelInsurancePlanViewSet,
    PlanCoverageViewSet, MealCategoryViewSet, MealOptionViewSet,
    AssistanceServiceViewSet, BaggageOptionViewSet, PricingConfigurationViewSet
)
from .api.tracklog_views import TrackLogViewSet
from .api.import_views import UniversalImportView
from .api.otp_views import RequestOTPView, VerifyOTPAndResetView, SetPasswordWithTokenView
from .api.dcs_views import get_dcs_flights, get_dcs_manifest, process_dcs_checkin, scan_qr_lookup, get_dcs_passenger_details, get_dcs_pnr_details, download_boarding_pass_view, assign_dcs_seat


# Create a router and register our viewsets
router = DefaultRouter()

# DASHBOARD
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

# USERS
router.register(r'students', StudentsViewSet, basename='student')
router.register(r'instructors', InstructorsViewSet, basename='instructor')

# MANAGE FLIGHT
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'flights', FlightViewSet, basename='flight')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'seats', SeatViewSet, basename='seat')
router.register(r'seat-requirements', SeatRequirementViewSet, basename='seatrequirement')

# ASSETS
router.register(r'airlines', AirlineViewSet, basename='airline')
router.register(r'airports', AirportViewSet, basename='airport')
router.register(r'aircraft', AircraftViewSet, basename='aircraft')
router.register(r'seat-classes', SeatClassViewSet, basename='seatclass')
router.register(r'add-ons', AddOnTypeViewSet, basename='addon')

# BOOKING & PASSENGER
router.register(r'booking-details', BookingDetailViewSet, basename='bookingdetail')
router.register(r'passengers', PassengerInfoViewSet, basename='passenger')
router.register(r'checkins', CheckInDetailViewSet, basename='checkin')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')

# TAX & FEES
router.register(r'airport-fees', AirportFeeViewSet, basename='airportfee')
router.register(r'tax-types', TaxTypeViewSet, basename='taxtype')
router.register(r'airline-taxes', AirlineTaxViewSet, basename='airlinetax')
router.register(r'passenger-tax-rates', PassengerTypeTaxRateViewSet, basename='passengertaxrate')
router.register(r'booking-taxes', BookingTaxViewSet, basename='bookingtax')

# EXTRA SERVICES & CONFIG
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'seat-class-features', SeatClassFeatureViewSet, basename='seatclassfeature')
router.register(r'insurance-providers', InsuranceProviderViewSet, basename='insuranceprovider')
router.register(r'insurance-benefits', InsuranceBenefitViewSet, basename='insurancebenefit')
router.register(r'insurance-coverage-types', InsuranceCoverageTypeViewSet, basename='insurancecoveragetype')
router.register(r'insurance-plans', TravelInsurancePlanViewSet, basename='insuranceplan')
router.register(r'plan-coverages', PlanCoverageViewSet, basename='plancoverage')
router.register(r'meal-categories', MealCategoryViewSet, basename='mealcategory')
router.register(r'meal-options', MealOptionViewSet, basename='mealoption')
router.register(r'assistance-services', AssistanceServiceViewSet, basename='assistanceservice')
router.register(r'baggage-options', BaggageOptionViewSet, basename='baggageoption')
router.register(r'pricing-config', PricingConfigurationViewSet, basename='pricingconfig')
router.register(r'tracklogs', TrackLogViewSet, basename='tracklog')

urlpatterns = [
    # Manual path for login
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    
    # OTP Password Reset
    path('auth/otp/request/', RequestOTPView.as_view(), name='otp-request'),
    path('auth/otp/reset/', VerifyOTPAndResetView.as_view(), name='otp-reset'),
    path('auth/set-password/', SetPasswordWithTokenView.as_view(), name='set-password'),
    
    # DCS Simulator paths
    path('dcs/flights/', get_dcs_flights, name='dcs_flights'),
    path('dcs/manifest/<int:schedule_id>/', get_dcs_manifest, name='dcs_manifest'),
    path('dcs/process-checkin/', process_dcs_checkin, name='dcs_process_checkin'),
    path('dcs/passenger/<int:booking_detail_id>/', get_dcs_passenger_details, name='dcs_passenger_details'),
    path('dcs/pnr/<str:pnr>/<int:schedule_id>/', get_dcs_pnr_details, name='dcs_pnr_details'),
    path('dcs/boarding-pass/<int:booking_detail_id>/', download_boarding_pass_view, name='dcs_boarding_pass'),
    path('dcs/scan-qr/', scan_qr_lookup, name='dcs_scan_qr'),
    path('dcs/assign-seat/', assign_dcs_seat, name='dcs_assign_seat'),
    
    # Universal CSV Import
    path('universal-import/', UniversalImportView.as_view(), name='universal-import'),
    
    # Include all the router-generated CRUD URLs
    path('', include(router.urls)),
]