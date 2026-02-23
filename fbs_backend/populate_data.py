# populate_data.py
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django
# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
try:
    django.setup()
except Exception:
    pass

from django.utils import timezone
from django.contrib.auth.models import User
from app.models import (
    Country, Airline, SeatClass, Aircraft, Airport, Route, Flight, 
    Schedule, Seat, SeatClassFeature, PassengerInfo,
    AddOnType, AddOn, MealCategory, MealOption, AssistanceService,
    BaggageOption, TaxType, AirlineTax, AirportFee, PassengerTypeTaxRate,
    InsuranceProvider, InsuranceCoverageType, InsuranceBenefit,
    TravelInsurancePlan, PlanCoverage,
    Booking, BookingContact, BookingDetail, Payment,
    CheckInDetail, TrackLog, PricingConfiguration, Students
)
from fbs_instructor.models import (
    Instructor, Section, SectionEnrollment, Activity, 
    ActivityPassenger, ActivityAddOn, ActivityStudentBinding
)

def create_countries():
    """Create sample countries"""
    countries_data = [
        {'name': 'Philippines', 'code': 'PH', 'currency': 'PHP'},
        {'name': 'United States', 'code': 'US', 'currency': 'USD'},
        {'name': 'Japan', 'code': 'JP', 'currency': 'JPY'},
        {'name': 'Singapore', 'code': 'SG', 'currency': 'SGD'},
        {'name': 'United Arab Emirates', 'code': 'AE', 'currency': 'AED'},
        {'name': 'South Korea', 'code': 'KR', 'currency': 'KRW'},
        {'name': 'Australia', 'code': 'AU', 'currency': 'AUD'},
        {'name': 'United Kingdom', 'code': 'GB', 'currency': 'GBP'},
    ]
    
    countries = {}
    for data in countries_data:
        country, created = Country.objects.get_or_create(**data)
        countries[data['code']] = country
        print(f"Created country: {country.name}")
    
    return countries

def create_airlines():
    """Create sample airlines"""
    airlines_data = [
        {'name': 'Philippine Airlines', 'code': 'PR'},
        {'name': 'Cebu Pacific Air', 'code': '5J'},
        {'name': 'AirAsia Philippines', 'code': 'Z2'},
        {'name': 'Qatar Airways', 'code': 'QR'},
        {'name': 'Singapore Airlines', 'code': 'SQ'},
        {'name': 'Emirates', 'code': 'EK'},
        {'name': 'Japan Airlines', 'code': 'JL'},
    ]
    
    airlines = {}
    for data in airlines_data:
        airline, created = Airline.objects.get_or_create(**data)
        airlines[data['code']] = airline
        print(f"Created airline: {airline.name}")
    
    return airlines

def create_seat_classes(airlines):
    """Create seat classes for airlines"""
    seat_classes_config = {
        'PR': [  # Philippine Airlines
            {'name': 'Business Class', 'price_multiplier': Decimal('2.5'), 'description': 'Premium service with lie-flat seats'},
            {'name': 'Premium Economy', 'price_multiplier': Decimal('1.8'), 'description': 'Extra legroom and enhanced service'},
            {'name': 'Economy Class', 'price_multiplier': Decimal('1.0'), 'description': 'Standard seating'},
        ],
        '5J': [  # Cebu Pacific
            {'name': 'Premium Seat', 'price_multiplier': Decimal('1.5'), 'description': 'Extra legroom and priority boarding'},
            {'name': 'Standard Seat', 'price_multiplier': Decimal('1.0'), 'description': 'Regular seating'},
            {'name': 'Basic Seat', 'price_multiplier': Decimal('0.8'), 'description': 'No frills, base fare only'},
        ],
        'Z2': [  # AirAsia
            {'name': 'Hot Seat', 'price_multiplier': Decimal('1.3'), 'description': 'Extra legroom and priority boarding'},
            {'name': 'Standard Seat', 'price_multiplier': Decimal('1.0'), 'description': 'Regular seating'},
            {'name': 'Value Seat', 'price_multiplier': Decimal('0.7'), 'description': 'Economical option'},
        ],
        'QR': [  # Qatar Airways
            {'name': 'First Class', 'price_multiplier': Decimal('4.0'), 'description': 'Luxury suite experience'},
            {'name': 'Business Class', 'price_multiplier': Decimal('2.5'), 'description': 'Qsuite with privacy'},
            {'name': 'Economy Class', 'price_multiplier': Decimal('1.0'), 'description': 'Comfortable seating'},
        ],
    }
    
    seat_classes = {}
    for airline_code, classes in seat_classes_config.items():
        if airline_code in airlines:
            airline = airlines[airline_code]
            for class_data in classes:
                seat_class, created = SeatClass.objects.get_or_create(
                    airline=airline,
                    name=class_data['name'],
                    defaults={
                        'price_multiplier': class_data['price_multiplier'],
                        'description': class_data['description']
                    }
                )
                key = f"{airline_code}_{class_data['name'].replace(' ', '_').lower()}"
                seat_classes[key] = seat_class
                print(f"Created seat class: {airline.name} - {seat_class.name}")
    
    return seat_classes

def create_aircrafts(airlines):
    """Create sample aircraft"""
    aircrafts_config = [
        {'model': 'Airbus A321neo', 'capacity': 214, 'airline_code': 'PR'},
        {'model': 'Airbus A330-300', 'capacity': 309, 'airline_code': 'PR'},
        {'model': 'Airbus A320', 'capacity': 180, 'airline_code': '5J'},
        {'model': 'Airbus A321', 'capacity': 230, 'airline_code': '5J'},
        {'model': 'Airbus A320', 'capacity': 180, 'airline_code': 'Z2'},
        {'model': 'Boeing 777-300ER', 'capacity': 361, 'airline_code': 'QR'},
        {'model': 'Airbus A350-900', 'capacity': 283, 'airline_code': 'QR'},
    ]
    
    aircrafts = {}
    for config in aircrafts_config:
        airline = airlines[config['airline_code']]
        aircraft, created = Aircraft.objects.get_or_create(
            model=config['model'],
            airline=airline,
            defaults={'capacity': config['capacity']}
        )
        key = f"{config['airline_code']}_{config['model'].replace(' ', '_')}"
        aircrafts[key] = aircraft
        print(f"Created aircraft: {airline.name} - {aircraft.model}")
    
    return aircrafts

