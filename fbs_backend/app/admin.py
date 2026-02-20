from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from .models import *
from .models import SeatClass, Schedule
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile  # make sure the import is correct

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.forms.models import BaseInlineFormSet
from .models import UserProfile


class UserProfileInlineFormSet(BaseInlineFormSet):
    """
    Prevent Django admin from trying to create a second UserProfile.
    """
    def save_new(self, form, commit=True):
        # Always reuse existing profile
        return UserProfile.objects.get(user=self.instance)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    formset = UserProfileInlineFormSet
    can_delete = False
    extra = 0
    max_num = 1
    verbose_name_plural = "Profile"


def get_role(obj):
    return getattr(obj.userprofile, 'role', '—')

get_role.short_description = 'Role'


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        get_role,
    )

# ============================================================
# STUDENT ADMINISTRATION
# ============================================================

@admin.register(Students)
class StudentAdmin(admin.ModelAdmin):
    # This controls the columns visible in the table list view
    list_display = (
        'student_number', 
        'first_name', 
        'mi', 
        'last_name', 
        'gender',  # ? Added gender to list view
        'email', 
        'phone_number', 
        'date_enrolled',
        'user'
    )
    
    # Adds a search bar for these specific fields
    search_fields = ('student_number', 'first_name', 'last_name', 'email')
    
    # Adds a filter sidebar for the enrollment date and gender
    list_filter = ('date_enrolled', 'gender')  # ? Added gender filter
    
    # Orders the list so the newest students appear at the top
    ordering = ('-date_enrolled',)
    
    # Makes the auto-generated date field viewable but not editable
    readonly_fields = ('date_enrolled',)

    # Groups the fields nicely when you click on a student to edit them
    fieldsets = (
        ('Account Details', {
            'fields': ('user', 'student_number')
        }),
        ('Personal Information', {
            'fields': (('first_name', 'mi', 'last_name'), 'gender', 'email', 'phone_number')  # ? Added gender field
        }),
        ('System Information', {
            'fields': ('date_enrolled', 'password'),
        }),
    )

    
