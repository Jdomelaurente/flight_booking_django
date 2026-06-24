import requests
import json

try:
    url = "http://127.0.0.1:8000/api/admin/login/"
    data = {"username": "admin", "password": "password"}
    headers = {"Content-Type": "application/json"}
    
    print(f"Sending POST to {url}...")
    response = requests.post(url, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print("Response Content:")
    print(response.text)
    
    with open("login_error_report.json", "w") as f:
        f.write(response.text)
except Exception as e:
    print(f"Error: {e}")
