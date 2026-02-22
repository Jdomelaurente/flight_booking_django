import requests
import json

def verify_nested_data():
    url = "http://127.0.0.1:8000/api/airline-taxes/"
    print(f"Testing URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"  Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', data)
            if results and len(results) > 0:
                first_item = results[0]
                print(f"  First Item: {json.dumps(first_item, indent=2)}")
                if isinstance(first_item.get('airline'), dict) and isinstance(first_item.get('tax_type'), dict):
                    print("  SUCCESS: Data is nested as expected.")
                else:
                    print("  FAILURE: Data is not nested correctly.")
            else:
                print("  No results found.")
    except Exception as e:
        print(f"  Request Error: {e}")

if __name__ == "__main__":
    verify_nested_data()
