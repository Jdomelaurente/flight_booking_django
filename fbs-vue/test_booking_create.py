import json
from django.test import Client
from app.models import Booking

c = Client(SERVER_NAME='localhost')
# Using 16274 base_price for premium as in user's UI
data = {
    'trip_type': 'one_way',
    'passengers': [
        {'type': 'Adult', 'title': 'MR', 'first_name': 'Test', 'last_name': 'User', 'date_of_birth': '1990-01-01', 'key': 'pax_1', 'nationality': 'PH', 'passport_number': '123', 'passport_expiry': '2030-01-01'}
    ],
    'contact_info': {'email': 'test@test.com', 'phone': '1234', 'firstName': 'Test', 'lastName': 'User'},
    'passengerCount': {'adult': 1},
    'selectedOutbound': {
        'id': 109,
        'schedule_id': 109,
        'price': 16274.00,
        'class_type': 'Premium Economy',
        'fare_family': 'premium'
    },
    'addons': {
        'baggage': {}, 'meals': {}, 'wheelchair': {}, 'seats': {}
    }
}

response = c.post('/flightapp/create-booking/', json.dumps(data), content_type='application/json')
print("Status:", response.status_code)
print("Data:", response.content)
if response.status_code == 200:
    b = Booking.objects.get(id=response.json()['booking_id'])
    print("====== DB Booking ======")
    print("DB Total:", b.total_amount)
    for d in b.details.all():
        print("Detail Price:", d.price)
    print("Taxes:", [(t.tax_type.code, t.amount) for t in b.taxes.all()])
