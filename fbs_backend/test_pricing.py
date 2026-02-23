#!/usr/bin/env python
"""
Quick test script for Philippine pricing system
"""

import os
import django
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from datetime import date, timedelta
from django.utils import timezone

# Import from the correct module path
try:
    # Try absolute import
    from flightapp.pricing.ph_holiday_calendar import PhilippineCalendar
    from flightapp.pricing.ph_predictor import PHDynamicPricingEngine, export_ph_pricing_csv
except ImportError:
    # Try relative import if files are in same directory
    try:
        from .ph_holiday_calendar import PhilippineCalendar
        from .ph_predictor import PHDynamicPricingEngine, export_ph_pricing_csv
    except ImportError:
        print("Error: Could not import pricing modules")
        sys.exit(1)

from app.models import Schedule, SeatClass, Route, BookingDetail


def test_holiday_calendar():
    """Test Philippine holiday detection"""
    print("\n" + "="*50)
    print("TEST 1: Holiday Calendar")
    print("="*50)
    
    test_dates = [
        (2025, 1, 15, "Sinulog"),
        (2025, 4, 17, "Holy Week"),
        (2025, 12, 25, "Christmas"),
        (2025, 6, 15, "Regular day"),
    ]
    
    for year, month, day, name in test_dates:
        d = date(year, month, day)
        impact = PhilippineCalendar.get_holiday_impact(d)
        print(f"\n{name} ({d}):")
        print(f"  is_fiesta: {impact['is_fiesta']}")
        print(f"  is_long_weekend: {impact['is_long_weekend']}")
        print(f"  impact_score: {impact['impact_score']}")
        print(f"  holiday_name: {impact['holiday_name']}")


def test_pricing_engine():
    """Test pricing calculation"""
    print("\n" + "="*50)
    print("TEST 2: Pricing Engine")
    print("="*50)
    
    try:
        # Get test data
        schedule = Schedule.objects.first()
        if not schedule:
            print("? No schedules found in database")
            return
        
        seat_class = SeatClass.objects.filter(airline=schedule.flight.airline).first()
        if not seat_class:
            print("? No seat classes found")
            return
        
        print(f"\nTesting with: {schedule.flight.flight_number}")
        print(f"Route: {schedule.flight.route}")
        print(f"Departure: {schedule.departure_time}")
        print(f"Base price: ?{schedule.flight.route.base_price}")
        
        # Test dynamic pricing
        engine = PHDynamicPricingEngine()
        
        for ptype in ['Adult', 'Child', 'Infant']:
            result = engine.get_price(schedule, seat_class, ptype)
            print(f"\n  {ptype}:")
            print(f"    Base fare: ?{result['base_fare']}")
            print(f"    Total: ?{result['total_with_taxes']}")
            print(f"    Lead time: {result['factors']['lead_time']}")
            print(f"    Demand level: {result['factors']['demand_level']}")
        
        print("\n? Pricing engine working!")
        
    except Exception as e:
        print(f"\n? Error: {e}")
        import traceback
        traceback.print_exc()


def test_csv_export():
    """Test CSV export"""
    print("\n" + "="*50)
    print("TEST 3: CSV Export")
    print("="*50)
    
    try:
        count = BookingDetail.objects.filter(price__gt=0).count()
        print(f"Found {count} booking records")
        
        if count < 5:
            print("? Not enough data for export (need at least 5)")
            return
        
        filepath = export_ph_pricing_csv('test_export.csv')
        print(f"? CSV exported to: {filepath}")
        
        # Verify file exists
        if os.path.exists(filepath):
            import pandas as pd
            df = pd.read_csv(filepath)
            print(f"? File contains {len(df)} rows")
            print(f"Columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"\n? Error: {e}")
        import traceback
        traceback.print_exc()


def test_fiesta_pricing():
    """Test fiesta premium pricing"""
    print("\n" + "="*50)
    print("TEST 4: Fiesta Premium (Sinulog)")
    print("="*50)
    
    try:
        # Find Cebu route
        cebu_route = Route.objects.filter(
            destination_airport__code='CEB'
        ).first()
        
        if not cebu_route:
            print("? No Cebu routes found")
            return
        
        # Get schedule around Sinulog (Jan 15)
        sinulog_date = timezone.now().replace(month=1, day=15)
        
        schedule = Schedule.objects.filter(
            flight__route=cebu_route,
            departure_time__month=1,
            departure_time__day=15
        ).first()
        
        if not schedule:
            # Create mock test
            print("Testing with mock Sinulog date...")
            
            regular_date = date(2025, 1, 10)  # Regular day
            sinulog_date = date(2025, 1, 15)  # Sinulog
            
            regular_impact = PhilippineCalendar.get_holiday_impact(regular_date)
            sinulog_impact = PhilippineCalendar.get_holiday_impact(sinulog_date)
            
            print(f"\nRegular day (Jan 10): {regular_impact['impact_score']}")
            print(f"Sinulog (Jan 15): {sinulog_impact['impact_score']}")
            print(f"Fiesta factor: {PhilippineCalendar.get_route_fiesta_factor('MNL', 'CEB', sinulog_date)}")
        
    except Exception as e:
        print(f"\n? Error: {e}")
        import traceback
        traceback.print_exc()


def test_schedule_methods():
    """Test Schedule model methods"""
    print("\n" + "="*50)
    print("TEST 5: Schedule Model Methods")
    print("="*50)
    
    try:
        schedule = Schedule.objects.first()
        if not schedule:
            print("? No schedules found")
            return
        
        print(f"\nSchedule: {schedule}")
        print(f"Duration: {schedule.duration()}")
        print(f"Is open: {schedule.is_open}")
        
        # Test dynamic price
        price_result = schedule.get_dynamic_price()
        if price_result:
            print(f"Dynamic price available: {price_result}")
        else:
            print("No dynamic price available (may need seat classes)")
        
        # Test holiday impact
        holiday_impact = schedule.ph_holiday_impact
        print(f"Holiday impact: {holiday_impact.get('holiday_name', 'None')}")
        
        print("\n? Schedule methods working!")
        
    except Exception as e:
        print(f"\n? Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("Philippine Flight Pricing System Test")
    print("=" * 50)
    
    test_holiday_calendar()
    test_pricing_engine()
    test_schedule_methods()
    test_csv_export()
    test_fiesta_pricing()
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)