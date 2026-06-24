import requests
import json
import traceback

try:
    response = requests.get('http://127.0.0.1:8000/api/schedules/?origin=MNL&destination=CEB&departure=2026-03-05')
    data = response.json()
    if 'results' in data:
        data = data['results']
    print(f"Total flights: {len(data)}")
    for f in data:
        print(f"Flight {f['flight_number']}: Price: {f.get('price')}, ML Base Price: {f.get('ml_base_price')}")
except Exception as e:
    traceback.print_exc()
