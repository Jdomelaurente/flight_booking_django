# flightapp/serializers.py
from rest_framework import serializers
from django.db.models import Q
from decimal import Decimal
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from app.models import (
    Country, Airline, SeatClass, Aircraft, Airport,
    Route, Flight, Schedule, Seat, PassengerInfo,
    Booking, BookingDetail, AddOnType, AddOn,
    InsuranceProvider, InsuranceCoverageType, InsuranceBenefit,
    TravelInsurancePlan, PlanCoverage, BookingInsuranceRecord,
    TaxType, AirlineTax, AirportFee, PassengerTypeTaxRate, MealCategory,
    MealOption, AssistanceService, BaggageOption, BookingTax,
    Payment, CheckInDetail, TrackLog
)



class CountrySerializer(serializers.ModelSerializer):
    """Serializer to handle Country details inside Airport responses."""
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'currency']

class AirportSerializer(serializers.ModelSerializer):
    # Nested country details (read-only)
    country_details = CountrySerializer(source='country', read_only=True)
    
    # Adding the properties from your model as fields
    is_international = serializers.ReadOnlyField()
    is_domestic = serializers.ReadOnlyField()
    is_philippine_airport = serializers.ReadOnlyField()
    
    # Display the human-readable version of the choice field
    airport_type_display = serializers.CharField(
        source='get_airport_type_display', 
        read_only=True
    )

    class Meta:
        model = Airport
        fields = [
            'id', 
            'name', 
            'code', 
            'city', 
            'location', 
            'airport_type', 
            'airport_type_display',
            'country',         # Used for POST/PUT (expects the ID)
            'country_details', # Used for GET (provides the object)
            'is_international',
            'is_domestic',
            'is_philippine_airport'
        ]
        # We keep 'country' writeable for creation, but 'country_details' for display
        extra_kwargs = {
            'country': {'write_only': True}
        }



class ScheduleSerializer(serializers.ModelSerializer):
    # These "source" fields reach through the Foreign Keys
    airline_name = serializers.ReadOnlyField(source='flight.airline.name')
    airline_code = serializers.ReadOnlyField(source='flight.airline.code')
    flight_number = serializers.ReadOnlyField(source='flight.flight_number')
    
    # Route info
    origin = serializers.ReadOnlyField(source='flight.route.origin_airport.code')
    origin_city = serializers.ReadOnlyField(source='flight.route.origin_airport.city')
    destination = serializers.ReadOnlyField(source='flight.route.destination_airport.code')
    destination_city = serializers.ReadOnlyField(source='flight.route.destination_airport.city')
    
    # Helper method for duration (calls the model method)
    flight_duration = serializers.ReadOnlyField(source='duration')
    
    # Seat class fields
    available_classes = serializers.SerializerMethodField()
    seat_classes = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    is_domestic = serializers.SerializerMethodField()
    
    # ============ ML PRICING FIELDS ============
    # Override price to use ML price first
    price = serializers.SerializerMethodField()
    ml_base_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True,
        allow_null=True
    )
    ml_price_updated_at = serializers.DateTimeField(
        read_only=True,
        allow_null=True,
        format='%Y-%m-%d %H:%M:%S'
    )
    using_ml_price = serializers.SerializerMethodField()
    price_age_hours = serializers.SerializerMethodField()
    # ============================================
    
    def get_available_classes(self, obj):
        """Get unique seat classes with available seats"""
        from app.models import Seat
        seat_classes = Seat.objects.filter(
            schedule=obj,
            is_available=True
        ).values_list('seat_class__name', flat=True).distinct()
        return list(seat_classes)
    
    def get_seat_classes(self, obj):
        """Get seat classes with details"""
        from app.models import Seat
        seat_classes = Seat.objects.filter(
            schedule=obj,
            is_available=True
        ).select_related('seat_class').distinct('seat_class__name')
        
        return [
            {
                'name': seat.seat_class.name if seat.seat_class else 'Economy',
                'price_multiplier': float(seat.seat_class.price_multiplier) if seat.seat_class else 1.0
            }
            for seat in seat_classes
        ]
    
    def get_available_seats(self, obj):
        """Get total available seats count"""
        from app.models import Seat
        return Seat.objects.filter(schedule=obj, is_available=True).count()
    
    def get_is_domestic(self, obj):
        """Check if flight is domestic"""
        return obj.flight.route.is_domestic if obj.flight and obj.flight.route else False
    
    # ============ ML PRICING METHODS ============
    def get_price(self, obj):
        """Use ML price if available, otherwise fallback to regular price"""
        if hasattr(obj, 'ml_base_price') and obj.ml_base_price is not None:
            return obj.ml_base_price
        return obj.price if obj.price else Decimal('0.00')
    
    def get_using_ml_price(self, obj):
        """Indicate if ML price is being used"""
        return hasattr(obj, 'ml_base_price') and obj.ml_base_price is not None
    
    def get_price_age_hours(self, obj):
        """Get age of ML price in hours"""
        if obj.ml_price_updated_at:
            from django.utils import timezone
            delta = timezone.now() - obj.ml_price_updated_at
            return round(delta.total_seconds() / 3600, 1)
        return None
    # ============================================

    class Meta:
        model = Schedule
        fields = [
            'id', 'flight_number', 'airline_name', 'airline_code',
            'origin', 'origin_city', 'destination', 'destination_city',
            'departure_time', 'arrival_time', 'price', 'status', 
            'flight_duration', 'available_classes', 'seat_classes', 
            'available_seats', 'is_domestic',
            # ML pricing fields
            'ml_base_price', 'ml_price_updated_at', 'using_ml_price', 'price_age_hours'
        ]


