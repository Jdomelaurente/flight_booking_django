import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import SeatClass, FareBundle, FareBundleFeature
import decimal

economy_classes = SeatClass.objects.filter(name__icontains='economy')
for seat_class in economy_classes:
    # 1. Economy Saver (Basic)
    basic, created = FareBundle.objects.update_or_create(
        seat_class=seat_class, type_code='basic',
        defaults={
            'name': 'Economy Saver',
            'markup_fee': decimal.Decimal('0.00'),
            'description': 'Travel light with our most affordable fare.',
            'icon_svg': 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
            'display_order': 1
        }
    )
    if created:
        for f in ['7kg Carry-on baggage only', 'Standard seat (assigned at check-in)', 'Non-refundable', 'High change fee']:
            FareBundleFeature.objects.create(fare_bundle=basic, feature_text=f, display_order=len(f))
    
    # 2. Economy Value (Standard)
    standard, created = FareBundle.objects.update_or_create(
        seat_class=seat_class, type_code='standard',
        defaults={
            'name': 'Economy Value',
            'markup_fee': decimal.Decimal('1200.00'),
            'description': 'The smart choice. Includes checked baggage.',
            'icon_svg': 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10',
            'display_order': 2
        }
    )
    if created:
        for f in ['7kg Carry-on baggage', '20kg Checked baggage included', 'Free Standard Seat selection', 'Rebookable with reduced fee', 'Priority check-in']:
            FareBundleFeature.objects.create(fare_bundle=standard, feature_text=f, display_order=len(f))

    # 3. Economy Flex (Flex)
    flex, created = FareBundle.objects.update_or_create(
        seat_class=seat_class, type_code='flex',
        defaults={
            'name': 'Economy Flex',
            'markup_fee': decimal.Decimal('2500.00'),
            'description': 'Maximum flexibility and comfort.',
            'icon_svg': 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z',
            'display_order': 3
        }
    )
    if created:
        for f in ['7kg Carry-on baggage', '30kg Checked baggage included', 'Free Premium Seat selection', 'Free cancellations (Refundable)', 'No change fee (Fare diff applies)']:
            FareBundleFeature.objects.create(fare_bundle=flex, feature_text=f, display_order=len(f))
    print(f'Updated bundles for {seat_class.name}')
