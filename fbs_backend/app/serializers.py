<<<<<<< HEAD
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import AirlineTax, AirportFee, Booking, BookingDetail, BookingTax, CheckInDetail, PassengerInfo, Students, PassengerTypeTaxRate, Route, Airline, SeatClass, Aircraft, Airport, AddOnType, Flight, Schedule, Seat, TaxType, TrackLog, SeatRequirement, Payment
from fbs_instructor.models import Instructor

# ==========================================
# USER SERIALIZER
# ==========================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Added first_name and last_name to the fields
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# ==========================================
# STUDENT SERIALIZER
# ==========================================
class StudentsSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Students
        fields = [
            'id', 
            'student_number', 
            'first_name', 
            'last_name', 
            'mi', 
            'full_name',
            'email', 
            'phone_number', 
            'gender', 
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


=======
# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AirlineTax, AirportFee, Booking, BookingDetail, BookingTax, CheckInDetail, PassengerInfo, PassengerTypeTaxRate, Route, Airline, SeatClass, Aircraft, Airport, AddOnType, Flight, Schedule, Seat, TaxType, TrackLog, SeatRequirement


>>>>>>> 7926be7605482d3d0aa1a2a6cb1ccb63031afcdf
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
                  'aircraft', 'aircraft_display', 'route', 'route_display']

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

    class Meta:
        model = Schedule
        fields = [
            'id', 
            'flight', 
            'flight_number',
            'flight_detail',  # Add this for nested data
            'aircraft_name',
            'aircraft_capacity',
            'departure_time', 
            'arrival_time', 
            'price', 
            'status', 
            'status_display', 
            'duration_display'
        ]
        depth = 2  # This will auto-nest related objects 2 levels deep


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
        """Check if seat is linked to an active booking (pending or confirmed)"""
        return BookingDetail.objects.filter(
            seat=obj,
            status__in=['pending', 'confirmed', 'checkin', 'boarding', 'completed']
        ).exists()
    
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
        fields = ['id', 'name', 'code']

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
        fields = ['id', 'name', 'code', 'city', 'country', 'country_name', 'location', 'airport_type', 'airport_type_display']

class AddOnTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOnType
        fields = ['id', 'name', 'description']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
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
    arrival_time = serializers.ReadOnlyField(source='schedule.arrival_time')
    seat_number = serializers.ReadOnlyField(source='seat.seat_number')
    seat_class_name = serializers.ReadOnlyField(source='seat_class.name')
    airline_name = serializers.ReadOnlyField(source='schedule.flight.airline.name')
    
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
            'booking_date',
            'price',
            'tax_amount',
            'status',
        ]
    
    def get_passenger_name(self, obj):
        """Get passenger's full name."""
        return obj.passenger.get_full_name()

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
    
    passenger_name = serializers.ReadOnlyField(source='passenger_name')
    flight_number = serializers.ReadOnlyField(source='flight_number')
    route_display = serializers.ReadOnlyField(source='route')
    departure_time = serializers.ReadOnlyField(source='departure_time')
    seat_number = serializers.ReadOnlyField(source='seat_number')
    
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
        # Set status to checked-in by default
        validated_data['status'] = 'checked-in'
        
        # Generate boarding pass if not provided
        if 'boarding_pass' not in validated_data or not validated_data['boarding_pass']:
            instance = CheckInDetail(**validated_data)
            validated_data['boarding_pass'] = instance.generate_boarding_pass()
        
        return super().create(validated_data)


class CheckInListSerializer(serializers.ModelSerializer):
    """Simplified serializer for check-in list view"""
    passenger_name = serializers.ReadOnlyField(source='passenger_name')
    flight_number = serializers.ReadOnlyField(source='flight_number')
    route = serializers.ReadOnlyField(source='route')
    departure_time = serializers.DateTimeField()
    seat_number = serializers.ReadOnlyField(source='seat_number')
    
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
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Booking
        fields = ['id', 'user', 'user_name', 'trip_type', 'status', 'created_at', 'total_amount']

# Your existing BookingTaxSerializer
class BookingTaxSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    tax_type = TaxTypeSerializer(read_only=True)
    
    class Meta:
        model = BookingTax
        fields = ['id', 'booking', 'tax_type', 'amount', 'passenger_type', 'created_at']
<<<<<<< HEAD
=======

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Added first_name and last_name to the fields
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
>>>>>>> 7926be7605482d3d0aa1a2a6cb1ccb63031afcdf
