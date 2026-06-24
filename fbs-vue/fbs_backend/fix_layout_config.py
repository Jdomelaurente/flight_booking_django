import os
import django
import json
from collections import defaultdict

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Aircraft, Seat, Schedule, SeatClass

def fix_layout_configs():
    print("Starting layout configuration fix...")
    
    aircrafts = Aircraft.objects.all()
    
    for aircraft in aircrafts:
        print(f"\nChecking Aircraft: {aircraft.model} (ID: {aircraft.id}) - {aircraft.airline.name}")
        
        # Find a schedule with seats for this aircraft to use as reference
        # We need a schedule that actually has seats generated
        latest_schedule = None
        for schedule in aircraft.flights.first().schedules.order_by('-departure_time'):
            if schedule.seats.exists():
                latest_schedule = schedule
                break
        
        # If looking through flight relation failed, try direct Schedule query
        if not latest_schedule:
             # Try finding via Flight relation more broadly if the above didn't work (e.g. no first flight)
             # But typical path is aircraft -> flights -> schedules
             pass

        if not latest_schedule:
            # Try finding ANY schedule for this aircraft
            from app.models import Schedule
            latest_schedule = Schedule.objects.filter(flight__aircraft=aircraft).annotate(
                seat_count=django.db.models.Count('seats')
            ).filter(seat_count__gt=0).order_by('-departure_time').first()

        if not latest_schedule:
            print(f"  -> Skipped: No schedules with seats found for this aircraft.")
            continue
            
        print(f"  -> Using Schedule ID {latest_schedule.id} as reference.")
        
        # Get all seats
        seats = Seat.objects.filter(schedule=latest_schedule)
        
        # Group by Seat Class
        class_stats = defaultdict(lambda: {'min_row': 999, 'max_row': 0, 'cols': set(), 'count': 0})
        
        for seat in seats:
            if not seat.seat_class:
                continue
                
            stats = class_stats[seat.seat_class.id]
            
            # Update row stats
            if seat.row:
                stats['min_row'] = min(stats['min_row'], seat.row)
                stats['max_row'] = max(stats['max_row'], seat.row)
            
            # Update col stats
            if seat.column:
                stats['cols'].add(seat.column)
            
            stats['count'] += 1
            
        # Build new config
        new_seat_classes_config = []
        total_seats = 0
        
        # Sort by min_row to keep order
        sorted_class_ids = sorted(class_stats.keys(), key=lambda k: class_stats[k]['min_row'])
        
        for class_id in sorted_class_ids:
            stats = class_stats[class_id]
            seat_class = SeatClass.objects.get(id=class_id)
            
            # Calculate logic rows/cols
            # Heuristic: Columns is just the number of unique column letters found
            columns_count = len(stats['cols'])
            
            # If columns count is weird (e.g. 0 or odd number not typical), default to standard
            if columns_count == 0:
                columns_count = 6
            
            # Heuristic for rows: (max - min) + 1
            rows_count = (stats['max_row'] - stats['min_row']) + 1
            
            # Robustness: existing config might have color info we want to keep?
            # Or just use the model default
            color = seat_class.color or '#fe3787'
            
            config_entry = {
                'class_id': class_id,
                'name': seat_class.name,
                'rows': rows_count,
                'columns': columns_count,
                'start_row': stats['min_row'],
                'color': color,
                'price_multiplier': float(seat_class.price_multiplier)
            }
            
            new_seat_classes_config.append(config_entry)
            total_seats += stats['count']
            print(f"  -> Found Class: {seat_class.name} | Rows: {rows_count} | Cols: {columns_count}")

        if not new_seat_classes_config:
            print("  -> No seat classes found in seat data.")
            continue

        # Construct final JSON
        layout_config = {
            'seat_classes': new_seat_classes_config,
            'total_seats': total_seats,
            'updated_by': 'fix_script'
        }
        
        # Save
        if aircraft.layout_config != layout_config:
            print(f"  -> Updating layout config...")
            aircraft.layout_config = layout_config
            aircraft.save()
            print("  -> SAVED.")
        else:
            print("  -> Layout config already matches.")

if __name__ == '__main__':
    try:
        fix_layout_configs()
        print("\nDone.")
    except Exception as e:
        print(f"\nError: {e}")
