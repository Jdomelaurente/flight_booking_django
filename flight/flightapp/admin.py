# flightapp/admin.py
from django.contrib import admin
from .models import (
    User,
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
    Instructor,
    TrackLog,
    AddOn,
    AddOnType,
    # Tax system models
    TaxType,
    AirlineTax,
    AirportFee,
    TravelTaxRate,
    BookingTax,
    InsurancePlan,
    BookingDetailInsurance,
    Country
)

# ============================================================
# CUSTOM ADMIN CLASSES FOR BETTER DISPLAY
# ============================================================
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'currency']
    search_fields = ['name', 'code']
    ordering = ['name']



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'last_login', 'created_at']
    list_filter = ['role', 'last_login']
    search_fields = ['username', 'email']
    ordering = ['-created_at']

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    ordering = ['code']

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ['model', 'airline', 'capacity']
    list_filter = ['airline']
    search_fields = ['model', 'airline__name']
    ordering = ['airline', 'model']

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'city', 'country', 'airport_type']
    list_filter = ['airport_type', 'country']
    search_fields = ['code', 'name', 'city', 'country']
    ordering = ['code']

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['origin_airport', 'destination_airport', 'base_price', 'is_domestic', 'is_international']
    list_filter = ['origin_airport', 'destination_airport']
    search_fields = ['origin_airport__code', 'destination_airport__code']
    ordering = ['origin_airport']
    
    def is_domestic(self, obj):
        return obj.is_domestic
    is_domestic.boolean = True
    
    def is_international(self, obj):
        return obj.is_international
    is_international.boolean = True

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'airline', 'aircraft', 'route']
    list_filter = ['airline', 'route']
    search_fields = ['flight_number', 'airline__code']
    ordering = ['flight_number']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['flight', 'departure_time', 'arrival_time', 'duration', 'status']
    list_filter = ['status', 'departure_time', 'flight__airline']
    search_fields = ['flight__flight_number']
    ordering = ['-departure_time']
    
    def duration(self, obj):
        return obj.duration()

@admin.register(SeatClass)
class SeatClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'airline', 'price_multiplier']
    list_filter = ['airline']
    search_fields = ['name', 'airline__code']
    ordering = ['airline', 'name']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'seat_number', 'seat_class', 'is_available']
    list_filter = ['is_available', 'schedule__flight__airline', 'seat_class']
    search_fields = ['seat_number', 'schedule__flight__flight_number']
    ordering = ['schedule', 'seat_number']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'trip_type', 'status', 'created_at', 'total_amount']
    list_filter = ['status', 'trip_type', 'created_at']
    search_fields = ['student__first_name', 'student__last_name', 'student__student_number']
    ordering = ['-created_at']
    
    def total_amount(self, obj):
        return f"₱{obj.total_amount}"
    total_amount.short_description = 'Total'

@admin.register(BookingDetail)
class BookingDetailAdmin(admin.ModelAdmin):
    list_display = ['booking', 'passenger', 'schedule', 'seat', 'price', 'booking_date']
    list_filter = ['schedule__flight__airline', 'booking_date']
    search_fields = ['booking__id', 'passenger__first_name', 'passenger__last_name']
    ordering = ['-booking_date']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'method', 'status', 'payment_date']
    list_filter = ['status', 'method', 'payment_date']
    search_fields = ['booking__id', 'transaction_id']
    ordering = ['-payment_date']

@admin.register(CheckInDetail)
class CheckInDetailAdmin(admin.ModelAdmin):
    list_display = ['booking_detail', 'check_in_time', 'baggage_count', 'baggage_weight']
    list_filter = ['check_in_time']
    search_fields = ['booking_detail__booking__id']
    ordering = ['-check_in_time']

@admin.register(PassengerInfo)
class PassengerInfoAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'passenger_type', 'date_of_birth', 'nationality']
    list_filter = ['passenger_type', 'gender', 'nationality']
    search_fields = ['first_name', 'last_name', 'passport_number']
    ordering = ['last_name', 'first_name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_number', 'first_name', 'last_name', 'email', 'phone']
    search_fields = ['student_number', 'first_name', 'last_name', 'email']
    ordering = ['student_number']

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'instructor_id', 'phone']
    search_fields = ['first_name', 'last_name', 'email', 'instructor_id']
    ordering = ['last_name', 'first_name']

