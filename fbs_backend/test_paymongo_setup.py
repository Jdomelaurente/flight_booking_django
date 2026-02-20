# test_paymongo_setup.py
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from flightapp.services.paymongo_service import PayMongoService

def test_paymongo():
    print("=== Testing PayMongo Service ===")
    
    try:
        service = PayMongoService()
        print("? PayMongoService initialized successfully")
        
        # Test 1: Create payment intent
        print("\n? Test 1: Creating payment intent...")
        result = service.create_payment_intent(
            amount=100.00,
            description="Test Flight Booking",
            metadata={"test": "true", "booking_id": "999"}
        )
        
        if result['success']:
            print(f"? Payment Intent Created:")
            print(f"   Intent ID: {result['intent_id']}")
            print(f"   Client Key: {result['client_key']}")
            print(f"   Status: {result['status']}")
            print(f"   Amount: {result['amount']} centavos")
            
            # Test 2: Retrieve payment intent
            print("\n? Test 2: Retrieving payment intent...")
            retrieve_result = service.retrieve_payment_intent(result['intent_id'])
            if retrieve_result['success']:
                print(f"? Retrieved Payment Intent")
                print(f"   Status: {retrieve_result['status']}")
            else:
                print(f"? Failed to retrieve: {retrieve_result.get('error')}")
                
        else:
            print(f"? Failed to create payment intent:")
            print(f"   Error: {result.get('error')}")
            
        # Test 3: Create GCash source
        print("\n? Test 3: Creating GCash payment source...")
        gcash_result = service.create_payment_source(
            amount=50.00,
            type="gcash"
        )
        
        if gcash_result['success']:
            print(f"? GCash Payment Source Created:")
            print(f"   Source ID: {gcash_result['source_id']}")
            print(f"   Checkout URL: {gcash_result['checkout_url']}")
        else:
            print(f"? Failed to create GCash source:")
            print(f"   Error: {gcash_result.get('error')}")
            
    except Exception as e:
        print(f"? Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_paymongo()