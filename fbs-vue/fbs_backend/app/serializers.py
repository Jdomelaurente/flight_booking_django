from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    AirlineTax, AirportFee, Booking, BookingDetail, BookingTax, CheckInDetail,
    PassengerInfo, Students, PassengerTypeTaxRate, Route, Airline, SeatClass,
    Aircraft, Airport, AddOnType, AddOn, Flight, Schedule, Seat, TaxType, TrackLog,
    SeatRequirement, Payment, Country, SeatClassFeature,
    InsuranceProvider, InsuranceBenefit, InsuranceCoverageType, TravelInsurancePlan,
    PlanCoverage, MealCategory, MealOption, AssistanceService, BaggageOption,
    PricingConfiguration
)
from fbs_instructor.models import Instructor

# ==========================================
# USER SERIALIZER
# ==========================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Added first_name and last_name to the fields
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class StudentsSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Students
        fields = [
            'id', 
            'username',
            'student_number', 
            'first_name', 
            'last_name', 
            'mi', 
            'full_name',
            'email', 
            'phone_number', 
            'gender', 
            'course',
            'year_level',
            'date_enrolled'
        ]
        read_only_fields = ['date_enrolled']

    def get_full_name(self, obj):
        if obj.mi:
            return f"{obj.first_name} {obj.mi}. {obj.last_name}"
        return f"{obj.first_name} {obj.last_name}"


# ==========================================
# INSTRUCTOR SERIALIZER
# ==========================================
class InstructorsSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Instructor
        fields = [
            'id', 
            'instructor_id', 
            'first_name', 
            'last_name', 
            'middle_initial', 
            'full_name',
            'email', 
            'phone'
        ]

    def get_full_name(self, obj):
        parts = [obj.first_name, f"{obj.middle_initial}." if obj.middle_initial else None, obj.last_name]
        return " ".join([p for p in parts if p])
# ==========================================
# MANAGE FLIGHT
# ==========================================
class RouteSerializer(serializers.ModelSerializer):
    # This allows you to see the airport codes in the GET request
    origin_info = serializers.StringRelatedField(source='origin_airport', read_only=True)
    destination_info = serializers.StringRelatedField(source='destination_airport', read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'origin_airport', 'destination_airport', 'origin_info', 'destination_info', 'base_price']

class FlightSerializer(serializers.ModelSerializer):
    airline_display = serializers.ReadOnlyField(source='airline.name')
    aircraft_display = serializers.ReadOnlyField(source='aircraft.model')
    route_display = serializers.ReadOnlyField(source='route.__str__')

    class Meta:
        model = Flight
        fields = ['id', 'flight_number', 'airline', 'airline_display', 
                  'aircraft', 'aircraft_display', 'route', 'route_display', 'total_stops', 'layovers_data']

class ScheduleSerializer(serializers.ModelSerializer):
    flight_number = serializers.ReadOnlyField(source='flight.flight_number')
    duration_display = serializers.ReadOnlyField(source='duration')
    aircraft_name = serializers.ReadOnlyField(source='flight.aircraft.model')
    aircraft_capacity = serializers.ReadOnlyField(source='flight.aircraft.capacity')
    
    # Add nested flight data with full aircraft info
    flight_detail = FlightSerializer(source='flight', read_only=True)

    flight = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all(),
        required=True,
        allow_null=False
    )
    
    status = serializers.ReadOnlyField(source='automatic_status')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    available_seat_classes = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = [
            'id', 
            'flight', 
            'flight_number',
            'flight_detail',
            'aircraft_name',
            'aircraft_capacity',
            'departure_time', 
            'arrival_time', 
            'price', 
            'status', 
            'status_display', 
            'duration_display',
            'available_seat_classes'
        ]

    def get_available_seat_classes(self, obj):
        """Get seat classes from aircraft layout config"""
        if obj.flight and obj.flight.aircraft:
            config = obj.flight.aircraft.get_layout_config()
            return config.get('seat_classes', [])
        return []


class SeatRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatRequirement
        fields = '__all__'


# Update your SeatSerializer in serializers.py
# Add this to your serializers.py

class SeatSerializer(serializers.ModelSerializer):
    class_name = serializers.ReadOnlyField(source='seat_class.name')
    final_price = serializers.ReadOnlyField()
    final_price_display = serializers.SerializerMethodField()
    seat_features = serializers.ReadOnlyField()
    special_requirements = serializers.ReadOnlyField()
    price_breakdown = serializers.ReadOnlyField()
    seat_code = serializers.ReadOnlyField()
    is_booked = serializers.SerializerMethodField()
    is_locked = serializers.ReadOnlyField() # Model Property
    is_locked_by_me = serializers.SerializerMethodField()
    
    # Requirements relation
    requirements_detail = SeatRequirementSerializer(source='requirements', many=True, read_only=True)
    
    # Additional fields for frontend
    schedule_price = serializers.ReadOnlyField(source='schedule.price')
    seat_class_multiplier = serializers.ReadOnlyField(source='seat_class.price_multiplier')
    
    class Meta:
        model = Seat
        fields = '__all__'
        read_only_fields = ['price_adjustment_auto', 'seat_code']

    def get_final_price_display(self, obj):
        return f"₱{obj.final_price:,.2f}"
    
    def get_is_booked(self, obj):
        """Check if seat is linked to an active booking OR is locked by another session"""
        
        # 1. Existing Booking Check
        is_permanently_booked = BookingDetail.objects.filter(
            seat=obj,
            status__in=['pending', 'confirmed', 'checkin', 'boarding', 'completed']
        ).exists()
        
        if is_permanently_booked:
            return True
            
        # 2. Lock check (Locked by someone else)
        if obj.is_locked:
            request = self.context.get('request')
            session_id = None
            if request:
                session_id = request.query_params.get('session_id') or request.data.get('session_id')
                if not session_id and hasattr(request, 'session'):
                    session_id = request.session.session_key
            
            # If locked by someone else, it's "booked" (unavailable)
            return obj.locked_by_session != session_id
            
        return False

    def get_is_locked_by_me(self, obj):
        """Check if THIS specific session holds the lock"""
        request = self.context.get('request')
        if not request or not obj.is_locked:
            return False
            
        session_id = request.query_params.get('session_id') or request.data.get('session_id')
        if not session_id and hasattr(request, 'session'):
            session_id = request.session.session_key
            
        return obj.locked_by_session == session_id
    
    def to_representation(self, instance):
        """Custom representation to include dynamic prices from database"""
        data = super().to_representation(instance)
        
        # Add dynamic price adjustments info from SeatRequirement table
        reqs = SeatRequirement.objects.all()
        req_info = {}
        for r in reqs:
            req_info[r.code] = {
                'id': r.id,
                'name': r.name,
                'price': float(r.price),
                'icon': r.icon,
                'description': r.description
            }
            
        data['price_adjustments_info'] = req_info
        return data


# ==========================================
# ASSETS
# ==========================================
class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ['id', 'name', 'code', 'logo']

class SeatClassSerializer(serializers.ModelSerializer):
    airline_name = serializers.ReadOnlyField(source='airline.name')  # Already exists
    class Meta:
        model = SeatClass
        fields = ['id', 'name', 'price_multiplier', 'airline', 'airline_name', 'description', 'is_active', 'color']

class AircraftSerializer(serializers.ModelSerializer):
    airline_name = serializers.ReadOnlyField(source='airline.name')

    class Meta:
        model = Aircraft
        fields = ['id', 'model', 'capacity', 'airline', 'airline_name', 'layout_config']
    
    def to_representation(self, instance):
        """Include computed layout config"""
        data = super().to_representation(instance)
        data['computed_layout'] = instance.get_layout_config()
        return data

class AirportSerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField(source='country.name')
    airport_type_display = serializers.CharField(source='get_airport_type_display', read_only=True)

    class Meta:
        model = Airport
        # MAKE SURE 'id' IS HERE!
        fields = ['id', 'name', 'code', 'city', 'country', 'country_name', 'location', 'airport_type', 'airport_type_display', 'latitude', 'longitude']

class AddOnTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOnType
        fields = ['id', 'name', 'description']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


# ==========================================
# COUNTRY
# ==========================================
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'currency']


# ==========================================
# SEAT CLASS FEATURE & FARE BUNDLES
# ==========================================
from .models import FareBundle, FareBundleFeature

class SeatClassFeatureSerializer(serializers.ModelSerializer):
    seat_class_name = serializers.ReadOnlyField(source='seat_class.name')
    class Meta:
        model = SeatClassFeature
        fields = ['id', 'seat_class', 'seat_class_name', 'feature', 'icon', 'display_order', 'is_active']

class FareBundleFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FareBundleFeature
        fields = ['id', 'feature_text', 'display_order', 'is_active']

class FareBundleSerializer(serializers.ModelSerializer):
    features = FareBundleFeatureSerializer(source='bundle_features', many=True, read_only=True)
    
    class Meta:
        model = FareBundle
        fields = ['id', 'seat_class', 'name', 'type_code', 'markup_fee', 'description', 'icon_svg', 'display_order', 'is_active', 'features']