def create_airports(countries):
    """Create sample airports"""
    airports_data = [
        {'name': 'Ninoy Aquino International Airport', 'code': 'MNL', 'city': 'Manila', 
         'country_code': 'PH', 'airport_type': 'international'},
        {'name': 'Mactan-Cebu International Airport', 'code': 'CEB', 'city': 'Cebu',
         'country_code': 'PH', 'airport_type': 'international'},
        {'name': 'Clark International Airport', 'code': 'CRK', 'city': 'Angeles',
         'country_code': 'PH', 'airport_type': 'international'},
        {'name': 'Davao International Airport', 'code': 'DVO', 'city': 'Davao',
         'country_code': 'PH', 'airport_type': 'domestic'},
        {'name': 'Kalibo International Airport', 'code': 'KLO', 'city': 'Kalibo',
         'country_code': 'PH', 'airport_type': 'international'},
        {'name': 'Puerto Princesa International Airport', 'code': 'PPS', 'city': 'Puerto Princesa',
         'country_code': 'PH', 'airport_type': 'domestic'},
        {'name': 'Caticlan (Boracay) Airport', 'code': 'MPH', 'city': 'Malay',
         'country_code': 'PH', 'airport_type': 'domestic'},
        {'name': 'Iloilo International Airport', 'code': 'ILO', 'city': 'Iloilo',
         'country_code': 'PH', 'airport_type': 'domestic'},
        {'name': 'New York John F. Kennedy Airport', 'code': 'JFK', 'city': 'New York',
         'country_code': 'US', 'airport_type': 'international'},
        {'name': 'Tokyo Narita International Airport', 'code': 'NRT', 'city': 'Tokyo',
         'country_code': 'JP', 'airport_type': 'international'},
        {'name': 'Singapore Changi Airport', 'code': 'SIN', 'city': 'Singapore',
         'country_code': 'SG', 'airport_type': 'international'},
        {'name': 'Dubai International Airport', 'code': 'DXB', 'city': 'Dubai',
         'country_code': 'AE', 'airport_type': 'international'},
        {'name': 'Incheon International Airport', 'code': 'ICN', 'city': 'Seoul',
         'country_code': 'KR', 'airport_type': 'international'},
        {'name': 'Sydney Kingsford Smith Airport', 'code': 'SYD', 'city': 'Sydney',
         'country_code': 'AU', 'airport_type': 'international'},
    ]
    
    airports = {}
    for data in airports_data:
        country = countries[data['country_code']]
        airport, created = Airport.objects.get_or_create(
            code=data['code'],
            defaults={
                'name': data['name'],
                'city': data['city'],
                'country': country,
                'airport_type': data['airport_type']
            }
        )
        airports[data['code']] = airport
        print(f"Created airport: {airport.code} - {airport.name}")
    
    return airports

def create_routes(airports):
    """Create sample flight routes"""
    routes_data = [
        {'origin': 'MNL', 'destination': 'CEB', 'base_price': Decimal('2000.00')},
        {'origin': 'MNL', 'destination': 'DVO', 'base_price': Decimal('3500.00')},
        {'origin': 'MNL', 'destination': 'CRK', 'base_price': Decimal('1500.00')},
        {'origin': 'CEB', 'destination': 'MNL', 'base_price': Decimal('2000.00')},
        {'origin': 'MNL', 'destination': 'PPS', 'base_price': Decimal('2800.00')},
        {'origin': 'MNL', 'destination': 'MPH', 'base_price': Decimal('3200.00')},
        {'origin': 'MPH', 'destination': 'CEB', 'base_price': Decimal('2500.00')},
        {'origin': 'ILO', 'destination': 'MNL', 'base_price': Decimal('1800.00')},
        {'origin': 'MNL', 'destination': 'SIN', 'base_price': Decimal('8000.00')},
        {'origin': 'MNL', 'destination': 'NRT', 'base_price': Decimal('15000.00')},
        {'origin': 'MNL', 'destination': 'DXB', 'base_price': Decimal('20000.00')},
        {'origin': 'MNL', 'destination': 'JFK', 'base_price': Decimal('40000.00')},
        {'origin': 'CEB', 'destination': 'ICN', 'base_price': Decimal('1200.00')},
        {'origin': 'CRK', 'destination': 'KLO', 'base_price': Decimal('2500.00')},
        {'origin': 'DVO', 'destination': 'JFK', 'base_price': Decimal('60000.00')},
    ]
    
    routes = []
    for data in routes_data:
        route, created = Route.objects.get_or_create(
            origin_airport=airports[data['origin']],
            destination_airport=airports[data['destination']],
            defaults={'base_price': data['base_price']}
        )
        routes.append(route)
        print(f"Created route: {route.origin_airport.code} ? {route.destination_airport.code}")
    
    return routes

def create_flights(airlines, aircrafts, routes):
    """Create sample flights"""
    flights_data = [
        {'flight_number': 'PR123', 'airline_code': 'PR', 'aircraft_key': 'PR_Airbus_A321neo', 'route_idx': 0},
        {'flight_number': '5J456', 'airline_code': '5J', 'aircraft_key': '5J_Airbus_A320', 'route_idx': 1},
        {'flight_number': 'Z2789', 'airline_code': 'Z2', 'aircraft_key': 'Z2_Airbus_A320', 'route_idx': 2},
        {'flight_number': 'QR789', 'airline_code': 'QR', 'aircraft_key': 'QR_Boeing_777-300ER', 'route_idx': 5},
        {'flight_number': 'PR890', 'airline_code': 'PR', 'aircraft_key': 'PR_Airbus_A330-300', 'route_idx': 6},
        {'flight_number': '5J901', 'airline_code': '5J', 'aircraft_key': '5J_Airbus_A321', 'route_idx': 3},
        {'flight_number': 'PR234', 'airline_code': 'PR', 'aircraft_key': 'PR_Airbus_A321neo', 'route_idx': 4},
        {'flight_number': 'PR999', 'airline_code': 'PR', 'aircraft_key': 'PR_Airbus_A321neo', 'route_idx': 14}, # DVO-JFK
        {'flight_number': 'Z2123', 'airline_code': 'Z2', 'aircraft_key': 'Z2_Airbus_A320', 'route_idx': 7},
        {'flight_number': 'QR456', 'airline_code': 'QR', 'aircraft_key': 'QR_Airbus_A350-900', 'route_idx': 8},
        {'flight_number': 'PR456', 'airline_code': 'PR', 'aircraft_key': 'PR_Airbus_A321neo', 'route_idx': 10}, # MNL-PPS
        {'flight_number': '5J789', 'airline_code': '5J', 'aircraft_key': '5J_Airbus_A320', 'route_idx': 11},   # MNL-MPH
        {'flight_number': 'Z2456', 'airline_code': 'Z2', 'aircraft_key': 'Z2_Airbus_A320', 'route_idx': 13},  # ILO-MNL
    ]
    
    flights = {}
    for data in flights_data:
        airline = airlines[data['airline_code']]
        aircraft = aircrafts[data['aircraft_key']]
        route = routes[data['route_idx']]
        
        flight, created = Flight.objects.update_or_create(
            flight_number=data['flight_number'],
            defaults={
                'airline': airline,
                'aircraft': aircraft,
                'route': route
            }
        )
        flights[data['flight_number']] = flight
        print(f"{'Created' if created else 'Updated'} flight: {flight.flight_number}")
    
    return flights

