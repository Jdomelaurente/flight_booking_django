import requests

try:
    response = requests.get('http://127.0.0.1:8000/api/students/export/')
    print("Full Headers:", response.text.splitlines()[0])
except Exception as e:
    print("Error:", e)