class SeatSerializer(serializers.ModelSerializer):
    seat_class = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    seat_code = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    
    class Meta:
        model = Seat
        fields = [
            'id', 'seat_code', 'seat_number', 'row', 'column', 'is_available', 
            'price_adjustment', 'final_price', 'seat_class', 'seat_class_name',
            'is_window', 'is_aisle', 'has_extra_legroom', 'is_exit_row', 
            'is_wheelchair_accessible', 'has_bassinet', 'has_nut_allergy', 
            'is_unaccompanied_minor', 'is_bulkhead', 'price_adjustment_manual',
            'features'
        ]
    
    def get_seat_class(self, obj):
        if obj.seat_class:
            return {
                'id': obj.seat_class.id,
                'name': obj.seat_class.name,
                'price_multiplier': float(obj.seat_class.price_multiplier)
            }
        return None
    
    def get_final_price(self, obj):
        """Get final price using ML base price if available"""
        try:
            # Use the final_price property from your Seat model
            # This will now use schedule.ml_base_price if available
            return float(obj.final_price)
        except:
            # Fallback calculation with ML price first
            if obj.schedule:
                # Use ML base price if available, otherwise regular price
                base_price = obj.schedule.ml_base_price or obj.schedule.price or Decimal('0.00')
            else:
                base_price = Decimal('0.00')
            
            multiplier = obj.seat_class.price_multiplier if obj.seat_class else Decimal('1.00')
            adjustment = obj.price_adjustment if obj.price_adjustment else Decimal('0.00')
            return float((base_price * multiplier) + adjustment)
    
    def get_seat_code(self, obj):
        return f"{obj.row}{obj.column}" if obj.row and obj.column else obj.seat_number
    
    def get_features(self, obj):
        # Use the seat_features property from your Seat model
        features = []
        if obj.has_extra_legroom:
            features.append("Extra Legroom")
        if obj.is_exit_row:
            features.append("Exit Row")
        if obj.is_bulkhead:
            features.append("Bulkhead")
        if obj.is_window:
            features.append("Window")
        if obj.is_aisle:
            features.append("Aisle")
        return features
    def get_features(self, obj):
        # Use the seat_features property from your Seat model
        features = []
        if obj.has_extra_legroom:
            features.append("Extra Legroom")
        if obj.is_exit_row:
            features.append("Exit Row")
        if obj.is_bulkhead:
            features.append("Bulkhead")
        if obj.is_window:
            features.append("Window")
        if obj.is_aisle:
            features.append("Aisle")
        return features



class MealOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealOption
        fields = [
            'id', 'name', 'description', 'meal_type', 'price', 
            'is_included', 'dietary_info', 'image_url', 'is_free'
        ]

class AssistanceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistanceService
        fields = [
            'id', 'name', 'service_type', 'level', 'description', 
            'price', 'is_included', 'advance_notice_text', 'is_free'
        ]

class BaggageOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaggageOption
        fields = [
            'id', 'name', 'weight_kg', 'formatted_weight', 
            'price', 'is_included', 'is_free'
        ]

# ============================================================
# BOOKING & PAYMENT SERIALIZERS
# ============================================================

class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for booking display"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields

class PassengerInfoSerializer(serializers.ModelSerializer):
    """Serializer for passenger information"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PassengerInfo
        fields = [
            'id', 'first_name', 'middle_name', 'last_name', 'full_name',
            'title', 'date_of_birth', 'passport_number', 'nationality',
            'passenger_type', 'linked_adult'
        ]
    
    def get_full_name(self, obj):
        """Return full name of passenger"""
        return obj.get_full_name()

class SimpleScheduleSerializer(serializers.ModelSerializer):
    """Simplified schedule serializer for booking details"""
    flight_number = serializers.CharField(source='flight.flight_number', read_only=True)
    airline_code = serializers.CharField(source='flight.airline.code', read_only=True)
    origin = serializers.CharField(source='flight.route.origin_airport.code', read_only=True)
    destination = serializers.CharField(source='flight.route.destination_airport.code', read_only=True)
    
    class Meta:
        model = Schedule
        fields = ['id', 'flight_number', 'airline_code', 'origin', 'destination', 
                 'departure_time', 'arrival_time', 'price']

class SimpleSeatSerializer(serializers.ModelSerializer):
    """Simplified seat serializer for booking details"""
    seat_class_name = serializers.CharField(source='seat_class.name', read_only=True)
    
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'row', 'column', 'seat_class_name']

class AddOnSerializer(serializers.ModelSerializer):
    """Serializer for add-ons linked to booking details"""
    type_name = serializers.CharField(source='type.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AddOn
        fields = ['id', 'name', 'type', 'type_name', 'price', 'included', 'description']

class BookingDetailSerializer(serializers.ModelSerializer):
    """Serializer for booking details (passenger-flight combinations)"""
    passenger = PassengerInfoSerializer(read_only=True)
    schedule = SimpleScheduleSerializer(read_only=True)
    seat = SimpleSeatSerializer(read_only=True)
    addons = AddOnSerializer(many=True, read_only=True)
    seat_class_name = serializers.CharField(source='seat_class.name', read_only=True, allow_null=True)
    
    # Computed fields
    total_with_insurance = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    has_insurance = serializers.BooleanField(read_only=True)
    insurance_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = BookingDetail
        fields = [
            'id', 'passenger', 'schedule', 'seat', 'seat_class', 'seat_class_name',
            'booking_date', 'price', 'tax_amount', 'status', 'passenger_type',
            'addons', 'total_with_insurance', 'has_insurance', 'insurance_cost',
            'total_amount'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment records"""
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'method', 'transaction_id', 
            'payment_date', 'status'
        ]
        read_only_fields = ['payment_date']

class BookingSerializer(serializers.ModelSerializer):
    """Main booking serializer"""
    user = UserSerializer(read_only=True)
    details = BookingDetailSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    
    # Computed fields
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    has_insurance = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'trip_type', 'status', 'created_at',
            'base_fare_total', 'insurance_total', 'tax_total', 'total_amount',
            'has_insurance', 'details', 'payments'
        ]
        read_only_fields = ['created_at', 'base_fare_total', 'insurance_total', 'tax_total']