def create_schedules(flights):
    """Create flight schedules for the next 30 days"""
    schedules = []
    today = timezone.now()
    
    schedule_configs = [
        {'flight_number': 'PR999', 'fixed_date': '2026-03-11', 'hour': 21, 'minute': 0, 'duration_hours': 18},
        {'flight_number': 'PR123', 'days_from_now': 2, 'hour': 8, 'minute': 0, 'duration_hours': 1.5},
        {'flight_number': '5J456', 'days_from_now': 3, 'hour': 14, 'minute': 30, 'duration_hours': 2},
        {'flight_number': 'Z2789', 'days_from_now': 1, 'hour': 10, 'minute': 15, 'duration_hours': 0.75},
        {'flight_number': 'PR456', 'days_from_now': 2, 'hour': 9, 'minute': 30, 'duration_hours': 1.25},
        {'flight_number': '5J789', 'days_from_now': 3, 'hour': 7, 'minute': 45, 'duration_hours': 1},
        {'flight_number': 'Z2456', 'days_from_now': 1, 'hour': 16, 'minute': 20, 'duration_hours': 1.15},
        {'flight_number': 'QR789', 'days_from_now': 5, 'hour': 22, 'minute': 0, 'duration_hours': 8},
        {'flight_number': 'PR890', 'days_from_now': 4, 'hour': 1, 'minute': 30, 'duration_hours': 10},
        {'flight_number': '5J901', 'days_from_now': 6, 'hour': 16, 'minute': 45, 'duration_hours': 1.25},
        {'flight_number': 'PR234', 'days_from_now': 7, 'hour': 12, 'minute': 0, 'duration_hours': 3.5},
        {'flight_number': 'Z2123', 'days_from_now': 8, 'hour': 20, 'minute': 30, 'duration_hours': 16},
        {'flight_number': 'QR456', 'days_from_now': 9, 'hour': 9, 'minute': 15, 'duration_hours': 4},
    ]
    
    for config in schedule_configs:
        flight = flights[config['flight_number']]
        
        # Handle fixed date or multiple schedules
        if 'fixed_date' in config:
            from datetime import datetime
            dt = datetime.strptime(config['fixed_date'], '%Y-%m-%d')
            departure_time = timezone.make_aware(dt.replace(hour=config['hour'], minute=config['minute']))
            offsets = [0]
        else:
            offsets = range(0, 30, 7) # Every week for a month

        for day_offset in offsets:
            if 'fixed_date' not in config:
                departure_time = (today + timezone.timedelta(days=config['days_from_now'] + day_offset)).replace(
                    hour=config['hour'], minute=config['minute'], second=0, microsecond=0
                )
            
            arrival_time = departure_time + timezone.timedelta(hours=config['duration_hours'])
            
            schedule, created = Schedule.objects.get_or_create(
                flight=flight,
                departure_time=departure_time,
                defaults={
                    'arrival_time': arrival_time,
                    'price': flight.route.base_price,
                    'status': 'Open'
                }
            )
            
            schedules.append(schedule)
            if created:
                print(f"Created schedule: {schedule.flight.flight_number} on {departure_time.date()}")
            else:
                print(f"Existing schedule found: {schedule.flight.flight_number} on {departure_time.date()}")
    
    return schedules

def create_seats_for_all_schedules(schedules, seat_classes):
    """Create seats for all schedules based on aircraft configuration"""
    for schedule in schedules:
        aircraft = schedule.flight.aircraft
        airline = schedule.flight.airline
        
        # Get seat classes for this airline
        airline_seat_classes = seat_classes.get(airline.code, [])
        if not airline_seat_classes:
            # Get seat classes for this airline code
            airline_seat_classes = SeatClass.objects.filter(airline=airline)
            if not airline_seat_classes.exists():
                airline_seat_classes = SeatClass.objects.filter(airline__isnull=True)
        
        # Create seats based on aircraft capacity
        # For simplicity, we'll create a basic seat map
        seats_created = 0
        total_capacity = aircraft.capacity
        
        # Simple seat configuration: A-F columns, rows based on capacity
        columns = ['A', 'B', 'C', 'D', 'E', 'F']
        rows_needed = (total_capacity // len(columns)) + 1
        
        current_row = 1
        seat_class_index = 0
        seat_classes_list = list(airline_seat_classes)
        
        for row in range(1, rows_needed + 1):
            for col in columns:
                if seats_created >= total_capacity:
                    break
                
                # Assign seat class based on row (simulating different classes)
                if row <= 4 and len(seat_classes_list) >= 3:
                    seat_class = seat_classes_list[0]  # Business/Front
                elif row <= 8 and len(seat_classes_list) >= 2:
                    seat_class = seat_classes_list[1]  # Premium/Comfort
                else:
                    seat_class = seat_classes_list[-1]  # Economy
                
                # Determine seat features
                is_window = col in ['A', 'F']
                is_aisle = col in ['C', 'D']
                is_exit_row = row in [11, 26]  # Common exit rows
                is_bulkhead = row in [1, 5, 10]
                has_extra_legroom = row in range(5, 10)  # Comfort rows
                
                # Price adjustment for premium features
                price_adjustment = Decimal('0.00')
                if has_extra_legroom:
                    price_adjustment += Decimal('500.00')
                if is_exit_row:
                    price_adjustment += Decimal('800.00')
                if is_bulkhead:
                    price_adjustment += Decimal('300.00')
                
                seat, created = Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_class=seat_class,
                    row=row,
                    column=col,
                    defaults={
                        'seat_number': f"{row}{col}",
                        'is_available': random.choice([True, True, True, False]),  # 75% available
                        'has_extra_legroom': has_extra_legroom,
                        'is_exit_row': is_exit_row,
                        'is_bulkhead': is_bulkhead,
                        'is_window': is_window,
                        'is_aisle': is_aisle,
                        'price_adjustment': price_adjustment
                    }
                )
                
                if created:
                    seats_created += 1
        
        print(f"Created {seats_created} seats for {schedule.flight.flight_number} on {schedule.departure_time.date()}")