# ==========================================
# INSURANCE
# ==========================================
class InsuranceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceProvider
        fields = ['id', 'name', 'code', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class InsuranceBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceBenefit
        fields = ['id', 'name', 'description', 'icon_class', 'display_order', 'is_active']

class InsuranceCoverageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCoverageType
        fields = ['id', 'name', 'code', 'icon_class', 'display_order', 'is_active']

class TravelInsurancePlanSerializer(serializers.ModelSerializer):
    provider_name = serializers.ReadOnlyField(source='provider.name')
    class Meta:
        model = TravelInsurancePlan
        fields = ['id', 'name', 'provider', 'provider_name', 'retail_price', 'is_active', 'display_order', 'description', 'airlines']

class PlanCoverageSerializer(serializers.ModelSerializer):
    plan_name = serializers.ReadOnlyField(source='insurance_plan.name')
    coverage_type_name = serializers.ReadOnlyField(source='coverage_type.name')
    class Meta:
        model = PlanCoverage
        fields = ['id', 'insurance_plan', 'plan_name', 'coverage_type', 'coverage_type_name', 'amount', 'description']


# ==========================================
# MEALS
# ==========================================
class MealCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MealCategory
        fields = ['id', 'name', 'description', 'display_order']

class MealOptionSerializer(serializers.ModelSerializer):
    airline_name = serializers.ReadOnlyField(source='airline.name')
    is_available = serializers.BooleanField(source='is_active', default=True)
    class Meta:
        model = MealOption
        fields = ['id', 'name', 'meal_type', 'airline', 'airline_name', 'price', 'is_available', 'display_order']


# ==========================================
# ASSISTANCE
# ==========================================
class AssistanceServiceSerializer(serializers.ModelSerializer):
    airline_name = serializers.ReadOnlyField(source='airline.name')
    is_available = serializers.BooleanField(source='is_active', default=True)
    class Meta:
        model = AssistanceService
        fields = ['id', 'name', 'service_type', 'airline', 'airline_name', 'price', 'is_available', 'display_order']


# ==========================================
# BAGGAGE
# ==========================================
class BaggageOptionSerializer(serializers.ModelSerializer):
    airline_name = serializers.ReadOnlyField(source='airline.name')
    is_available = serializers.BooleanField(source='is_active', default=True)
    class Meta:
        model = BaggageOption
        fields = ['id', 'weight_kg', 'airline', 'airline_name', 'price', 'is_available', 'display_order']


# ==========================================
# PRICING CONFIGURATION
# ==========================================
class PricingConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingConfiguration
        fields = '__all__'


# ==========================================
# BOOKING MANAGEMENT SERIALIZERS
# ==========================================
class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for booking details with passenger and flight information.
    """
    # Related fields for easy access
    passenger_name = serializers.SerializerMethodField()
    passenger_type = serializers.ReadOnlyField(source='passenger.passenger_type')
    flight_number = serializers.ReadOnlyField(source='schedule.flight.flight_number')
    route_display = serializers.ReadOnlyField(source='schedule.flight.route.__str__')
    departure_time = serializers.ReadOnlyField(source='schedule.departure_time')
    seat_number = serializers.SerializerMethodField()
    seat_class_name = serializers.SerializerMethodField()
    airline_name = serializers.ReadOnlyField(source='schedule.flight.airline.name')
    arrival_time = serializers.ReadOnlyField(source='schedule.arrival_time')
    addons = serializers.PrimaryKeyRelatedField(many=True, queryset=AddOn.objects.all(), required=False)
    addon_details = serializers.SerializerMethodField()

    class Meta:
        model = BookingDetail
        fields = [
            'id',
            'booking',
            'passenger',
            'passenger_name',
            'passenger_type',
            'schedule',
            'flight_number',
            'airline_name',
            'route_display',
            'departure_time',
            'arrival_time',
            'seat',
            'seat_number',
            'seat_class_name',
            'addons',
            'addon_details',
            'booking_date',
            'price',
            'tax_amount',
            'status',
        ]

    def get_passenger_name(self, obj):
        """Get passenger's full name."""
        return obj.passenger.get_full_name()

    def get_seat_number(self, obj):
        """Get seat number safely."""
        return obj.seat.seat_number if obj.seat else "NOT ASSIGNED"

    def get_seat_class_name(self, obj):
        """Get seat class name safely."""
        return obj.seat_class.name if obj.seat_class else "Standard"

    def get_addon_details(self, obj):
        """Get list of addon names."""
        return [a.name for a in obj.addons.all()]

    def validate_seat(self, value):
        """Ensure the chosen seat is available for the same schedule."""
        if value:
            # If we are changing seats, check availability
            # (Note: Current seat of this booking detail is technically 'occupied')
            booking_detailId = self.instance.id if self.instance else None
            # If the seat is already assigned to THIS booking detail, it's fine
            if self.instance and self.instance.seat == value:
                return value
                
            if not value.is_available:
                raise serializers.ValidationError("This seat is no longer available.")
                
            # Double check it belongs to the same schedule
            if self.instance and value.schedule != self.instance.schedule:
                raise serializers.ValidationError("Selected seat does not belong to this flight schedule.")
                
        return value

    def update(self, instance, validated_data):
        """Update instance and handle seat availability toggle."""
        old_seat = instance.seat
        new_seat = validated_data.get('seat', old_seat)
        
        # If seat changed
        if old_seat != new_seat:
            if old_seat:
                old_seat.is_available = True
                old_seat.save(update_fields=['is_available'])
            if new_seat:
                new_seat.is_available = False
                new_seat.save(update_fields=['is_available'])
        
        return super().update(instance, validated_data)

# ==========================================
# PASSENGER MANAGEMENT SERIALIZERS
# ==========================================
class PassengerInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for passenger information with additional computed fields.
    """
    # Computed fields
    booking_count = serializers.SerializerMethodField()
    last_booking = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = PassengerInfo
        fields = [
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'title',
            'date_of_birth',
            'passport_number',
            'passport_expiry',
            'nationality',
            'passenger_type',
            'linked_adult',
            # Computed fields
            'booking_count',
            'last_booking',
            'full_name',
            'age',
        ]
    
    def get_booking_count(self, obj):
        """Get number of bookings for this passenger."""
        return BookingDetail.objects.filter(passenger=obj).count()
    
    def get_last_booking(self, obj):
        """Get the most recent booking date."""
        last_booking = BookingDetail.objects.filter(
            passenger=obj
        ).order_by('-booking_date').first()
        return last_booking.booking_date if last_booking else None
    
    def get_full_name(self, obj):
        """Get full name of passenger."""
        if obj.middle_name:
            return f"{obj.first_name} {obj.middle_name} {obj.last_name}"
        return f"{obj.first_name} {obj.last_name}"
    
    def get_age(self, obj):
        """Calculate age from date of birth."""
        if obj.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None

# ==========================================
# CHECK-IN SERIALIZERS
# ==========================================
class PassengerCheckInSerializer(serializers.ModelSerializer):
    """Serializer for passenger info in check-ins"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PassengerInfo
        fields = ['id', 'first_name', 'last_name', 'full_name', 'passport_number']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class BookingDetailCheckInSerializer(serializers.ModelSerializer):
    """Serializer for booking details in check-ins"""
    passenger = PassengerCheckInSerializer()
    schedule_info = serializers.SerializerMethodField()
    
    class Meta:
        model = BookingDetail
        fields = ['id', 'passenger', 'seat', 'schedule_info']
    
    def get_schedule_info(self, obj):
        return {
            'flight_number': obj.schedule.flight.flight_number,
            'departure_time': obj.schedule.departure_time,
            'route': str(obj.schedule.flight.route)
        }


class CheckInDetailSerializer(serializers.ModelSerializer):
    """Main serializer for check-in details"""
    booking_detail = BookingDetailCheckInSerializer(read_only=True)
    booking_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=BookingDetail.objects.all(),
        write_only=True,
        source='booking_detail'
    )
    
    passenger_name = serializers.ReadOnlyField()
    flight_number = serializers.ReadOnlyField()
    route_display = serializers.ReadOnlyField(source='route')
    departure_time = serializers.ReadOnlyField()
    seat_number = serializers.ReadOnlyField()
    
    # For creating check-ins
    seat_assignment = serializers.CharField(required=False, allow_blank=True)
    baggage_count = serializers.IntegerField(min_value=0, default=0)
    baggage_weight = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, default=0)
    
    class Meta:
        model = CheckInDetail
        fields = [
            'id',
            'booking_detail',
            'booking_detail_id',
            'check_in_time',
            'check_in_counter',
            'agent_id',
            'baggage_count',
            'baggage_weight',
            'boarding_pass',
            'seat_assignment',
            'gate_number',
            'status',
            'has_declared_safety',
            'special_instructions',
            'created_at',
            'updated_at',
            # Read-only fields for display
            'passenger_name',
            'flight_number',
            'route_display',
            'departure_time',
            'seat_number',
        ]
        read_only_fields = ['boarding_pass', 'check_in_time', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate check-in data"""
        booking_detail = data.get('booking_detail')
        
        # Check if booking detail exists and is confirmed
        if booking_detail and booking_detail.status != 'confirmed':
            raise serializers.ValidationError({
                'booking_detail': 'Booking must be confirmed before check-in'
            })
        
        # Check if already checked in
        if CheckInDetail.objects.filter(
            booking_detail=booking_detail,
            status__in=['checked-in', 'boarding']
        ).exists():
            raise serializers.ValidationError({
                'booking_detail': 'Passenger is already checked in'
            })
        
        return data
    
    def create(self, validated_data):
        """Create a new check-in record"""
        # Set status to checked-in by default if not provided
        if 'status' not in validated_data:
            validated_data['status'] = 'checked-in'
        
        instance = super().create(validated_data)
        
        # Generate boarding pass if not provided
        if not instance.boarding_pass:
            instance.generate_boarding_pass()
        
        return instance


class CheckInListSerializer(serializers.ModelSerializer):
    """Simplified serializer for check-in list view"""
    passenger_name = serializers.ReadOnlyField()
    flight_number = serializers.ReadOnlyField()
    route = serializers.ReadOnlyField()
    departure_time = serializers.ReadOnlyField()
    seat_number = serializers.ReadOnlyField()
    
    class Meta:
        model = CheckInDetail
        fields = [
            'id',
            'passenger_name',
            'flight_number',
            'route',
            'departure_time',
            'seat_number',
            'check_in_time',
            'check_in_counter',
            'baggage_count',
            'baggage_weight',
            'boarding_pass',
            'status',
            'gate_number',
        ]
    
class TrackLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = TrackLog
        fields = ['id', 'user', 'action', 'timestamp']
    
    def get_user(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email
            }
        return None
    
class TaxTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxType
        fields = '__all__'

class AirportFeeSerializer(serializers.ModelSerializer):
    airport = AirportSerializer(read_only=True)
    tax_type = TaxTypeSerializer(read_only=True)
    
    class Meta:
        model = AirportFee
        fields = ['id', 'airport', 'tax_type', 'amount']
    
    def create(self, validated_data):
        airport_id = self.initial_data.get('airport_id')
        tax_type_id = self.initial_data.get('tax_type_id')
        
        validated_data['airport_id'] = airport_id
        validated_data['tax_type_id'] = tax_type_id
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        airport_id = self.initial_data.get('airport_id')
        tax_type_id = self.initial_data.get('tax_type_id')
        
        if airport_id:
            instance.airport_id = airport_id
        if tax_type_id:
            instance.tax_type_id = tax_type_id
            
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance

class AirlineTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirlineTax
        fields = ['id', 'airline', 'tax_type', 'amount']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['airline'] = AirlineSerializer(instance.airline).data if instance.airline else None
        rep['tax_type'] = TaxTypeSerializer(instance.tax_type).data if instance.tax_type else None
        return rep

class PassengerTypeTaxRateSerializer(serializers.ModelSerializer):
    tax_type = TaxTypeSerializer(read_only=True)
    
    class Meta:
        model = PassengerTypeTaxRate
        fields = ['id', 'tax_type', 'passenger_type', 'amount']
    
    def create(self, validated_data):
        tax_type_id = self.initial_data.get('tax_type')
        validated_data['tax_type_id'] = tax_type_id
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        tax_type_id = self.initial_data.get('tax_type')
        if tax_type_id:
            instance.tax_type_id = tax_type_id
        instance.passenger_type = validated_data.get('passenger_type', instance.passenger_type)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance
    
# Add this before BookingTaxSerializer
class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    contact_phone = serializers.SerializerMethodField()
    contact_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'pnr', 'user', 'user_name', 'user_email', 'contact_phone', 'contact_email', 'trip_type', 'status', 'created_at', 'total_amount']

    def get_user_name(self, obj):
        # Try to get the lead passenger's name first for the manifest
        first_detail = obj.details.first()
        if first_detail and first_detail.passenger:
            return first_detail.passenger.get_full_name()
            
        # Fallback to booking contact info
        if hasattr(obj, 'contact') and obj.contact:
            return f"{obj.contact.first_name} {obj.contact.last_name}"
            
        # Fallback to the account user who made the booking
        return obj.user.get_full_name() if obj.user else None

    def get_user_email(self, obj):
        if hasattr(obj, 'contact') and obj.contact:
            return obj.contact.email
        return obj.user.email if obj.user else None

    def get_contact_phone(self, obj):
        if hasattr(obj, 'contact') and obj.contact:
            return obj.contact.phone
        return None

    def get_contact_email(self, obj):
        return self.get_user_email(obj)

# Your existing BookingTaxSerializer
class BookingTaxSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    tax_type = TaxTypeSerializer(read_only=True)
    
    class Meta:
        model = BookingTax
        fields = ['id', 'booking', 'tax_type', 'amount', 'passenger_type', 'created_at']