@admin.register(BookingContact)
class BookingContactAdmin(admin.ModelAdmin):
    list_display = ('booking', 'first_name', 'last_name', 'email', 'phone', 'created_at')
    list_filter = ('created_at', 'title')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'booking__id')
    readonly_fields = ('created_at', 'updated_at')
    
    # Simple fieldsets with only the fields that exist in your model
    fieldsets = (
        ('Contact Information', {
            'fields': (
                'booking',
                ('title', 'first_name', 'middle_name', 'last_name'),
                ('email', 'phone'),
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
# ============================================================
# INLINE ADMIN CLASSES
# ============================================================

class AirportInline(admin.TabularInline):
    model = Airport
    extra = 0
    fields = ('name', 'code', 'city', 'airport_type')
    readonly_fields = ('is_international', 'is_domestic', 'is_philippine_airport')


class SeatClassInline(admin.TabularInline):
    model = SeatClass
    extra = 0
    fields = ('name', 'price_multiplier', 'description')


class AircraftInline(admin.TabularInline):
    model = Aircraft
    extra = 0
    fields = ('model', 'capacity')


class RouteInline(admin.TabularInline):
    model = Route
    extra = 0
    fields = ('origin_airport', 'destination_airport', 'base_price', 'is_domestic', 'is_international')
    readonly_fields = ('is_domestic', 'is_international', 'is_philippine_domestic')


class FlightInline(admin.TabularInline):
    model = Flight
    extra = 0
    fields = ('flight_number', 'aircraft', 'route')
    readonly_fields = ('route_display',)


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0
    fields = ('departure_time', 'arrival_time', 'price', 'status')
    # Remove duration from fields since it requires both times to be set
    
    # Or if you want to keep duration, make it a method that handles None values:
    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj and obj.departure_time and obj.arrival_time:
            fields.append('duration')
        return fields


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0
    fields = ('seat_number', 'seat_class', 'is_available')
    readonly_fields = ('is_available',)


class PlanCoverageInline(admin.TabularInline):
    model = PlanCoverage
    extra = 0
    fields = ('coverage_type', 'amount', 'description')


class BookingDetailInline(admin.TabularInline):
    model = BookingDetail
    extra = 0
    fields = ('passenger', 'schedule', 'seat', 'price', 'get_has_insurance', 'status')
    readonly_fields = ('get_has_insurance', 'get_total_amount')
    show_change_link = True
    
    def get_has_insurance(self, obj):
        return obj.get_has_insurance()
    get_has_insurance.short_description = "Has Insurance"
    get_has_insurance.boolean = True
    
    def get_total_amount(self, obj):
        return obj.get_total_amount()
    get_total_amount.short_description = "Total"


class BookingTaxInline(admin.TabularInline):
    model = BookingTax
    extra = 0
    fields = ('tax_type', 'passenger_type', 'amount')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('method', 'amount', 'status', 'payment_date')
    readonly_fields = ('payment_date',)


class CheckInDetailInline(admin.TabularInline):
    model = CheckInDetail
    extra = 0
    fields = ('check_in_time', 'boarding_pass', 'baggage_count', 'baggage_weight')
    readonly_fields = ('check_in_time',)


class TrackLogInline(admin.TabularInline):
    model = TrackLog
    extra = 0
    fields = ('action', 'timestamp')
    readonly_fields = ('timestamp',)


# ============================================================
# MAIN ADMIN CLASSES
# ============================================================

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'currency', 'airport_count')
    list_filter = ('currency',)
    search_fields = ('name', 'code')
    ordering = ('name',)
    inlines = [AirportInline]
    
    def airport_count(self, obj):
        return obj.airports.count()
    airport_count.short_description = 'Airports'


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'flight_count', 'aircraft_count', 'seat_class_count')
    list_filter = ('code',)
    search_fields = ('name', 'code')
    ordering = ('code',)
    inlines = [SeatClassInline, AircraftInline]
    
    def flight_count(self, obj):
        return obj.flights.count()
    flight_count.short_description = 'Flights'
    
    def aircraft_count(self, obj):
        return obj.aircrafts.count()
    aircraft_count.short_description = 'Aircraft'
    
    def seat_class_count(self, obj):
        return obj.seat_classes.count()
    seat_class_count.short_description = 'Seat Classes'


class SeatClassFeatureInline(admin.TabularInline):
    model = SeatClassFeature
    extra = 1
@admin.register(SeatClass)
class SeatClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'airline', 'price_multiplier', 'is_active']
    list_filter = ['airline', 'is_active']
    search_fields = ['name', 'airline__name']
    inlines = [SeatClassFeatureInline]
    
    def description_short(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_short.short_description = 'Description'
    
@admin.register(SeatClassFeature)
class SeatClassFeatureAdmin(admin.ModelAdmin):
    list_display = ['seat_class', 'feature', 'display_order', 'is_active']
    list_filter = ['seat_class', 'is_active']
    search_fields = ['feature', 'seat_class__name']

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('model', 'airline', 'capacity', 'flight_count')
    list_filter = ('airline', 'capacity')
    search_fields = ('model', 'airline__name')
    ordering = ('airline', 'model')
    raw_id_fields = ('airline',)
    
    def flight_count(self, obj):
        return obj.flights.count()
    flight_count.short_description = 'Flights'


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'country', 'airport_type', 'is_international', 'is_philippine_airport')
    list_filter = ('airport_type', 'country', 'city')
    search_fields = ('name', 'code', 'city', 'country__name')
    ordering = ('country', 'code')
    raw_id_fields = ('country',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'city', 'country', 'location')
        }),
        ('Type & Classification', {
            'fields': ('airport_type', 'is_international', 'is_domestic', 'is_philippine_airport')
        }),
    )
    readonly_fields = ('is_international', 'is_domestic', 'is_philippine_airport')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('origin_airport', 'destination_airport', 'base_price', 
                    'is_domestic', 'is_international', 'flight_count', 'is_philippine_domestic')
    list_filter = ('origin_airport__country', 'destination_airport__country', 
                   'origin_airport__airport_type', 'destination_airport__airport_type')
    search_fields = ('origin_airport__name', 'destination_airport__name',
                     'origin_airport__code', 'destination_airport__code')
    ordering = ('origin_airport', 'destination_airport')
    raw_id_fields = ('origin_airport', 'destination_airport')
    
    def flight_count(self, obj):
        return obj.flights.count()
    flight_count.short_description = 'Flights'
    
    fieldsets = (
        ('Route Information', {
            'fields': ('origin_airport', 'destination_airport', 'base_price')
        }),
        ('Classification', {
            'fields': ('is_domestic', 'is_international', 'is_philippine_domestic')
        }),
    )
    readonly_fields = ('is_domestic', 'is_international', 'is_philippine_domestic')


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'airline', 'aircraft', 'route', 'schedule_count')
    list_filter = ('airline', 'aircraft__model')
    search_fields = ('flight_number', 'airline__name', 'route__origin_airport__code')
    ordering = ('flight_number',)
    raw_id_fields = ('airline', 'aircraft', 'route')
    inlines = [ScheduleInline]
    
    def schedule_count(self, obj):
        return obj.schedules.count()
    schedule_count.short_description = 'Schedules'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('flight', 'departure_time', 'arrival_time', 'duration', 
                    'price', 'status', 'seat_count', 'available_seats')
    list_filter = ('status', 'departure_time', 'flight__airline')
    search_fields = ('flight__flight_number', 'flight__airline__name')
    date_hierarchy = 'departure_time'
    ordering = ('-departure_time',)
    raw_id_fields = ('flight',)
    inlines = [SeatInline]
    
    # Make duration method handle None values in list_display
    def duration(self, obj):
        if obj.departure_time and obj.arrival_time:
            diff = obj.arrival_time - obj.departure_time
            total_minutes = int(diff.total_seconds() // 60)
            hours, minutes = divmod(total_minutes, 60)
            days = diff.days

            if days > 0:
                return f"{hours}h {minutes}m (+{days}d)"
            return f"{hours}h {minutes}m"
        return "N/A"
    duration.short_description = 'Duration'
    
    def seat_count(self, obj):
        return obj.seats.count()
    seat_count.short_description = 'Total Seats'
    
    def available_seats(self, obj):
        return obj.seats.filter(is_available=True).count()
    available_seats.short_description = 'Available'
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('flight', 'departure_time', 'arrival_time', 'price', 'status')
        }),
        ('Calculated Fields', {
            'fields': ('is_open',)
        }),
    )
    readonly_fields = ('is_open',)  # Remove duration from readonly_fields
    
    actions = ['mark_as_open', 'mark_as_closed']
    
    def mark_as_open(self, request, queryset):
        updated = queryset.update(status='Open')
        self.message_user(request, f'{updated} schedule(s) marked as Open.')
    mark_as_open.short_description = "Mark selected schedules as Open"
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='Closed')
        self.message_user(request, f'{updated} schedule(s) marked as Closed.')
    mark_as_closed.short_description = "Mark selected schedules as Closed"


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = (
        'seat_number', 'schedule', 'seat_class', 'is_available', 
        'row', 'column', 'is_exit_row', 'is_wheelchair_accessible', 
        'display_requirements', 'booking_link'
    )
    list_filter = (
        'is_available', 'seat_class', 'is_exit_row', 
        'is_wheelchair_accessible', 'schedule__flight__airline'
    )
    search_fields = ('seat_number', 'schedule__flight__flight_number')
    ordering = ('schedule', 'seat_number')
    raw_id_fields = ('schedule', 'seat_class')
    list_editable = ('is_available', 'is_exit_row', 'is_wheelchair_accessible')
    filter_horizontal = ('requirements',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('schedule', 'seat_class', 'seat_number', 'is_available')
        }),
        ('Position', {
            'fields': ('row', 'column')
        }),
        ('Static Features (Booleans)', {
            'fields': (
                ('is_window', 'is_aisle'),
                ('is_exit_row', 'is_bulkhead', 'has_extra_legroom'),
                ('is_wheelchair_accessible', 'has_bassinet'),
                ('has_nut_allergy', 'is_unaccompanied_minor'),
            )
        }),
        ('Dynamic Requirements', {
            'fields': ('requirements',),
            'description': 'Select multiple special requirements from the database.'
        }),
        ('Pricing', {
            'fields': (('price_adjustment_auto', 'price_adjustment_manual'),)
        }),
    )
    readonly_fields = ('price_adjustment_auto',)

    def display_requirements(self, obj):
        return ", ".join([r.name for r in obj.requirements.all()])
    display_requirements.short_description = 'Requirements'

    def booking_link(self, obj):
        booking_detail = BookingDetail.objects.filter(seat=obj).first()
        if booking_detail:
            url = reverse('admin:app_bookingdetail_change', args=[booking_detail.id])
            return format_html('<a href="{}">View Booking</a>', url)
        return '-'
    booking_link.short_description = 'Booking'