def create_seat_class_features(seat_classes):
    """Create features for seat classes"""
    features_config = {
        'Business Class': [
            {'feature': 'Lie-flat seats', 'icon': 'fas fa-bed'},
            {'feature': 'Priority check-in', 'icon': 'fas fa-star'},
            {'feature': 'Gourmet meals', 'icon': 'fas fa-utensils'},
            {'feature': 'Premium entertainment', 'icon': 'fas fa-tv'},
        ],
        'Premium Economy': [
            {'feature': 'Extra legroom', 'icon': 'fas fa-arrows-alt-v'},
            {'feature': 'Priority boarding', 'icon': 'fas fa-flag-checkered'},
            {'feature': 'Enhanced meal service', 'icon': 'fas fa-concierge-bell'},
        ],
        'Economy Class': [
            {'feature': 'Standard seating', 'icon': 'fas fa-chair'},
            {'feature': 'In-flight entertainment', 'icon': 'fas fa-headphones'},
            {'feature': 'Complimentary snacks', 'icon': 'fas fa-cookie-bite'},
        ],
        'Premium Seat': [
            {'feature': 'Extra legroom', 'icon': 'fas fa-arrows-alt-v'},
            {'feature': 'Priority boarding', 'icon': 'fas fa-flag-checkered'},
            {'feature': 'Front row seating', 'icon': 'fas fa-angle-double-up'},
        ],
    }
    
    for seat_class_key, seat_class in seat_classes.items():
        class_name = seat_class.name
        if class_name in features_config:
            for i, feature_data in enumerate(features_config[class_name]):
                SeatClassFeature.objects.get_or_create(
                    seat_class=seat_class,
                    feature=feature_data['feature'],
                    defaults={
                        'icon': feature_data['icon'],
                        'display_order': i,
                        'is_active': True
                    }
                )
    
    print("Created seat class features")

def create_passenger_info():
    """Create sample passenger information"""
    passengers = [
        {
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'title': 'MR',
            'date_of_birth': '1990-05-15',
            'passport_number': 'P1234567',
            'nationality': 'Filipino',
            'passenger_type': 'Adult'
        },
        {
            'first_name': 'Maria',
            'last_name': 'Santos',
            'title': 'MRS',
            'date_of_birth': '1992-08-22',
            'passport_number': 'P7654321',
            'nationality': 'Filipino',
            'passenger_type': 'Adult'
        },
        {
            'first_name': 'Pedro',
            'last_name': 'Reyes',
            'title': 'MR',
            'date_of_birth': '2015-03-10',
            'passport_number': None,
            'nationality': 'Filipino',
            'passenger_type': 'Child',
            'linked_adult': 1  # Reference to first passenger
        },
        {
            'first_name': 'Anna',
            'middle_name': 'Marie',
            'last_name': 'Gonzales',
            'title': 'MS',
            'date_of_birth': '1988-11-30',
            'passport_number': 'P9876543',
            'nationality': 'American',
            'passenger_type': 'Adult'
        },
        {
            'first_name': 'John',
            'last_name': 'Smith',
            'title': 'MR',
            'date_of_birth': '1985-07-04',
            'passport_number': 'US123456',
            'nationality': 'American',
            'passenger_type': 'Adult'
        },
    ]
    
    passenger_objects = []
    for i, passenger_data in enumerate(passengers):
        linked_adult = None
        if 'linked_adult' in passenger_data:
            linked_adult = passenger_objects[passenger_data['linked_adult']]
            del passenger_data['linked_adult']
        
        passenger, created = PassengerInfo.objects.get_or_create(
            first_name=passenger_data['first_name'],
            last_name=passenger_data['last_name'],
            defaults=passenger_data
        )
        
        if linked_adult:
            passenger.linked_adult = linked_adult
            passenger.save()
        
        passenger_objects.append(passenger)
        print(f"Created passenger: {passenger.get_full_name()}")
    
    return passenger_objects

def create_addon_types():
    """Create add-on types"""
    addon_types = [
        {'name': 'Insurance', 'description': 'Travel insurance plans'},
        {'name': 'Meal', 'description': 'In-flight meal options'},
        {'name': 'Baggage', 'description': 'Extra baggage allowance'},
        {'name': 'Assistance', 'description': 'Special assistance services'},
        {'name': 'Seat Selection', 'description': 'Premium seat selection'},
    ]
    
    addon_type_objects = {}
    for data in addon_types:
        addon_type, created = AddOnType.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        addon_type_objects[data['name']] = addon_type
        print(f"Created add-on type: {addon_type.name}")
    
    return addon_type_objects

def create_meal_categories():
    """Create meal categories"""
    categories = [
        {'name': 'Main Course', 'description': 'Hearty meals for the flight', 'display_order': 1},
        {'name': 'Snacks', 'description': 'Light snacks and refreshments', 'display_order': 2},
        {'name': 'Beverages', 'description': 'Drinks and beverages', 'display_order': 3},
        {'name': 'Special Meals', 'description': 'Dietary-specific meals', 'display_order': 4},
    ]
    
    meal_categories = {}
    for data in categories:
        category, created = MealCategory.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        meal_categories[data['name']] = category
        print(f"Created meal category: {category.name}")
    
    return meal_categories

