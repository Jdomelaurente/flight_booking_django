from app.models import Schedule, Seat, SeatClass, Aircraft
from django.db.models import Q
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
        print(f"Missing seat classes, skipping schedule {schedule.id}")
        return 0
    
    seats_created = 0
    
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

print("Starting Seat Seeding...")
schedules = Schedule.objects.all()
total_seats = 0
schedules_updated = 0

for schedule in schedules:
    # Check for "bad" seats (numeric codes or missing row/col)
    bad_seats = Seat.objects.filter(schedule=schedule).filter(
        Q(row__isnull=True) | Q(column__isnull=True) | Q(seat_number__regex=r'^\d+$')
    )
    
    existing_count = Seat.objects.filter(schedule=schedule).count()
    
    if existing_count > 0 and not bad_seats.exists():
        print(f"Skipping Schedule {schedule.id} (already has {existing_count} valid seats)")
        continue
    
    if bad_seats.exists():
        print(f"Repairing Schedule {schedule.id}: Found {bad_seats.count()} bad seats of {existing_count} total.")
        bad_seats.delete()
    
    aircraft = schedule.flight.aircraft if schedule.flight else None
    print(f"Creating seats for Schedule {schedule.id}")
    seats_created = create_seats_for_aircraft(schedule, aircraft)
    
    if seats_created > 0:
        total_seats += seats_created
        schedules_updated += 1
        print(f"Successfully created {seats_created} seats")

print(f"\nSeeding completed!")
print(f"Schedules updated/repaired: {schedules_updated}")
print(f"Total seats created: {total_seats}")