@admin.register(SeatRequirement)
class SeatRequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'icon')
    list_editable = ('price',)
    search_fields = ('name', 'code')


# ============================================================
# INSURANCE ADMIN CLASSES
# ============================================================

@admin.register(InsuranceProvider)
class InsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'default_commission_rate', 'plan_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)
    inlines = []
    
    def plan_count(self, obj):
        return obj.insurance_plans.count()
    plan_count.short_description = 'Plans'


@admin.register(InsuranceBenefit)
class InsuranceBenefitAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'is_active', 'icon_display')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('display_order', 'name')
    list_editable = ('display_order', 'is_active')
    
    def icon_display(self, obj):
        if obj.icon_class:
            return format_html('<i class="{}"></i> {}', obj.icon_class, obj.icon_class)
        return '-'
    icon_display.short_description = 'Icon'


@admin.register(InsuranceCoverageType)
class InsuranceCoverageTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'unit', 'display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('display_order', 'name')
    list_editable = ('display_order', 'is_active')


@admin.register(TravelInsurancePlan)
class TravelInsurancePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'retail_price', 'wholesale_price', 
                    'commission_rate', 'plan_type', 'is_active', 'airline_count')
    list_filter = ('provider', 'plan_type', 'is_active', 'seller_type')
    search_fields = ('name', 'provider__name', 'description')
    ordering = ('provider', 'retail_price')
    filter_horizontal = ('airlines', 'benefits')
    inlines = [PlanCoverageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('provider', 'name', 'description', 'plan_type', 'best_for')
        }),
        ('Pricing', {
            'fields': ('retail_price', 'wholesale_price')
        }),
        ('Availability', {
            'fields': ('airlines', 'seller_type', 'coverage_duration_days')
        }),
        ('Legal & Documents', {
            'fields': ('policy_document_url', 'terms_conditions_url', 'claims_contact')
        }),
        ('Display & Status', {
            'fields': ('benefits', 'is_default', 'is_active', 'display_order')
        }),
    )
    
    def airline_count(self, obj):
        return obj.airlines.count()
    airline_count.short_description = 'Airlines'
    
    readonly_fields = ('commission_amount', 'commission_rate')
    
    def save_model(self, request, obj, form, change):
        # Auto-calculate wholesale price if not set
        if not obj.wholesale_price:
            commission_rate = obj.provider.default_commission_rate
            obj.wholesale_price = obj.retail_price * (1 - commission_rate / 100)
        super().save_model(request, obj, form, change)