def create_meal_options(airlines, meal_categories):
    """Create meal options for airlines"""
    meal_options = [
        {
            'airline_code': 'PR',
            'name': 'Adobo Chicken Rice',
            'description': 'Classic Filipino adobo with steamed rice',
            'meal_type': 'standard',
            'category': 'Main Course',
            'price': Decimal('500.00'),
            'calories': 650,
            'contains': 'Chicken, soy sauce, vinegar, garlic, rice',
            'allergens': 'Soy, Garlic',
        },
        {
            'airline_code': 'PR',
            'name': 'Vegetarian Pasta',
            'description': 'Pasta with tomato sauce and vegetables',
            'meal_type': 'vegetarian',
            'category': 'Main Course',
            'price': Decimal('450.00'),
            'calories': 500,
            'contains': 'Pasta, tomatoes, bell peppers, mushrooms',
            'allergens': 'Gluten',
        },
        {
            'airline_code': '5J',
            'name': 'Chicken Sandwich',
            'description': 'Grilled chicken sandwich with lettuce and mayo',
            'meal_type': 'standard',
            'category': 'Snacks',
            'price': Decimal('300.00'),
            'calories': 420,
            'contains': 'Chicken, bread, lettuce, mayonnaise',
            'allergens': 'Gluten, Egg',
        },
        {
            'airline_code': 'QR',
            'name': 'Arabic Mezze Platter',
            'description': 'Assorted Arabic appetizers with pita bread',
            'meal_type': 'standard',
            'category': 'Main Course',
            'price': Decimal('800.00'),
            'calories': 550,
            'contains': 'Hummus, baba ghanoush, tabbouleh, pita bread',
            'allergens': 'Sesame, Gluten',
        },
    ]
    
    meal_option_objects = []
    for meal_data in meal_options:
        airline = airlines[meal_data['airline_code']]
        category = meal_categories[meal_data['category']]
        
        meal_option, created = MealOption.objects.get_or_create(
            airline=airline,
            name=meal_data['name'],
            defaults={
                'description': meal_data['description'],
                'meal_type': meal_data['meal_type'],
                'category': category,
                'price': meal_data['price'],
                'calories': meal_data['calories'],
                'contains': meal_data['contains'],
                'allergens': meal_data['allergens'],
            }
        )
        
        meal_option_objects.append(meal_option)
        print(f"Created meal option: {meal_option.name}")
    
    return meal_option_objects

def create_assistance_services(airlines):
    """Create special assistance services"""
    services = [
        {
            'airline_code': 'PR',
            'name': 'Wheelchair Assistance - Standard',
            'service_type': 'wheelchair',
            'level': 'standard',
            'description': 'Wheelchair assistance from check-in to boarding gate',
            'price': Decimal('0.00'),
            'is_included': True,
        },
        {
            'airline_code': 'PR',
            'name': 'Unaccompanied Minor Service',
            'service_type': 'unaccompanied_minor',
            'level': 'premium',
            'description': 'Special care for children traveling alone',
            'price': Decimal('2000.00'),
            'is_included': False,
        },
        {
            'airline_code': '5J',
            'name': 'Medical Assistance',
            'service_type': 'medical',
            'level': 'standard',
            'description': 'Basic medical assistance during travel',
            'price': Decimal('0.00'),
            'is_included': True,
        },
    ]
    
    service_objects = []
    for service_data in services:
        airline = airlines[service_data['airline_code']]
        
        assistance_service, created = AssistanceService.objects.get_or_create(
            airline=airline,
            name=service_data['name'],
            defaults={
                'service_type': service_data['service_type'],
                'level': service_data['level'],
                'description': service_data['description'],
                'price': service_data['price'],
                'is_included': service_data['is_included'],
            }
        )
        
        service_objects.append(assistance_service)
        print(f"Created assistance service: {assistance_service.name}")
    
    return service_objects

def create_baggage_options(airlines):
    """Create baggage options"""
    baggage_options = [
        {'airline_code': 'PR', 'weight_kg': 5, 'price': Decimal('500.00'), 'name': '5kg Extra Baggage'},
        {'airline_code': 'PR', 'weight_kg': 10, 'price': Decimal('800.00'), 'name': '10kg Extra Baggage'},
        {'airline_code': '5J', 'weight_kg': 5, 'price': Decimal('400.00'), 'name': '5kg Extra Baggage'},
        {'airline_code': '5J', 'weight_kg': 15, 'price': Decimal('1000.00'), 'name': '15kg Extra Baggage'},
        {'airline_code': 'Z2', 'weight_kg': 10, 'price': Decimal('600.00'), 'name': '10kg Extra Baggage'},
        {'airline_code': 'QR', 'weight_kg': 20, 'price': Decimal('1500.00'), 'name': '20kg Extra Baggage'},
    ]
    
    baggage_objects = []
    for baggage_data in baggage_options:
        airline = airlines[baggage_data['airline_code']]
        
        baggage_option, created = BaggageOption.objects.get_or_create(
            airline=airline,
            weight_kg=baggage_data['weight_kg'],
            defaults={
                'name': baggage_data['name'],
                'price': baggage_data['price'],
            }
        )
        
        baggage_objects.append(baggage_option)
        print(f"Created baggage option: {baggage_option.name}")
    
    return baggage_objects

def create_insurance_providers():
    """Create insurance providers"""
    providers = [
        {
            'name': 'Malayan Insurance',
            'code': 'MAL',
            'description': 'Leading Philippine insurance provider',
            'contact_email': 'info@malayan.com',
            'contact_phone': '+632 8888 9999',
            'default_commission_rate': Decimal('15.00'),
        },
        {
            'name': 'AXA Philippines',
            'code': 'AXA',
            'description': 'Global insurance company with local presence',
            'contact_email': 'ph@axa.com',
            'contact_phone': '+632 7777 8888',
            'default_commission_rate': Decimal('18.00'),
        },
        {
            'name': 'Allianz PNB Life',
            'code': 'APL',
            'description': 'International insurance provider',
            'contact_email': 'service@allianzpnblife.com.ph',
            'contact_phone': '+632 6666 7777',
            'default_commission_rate': Decimal('16.50'),
        },
    ]
    
    provider_objects = {}
    for provider_data in providers:
        provider, created = InsuranceProvider.objects.get_or_create(
            name=provider_data['name'],
            defaults=provider_data
        )
        provider_objects[provider.code] = provider
        print(f"Created insurance provider: {provider.name}")
    
    return provider_objects

def create_insurance_coverage_types():
    """Create insurance coverage types"""
    coverage_types = [
        {
            'name': 'Medical Expenses',
            'code': 'MED',
            'description': 'Coverage for medical treatment during travel',
            'unit': 'PHP',
            'icon_class': 'fas fa-stethoscope',
            'display_order': 1,
        },
        {
            'name': 'Trip Cancellation',
            'code': 'CANCEL',
            'description': 'Reimbursement for cancelled trips',
            'unit': 'PHP',
            'icon_class': 'fas fa-ban',
            'display_order': 2,
        },
        {
            'name': 'Baggage Loss',
            'code': 'BAGGAGE',
            'description': 'Compensation for lost or delayed baggage',
            'unit': 'PHP',
            'icon_class': 'fas fa-suitcase',
            'display_order': 3,
        },
        {
            'name': 'Personal Accident',
            'code': 'ACCIDENT',
            'description': 'Coverage for accidental death or disability',
            'unit': 'PHP',
            'icon_class': 'fas fa-user-injured',
            'display_order': 4,
        },
        {
            'name': 'Flight Delay',
            'code': 'DELAY',
            'description': 'Compensation for flight delays',
            'unit': 'per hour',
            'icon_class': 'fas fa-clock',
            'display_order': 5,
        },
    ]
    
    coverage_objects = {}
    for coverage_data in coverage_types:
        coverage_type, created = InsuranceCoverageType.objects.get_or_create(
            code=coverage_data['code'],
            defaults=coverage_data
        )
        coverage_objects[coverage_data['code']] = coverage_type
        print(f"Created coverage type: {coverage_type.name}")
    
    return coverage_objects

