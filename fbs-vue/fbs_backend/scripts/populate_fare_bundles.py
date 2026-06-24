import os
import django
import sys

# Set up Django environment
sys.path.append('c:/Users/user/OneDrive/Desktop/Folders/Fbs/fbs-vue/fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import SeatClass, FareBundle, FareBundleFeature

def populate():
    # 1. Get Seat Classes
    economy = SeatClass.objects.filter(name__icontains='Economy').exclude(name__icontains='Premium').first()
    premium = SeatClass.objects.filter(name__icontains='Premium').first()
    business = SeatClass.objects.filter(name__icontains='Business').first()

    if not economy or not premium or not business:
        print("Required seat classes not found!")
        return

    # Clear existing bundles to avoid duplicates if re-running
    FareBundle.objects.all().delete()
    print("Cleared existing fare bundles.")

    # 2. Economy Bundles
    economy_bundles = [
        {
            'name': 'Economy Saver',
            'type_code': 'basic',
            'markup_fee': 0,
            'description': 'Travel light with our most affordable fare. Essential services for your journey.',
            'features': ['7kg Carry-on baggage only', 'Standard seat (assigned at check-in)', 'Non-refundable', 'High change fee']
        },
        {
            'name': 'Economy Value',
            'type_code': 'standard',
            'markup_fee': 1200,
            'description': 'The smart choice. Includes checked baggage and free standard seat selection.',
            'features': ['7kg Carry-on baggage', '20kg Checked baggage included', 'Free Standard Seat selection', 'Rebookable with reduced fee', 'Priority check-in']
        },
        {
            'name': 'Economy Flex',
            'type_code': 'premium',
            'markup_fee': 2500,
            'description': 'Maximum flexibility and comfort. Premium priority perks and fully refundable.',
            'features': ['7kg Carry-on baggage', '30kg Checked baggage included', 'Free Premium Seat selection', 'Free cancellations (Refundable)', 'No change fee']
        }
    ]

    for b_data in economy_bundles:
        bundle = FareBundle.objects.create(
            seat_class=economy,
            name=b_data['name'],
            type_code=b_data['type_code'],
            markup_fee=b_data['markup_fee'],
            description=b_data['description']
        )
        for f_text in b_data['features']:
            FareBundleFeature.objects.create(fare_bundle=bundle, feature_text=f_text)
    
    print(f"Created {len(economy_bundles)} bundles for {economy.name}")

    # 3. Premium Economy Bundles
    premium_bundles = [
        {
            'name': 'Premium Saver',
            'type_code': 'basic',
            'markup_fee': 0,
            'description': 'Enjoy enhanced comfort with standard premium perks.',
            'features': ['7kg Carry-on baggage', '20kg Checked baggage', 'Premium Economy seating', 'Non-refundable']
        },
        {
            'name': 'Premium Value',
            'type_code': 'standard',
            'markup_fee': 2000,
            'description': 'Enhanced flexibility and full allowance for your premium journey.',
            'features': ['7kg Carry-on baggage', '30kg Checked baggage', 'Free premium seat selection', 'Low rebooking fees', 'Priority boarding']
        },
        {
            'name': 'Premium Flex',
            'type_code': 'premium',
            'markup_fee': 4000,
            'description': 'The ultimate premium experience with full seasonal flexibility.',
            'features': ['7kg Carry-on baggage', '40kg Checked baggage', 'Fully refundable', 'No change fees', 'Lounge access (where available)']
        }
    ]

    for b_data in premium_bundles:
        bundle = FareBundle.objects.create(
            seat_class=premium,
            name=b_data['name'],
            type_code=b_data['type_code'],
            markup_fee=b_data['markup_fee'],
            description=b_data['description']
        )
        for f_text in b_data['features']:
            FareBundleFeature.objects.create(fare_bundle=bundle, feature_text=f_text)
    
    print(f"Created {len(premium_bundles)} bundles for {premium.name}")

    # 4. Business Bundles
    business_bundles = [
        {
            'name': 'Business Standard',
            'type_code': 'standard',
            'markup_fee': 0,
            'description': 'Full business class service with essential flexibility.',
            'features': ['2x7kg Carry-on', '40kg Checked baggage', 'Lounge access', 'Priority lanes', 'Full flat bed']
        },
        {
            'name': 'Business Plus',
            'type_code': 'premium',
            'markup_fee': 5000,
            'description': 'The pinnacle of luxury with maximum flexibility and dedicated concierge.',
            'features': ['2x7kg Carry-on', '50kg Checked baggage', 'Fully refundable', 'Unlimited changes', 'Premium lounge access', 'Limo transfer (where available)']
        }
    ]

    for b_data in business_bundles:
        bundle = FareBundle.objects.create(
            seat_class=business,
            name=b_data['name'],
            type_code=b_data['type_code'],
            markup_fee=b_data['markup_fee'],
            description=b_data['description']
        )
        for f_text in b_data['features']:
            FareBundleFeature.objects.create(fare_bundle=bundle, feature_text=f_text)
    
    print(f"Created {len(business_bundles)} bundles for {business.name}")

if __name__ == "__main__":
    populate()