@admin.register(PlanCoverage)
class PlanCoverageAdmin(admin.ModelAdmin):
    list_display = ('insurance_plan', 'coverage_type', 'amount', 'formatted_amount')
    list_filter = ('coverage_type', 'insurance_plan__provider')
    search_fields = ('insurance_plan__name', 'coverage_type__name')
    ordering = ('insurance_plan', 'coverage_type__display_order')
    raw_id_fields = ('insurance_plan', 'coverage_type')
    
    def formatted_amount(self, obj):
        return f"?{obj.amount:,.2f}"
    formatted_amount.short_description = 'Amount'


@admin.register(BookingInsuranceRecord)
class BookingInsuranceRecordAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'booking_detail_link', 'insurance_plan', 
                    'sale_price', 'commission_rate', 'status', 'is_valid', 'purchased_at')
    list_filter = ('status', 'insurance_plan__provider', 'purchased_at')
    search_fields = ('policy_number', 'booking_detail__passenger__first_name',
                     'booking_detail__passenger__last_name')
    date_hierarchy = 'purchased_at'
    ordering = ('-purchased_at',)
    raw_id_fields = ('booking_detail', 'insurance_plan')
    readonly_fields = ('policy_number', 'purchased_at', 'updated_at', 
                       'policy_issued_at', 'is_valid', 'financial_summary')
    
    fieldsets = (
        ('Policy Information', {
            'fields': ('policy_number', 'booking_detail', 'insurance_plan', 'status')
        }),
        ('Coverage Period', {
            'fields': ('coverage_start', 'coverage_end')
        }),
        ('Financial Details', {
            'fields': ('sale_price', 'commission_rate', 'commission_amount', 
                      'provider_payout', 'insured_amount', 'financial_summary')
        }),
        ('Timestamps', {
            'fields': ('purchased_at', 'policy_issued_at', 'updated_at')
        }),
    )
    
    def booking_detail_link(self, obj):
        if obj.booking_detail:
            url = reverse('admin:app_bookingdetail_change', args=[obj.booking_detail.id])
            return format_html('<a href="{}">{}</a>', url, obj.booking_detail.passenger.get_full_name())
        return '-'
    booking_detail_link.short_description = 'Passenger'
    
    def financial_summary(self, obj):
        return f"Sale: ?{obj.sale_price:,.2f} | Commission: ?{obj.commission_amount:,.2f} ({obj.commission_rate}%) | Payout: ?{obj.provider_payout:,.2f}"
    financial_summary.short_description = 'Financial Summary'


# ============================================================
# PASSENGER & BOOKING ADMIN CLASSES
# ============================================================

