import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule, Seat, SeatClass, Aircraft
from decimal import Decimal

def create_seats_for_aircraft(schedule, aircraft):
    """Create seats based on aircraft configuration"""
    
    # Get seat classes
    seat_classes = {
        'First Class': SeatClass.objects.filter(name__iexact='First Class').first(),
        'Business': SeatClass.objects.filter(name__iexact='Business').first(),
        'Economy': SeatClass.objects.filter(name__iexact='Economy').first(),
    }
    
    # Skip if seat classes don't exist
    if not all(seat_classes.values()):
        print(f"?? Missing seat classes, skipping schedule {schedule.id}")
        return 0
    
    seats_created = 0
    
    # Airbus A321 configuration (220 seats)
    # First Class: Rows 1-3 (4 seats per row, columns A,C,D,F)
    # Business: Rows 4-8 (6 seats per row, columns A,B,C,D,E,F)  
    # Economy: Rows 9-40 (6 seats per row, columns A,B,C,D,E,F)
    
    model_name = aircraft.model if aircraft else 'Airbus A321'
    
    if 'A321' in model_name or 'Airbus' in model_name:
        # First Class (Rows 1-3)
        for row in range(1, 4):
            for col in ['A', 'C', 'D', 'F']:
                seat_number = f"{row}{col}"
                seat, created = Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=seat_number,
                    defaults={
                        'seat_class': seat_classes['First Class'],
                        'row': row,
                        'column': col,
                        'is_available': True,
                        'is_window': col in ['A', 'F'],
                        'is_aisle': col in ['C', 'D'],
                        'price_adjustment': Decimal('500.00') if row == 1 else Decimal('0.00'),
                    }
                )
                if created:
                    seats_created += 1
        
        # Business Class (Rows 4-8)
        for row in range(4, 9):
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                seat_number = f"{row}{col}"
                seat, created = Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=seat_number,
                    defaults={
                        'seat_class': seat_classes['Business'],
                        'row': row,
                        'column': col,
                        'is_available': True,
                        'is_window': col in ['A', 'F'],
                        'is_aisle': col in ['C', 'D'],
                        'price_adjustment': Decimal('200.00') if row == 4 else Decimal('0.00'),
                    }
                )
                if created:
                    seats_created += 1
        
        # Economy Class (Rows 9-40)
        for row in range(9, 41):
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                seat_number = f"{row}{col}"
                
                # Exit rows have extra legroom
                is_exit = row in [12, 24]
                
                seat, created = Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=seat_number,
                    defaults={
                        'seat_class': seat_classes['Economy'],
                        'row': row,
                        'column': col,
                        'is_available': True,
                        'is_window': col in ['A', 'F'],
                        'is_aisle': col in ['C', 'D'],
                        'is_exit_row': is_exit,
                        'has_extra_legroom': is_exit,
                        'price_adjustment': Decimal('150.00') if is_exit else Decimal('0.00'),
                    }
                )
                if created:
                    seats_created += 1
    
    elif 'Boeing 737' in model_name:
        # Boeing 737 configuration (similar to A321)
        # Simplified version
        for row in range(1, 35):
            seat_class = seat_classes['First Class'] if row <= 3 else (
                seat_classes['Business'] if row <= 8 else seat_classes['Economy']
            )
            
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                seat_number = f"{row}{col}"
                is_exit = row in [12, 24]
                
                seat, created = Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=seat_number,
                    defaults={
                        'seat_class': seat_class,
                        'row': row,
                        'column': col,
                        'is_available': True,
                        'is_window': col in ['A', 'F'],
                        'is_aisle': col in ['C', 'D'],
                        'is_exit_row': is_exit,
                        'has_extra_legroom': is_exit,
                        'price_adjustment': Decimal('100.00') if is_exit else Decimal('0.00'),
                    }
                )
                if created:
                    seats_created += 1
    
    else:
        # Default configuration for unknown aircraft
        for row in range(1, 31):
            seat_class = seat_classes['Economy']
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                seat_number = f"{row}{col}"
                seat, created = Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=seat_number,
                    defaults={
                        'seat_class': seat_class,
                        'row': row,
                        'column': col,
                        'is_available': True,
                        'is_window': col in ['A', 'F'],
                        'is_aisle': col in ['C', 'D'],
                    }
                )
                if created:
                    seats_created += 1
    
    return seats_created

def main():
    print("? Starting Seat Seeding...")
    
    # Get all schedules without seats or with few seats
    schedules = Schedule.objects.all()
    
    total_seats = 0
    schedules_updated = 0
    
    for schedule in schedules:
        existing_seats = Seat.objects.filter(schedule=schedule).count()
        
        if existing_seats > 0:
            print(f"?? Schedule {schedule.id} already has {existing_seats} seats, skipping...")
            continue
        
        aircraft = schedule.flight.aircraft if schedule.flight else None
        
        print(f"?? Creating seats for Schedule {schedule.id} ({schedule.flight.flight_number if schedule.flight else 'N/A'})")
        print(f"   Aircraft: {aircraft.model if aircraft else 'Unknown'}")
        
        seats_created = create_seats_for_aircraft(schedule, aircraft)
        
        if seats_created > 0:
            total_seats += seats_created
            schedules_updated += 1
            print(f"   ? Created {seats_created} seats")
        else:
            print(f"   ?? No seats created")
    
    print(f"\n? Seat seeding completed!")
    print(f"   Schedules updated: {schedules_updated}")
    print(f"   Total seats created: {total_seats}")

if __name__ == '__main__':
    main()
