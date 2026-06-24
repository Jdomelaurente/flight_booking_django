import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Schedule, Seat
from django.db.models import Max

def debug_layout():
    try:
        # Get the problematic schedule (ID 6 based on previous context)
        s = Schedule.objects.get(id=6)
        print(f"Checking Schedule ID: {s.id}")
        
        # Get seats using the SAME logic as the viewset (filtered)
        seats = Seat.objects.filter(schedule=s)
        total_seats = seats.count()
        print(f"Total seats returned by API (simulated): {total_seats}")
        
        # Emulate frontend grouping
        seats_by_class = {}
        for seat in seats:
            cid = seat.seat_class_id
            if cid not in seats_by_class:
                seats_by_class[cid] = []
            seats_by_class[cid].append(seat)
            
        print("\n--- Frontend Layout Calculation ---")
        for cid, class_seats in seats_by_class.items():
            # Frontend: Math.max(...classSeats.map(s => s.row || 1))
            rows = 0
            cols = 0
            for seat in class_seats:
                if seat.row > rows: rows = seat.row
                # Frontend col calculation
                # const col = s.column;
                # return typeof col === 'string' ? col.charCodeAt(0) - 64 : parseInt(col) || 1;
                c_val = 0
                if isinstance(seat.column, str) and len(seat.column) == 1:
                    c_val = ord(seat.column) - 64
                else:
                    try:
                        c_val = int(seat.column)
                    except:
                        c_val = 1
                
                if c_val > cols: cols = c_val
            
            print(f"Class {cid}: Count={len(class_seats)}")
            print(f"  -> Max Row (Frontend 'rows'): {rows}")
            print(f"  -> Max Col (Frontend 'columns'): {cols}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    debug_layout()
