# check_payment_intent.py
import requests
import base64
import json
from decouple import config

secret_key = config('PAYMONGO_SECRET_KEY', default='')
auth_string = f"{secret_key}:"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Basic {encoded_auth}"
}

# Your payment intent ID from the URL
payment_intent_id = "pi_rMa8wGupzjKApRGBMsMraN6M"

print(f"Checking payment intent: {payment_intent_id}")

# Get payment intent details
intent_url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}"
response = requests.get(intent_url, headers=headers)

if response.status_code == 200:
    data = response.json()
    intent = data['data']
    attributes = intent['attributes']
    
    print(f"\n? Payment Intent Found!")
    print(f"ID: {intent['id']}")
    print(f"Status: {attributes['status']}")
    print(f"Amount: {attributes['amount'] / 100} PHP")
    print(f"Description: {attributes.get('description', 'N/A')}")
    print(f"Currency: {attributes['currency']}")
    
    # Check metadata
    metadata = attributes.get('metadata', {})
    print(f"Metadata: {json.dumps(metadata, indent=2)}")
    
    # Check payments
    payments = attributes.get('payments', [])
    print(f"\nPayments found: {len(payments)}")
    
    for payment in payments:
        payment_attrs = payment['attributes']
        print(f"\n  Payment ID: {payment['id']}")
        print(f"  Status: {payment_attrs['status']}")
        print(f"  Amount: {payment_attrs['amount'] / 100} PHP")
        print(f"  Source Type: {payment_attrs.get('source', {}).get('type', 'N/A')}")
        
        if payment_attrs['status'] == 'paid':
            print("  ? THIS PAYMENT IS PAID!")
            
            # Check if we can process it
            payment_metadata = payment_attrs.get('metadata', {})
            booking_id = payment_metadata.get('booking_id')
            
            if booking_id:
                print(f"  ? Associated with booking: {booking_id}")
                
                # You can now call your Django endpoint to process this
                print(f"\n? You should now call:")
                print(f"   POST http://localhost:8000/api/verify-and-process-payment/")
                print(f"   Body: {{")
                print(f"     'booking_id': '{booking_id}',")
                print(f"     'payment_intent_id': '{payment_intent_id}'")
                print(f"   }}")
        else:
            print(f"  ?? Payment status is: {payment_attrs['status']}")
    
else:
    print(f"? Failed to get payment intent: {response.status_code}")
    print(f"Response: {response.text}")