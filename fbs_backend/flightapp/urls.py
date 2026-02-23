# flightapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .insurance_views import TravelInsurancePlanViewSet

router = DefaultRouter()
router.register(r'countries', views.CountryViewSet)
router.register(r'airports', views.AirportViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'seats', views.SeatViewSet)
router.register(r'meal-options', views.MealOptionViewSet)
router.register(r'assistance-services', views.AssistanceServiceViewSet)
router.register(r'baggage-options', views.BaggageOptionViewSet)
router.register(r'bookings', views.BookingViewSet)  
router.register(r'insurance-plans', TravelInsurancePlanViewSet, basename='insurance-plan')

urlpatterns = [
    path('api/', include(router.urls)),

    # Dynamic pricing endpoints
    path('api/test-dynamic-pricing/', views.test_dynamic_pricing, name='test-dynamic-pricing'),
    path('api/predict-price/', views.predict_flight_price, name='predict-price'),

    # Payment endpoints
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('create-payment-source/', views.create_payment_source, name='create_payment_source'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),  
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('attach-payment-method/', views.attach_payment_method, name='attach_payment_method'),
    # Booking endpoints
    path('validate-activity-code/', views.validate_activity_code, name='validate_activity_code'),
    path('create-booking/', views.create_booking, name='create_booking'),
    path('update-booking/<int:booking_id>/', views.update_booking, name='update_booking'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('process-payment-callback/', views.process_payment_callback, name='process_payment_callback'),
    path('check-payment-status/<int:booking_id>/', views.check_payment_status, name='check_payment_status'),
    path('paymongo-webhook/', views.paymongo_webhook, name='paymongo_webhook'),
    path('booking/<int:booking_id>/', views.get_booking_details, name='get_booking_details'),
    path('api/verify-and-process-payment/', views.verify_and_process_payment, name='verify_and_process_payment'),
    path('api/test-paymongo-setup', views.test_paymongo_setup, name='test_paymongo_setup'),
    path('check-booking-status/<int:booking_id>/', views.check_booking_status, name='check_booking_status'),
    # flightapp/urls.py
    path('verify-session-payment/', views.verify_session_payment, name='verify_session_payment'),
    path('seat-class-features/', views.get_seat_class_features, name='seat_class_features'),
    path('api/seat-class-features/', views.get_seat_class_features, name='seat_class_features'),

        # PDF download endpoints
    path('download-boarding-pass/<int:booking_detail_id>/', views.download_boarding_pass, name='download_boarding_pass'),
    path('download-itinerary/<int:booking_id>/', views.download_itinerary, name='download_itinerary'),

    # Pricing
    path('calculate-price/', views.calculate_booking_price, name='calculate_booking_price'),

]