def create_insurance_benefits():
    """Create insurance benefits"""
    benefits = [
        {'name': '24/7 Emergency Assistance', 'icon_class': 'fas fa-phone-alt', 'display_order': 1},
        {'name': 'Medical Evacuation', 'icon_class': 'fas fa-ambulance', 'display_order': 2},
        {'name': 'Trip Interruption', 'icon_class': 'fas fa-exclamation-triangle', 'display_order': 3},
        {'name': 'Lost Passport Assistance', 'icon_class': 'fas fa-passport', 'display_order': 4},
        {'name': 'Legal Assistance', 'icon_class': 'fas fa-balance-scale', 'display_order': 5},
        {'name': 'Family Coverage', 'icon_class': 'fas fa-users', 'display_order': 6},
    ]
    
    benefit_objects = {}
    for benefit_data in benefits:
        benefit, created = InsuranceBenefit.objects.get_or_create(
            name=benefit_data['name'],
            defaults=benefit_data
        )
        benefit_objects[benefit_data['name']] = benefit
        print(f"Created insurance benefit: {benefit.name}")
    
    return benefit_objects

def create_travel_insurance_plans(providers, airlines, coverage_types, benefits):
    """Create travel insurance plans"""
    plans = [
        {
            'provider_code': 'MAL',
            'name': 'Travel Lite',
            'description': 'Basic coverage for occasional travelers',
            'retail_price': Decimal('500.00'),
            'wholesale_price': Decimal('425.00'),
            'plan_type': 'basic',
            'best_for': 'Short domestic trips',
            'coverage_duration_days': 15,
            'seller_type': 'booking_platform',
            'is_default': True,
            'coverages': [
                {'coverage_code': 'MED', 'amount': Decimal('100000.00')},
                {'coverage_code': 'BAGGAGE', 'amount': Decimal('20000.00')},
            ],
            'benefits': ['24/7 Emergency Assistance'],
        },
        {
            'provider_code': 'AXA',
            'name': 'Travel Standard',
            'description': 'Comprehensive coverage for regular travelers',
            'retail_price': Decimal('1200.00'),
            'wholesale_price': Decimal('984.00'),
            'plan_type': 'standard',
            'best_for': 'International trips',
            'coverage_duration_days': 30,
            'seller_type': 'booking_platform',
            'is_default': False,
            'coverages': [
                {'coverage_code': 'MED', 'amount': Decimal('500000.00')},
                {'coverage_code': 'CANCEL', 'amount': Decimal('50000.00')},
                {'coverage_code': 'BAGGAGE', 'amount': Decimal('50000.00')},
                {'coverage_code': 'DELAY', 'amount': Decimal('1000.00')},
            ],
            'benefits': ['24/7 Emergency Assistance', 'Medical Evacuation', 'Lost Passport Assistance'],
        },
        {
            'provider_code': 'APL',
            'name': 'Travel Premium',
            'description': 'Premium coverage for frequent travelers',
            'retail_price': Decimal('2500.00'),
            'wholesale_price': Decimal('2050.00'),
            'plan_type': 'premium',
            'best_for': 'Business and luxury travel',
            'coverage_duration_days': 60,
            'seller_type': 'airline',
            'is_default': False,
            'coverages': [
                {'coverage_code': 'MED', 'amount': Decimal('1000000.00')},
                {'coverage_code': 'CANCEL', 'amount': Decimal('100000.00')},
                {'coverage_code': 'BAGGAGE', 'amount': Decimal('100000.00')},
                {'coverage_code': 'ACCIDENT', 'amount': Decimal('2000000.00')},
                {'coverage_code': 'DELAY', 'amount': Decimal('2000.00')},
            ],
            'benefits': ['24/7 Emergency Assistance', 'Medical Evacuation', 'Trip Interruption', 
                        'Lost Passport Assistance', 'Legal Assistance', 'Family Coverage'],
        },
    ]
    
    plan_objects = []
    for plan_data in plans:
        provider = providers[plan_data['provider_code']]
        
        plan, created = TravelInsurancePlan.objects.get_or_create(
            provider=provider,
            name=plan_data['name'],
            defaults={
                'description': plan_data['description'],
                'retail_price': plan_data['retail_price'],
                'wholesale_price': plan_data['wholesale_price'],
                'plan_type': plan_data['plan_type'],
                'best_for': plan_data['best_for'],
                'coverage_duration_days': plan_data['coverage_duration_days'],
                'seller_type': plan_data['seller_type'],
                'is_default': plan_data['is_default'],
            }
        )
        
        # Add airlines if specified
        if 'airlines' in plan_data:
            for airline_code in plan_data['airlines']:
                if airline_code in airlines:
                    plan.airlines.add(airlines[airline_code])
        
        # Add coverages
        for coverage_data in plan_data['coverages']:
            coverage_type = coverage_types[coverage_data['coverage_code']]
            PlanCoverage.objects.get_or_create(
                insurance_plan=plan,
                coverage_type=coverage_type,
                defaults={'amount': coverage_data['amount']}
            )
        
        # Add benefits
        for benefit_name in plan_data['benefits']:
            if benefit_name in benefits:
                plan.benefits.add(benefits[benefit_name])
        
        plan_objects.append(plan)
        print(f"Created insurance plan: {plan.name}")
    
    return plan_objects