@admin.register(PassengerInfo)
class PassengerInfoAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'title', 'date_of_birth', 'passenger_type', 
                    'nationality', 'booking_count', 'has_passport')
    list_filter = ('passenger_type', 'title', 'nationality')
    search_fields = ('first_name', 'last_name', 'passport_number')
    ordering = ('last_name', 'first_name')
    raw_id_fields = ('linked_adult',)
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'last_name'
    
    def booking_count(self, obj):
        return BookingDetail.objects.filter(passenger=obj).count()
    booking_count.short_description = 'Bookings'
    
    def has_passport(self, obj):
        return bool(obj.passport_number)
    has_passport.boolean = True
    has_passport.short_description = 'Passport'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'trip_type', 'status', 'created_at', 
                    'get_total_amount', 'get_has_insurance', 'payment_status')
    list_filter = ('status', 'trip_type', 'created_at', 'user')
    search_fields = ('id', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [BookingDetailInline, BookingTaxInline, PaymentInline]
    readonly_fields = ('created_at', 'get_total_amount', 'get_has_insurance', 'financial_summary')
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'trip_type', 'status', 'created_at')
        }),
        ('Financial Summary', {
            'fields': ('base_fare_total', 'insurance_total', 'tax_total', 
                      'get_total_amount', 'financial_summary')
        }),
    )

    def get_total_amount(self, obj):
        return obj.total_amount
    get_total_amount.short_description = "Total Amount"
    
    def get_has_insurance(self, obj):
        return obj.has_insurance
    get_has_insurance.short_description = "Has Insurance"
    get_has_insurance.boolean = True
    
    def payment_status(self, obj):
        payment = obj.payment
        if payment:
            color = 'green' if payment.status == 'Completed' else 'orange' if payment.status == 'Pending' else 'red'
            return format_html('<span style="color: {};">{}</span>', color, payment.status)
        return '-'
    payment_status.short_description = 'Payment Status'
    
    def financial_summary(self, obj):
        return f"Base Fare: ?{obj.base_fare_total:,.2f} | Insurance: ?{obj.insurance_total:,.2f} | Tax: ?{obj.tax_total:,.2f} | Total: ?{obj.total_amount:,.2f}"
    financial_summary.short_description = 'Breakdown'
    
    actions = ['mark_as_confirmed', 'cancel_bookings']
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='Confirmed')
        self.message_user(request, f'{updated} booking(s) marked as Confirmed.')
    mark_as_confirmed.short_description = "Mark selected bookings as Confirmed"
    
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(status='Cancelled')
        self.message_user(request, f'{updated} booking(s) cancelled.')
    cancel_bookings.short_description = "Cancel selected bookings"



@admin.register(BookingDetail)
class BookingDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'schedule', 'price', 'get_pricing_factors', 'is_fiesta_period']
    
    def get_pricing_factors(self, obj):
        from flightapp.pricing.ph_holiday_calendar import PhilippineCalendar
        impact = PhilippineCalendar.get_holiday_impact(obj.schedule.departure_time.date())
        
        badges = []
        if impact['is_fiesta']:
            badges.append("? Fiesta")
        if impact['is_long_weekend']:
            badges.append("?? Long Weekend")
        if impact['is_payday']:
            badges.append("? Payday")
        
        return " | ".join(badges) if badges else "Standard"
    get_pricing_factors.short_description = "PH Factors"
    
    def is_fiesta_period(self, obj):
        from flightapp.pricing.ph_holiday_calendar import PhilippineCalendar
        impact = PhilippineCalendar.get_holiday_impact(obj.schedule.departure_time.date())
        return impact['is_fiesta']
    is_fiesta_period.boolean = True


# ============================================================
# ADD-ONS ADMIN
# ============================================================

@admin.register(AddOnType)
class AddOnTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'addon_count')
    search_fields = ('name', 'description')
    
    def addon_count(self, obj):
        return obj.addons.count()
    addon_count.short_description = 'Add-ons'


@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ('name', 'airline', 'type', 'price', 'included', 'is_insurance', 'created_at')
    list_filter = ('type', 'airline', 'included', 'created_at')
    search_fields = ('name', 'description', 'airline__name')
    raw_id_fields = ('airline', 'seat_class', 'type', 'insurance_plan')
    list_editable = ('price', 'included')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price', 'included')
        }),
        ('Associations', {
            'fields': ('airline', 'seat_class', 'type', 'insurance_plan')
        }),
    )


# ============================================================
# TAX SYSTEM ADMIN
# ============================================================

@admin.register(TaxType)
class TaxTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'base_amount', 'is_active', 
                    'applies_domestic', 'applies_international')
    list_filter = ('category', 'is_active', 'applies_domestic', 'applies_international')
    search_fields = ('name', 'code', 'description')
    list_editable = ('is_active', 'base_amount')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'category', 'is_active')
        }),
        ('Calculation Rules', {
            'fields': ('per_passenger', 'adult_only', 'base_amount')
        }),
        ('Applicability', {
            'fields': ('applies_domestic', 'applies_international', 'applies_departure_country')
        }),
    )


