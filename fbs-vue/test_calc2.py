from django.test import RequestFactory
import json
from fbs_backend.app.models import *
from fbs_backend.flightapp.views import calculate_booking_price

req = RequestFactory().post('/flightapp/calculate-price/', 
    json.dumps({'passengers':[{'type':'Adult'}], 'trip_type': 'one_way', 'selectedOutbound':{'id':109, 'schedule_id':109, 'price':15567.50, 'fare_family':'premium'}}),
    content_type='application/json')
print(calculate_booking_price(req).data)
