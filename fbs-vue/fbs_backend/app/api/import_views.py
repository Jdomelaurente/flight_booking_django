import csv
import io
import traceback
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny

from app.models import Students, Airline, Airport, Flight, Route, Schedule, UserProfile, TrackLog, Aircraft, Country, TaxType, SeatClass, BaggageOption, MealOption, MealCategory
from fbs_instructor.models import Instructor

class UniversalImportView(APIView):
    """
    Universal CSV Import View for multiple models.
    Supports Students, Instructors, Airlines, Airports, Flights, and Routes.
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    MODEL_MAPPING = {
        'students': Students,
        'instructors': Instructor,
        'airlines': Airline,
        'airports': Airport,
        'aircrafts': Aircraft,
        'seat_classes': SeatClass,
        'baggage': BaggageOption,
        'meals': MealOption,
        'flights': Flight,
        'routes': Route,
        'schedules': Schedule,
        'taxes': TaxType,
    }

    def post(self, request, *args, **kwargs):
        model_type = request.data.get('model_type')
        if not model_type or model_type not in self.MODEL_MAPPING:
            return Response({"error": f"Invalid or missing model_type. Supported: {list(self.MODEL_MAPPING.keys())}"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read first chunk to detect delimiter
            raw_data = file.read()
            decoded_file = raw_data.decode('utf-8')
            
            # Detect delimiter (comma or tab)
            dialect = 'excel' # default
            if decoded_file:
                try:
                    sniffer = csv.Sniffer()
                    # Check first 2048 chars or full string if smaller
                    dialect = sniffer.sniff(decoded_file[:2048], delimiters=',\t')
                except:
                    pass # Fallback to default excel comma dialect
            
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string, dialect=dialect)
            
            success_count = 0
            failed_rows = []
            
            model_class = self.MODEL_MAPPING[model_type]
            
            for row in reader:
                try:
                    with transaction.atomic():
                        # Clean keys: handle spaces, underscores, and case-insensitivity
                        clean_row = {
                            k.strip().lower().replace(' ', '_').replace('&', '').replace('__', '_').strip('_'): v.strip() 
                            for k, v in row.items() if k
                        }
                        
                        if model_type == 'students':
                            self._handle_student(clean_row)
                        elif model_type == 'instructors':
                            self._handle_instructor(clean_row)
                        elif model_type == 'airlines':
                            self._handle_airline(clean_row)
                        elif model_type == 'airports':
                            self._handle_airport(clean_row)
                        elif model_type == 'aircrafts':
                            self._handle_aircraft(clean_row)
                        elif model_type == 'seat_classes':
                            self._handle_seat_class(clean_row)
                        elif model_type == 'baggage':
                            self._handle_baggage(clean_row)
                        elif model_type == 'meals':
                            self._handle_meal(clean_row)
                        elif model_type == 'flights':
                            self._handle_flight(clean_row)
                        elif model_type == 'routes':
                            self._handle_route(clean_row)
                        elif model_type == 'schedules':
                            self._handle_schedule(clean_row)
                        elif model_type == 'taxes':
                            self._handle_tax(clean_row)
                        
                        success_count += 1
                except Exception as e:
                    # Save the full row + the error message for the CSV report
                    error_row = dict(row)
                    error_row['Error'] = str(e)
                    failed_rows.append(error_row)

            if success_count > 0 and request.user.is_authenticated:
                TrackLog.objects.create(
                    user=request.user,
                    action=f"Bulk imported {success_count} {model_type} records."
                )

            # We return up to 10 display errors as before, 
            # but also the full failed_rows for the downloadable CSV
            display_errors = [f"Row {i+1}: {r['Error']}" for i, r in enumerate(failed_rows[:10])]
            
            return Response({
                "message": f"Import completed for {model_type}.",
                "success_count": success_count,
                "error_count": len(failed_rows),
                "errors": display_errors,
                "failed_rows": failed_rows
            }, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            return Response({"error": f"Critical error during processing: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_student(self, data):
        student_num = data.get('student_number') or data.get('id')
        if not student_num:
            raise ValueError("Missing student_number or id")
            
        username = data.get('username') or data.get('user')
        user = None
        
        email = data.get('email_address') or data.get('email')
        
        if username:
            email_val = email or f"{username}@fbs.com"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email_val,
                    'first_name': data.get('first_name', ''),
                    'last_name': data.get('last_name', ''),
                }
            )
            if created:
                user.set_password('Student123!') # Professional default
                user.save()
                UserProfile.objects.get_or_create(user=user, defaults={'role': 'student'})

        Students.objects.update_or_create(
            student_number=student_num,
            defaults={
                'user': user,
                'first_name': data.get('first_name', ''),
                'mi': data.get('middle_initial') or data.get('mi', ''),
                'last_name': data.get('last_name', ''),
                'email': email or '',
                'phone_number': data.get('phone_number') or data.get('phone') or '',
                'course': data.get('course') or data.get('course_name') or 'BSHM',
                'year_level': data.get('year_level') or data.get('year') or '1',
                'gender': 'mrs' if 'female' in (data.get('gender') or '').lower() else 'mr',
            }
        )

    def _handle_instructor(self, data):
        instructor_id = data.get('instructor_id') or data.get('id')
        if not instructor_id:
            raise ValueError("Missing instructor_id or id")
            
        username = data.get('username') or data.get('user')
        if not username:
             raise ValueError("Missing username")

        user = None
        email = data.get('email_address') or data.get('email') or f"{username}@fbs-admin.com"
        password = data.get('password') or 'Instructor123!'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'is_staff': True
            }
        )
        
        # Always set password if provided or on creation
        if created or data.get('password'):
            user.set_password(password)
            user.save()
            
        if created:
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'instructor'})

        Instructor.objects.update_or_create(
            instructor_id=instructor_id,
            defaults={
                'user': user,
                'first_name': data.get('first_name', ''),
                'middle_initial': data.get('middle_initial') or data.get('mi', ''),
                'last_name': data.get('last_name', ''),
                'email': email,
                'phone': data.get('phone_number') or data.get('phone', ''),
            }
        )

    def _handle_airline(self, data):
        code = data.get('iata_code') or data.get('airline_code') or data.get('code')
        if not code:
            raise ValueError("Missing IATA Code")
        
        Airline.objects.update_or_create(
            code=code,
            defaults={
                'name': data.get('airline_name') or data.get('name', ''),
            }
        )

    def _handle_airport(self, data):
        code = data.get('iata_code') or data.get('airport_code') or data.get('code')
        if not code:
            raise ValueError("Missing IATA Code")
            
        Airport.objects.update_or_create(
            code=code,
            defaults={
                'name': data.get('airport_name') or data.get('name', ''),
                'city': data.get('city', ''),
                'country': Country.objects.get_or_create(name=data.get('country', 'Philippines'))[0],
                'airport_type': (data.get('type') or data.get('airport_type', 'domestic')).lower(),
                'location': data.get('detailed_location') or data.get('location', ''),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
            }
        )

    def _handle_flight(self, data):
        import json
        fn = data.get('flight_number') or data.get('id')
        if not fn:
            raise ValueError("Missing Flight Number")
        
        airline_val = data.get('airline') or data.get('airline_owner') or data.get('airline_code')
        if not airline_val:
            raise ValueError("Missing Airline (must provide Airline)")
            
        from django.db.models import Q
        airline = Airline.objects.filter(Q(code=airline_val) | Q(name=airline_val)).first()
        if not airline:
            raise ValueError(f"Airline '{airline_val}' not found")

        aircraft_val = data.get('aircraft') or data.get('aircraft_model') or data.get('aircraft_id')
        if not aircraft_val:
            raise ValueError("Missing Aircraft (must provide Aircraft)")
            
        aircraft = None
        if str(aircraft_val).isdigit():
            aircraft = Aircraft.objects.filter(id=aircraft_val).first()
        else:
            # Try to connect to aircraft owned by this airline first
            aircraft = Aircraft.objects.filter(model=aircraft_val, airline=airline).first()
            if not aircraft:
                aircraft = Aircraft.objects.filter(model=aircraft_val).first()
                
        if not aircraft:
            raise ValueError(f"Aircraft '{aircraft_val}' not found in database")
        
        route_val = data.get('route') or data.get('flight_route') or data.get('route_id')
        if not route_val:
            raise ValueError("Missing Route")
            
        route = None
        if str(route_val).isdigit():
            route = Route.objects.filter(id=route_val).first()
        elif '-' in str(route_val):
            parts = str(route_val).split('-')
            if len(parts) == 2:
                route = Route.objects.filter(
                    origin_airport__code=parts[0].strip(), 
                    destination_airport__code=parts[1].strip()
                ).first()
                
        if not route:
            raise ValueError(f"Route '{route_val}' not found in database")

        # Parse layovers_data if present as JSON string
        layovers = []
        layovers_data_str = data.get('layovers_data')
        if layovers_data_str:
            try:
                layovers_str_clean = str(layovers_data_str).replace("'", '"')
                layovers = json.loads(layovers_str_clean)
            except Exception as e:
                raise ValueError(f"Invalid layovers_data JSON format: {e}")
        else:
            for i in range(1, 4):  # Support up to 3 stops for now
                stop_airport = data.get(f'stop{i}_airport') or data.get(f'stop{i}_code')
                if stop_airport:
                    layovers.append({
                        'airport': stop_airport,
                        'city': data.get(f'stop{i}_city', ''),
                        'duration': data.get(f'stop{i}_duration', '1h')
                    })
                    
        total_stops = data.get('total_stops')
        if total_stops is not None and str(total_stops).strip():
            total_stops = int(total_stops)
        else:
            total_stops = len(layovers)

        Flight.objects.update_or_create(
            flight_number=fn,
            defaults={
                'airline': airline,
                'aircraft': aircraft,
                'route': route,
                'total_stops': total_stops,
                'layovers_data': layovers
            }
        )

    def _handle_route(self, data):
        origin_val = data.get('origin_airport') or data.get('origin_airport_code') or data.get('origin_code') or data.get('origin')
        dest_val = data.get('destination_airport') or data.get('destination_airport_code') or data.get('destination_code') or data.get('destination')
        
        if not origin_val or not dest_val:
            raise ValueError("Missing Origin Airport or Destination Airport")
            
        from django.db.models import Q
        origin = Airport.objects.filter(Q(code=origin_val) | Q(name=origin_val)).first()
        dest = Airport.objects.filter(Q(code=dest_val) | Q(name=dest_val)).first()
        
        if not origin: raise ValueError(f"Origin airport '{origin_val}' not found")
        if not dest: raise ValueError(f"Destination airport '{dest_val}' not found")
        
        Route.objects.update_or_create(
            origin_airport=origin,
            destination_airport=dest,
            defaults={
                'base_price': data.get('base_price', 5000.00),
            }
        )

    def _handle_schedule(self, data):
        fn = data.get('flight_number')
        dep_time = data.get('departure_date_time') or data.get('departure_time')
        arr_time = data.get('arrival_date_time') or data.get('arrival_time')
        
        if not fn or not dep_time or not arr_time:
            raise ValueError("Missing Flight Number, Departure Time, or Arrival Time")
            
        flight = Flight.objects.filter(flight_number=fn).first()
        if not flight:
            raise ValueError(f"Flight '{fn}' not found")
        
        Schedule.objects.update_or_create(
            flight=flight,
            departure_time=dep_time,
            defaults={
                'arrival_time': arr_time,
                'price': data.get('price') or 1000.00,
                'status': data.get('status') or 'Open',
            }
        )

    def _handle_tax(self, data):
        code = data.get('tax_code') or data.get('code')
        if not code:
            raise ValueError("Missing Tax Code")
            
        TaxType.objects.update_or_create(
            code=code,
            defaults={
                'name': data.get('tax_name') or data.get('name', ''),
                'category': (data.get('category') or 'government').lower(),
                'base_amount': data.get('base_amount') or 0.00,
                'per_passenger': str(data.get('per_passenger', 'true')).lower() == 'true',
                'applies_domestic': str(data.get('applies_domestic', 'true')).lower() == 'true',
                'applies_international': str(data.get('applies_international', 'true')).lower() == 'true',
                'is_active': str(data.get('is_active', 'true')).lower() == 'true',
            }
        )

    def _handle_aircraft(self, data):
        model = data.get('aircraft_model') or data.get('model')
        if not model:
            raise ValueError("Missing Aircraft Model")
            
        airline_val = data.get('airline_owner') or data.get('airline_code') or data.get('airline')
        airline = None
        if airline_val:
            from django.db.models import Q
            airline = Airline.objects.filter(Q(code=airline_val) | Q(name=airline_val)).first()
            
        if not airline:
            raise ValueError(f"Airline '{airline_val}' not found")
            
        Aircraft.objects.update_or_create(
            model=model,
            airline=airline,
            defaults={
                'capacity': int(data.get('capacity') or 0),
            }
        )

    def _handle_baggage(self, data):
        airline_val = data.get('airline')
        if not airline_val: raise ValueError("Missing Airline")
        
        from django.db.models import Q
        airline = Airline.objects.filter(Q(code=airline_val) | Q(name=airline_val)).first()
        if not airline: raise ValueError(f"Airline '{airline_val}' not found")
        
        BaggageOption.objects.update_or_create(
            airline=airline,
            weight_kg=data.get('weight_kg') or 0,
            defaults={
                'name': data.get('baggage_name') or data.get('name', ''),
                'price': data.get('price') or 0.00,
                'is_included': str(data.get('is_included', 'false')).lower() == 'true',
            }
        )

    def _handle_meal(self, data):
        airline_val = data.get('airline')
        if not airline_val: raise ValueError("Missing Airline")
        
        from django.db.models import Q
        airline = Airline.objects.filter(Q(code=airline_val) | Q(name=airline_val)).first()
        if not airline: raise ValueError(f"Airline '{airline_val}' not found")
        
        category_name = data.get('category') or 'Main Course'
        category, _ = MealCategory.objects.get_or_create(name=category_name)
        
        MealOption.objects.update_or_create(
            airline=airline,
            name=data.get('meal_name') or data.get('name', ''),
            defaults={
                'meal_type': (data.get('meal_type') or 'standard').lower(),
                'category': category,
                'price': data.get('price') or 0.00,
                'is_included': str(data.get('is_included', 'false')).lower() == 'true',
            }
        )

    def _handle_seat_class(self, data):
        name = data.get('class_name') or data.get('name')
        if not name:
            raise ValueError("Missing Class Name")
            
        airline_val = data.get('airline') or data.get('airline_owner') or data.get('airline_code')
        airline = None
        if airline_val:
            from django.db.models import Q
            airline = Airline.objects.filter(Q(code=airline_val) | Q(name=airline_val)).first()
            if not airline:
                raise ValueError(f"Airline '{airline_val}' not found")
            
        price_multiplier = data.get('price_multiplier')
        if not price_multiplier:
            price_multiplier = 1.0

        SeatClass.objects.update_or_create(
            name=name,
            airline=airline,
            defaults={
                'price_multiplier': price_multiplier,
                'description': data.get('description', ''),
                'color': data.get('color', '#3b82f6'),
                'is_active': str(data.get('is_active', 'true')).lower() == 'true',
            }
        )