@admin.register(AirlineTax)
class AirlineTaxAdmin(admin.ModelAdmin):
    list_display = ('airline', 'tax_type', 'amount')
    list_filter = ('airline', 'tax_type__category')
    search_fields = ('airline__name', 'tax_type__name')
    raw_id_fields = ('airline', 'tax_type')


@admin.register(AirportFee)
class AirportFeeAdmin(admin.ModelAdmin):
    list_display = ('airport', 'tax_type', 'amount')
    list_filter = ('airport__country', 'tax_type')
    search_fields = ('airport__name', 'tax_type__name')
    raw_id_fields = ('airport', 'tax_type')


@admin.register(PassengerTypeTaxRate)
class PassengerTypeTaxRateAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'passenger_type', 'amount')
    list_filter = ('tax_type', 'passenger_type')
    search_fields = ('tax_type__name',)
    raw_id_fields = ('tax_type',)


@admin.register(BookingTax)
class BookingTaxAdmin(admin.ModelAdmin):
    list_display = ('booking', 'tax_type', 'passenger_type', 'amount')
    list_filter = ('tax_type', 'passenger_type')
    search_fields = ('booking__id', 'tax_type__name')
    raw_id_fields = ('booking', 'tax_type')


# ============================================================
# PAYMENT & CHECK-IN ADMIN
# ============================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking_link', 'amount', 'method', 'status', 'payment_date', 'transaction_id')
    list_filter = ('method', 'status', 'payment_date')
    search_fields = ('transaction_id', 'booking__id', 'booking__user__username')
    date_hierarchy = 'payment_date'
    ordering = ('-payment_date',)
    readonly_fields = ('payment_date',)
    
    def booking_link(self, obj):
        url = reverse('admin:app_booking_change', args=[obj.booking.id])
        return format_html('<a href="{}">Booking #{}</a>', url, obj.booking.id)
    booking_link.short_description = 'Booking'
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='Completed')
        self.message_user(request, f'{updated} payment(s) marked as Completed.')
    mark_as_completed.short_description = "Mark selected payments as Completed"
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='Failed')
        self.message_user(request, f'{updated} payment(s) marked as Failed.')
    mark_as_failed.short_description = "Mark selected payments as Failed"


@admin.register(CheckInDetail)
class CheckInDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking_detail_link', 'check_in_time', 'boarding_pass', 
                    'baggage_count', 'baggage_weight')
    list_filter = ('check_in_time', 'baggage_count')
    search_fields = ('boarding_pass', 'booking_detail__passenger__first_name')
    date_hierarchy = 'check_in_time'
    ordering = ('-check_in_time',)
    readonly_fields = ('check_in_time',)
    raw_id_fields = ('booking_detail',)
    
    def booking_detail_link(self, obj):
        url = reverse('admin:app_bookingdetail_change', args=[obj.booking_detail.id])
        return format_html('<a href="{}">{}</a>', url, obj.booking_detail.passenger.get_full_name())
    booking_detail_link.short_description = 'Passenger'


# ============================================================
# TRACKING ADMIN
# ============================================================

@admin.register(TrackLog)
class TrackLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_short', 'timestamp')
    list_filter = ('user', 'timestamp')
    search_fields = ('user__username', 'action')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    
    def action_short(self, obj):
        return obj.action[:100] + '...' if len(obj.action) > 100 else obj.action
    action_short.short_description = 'Action'


# ============================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================

# Customize admin site header and title
admin.site.site_header = "Flight Booking System Administration"
admin.site.site_title = "Flight Booking System Admin"
admin.site.index_title = "Welcome to Flight Booking System Administration"

# Optional: Add custom admin views or actions here

# Example: Add a summary dashboard action
class SummaryAdmin(admin.ModelAdmin):
    """Custom admin view for system summary"""
    def changelist_view(self, request, extra_context=None):
        # Add summary data to context
        extra_context = extra_context or {}
        
        # Get counts
        extra_context['total_bookings'] = Booking.objects.count()
        extra_context['total_flights'] = Flight.objects.count()
        extra_context['total_passengers'] = PassengerInfo.objects.count()
        extra_context['total_insurance_sales'] = BookingInsuranceRecord.objects.count()
        extra_context['revenue'] = Payment.objects.filter(status='Completed').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return super().changelist_view(request, extra_context)
    


# Add these imports at the top if not already there
from .models import MealCategory, MealOption, BaggageOption, AssistanceService

# ============================================================
# INLINE ADMIN CLASSES FOR ADD-ONS
# ============================================================

class MealOptionInline(admin.TabularInline):
    model = MealOption
    extra = 0
    fields = ('name', 'meal_type', 'price', 'is_included', 'is_active', 'display_order')
    readonly_fields = ('is_free',)
    show_change_link = True