# ============================================================
# CREATE BOOKING REQUEST SERIALIZERS
# ============================================================

# Update the CreatePassengerSerializer in flightapp/serializers.py:

class CreatePassengerSerializer(serializers.Serializer):
    """Serializer for passenger data during booking creation"""
    
    # Accept both camelCase and snake_case from frontend
    first_name = serializers.CharField(
        max_length=100, 
        required=False,  # Make it optional since we'll handle both formats
        allow_blank=True,
        default=""
    )
    firstName = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default=""
    )
    
    last_name = serializers.CharField(
        max_length=100, 
        required=False,
        allow_blank=True,
        default=""
    )
    lastName = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default=""
    )
    
    middle_name = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True, 
        default=""
    )
    middleName = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default=""
    )
    
    title = serializers.CharField(max_length=10)
    
    date_of_birth = serializers.CharField(
        required=False, 
        allow_blank=True, 
        default=""
    )
    dateOfBirth = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )
    
    nationality = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True, 
        default="Philippines"
    )
    
    passport_number = serializers.CharField(
        max_length=50, 
        required=False, 
        allow_blank=True, 
        default=""
    )
    passportNumber = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default=""
    )
    
    type = serializers.CharField(max_length=10, default="Adult")
    passenger_type = serializers.CharField(
        max_length=10, 
        required=False, 
        allow_blank=True, 
        default=""
    )
    
    key = serializers.CharField(
        max_length=50, 
        required=False, 
        allow_blank=True, 
        default=""
    )
    
    def to_internal_value(self, data):
        """Convert camelCase to snake_case and handle both formats"""
        # First, normalize the data
        normalized_data = {}
        
        # Handle all possible field name variations
        field_mapping = {
            'firstName': 'first_name',
            'first_name': 'first_name',
            'lastName': 'last_name',
            'last_name': 'last_name',
            'middleName': 'middle_name',
            'middle_name': 'middle_name',
            'dateOfBirth': 'date_of_birth',
            'date_of_birth': 'date_of_birth',
            'passportNumber': 'passport_number',
            'passport_number': 'passport_number',
        }
        
        for key, value in data.items():
            # Map to snake_case if needed
            normalized_key = field_mapping.get(key, key)
            normalized_data[normalized_key] = value
        
        # Ensure required fields are present
        if 'first_name' not in normalized_data:
            # Try to get from firstName
            if 'firstName' in data:
                normalized_data['first_name'] = data['firstName']
        
        if 'last_name' not in normalized_data:
            # Try to get from lastName
            if 'lastName' in data:
                normalized_data['last_name'] = data['lastName']
        
        # Handle type/passenger_type
        if 'passenger_type' in normalized_data and 'type' not in normalized_data:
            normalized_data['type'] = normalized_data['passenger_type']
        elif 'type' in normalized_data and 'passenger_type' not in normalized_data:
            normalized_data['passenger_type'] = normalized_data['type']
        
        return super().to_internal_value(normalized_data)
    
    def validate(self, data):
        """Validate passenger data"""
        # Get first name from either source
        first_name = data.get('first_name') or ''
        if not first_name:
            # Check if we have firstName
            first_name = data.get('firstName') or ''
        
        # Get last name from either source
        last_name = data.get('last_name') or ''
        if not last_name:
            # Check if we have lastName
            last_name = data.get('lastName') or ''
        
        # Validate required fields
        if not first_name:
            raise serializers.ValidationError({
                "first_name": "First name is required"
            })
        
        if not last_name:
            raise serializers.ValidationError({
                "last_name": "Last name is required"
            })
        
        # Get passenger type
        passenger_type = data.get('type') or data.get('passenger_type', 'Adult')
        
        if passenger_type not in ['Adult', 'Child', 'Infant']:
            raise serializers.ValidationError({
                "type": f"Invalid passenger type: {passenger_type}. Must be Adult, Child, or Infant."
            })
        
        # Ensure consistent field names
        data['first_name'] = first_name
        data['last_name'] = last_name
        data['type'] = passenger_type
        data['passenger_type'] = passenger_type
        
        return data
    
    def get_fields(self):
        """Dynamically get fields to handle both formats"""
        fields = super().get_fields()
        
        # If we're serializing (output), we want snake_case
        if self.context.get('request') and self.context['request'].method in ['GET', 'PUT', 'PATCH']:
            # Remove camelCase fields for output
            fields.pop('firstName', None)
            fields.pop('lastName', None)
            fields.pop('middleName', None)
            fields.pop('dateOfBirth', None)
            fields.pop('passportNumber', None)
        
        return fields