def create_addons(airlines, insurance_plans, meal_options, baggage_options, assistance_services, addon_types):
    """Create add-ons for booking"""
    addons = [
        # Insurance add-ons
        {
            'airline_code': 'PR',
            'type': 'Insurance',
            'insurance_plan': 0,  # Index in insurance_plans list
            'name': 'Travel Insurance - Basic',
            'description': 'Basic travel insurance coverage',
            'price': Decimal('500.00'),
            'included': False,
        },
        {
            'airline_code': 'PR',
            'type': 'Insurance',
            'insurance_plan': 1,
            'name': 'Travel Insurance - Comprehensive',
            'description': 'Comprehensive travel insurance',
            'price': Decimal('1200.00'),
            'included': False,
        },
        
        # Meal add-ons
        {
            'airline_code': 'PR',
            'type': 'Meal',
            'meal_option': 0,  # Index in meal_options list
            'name': 'Adobo Chicken Meal',
            'description': 'Traditional Filipino adobo with rice',
            'price': Decimal('500.00'),
            'included': False,
        },
        {
            'airline_code': '5J',
            'type': 'Meal',
            'meal_option': 2,
            'name': 'Chicken Sandwich',
            'description': 'Grilled chicken sandwich',
            'price': Decimal('300.00'),
            'included': False,
        },
        
        # Baggage add-ons
        {
            'airline_code': 'PR',
            'type': 'Baggage',
            'baggage_option': 0,
            'name': 'Extra 5kg Baggage',
            'description': 'Additional 5kg checked baggage',
            'price': Decimal('500.00'),
            'included': False,
        },
        {
            'airline_code': '5J',
            'type': 'Baggage',
            'baggage_option': 2,
            'name': 'Extra 5kg Baggage',
            'description': 'Additional 5kg checked baggage',
            'price': Decimal('400.00'),
            'included': False,
        },
        
        # Assistance add-ons
        {
            'airline_code': 'PR',
            'type': 'Assistance',
            'assistance_service': 1,
            'name': 'Unaccompanied Minor Service',
            'description': 'Special care for children traveling alone',
            'price': Decimal('2000.00'),
            'included': False,
        },
    ]
    
    addon_objects = []
    for addon_data in addons:
        airline = airlines[addon_data['airline_code']]
        addon_type = addon_types[addon_data['type']]
        
        # Get linked objects
        insurance_plan = None
        meal_option = None
        baggage_option = None
        assistance_service = None
        
        if 'insurance_plan' in addon_data:
            insurance_plan = insurance_plans[addon_data['insurance_plan']]
        if 'meal_option' in addon_data:
            meal_option = meal_options[addon_data['meal_option']]
        if 'baggage_option' in addon_data:
            baggage_option = baggage_options[addon_data['baggage_option']]
        if 'assistance_service' in addon_data:
            assistance_service = assistance_services[addon_data['assistance_service']]
        
        addon, created = AddOn.objects.get_or_create(
            airline=airline,
            name=addon_data['name'],
            defaults={
                'type': addon_type,
                'insurance_plan': insurance_plan,
                'meal_option': meal_option,
                'baggage_option': baggage_option,
                'assistance_service': assistance_service,
                'description': addon_data['description'],
                'price': addon_data['price'],
                'included': addon_data['included'],
            }
        )
        
        addon_objects.append(addon)
        print(f"Created add-on: {addon.name}")
    
    return addon_objects

def create_taxes():
    """Create tax types and rates"""
    # Tax types
    tax_types = [
        {
            'name': 'Philippine Travel Tax',
            'code': 'TIEZA',
            'description': 'Travel Tax imposed by TIEZA for passengers departing from Philippines',
            'category': 'government',
            'per_passenger': True,
            'adult_only': True,
            'applies_domestic': False,
            'applies_international': True,
            'applies_departure_country': 'PH',
            'base_amount': Decimal('1620.00'),
        },
        {
            'name': 'Passenger Service Charge',
            'code': 'PSC',
            'description': 'Terminal fee charged by airports',
            'category': 'airport',
            'per_passenger': True,
            'adult_only': False,
            'applies_domestic': True,
            'applies_international': True,
            'base_amount': Decimal('200.00'),
        },
        {
            'name': 'Value Added Tax',
            'code': 'VAT',
            'description': '12% VAT on airfare',
            'category': 'government',
            'per_passenger': False,
            'adult_only': False,
            'applies_domestic': True,
            'applies_international': True,
            'base_amount': Decimal('0.00'),  # Percentage based
        },
        {
            'name': 'Fuel Surcharge',
            'code': 'YQ',
            'description': 'Fuel surcharge imposed by airlines',
            'category': 'airline',
            'per_passenger': True,
            'adult_only': False,
            'applies_domestic': True,
            'applies_international': True,
            'base_amount': Decimal('500.00'),
        },
    ]
    
    tax_type_objects = {}
    for tax_data in tax_types:
        tax_type, created = TaxType.objects.get_or_create(
            code=tax_data['code'],
            defaults=tax_data
        )
        tax_type_objects[tax_data['code']] = tax_type
        print(f"Created tax type: {tax_type.name}")
    
    return tax_type_objects

def create_bookings_and_payments(users, passengers, schedules, seats, addons):
    """Create sample bookings and payments"""
    # Create a test user if not exists
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        test_user.set_password('password123')
        test_user.save()
        print(f"Created test user: {test_user.username}")
    
    # Create bookings
    bookings = []
    for i in range(3):  # Create 3 sample bookings
        booking = Booking.objects.create(
            user=test_user,
            trip_type='one_way',
            status='Pending',
            base_fare_total=Decimal('0.00'),
            insurance_total=Decimal('0.00'),
            tax_total=Decimal('0.00'),
            total_amount=Decimal('0.00')
        )
        
        # Create booking contact
        BookingContact.objects.create(
            booking=booking,
            first_name='Juan',
            last_name='Dela Cruz',
            email='juan@example.com',
            phone='+639123456789',
            title='MR'
        )
        
        bookings.append(booking)
        print(f"Created booking: {booking.id}")
    
    # Create booking details for first booking
    booking = bookings[0]
    schedule = schedules[0]  # First schedule
    available_seats = seats.filter(schedule=schedule, is_available=True)[:2]  # Take 2 seats
    
    if len(available_seats) >= 2:
        # First passenger
        booking_detail1 = BookingDetail.objects.create(
            booking=booking,
            passenger=passengers[0],
            schedule=schedule,
            seat=available_seats[0],
            seat_class=available_seats[0].seat_class,
            price=available_seats[0].final_price,
            tax_amount=Decimal('500.00'),
            status='confirmed'
        )
        
        # Add insurance add-on
        insurance_addon = addons[0]  # First insurance add-on
        booking_detail1.addons.add(insurance_addon)
        
        # Second passenger
        booking_detail2 = BookingDetail.objects.create(
            booking=booking,
            passenger=passengers[1],
            schedule=schedule,
            seat=available_seats[1],
            seat_class=available_seats[1].seat_class,
            price=available_seats[1].final_price,
            tax_amount=Decimal('500.00'),
            status='confirmed'
        )
        
        # Update seats as occupied
        for s in available_seats:
            s.is_available = False
            s.save()
        
        # Update booking totals
        booking.base_fare_total = booking_detail1.price + booking_detail2.price
        booking.insurance_total = insurance_addon.price
        booking.tax_total = booking_detail1.tax_amount + booking_detail2.tax_amount
        booking.total_amount = booking.base_fare_total + booking.insurance_total + booking.tax_total
        booking.save()
        
        print(f"Created booking details for booking {booking.id}")
        
        # Create payment
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_amount,
            method='GCash',
            transaction_id=f'TXN{booking.id:06d}',
            status='Completed'
        )
        print(f"Created payment: {payment.transaction_id}")
    
    return bookings