class BaggageOptionInline(admin.TabularInline):
    model = BaggageOption
    extra = 0
    fields = ('name', 'weight_kg', 'price', 'is_included', 'is_active', 'display_order')
    readonly_fields = ('is_free', 'formatted_weight')
    show_change_link = True

class AssistanceServiceInline(admin.TabularInline):
    model = AssistanceService
    extra = 0
    fields = ('name', 'service_type', 'level', 'price', 'is_included', 'is_active', 'display_order')
    readonly_fields = ('is_free', 'advance_notice_text')
    show_change_link = True

# ============================================================
# NEW ADMIN CLASSES FOR ADD-ONS
# ============================================================

@admin.register(MealCategory)
class MealCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'display_order', 'meal_count')
    list_filter = ('display_order',)
    search_fields = ('name', 'description')
    ordering = ('display_order', 'name')
    list_editable = ('display_order',)
    
    def description_short(self, obj):
        if obj.description:
            return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
        return '-'
    description_short.short_description = 'Description'
    
    def meal_count(self, obj):
        return obj.mealoption_set.count()
    meal_count.short_description = 'Meals'


@admin.register(MealOption)
class MealOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'airline', 'meal_type', 'category', 'price', 
                    'is_included', 'is_free', 'calories', 'is_active', 'display_order')
    list_filter = ('airline', 'meal_type', 'category', 'is_active', 
                   'available_on_domestic', 'available_on_international')
    search_fields = ('name', 'description', 'airline__name', 'category__name')
    list_editable = ('price', 'is_included', 'is_active', 'display_order')
    ordering = ('display_order', 'name')
    raw_id_fields = ('airline', 'category')
    filter_horizontal = ()
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'airline', 'meal_type', 'category', 'image_url')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'is_included', 'is_active', 'display_order')
        }),
        ('Nutritional Information', {
            'fields': ('calories', 'contains', 'allergens')
        }),
        ('Availability', {
            'fields': ('available_on_domestic', 'available_on_international',
                      'available_for_breakfast', 'available_for_lunch', 
                      'available_for_dinner')
        }),
    )
    
    readonly_fields = ('is_free', 'dietary_info')
    
    def dietary_info(self, obj):
        return obj.dietary_info
    dietary_info.short_description = 'Dietary Information'
    
    actions = ['activate_meals', 'deactivate_meals']
    
    def activate_meals(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} meal option(s) activated.')
    activate_meals.short_description = "Activate selected meal options"
    
    def deactivate_meals(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} meal option(s) deactivated.')
    deactivate_meals.short_description = "Deactivate selected meal options"


@admin.register(BaggageOption)
class BaggageOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'airline', 'formatted_weight', 'dimensions', 'price', 
                    'is_included', 'is_free', 'is_active', 'display_order')
    list_filter = ('airline', 'is_active', 'applies_domestic', 'applies_international')
    search_fields = ('name', 'description', 'airline__name')
    list_editable = ('price', 'is_included', 'is_active', 'display_order')
    ordering = ('display_order', 'weight_kg')
    raw_id_fields = ('airline',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'airline')
        }),
        ('Baggage Details', {
            'fields': ('weight_kg', 'dimensions')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'is_included', 'is_active', 'display_order')
        }),
        ('Applicability', {
            'fields': ('applies_domestic', 'applies_international', 
                      'passenger_type_applicable')
        }),
    )
    
    readonly_fields = ('is_free', 'formatted_weight')
    
    actions = ['activate_baggage_options', 'deactivate_baggage_options']
    
    def activate_baggage_options(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} baggage option(s) activated.')
    activate_baggage_options.short_description = "Activate selected baggage options"
    
    def deactivate_baggage_options(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} baggage option(s) deactivated.')
    deactivate_baggage_options.short_description = "Deactivate selected baggage options"


@admin.register(AssistanceService)
class AssistanceServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'airline', 'service_type', 'level', 'price', 
                    'is_included', 'is_free', 'advance_notice_text', 'is_active', 'display_order')
    list_filter = ('airline', 'service_type', 'level', 'is_active')
    search_fields = ('name', 'description', 'airline__name', 'notes')
    list_editable = ('price', 'is_included', 'is_active', 'display_order')
    ordering = ('display_order', 'name')
    raw_id_fields = ('airline',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'airline', 'service_type', 'level')
        }),
        ('Requirements & Notes', {
            'fields': ('requires_advance_notice', 'special_requirements', 'notes')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'is_included', 'is_active', 'display_order')
        }),
        ('Applicability', {
            'fields': ('passenger_type_applicable',)
        }),
    )
    
    readonly_fields = ('is_free', 'advance_notice_text')
    
    actions = ['activate_assistance_services', 'deactivate_assistance_services']
    
    def activate_assistance_services(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} assistance service(s) activated.')
    activate_assistance_services.short_description = "Activate selected assistance services"
    
    def deactivate_assistance_services(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} assistance service(s) deactivated.')
    deactivate_assistance_services.short_description = "Deactivate selected assistance services"