@admin.register(TrackLog)
class TrackLogAdmin(admin.ModelAdmin):
    list_display = ['student', 'action', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['student__first_name', 'student__last_name', 'action']
    ordering = ['-timestamp']

@admin.register(AddOnType)
class AddOnTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    ordering = ['name']

@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ['name', 'airline', 'type', 'price', 'included']
    list_filter = ['airline', 'type', 'included']
    search_fields = ['name', 'description', 'airline__code']
    ordering = ['airline', 'name']

# ============================================================
# TAX SYSTEM ADMIN CLASSES
# ============================================================

@admin.register(TaxType)
class TaxTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'per_passenger', 'adult_only', 'applies_domestic', 'applies_international', 'base_amount']
    list_filter = ['per_passenger', 'adult_only', 'applies_domestic', 'applies_international']
    search_fields = ['name', 'code']
    ordering = ['code']

@admin.register(AirlineTax)
class AirlineTaxAdmin(admin.ModelAdmin):
    list_display = ['airline', 'tax_type', 'amount']
    list_filter = ['airline', 'tax_type']
    search_fields = ['airline__code', 'tax_type__name']
    ordering = ['airline', 'tax_type']

@admin.register(AirportFee)
class AirportFeeAdmin(admin.ModelAdmin):
    list_display = ['airport', 'tax_type', 'amount']
    list_filter = ['airport', 'tax_type']
    search_fields = ['airport__code', 'tax_type__name']
    ordering = ['airport', 'tax_type']

@admin.register(TravelTaxRate)
class TravelTaxRateAdmin(admin.ModelAdmin):
    list_display = ['passenger_type', 'amount']
    list_filter = ['passenger_type']
    search_fields = ['passenger_type']
    ordering = ['passenger_type']

@admin.register(BookingTax)
class BookingTaxAdmin(admin.ModelAdmin):
    list_display = ['booking_detail', 'tax_type', 'amount', 'description']
    list_filter = ['tax_type']
    search_fields = ['booking_detail__booking__id', 'tax_type__name', 'description']
    ordering = ['-booking_detail__booking__id']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('booking_detail', 'booking_detail__booking', 'tax_type')

@admin.register(InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    list_display = ['airline', 'name', 'price', 'is_default', 'is_active']
    list_filter = ['airline', 'is_default', 'is_active']
    search_fields = ['name', 'airline__code', 'coverage_description']
    ordering = ['airline', 'name']

@admin.register(BookingDetailInsurance)
class BookingDetailInsuranceAdmin(admin.ModelAdmin):
    list_display = ['booking_detail', 'plan', 'purchased_at']
    list_filter = ['plan__airline', 'purchased_at']
    search_fields = ['booking_detail__id', 'plan__name']
    ordering = ['-purchased_at']

# ============================================================
# ALTERNATIVE: Simple registration (if you don't need custom admin)
# ============================================================
"""
# Or use simple registration for all models:
admin.site.register(User)
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
admin.site.register(Instructor)
admin.site.register(TrackLog)
admin.site.register(AddOnType)
admin.site.register(AddOn)
admin.site.register(TaxType)
admin.site.register(AirlineTax)
admin.site.register(AirportFee)
admin.site.register(TravelTaxRate)
admin.site.register(BookingTax)
admin.site.register(InsurancePlan)
admin.site.register(BookingDetailInsurance)
"""

# ============================================================
# INLINE ADMIN CLASSES FOR BETTER RELATIONSHIP VIEWING
# ============================================================

class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0
    readonly_fields = ['seat_number', 'seat_class', 'is_available']
    can_delete = False

class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0
    readonly_fields = ['departure_time', 'arrival_time', 'status']
    can_delete = False

class BookingDetailInline(admin.TabularInline):
    model = BookingDetail
    extra = 0
    readonly_fields = ['passenger', 'schedule', 'seat', 'price']
    can_delete = False

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['amount', 'method', 'status', 'payment_date']
    can_delete = False

class BookingTaxInline(admin.TabularInline):
    model = BookingTax
    extra = 0
    readonly_fields = ['tax_type', 'amount', 'description']
    can_delete = False

# Add these inlines to existing admin classes
ScheduleAdmin.inlines = [SeatInline]
FlightAdmin.inlines = [ScheduleInline]
BookingAdmin.inlines = [BookingDetailInline, PaymentInline]
BookingDetailAdmin.inlines = [BookingTaxInline]

print("✅ FlightApp Admin registered successfully!")
print("📋 Available models in admin:")
print("   - Airlines, Aircraft, Airports, Routes")
print("   - Flights, Schedules, Seats")
print("   - Bookings, Payments, Passengers")
print("   - Students, Instructors, Track Logs")
print("   - Add-ons and Add-on Types")
print("   - Tax System: Tax Types, Airline Taxes, Airport Fees")
print("   - Travel Tax Rates, Booking Taxes")
print("   - Insurance Plans")