class ContactInfoSerializer(serializers.Serializer):
    """Serializer for contact information"""
    title = serializers.CharField(max_length=10, required=False, allow_blank=True)
    firstName = serializers.CharField(max_length=100)
    lastName = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=50)

class SelectedFlightSerializer(serializers.Serializer):
    """Serializer for selected flight data"""
    id = serializers.IntegerField()
    schedule_id = serializers.IntegerField(required=False)
    flight_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=30, decimal_places=15)
    class_type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    origin = serializers.CharField(max_length=10, required=False, allow_blank=True)
    destination = serializers.CharField(max_length=10, required=False, allow_blank=True)
    departure_time = serializers.CharField(required=False, allow_blank=True)  # Changed from DateTimeField
    airline = serializers.CharField(max_length=100, required=False, allow_blank=True)
    airline_code = serializers.CharField(max_length=10, required=False, allow_blank=True)

class ReturnAddonDataSerializer(serializers.Serializer):
    """Serializer for return flight add-on data"""
    baggage = serializers.DictField(required=False, allow_null=True, default={})
    meals = serializers.DictField(required=False, allow_null=True, default={})
    wheelchair = serializers.DictField(required=False, allow_null=True, default={})
    
    def to_internal_value(self, data):
        """Handle null/None values"""
        if data is None:
            return {}
        return super().to_internal_value(data)

class AddonDataSerializer(serializers.Serializer):
    """Serializer for add-on data"""
    baggage = serializers.DictField(required=False)
    meals = serializers.DictField(required=False)
    wheelchair = serializers.DictField(required=False)
    seats = serializers.DictField(required=False)

class CreateBookingSerializer(serializers.Serializer):
    """Main serializer for creating a booking"""
    trip_type = serializers.CharField(max_length=20)
    passengers = CreatePassengerSerializer(many=True)
    contact_info = ContactInfoSerializer()
    selectedOutbound = SelectedFlightSerializer()
    selectedReturn = SelectedFlightSerializer(required=False, allow_null=True)
    addons = AddonDataSerializer(required=False)
    return_addons = ReturnAddonDataSerializer(required=False, allow_null=True)  
    passengerCount = serializers.DictField(required=False)
    total_amount = serializers.DecimalField(max_digits=30, decimal_places=15, required=False)  # Changed to False
    activity_id = serializers.IntegerField(required=False, allow_null=True)
    activity_code = serializers.CharField(max_length=8, required=False, allow_null=True, allow_blank=True)
    is_practice = serializers.BooleanField(required=False, default=False)
    
    def validate(self, data):
        """Custom validation for booking data"""
        # Ensure at least one passenger
        if not data.get('passengers'):
            raise serializers.ValidationError("At least one passenger is required")
        
        # Validate passenger types
        for passenger in data['passengers']:
            if passenger['type'] not in ['Adult', 'Child', 'Infant']:
                raise serializers.ValidationError(
                    f"Invalid passenger type: {passenger['type']}. Must be Adult, Child, or Infant."
                )
        
        # For round trips, both flights should be present
        if data.get('trip_type') == 'round_trip' and not data.get('selectedReturn'):
            raise serializers.ValidationError("Return flight is required for round trips")
        
        return data
