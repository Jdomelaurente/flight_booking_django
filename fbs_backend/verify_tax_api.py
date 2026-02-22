import requests
import traceback

ENDPOINTS = [
    "http://127.0.0.1:8000/api/tax-types/",
    "http://127.0.0.1:8000/api/airline-taxes/",
    "http://127.0.0.1:8000/api/passenger-tax-rates/",
    "http://127.0.0.1:8000/api/airport-fees/",
    "http://127.0.0.1:8000/api/airlines/"
]

def verify_tax_endpoints():
    for url in ENDPOINTS:
        print(f"Testing URL: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status Code: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error Content: {response.text[:500]}")
            else:
                try:
                    data = response.json()
                    print(f"  Item Count: {len(data)}")
                    if isinstance(data, list) and len(data) > 0:
                        print(f"  First Item Keys: {list(data[0].keys())}")
                except Exception as json_err:
                    print(f"  JSON Parsing Error: {json_err}")
                    print(f"  Raw Content: {response.text[:200]}")
        except Exception as e:
            print(f"  Request Error: {e}")
            # traceback.print_exc()
        print("-" * 30)

if __name__ == "__main__":
    verify_tax_endpoints()