# ============================================================
# UPDATE AIRLINE ADMIN TO INCLUDE ADD-ONS
# ============================================================

# First, unregister the existing AirlineAdmin if it exists
admin.site.unregister(Airline)

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'flight_count', 'aircraft_count', 
                    'seat_class_count', 'meal_count', 'baggage_count', 'assistance_count')
    list_filter = ('code',)
    search_fields = ('name', 'code')
    ordering = ('code',)
    
    # Add the new inlines for add-ons
    inlines = [
        SeatClassInline, 
        AircraftInline, 
        MealOptionInline, 
        BaggageOptionInline, 
        AssistanceServiceInline
    ]
    
    def flight_count(self, obj):
        return obj.flights.count()
    flight_count.short_description = 'Flights'
    
    def aircraft_count(self, obj):
        return obj.aircrafts.count()
    aircraft_count.short_description = 'Aircraft'
    
    def seat_class_count(self, obj):
        return obj.seat_classes.count()
    seat_class_count.short_description = 'Seat Classes'
    
    def meal_count(self, obj):
        return obj.meals.count()
    meal_count.short_description = 'Meal Options'
    
    def baggage_count(self, obj):
        return obj.baggage_options.count()
    baggage_count.short_description = 'Baggage Options'
    
    def assistance_count(self, obj):
        return obj.assistance_services.count()
    assistance_count.short_description = 'Assistance Services'


# ============================================================
# UPDATE ADDON ADMIN TO INCLUDE NEW FIELDS
# ============================================================

# First, unregister the existing AddOnAdmin if it exists
admin.site.unregister(AddOn)

@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ('name', 'airline', 'type', 'price', 'included', 
                    'is_insurance', 'is_meal', 'is_baggage', 'is_assistance', 'created_at')
    list_filter = ('type', 'airline', 'included', 'created_at')
    search_fields = ('name', 'description', 'airline__name')
    raw_id_fields = ('airline', 'seat_class', 'type', 'insurance_plan',
                     'meal_option', 'baggage_option', 'assistance_service')
    list_editable = ('price', 'included')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price', 'included')
        }),
        ('Associations', {
            'fields': ('airline', 'seat_class', 'type')
        }),
        ('Service Links', {
            'fields': ('insurance_plan', 'meal_option', 'baggage_option', 'assistance_service')
        }),
    )






# ============================================================
# PRICING CONFIGURATION
# ============================================================

@admin.register(PricingConfiguration)
class PricingConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for dynamic pricing configuration"""
    
    list_display = ('id', 'updated_at', 'anonymous_user_factor', 'loyal_user_factor')
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('User Factors', {
            'fields': (
                'anonymous_user_factor',
                'new_user_factor',
                'returning_user_factor',
                'loyal_user_factor',
            ),
            'description': 'Price multipliers based on user booking history'
        }),
        ('Demand Factors - Search Thresholds', {
            'fields': (
                'search_threshold_high',
                'search_threshold_medium',
                'search_threshold_low',
            ),
            'description': 'Search count thresholds for demand-based pricing'
        }),
        ('Demand Factors - Multipliers', {
            'fields': (
                'demand_factor_high',
                'demand_factor_medium',
                'demand_factor_low',
            ),
        }),
        ('Days Until Departure - Thresholds', {
            'fields': (
                'days_departure_critical',
                'days_departure_near',
                'days_departure_medium',
                'days_departure_far',
            ),
        }),
        ('Days Until Departure - Multipliers', {
            'fields': (
                'days_factor_critical',
                'days_factor_near',
                'days_factor_medium',
                'days_factor_far',
            ),
        }),
        ('Time-Based Factors', {
            'fields': (
                'peak_hour_factor',
                'weekend_factor',
                'peak_month_factor',
                'holiday_factor',
            ),
            'description': 'Multipliers for peak hours, weekends, and holidays'
        }),
        ('Inventory Factors - Occupancy Thresholds', {
            'fields': (
                'occupancy_high_threshold',
                'occupancy_medium_threshold',
                'occupancy_low_threshold',
            ),
        }),
        ('Inventory Factors - Multipliers', {
            'fields': (
                'occupancy_factor_high',
                'occupancy_factor_medium',
                'occupancy_factor_low',
            ),
        }),
        ('Metadata', {
            'fields': ('updated_at',),
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent creating multiple configurations (singleton pattern)"""
        return not PricingConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the configuration"""
        return False
