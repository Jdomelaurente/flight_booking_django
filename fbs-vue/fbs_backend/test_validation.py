from flightapp.serializers import CreateBookingSerializer

data = {
  "trip_type": "one_way",
  "passengers": [
    {
      "first_name": "June Dominiic",
      "last_name": "Laurente",
      "middle_name": "",
      "title": "MR",
      "date_of_birth": "2003-11-17",
      "nationality": "Philippines",
      "passport_number": "",
      "ph_discount_type": "none",
      "ph_discount_id": "",
      "type": "Adult",
      "associated_adult": None,
      "key": "pax_1"
    }
  ],
  "contact_info": {
    "title": "MR",
    "firstName": "JUNE",
    "lastName": "Laurente",
    "email": "junedominic.laurente@csucc.edu.ph",
    "phone": "9925450721",
    "middleName": "D"
  },
  "passengerCount": {
    "adult": 1,
    "children": 0,
    "infant": 0
  },
  "insurance_plan_id": None,
  "activity_id": None,
  "activity_code": None,
  "is_practice": True,
  "booking_session_id": "sess_axwflabnn_1773129105804",
  "fare_families": {
    "depart": "flex",
    "return": "basic"
  },
  "selectedOutbound": {
    "id": 1549,
    "schedule_id": 1549,
    "flight_number": "5J 561",
    "price": 13371,
    "class_type": "Economy GO Flexi",
    "origin": "MNL",
    "destination": "CEB",
    "departure_time": "2026-03-31T09:15:00+08:00",
    "airline_code": "5J",
    "fare_family": "flex"
  },
  "selectedReturn": None,
  "addons": {
    "baggage": {},
    "meals": {},
    "wheelchair": {},
    "seats": {}
  },
  "return_addons": None
}

serializer = CreateBookingSerializer(data=data)
if not serializer.is_valid():
    print("VALIDATION ERRORS:")
    print(serializer.errors)
else:
    print("Valid!")