# ============================================================
# PAYMENT PROCESSING SERIALIZERS
# ============================================================

class ProcessPaymentSerializer(serializers.Serializer):
    """Serializer for payment processing"""
    booking_id = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=50)
    transaction_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=30, decimal_places=15)
    
    def validate_payment_method(self, value):
        """Validate payment method"""
        valid_methods = ['GCash', 'Credit Card', 'Cash', 'Paypal']
        if value not in valid_methods:
            raise serializers.ValidationError(
                f"Invalid payment method. Must be one of: {', '.join(valid_methods)}"
            )
        return value

# ============================================================
# TAX SERIALIZERS
# ============================================================

class TaxTypeSerializer(serializers.ModelSerializer):
    """Serializer for tax types"""
    class Meta:
        model = TaxType
        fields = [
            'id', 'name', 'code', 'description', 'category',
            'per_passenger', 'adult_only', 'applies_domestic',
            'applies_international', 'applies_departure_country',
            'base_amount', 'is_active'
        ]

class BookingTaxSerializer(serializers.ModelSerializer):
    """Serializer for booking taxes"""
    tax_type_name = serializers.CharField(source='tax_type.name', read_only=True)
    tax_type_code = serializers.CharField(source='tax_type.code', read_only=True)
    
    class Meta:
        model = BookingTax
        fields = ['id', 'tax_type', 'tax_type_name', 'tax_type_code',
                 'amount', 'passenger_type']

# ============================================================
# MISCELLANEOUS SERIALIZERS
# ============================================================

class CheckInDetailSerializer(serializers.ModelSerializer):
    """Serializer for check-in details"""
    booking_detail_info = serializers.CharField(
        source='booking_detail.id', read_only=True
    )
    
    class Meta:
        model = CheckInDetail
        fields = [
            'id', 'booking_detail', 'booking_detail_info',
            'check_in_time', 'boarding_pass', 'baggage_count', 'baggage_weight'
        ]

class TrackLogSerializer(serializers.ModelSerializer):
    """Serializer for tracking logs"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TrackLog
        fields = ['id', 'user', 'username', 'action', 'timestamp']

# ============================================================
# SIMPLE SERIALIZERS FOR DROPDOWNS/LISTS
# ============================================================

class AirlineSimpleSerializer(serializers.ModelSerializer):
    """Simple airline serializer for dropdowns"""
    class Meta:
        model = Airline
        fields = ['id', 'code', 'name']

class RouteSimpleSerializer(serializers.ModelSerializer):
    """Simple route serializer for display"""
    origin_code = serializers.CharField(source='origin_airport.code', read_only=True)
    destination_code = serializers.CharField(source='destination_airport.code', read_only=True)
    is_domestic = serializers.BooleanField(read_only=True)
    is_international = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Route
        fields = ['id', 'origin_airport', 'destination_airport', 
                 'origin_code', 'destination_code', 'base_price',
                 'is_domestic', 'is_international']

# ============================================================
# RESPONSE SERIALIZERS
# ============================================================

class BookingResponseSerializer(serializers.Serializer):
    """Serializer for booking creation response"""
    success = serializers.BooleanField()
    booking_id = serializers.IntegerField()
    booking_reference = serializers.CharField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=30, decimal_places=15)
    message = serializers.CharField()

class PaymentResponseSerializer(serializers.Serializer):
    """Serializer for payment processing response"""
    success = serializers.BooleanField()
    payment_id = serializers.IntegerField(required=False)
    booking_status = serializers.CharField()
    booking_reference = serializers.CharField(required=False)
    message = serializers.CharField()

class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    success = serializers.BooleanField(default=False)
    error = serializers.CharField()