def create_pricing_config():
    """Create singleton pricing configuration"""
    config = PricingConfiguration.load()
    print("Created/Loaded pricing configuration")
    return config

def create_instructor_and_students(users):
    """Create instructor and student profiles for users"""
    # Create an instructor
    instructor_user, created = User.objects.get_or_create(
        username='instructor1',
        defaults={
            'email': 'instructor@example.com',
            'first_name': 'Prof.',
            'last_name': 'Smith'
        }
    )
    if created:
        instructor_user.set_password('password123')
        instructor_user.save()
    
    instructor, created = Instructor.objects.get_or_create(
        user=instructor_user,
        defaults={
            'instructor_id': 'INST001',
            'first_name': instructor_user.first_name,
            'last_name': instructor_user.last_name,
            'email': instructor_user.email
        }
    )
    print(f"Created instructor: {instructor.get_full_name()}")

    # Create some students
    students = []
    for i in range(1, 6):
        student_user, created = User.objects.get_or_create(
            username=f'student{i}',
            defaults={
                'email': f'student{i}@example.com',
                'first_name': f'Student{i}',
                'last_name': 'Test'
            }
        )
        if created:
            student_user.set_password('password123')
            student_user.save()
        
        student, created = Students.objects.get_or_create(
            user=student_user,
            defaults={
                'student_number': f'STUD202400{i}',
                'first_name': student_user.first_name,
                'last_name': student_user.last_name,
                'email': student_user.email,
                'gender': 'male' if i % 2 == 0 else 'female'
            }
        )
        students.append(student)
        print(f"Created student: {student.first_name} {student.last_name}")
    
    return instructor, students

def create_sections_and_activities(instructor, students):
    """Create sections, enrollments, and activities"""
    section, created = Section.objects.get_or_create(
        section_code='CS101-A',
        instructor=instructor.user,
        defaults={
            'section_name': 'Introduction to Computer Science',
            'semester': '1st Semester',
            'academic_year': '2024-2025',
            'schedule': 'MWF 08:00 AM - 10:00 AM'
        }
    )
    print(f"Created section: {section.section_name}")

    # Enroll students
    for student in students:
        SectionEnrollment.objects.get_or_create(section=section, student=student)
    print(f"Enrolled {len(students)} students in section {section.section_code}")

    # Create an activity
    activity, created = Activity.objects.get_or_create(
        title='Final Booking Project',
        section=section,
        defaults={
            'description': 'Book a flight from Manila to Singapore.',
            'due_date': timezone.now() + timezone.timedelta(days=14),
            'total_points': Decimal('100.00'),
            'status': 'published',
            'activity_code': 'FLY2024',
            'is_code_active': True,
            'instructions': 'Please follow the steps in the manual.'
        }
    )
    print(f"Created activity: {activity.title}")

    # Create student bindings
    for student in students:
        ActivityStudentBinding.objects.get_or_create(activity=activity, student=student)
    print(f"Created student bindings for activity {activity.title}")

    return section, activity

def create_sample_data():
    """Main function to create all sample data"""
    print("Starting data population...")
    
    # Create basic data
    countries = create_countries()
    airlines = create_airlines()
    seat_classes = create_seat_classes(airlines)
    aircrafts = create_aircrafts(airlines)
    airports = create_airports(countries)
    routes = create_routes(airports)
    flights = create_flights(airlines, aircrafts, routes)
    schedules = create_schedules(flights)
    
    # Create pricing config
    create_pricing_config()
    
    # Create instructor and student data
    instructor, students = create_instructor_and_students([])
    create_sections_and_activities(instructor, students)
    
    # Create seats for all schedules
    for schedule in schedules:
        create_seats_for_all_schedules([schedule], seat_classes)
    
    create_seat_class_features(seat_classes)
    passengers = create_passenger_info()
    
    # Create add-ons and services
    addon_types = create_addon_types()
    meal_categories = create_meal_categories()
    meal_options = create_meal_options(airlines, meal_categories)
    assistance_services = create_assistance_services(airlines)
    baggage_options = create_baggage_options(airlines)
    
    # Create insurance data
    insurance_providers = create_insurance_providers()
    coverage_types = create_insurance_coverage_types()
    insurance_benefits = create_insurance_benefits()
    insurance_plans = create_travel_insurance_plans(
        insurance_providers, airlines, coverage_types, insurance_benefits
    )
    
    # Create add-ons
    addons = create_addons(airlines, insurance_plans, meal_options, 
                          baggage_options, assistance_services, addon_types)
    
    # Create taxes
    create_taxes()
    
    # Get all seats for bookings
    all_seats = Seat.objects.all()
    
    # Create bookings (with test user)
    create_bookings_and_payments([], passengers, schedules, all_seats, addons)
    
    print("\n? Data population completed successfully!")
    print("\nSummary of created data:")
    print(f"- Countries: {Country.objects.count()}")
    print(f"- Airlines: {Airline.objects.count()}")
    print(f"- Airports: {Airport.objects.count()}")
    print(f"- Flights: {Flight.objects.count()}")
    print(f"- Schedules: {Schedule.objects.count()}")
    print(f"- Seats: {Seat.objects.count()}")
    print(f"- Passengers: {PassengerInfo.objects.count()}")
    print(f"- Insurance Plans: {TravelInsurancePlan.objects.count()}")
    print(f"- Add-ons: {AddOn.objects.count()}")
    print(f"- Bookings: {Booking.objects.count()}")
    print(f"- Instructors: {Instructor.objects.count()}")
    print(f"- Students: {Students.objects.count()}")
    print(f"- Sections: {Section.objects.count()}")
    print(f"- Activities: {Activity.objects.count()}")

if __name__ == '__main__':
    create_sample_data()