import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/api/schedules/')
    data = response.json()
    if 'results' in data:
        data = data['results']
    print(f"Total flights: {len(data)}")
    for f in data[:3]:
        print(f"Flight {f.get('flight_number')}: Price: {f.get('price')}, ML Base Price: {f.get('ml_base_price')}, Raw ML Price: {f.get('raw_ml_price')}")
except Exception as e:
    print(f"Error: {e}")
