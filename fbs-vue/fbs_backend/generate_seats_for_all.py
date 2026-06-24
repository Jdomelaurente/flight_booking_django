import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule, Aircraft, Seat, SeatClass
from django.db import transaction

def generate_all_seats():
    schedules = Schedule.objects.all()
    print(f"Generating seats for {schedules.count()} schedules...")
    
    for schedule in schedules:
        # Clear existing seats for this schedule first to ensure a clean run
        Seat.objects.filter(schedule=schedule).delete()
        
        aircraft = schedule.flight.aircraft
        layout = aircraft.get_layout_config()
        seat_classes_config = layout.get('seat_classes', [])
        
        if not seat_classes_config:
            print(f"  ⚠️ No layout for {aircraft.model} (Schedule {schedule.id}). Skipping.")
            continue
            
        created_count = 0
        with transaction.atomic():
            for sc_config in seat_classes_config:
                class_id = sc_config.get('class_id')
                rows = sc_config.get('rows', 0)
                columns = sc_config.get('columns', 0)
                start_row = sc_config.get('start_row', 1)
                
                try:
                    seat_class = SeatClass.objects.get(id=class_id)
                except SeatClass.DoesNotExist:
                    continue
                    
                for r in range(rows):
                    row_num = start_row + r
                    for c in range(columns):
                        col_num = c + 1
                        col_label = chr(64 + col_num)
                        
                        Seat.objects.create(
                            schedule=schedule,
                            seat_class=seat_class,
                            seat_number=f"{row_num}{col_label}",
                            row=row_num,
                            column=col_label,
                            is_window=(col_num == 1 or col_num == columns),
                            # Aisle logic
                            is_aisle=(columns == 6 and (col_num == 3 or col_num == 4)) or (columns == 4 and (col_num == 2 or col_num == 3))
                        )
                        created_count += 1
                        
        print(f"  ✅ {schedule.flight.flight_number}: Generated {created_count} seats.")

if __name__ == "__main__":
    generate_all_seats()
