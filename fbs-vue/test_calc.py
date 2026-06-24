from django.test import RequestFactory
import json
from fbs_backend.app.models import *
from fbs_backend.flightapp.views import calculate_booking_price

req = RequestFactory().post('/flightapp/calculate-price/', 
    json.dumps({'passengers':[{'type':'Adult'}], 'trip_type': 'one_way', 'segments': [{'selectedFlight':{'id':109, 'schedule_id':109, 'price':17157.0, 'fare_family':'premium'}}], 'sessionConfig': {'isPremium': False, 'testMode': True}}),
    content_type='application/json')
print(calculate_booking_price(req).data)
