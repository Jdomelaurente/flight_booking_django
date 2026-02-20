# flightapp/services/paymongo_service.py
import requests
import base64
import json
from django.conf import settings
from decouple import config

class PayMongoService:
    """Service for PayMongo payment processing"""
    
    def __init__(self):
        self.api_url = config('PAYMONGO_API_URL', default='https://api.paymongo.com/v1')
        self.secret_key = config('PAYMONGO_SECRET_KEY', default='')

        # Debug: Print configuration
        print(f"=== PAYMONGO CONFIGURATION ===")
        print(f"API URL: {self.api_url}")
        print(f"Secret Key Available: {'Yes' if self.secret_key else 'No'}")
        print(f"Secret Key Length: {len(self.secret_key) if self.secret_key else 0}")
        print(f"Secret Key Starts with 'sk_': {self.secret_key.startswith('sk_') if self.secret_key else False}")
        print(f"=================================")
        
        if not self.secret_key:
            raise ValueError("PAYMONGO_SECRET_KEY is not configured in environment variables")
        
        # PayMongo Basic Auth format: "secret_key:" (secret key followed by colon)
        auth_string = f"{self.secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {encoded_auth}"
        }
    def test_connection(self):
        """Test PayMongo connection"""
        try:
            print(f"\n=== TESTING PAYMONGO CONNECTION ===")
            print(f"Request URL: {self.api_url}/payment_intents")
            print(f"Headers: {self.headers}")
            
            # Make a simple request
            response = requests.get(f"{self.api_url}/payment_intents", 
                                  headers=self.headers, 
                                  timeout=10)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("? PayMongo connection successful!")
                return True
            else:
                print(f"? PayMongo connection failed: {response.status_code}")
                print(f"Response Body: {response.text}")
                return False
                
        except Exception as e:
            print(f"? Connection error: {str(e)}")
            return False
    # In flightapp/services/paymongo_service.py, update create_checkout_session:

    def create_checkout_session(self, amount, booking_id, description="Flight Booking Selection", **kwargs):
        """
        Creates a Checkout Session with webhook for real-time processing
        """
        try:
            amount_in_centavos = int(float(amount) * 100)
            url = f"{self.api_url}/checkout_sessions"
            
            print(f"\n? Creating checkout session for booking {booking_id}")
            print(f"   Amount: {amount} PHP ({amount_in_centavos} centavos)")
            
            # IMPORTANT: Your webhook URL must be accessible from the internet
            # Use ngrok for local development: https://ngrok.com/
            webhook_url = "http://localhost:8000/api/paymongo-webhook/"  # Update with your actual public URL
            
            payload = {
                "data": {
                    "attributes": {
                        "line_items": [{
                            "currency": "PHP",
                            "amount": amount_in_centavos,
                            "description": f"Flight Booking #{booking_id}",
                            "name": f"Booking #{booking_id}",
                            "quantity": 1
                        }],
                        "payment_method_types": ["card", "gcash", "grab_pay"],
                        "description": description,
                        "success_url": f"http://localhost:5173/payment-callback?booking_id={booking_id}&payment_success=true",
                        "cancel_url": f"http://localhost:5173/payment-callback?booking_id={booking_id}&payment_success=false",
                        "metadata": {
                            "booking_id": str(booking_id),
                            "booking_reference": f"BK{booking_id:08d}"
                        },
                        "webhook_url": webhook_url  # Add webhook for immediate processing
                    }
                }
            }
            
            print(f"   Success URL: {payload['data']['attributes']['success_url']}")
            print(f"   Webhook URL: {webhook_url}")
            print(f"   Metadata: {payload['data']['attributes']['metadata']}")
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            print(f"   PayMongo Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "checkout_url": data['data']['attributes']['checkout_url'],
                    "session_id": data['data']['id']
                }
            else:
                error_detail = response.text
                try:
                    error_data = response.json()
                    error_detail = error_data.get('errors', [{}])[0].get('detail', str(error_data))
                except:
                    pass
                
                print(f"? PayMongo Error: {error_detail}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_detail}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            print(f"? Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_payment_intent(self, amount, description="Flight Booking Payment", metadata=None):
        """
        Create a payment intent
        amount: in PHP (will be converted to centavos)
        """
        try:
            # Convert PHP to centavos
            amount_in_centavos = int(float(amount) * 100)
            
            url = f"{self.api_url}/payment_intents"

            attributes = {
                "amount": amount_in_centavos,
                "payment_method_allowed": [
                    "qrph", "card", "paymaya", "gcash", "grab_pay"
                ],
                "payment_method_options": {
                    "card": { "request_three_d_secure": "any" }
                },
                "currency": "PHP",
                "capture_type": "automatic",
                "description": description
            }

            if metadata:
                attributes["metadata"] = metadata
            
            payload = {
                "data": {
                    "attributes": attributes
                }
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data['data'],
                    "client_key": data['data']['attributes']['client_key'],
                    "intent_id": data['data']['id'],
                    "status": data['data']['attributes']['status'],
                    "amount": amount_in_centavos
                }
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                return {
                    "success": False,
                    "error": error_data,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def retrieve_payment_intent(self, intent_id):
        """
        Retrieve payment intent details
        """
        try:
            url = f"{self.api_url}/payment_intents/{intent_id}"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data['data'],
                    "status": data['data']['attributes']['status'],
                    "amount": data['data']['attributes']['amount']
                }
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                return {
                    "success": False,
                    "error": error_data,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_payment_source(self, amount, type="gcash", redirect_success=None, redirect_failed=None):
        """
        Create a payment source for GCash, GrabPay, etc.
        Returns checkout URL for redirect
        """
        try:
            amount_in_centavos = int(float(amount) * 100)
            
            url = f"{self.api_url}/sources"
            
            payload = {
                "data": {
                    "attributes": {
                        "amount": amount_in_centavos,
                        "currency": "PHP",
                        "type": type,
                        "redirect": {
                            "success": redirect_success or "http://localhost:5173/payment/success",
                            "failed": redirect_failed or "http://localhost:5173/payment/failed"
                        }
                    }
                }
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data['data'],
                    "source_id": data['data']['id'],
                    "checkout_url": data['data']['attributes']['redirect']['checkout_url'],
                    "status": data['data']['attributes']['status']
                }
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                return {
                    "success": False,
                    "error": error_data,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def attach_payment_method(self, intent_id, payment_method_id, return_url=None):
        """
        Attach a payment method to a payment intent
        """
        try:
            url = f"{self.api_url}/payment_intents/{intent_id}/attach"
            
            payload = {
                "data": {
                    "attributes": {
                        "payment_method": payment_method_id,
                        "return_url": return_url or "http://localhost:5173/payment/return"
                    }
                }
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data['data'],
                    "status": data['data']['attributes']['status']
                }
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                return {
                    "success": False,
                    "error": error_data,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Create global instance
paymongo_service = PayMongoService()