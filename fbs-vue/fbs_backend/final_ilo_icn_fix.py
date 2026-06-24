import os
import django
import random
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule, Route, Airline, Aircraft, Airport, Seat

def standardize_ilo_icn():
    try:
        z2 = Airline.objects.get(code='Z2')
        ilo = Airport.objects.get(code='ILO')
        icn = Airport.objects.get(code='ICN')
        
        # Get/Create Route
        route = Route.objects.get(origin_airport=ilo, destination_airport=icn)
        route_rev = Route.objects.get(origin_airport=icn, destination_airport=ilo)

        # Get Z2 aircraft
        aircraft = Aircraft.objects.filter(airline=z2).first()
        if not aircraft:
            print("No Z2 aircraft found!")
            return

        for r in [route, route_rev]:
            # Update all flights on this route to be Z2
            flights = Flight.objects.filter(route=r)
            for f in flights:
                f.airline = z2
                f.aircraft = aircraft
                f.save()
            print(f"Updated all flights on {r} to AirAsia (Z2)")

            # Important: We need to RE-GENERATE seats for all schedules on these flights
            # because the seats were generated with the old aircraft layout.
            schedules = Schedule.objects.filter(flight__route=r)
            for sch in schedules:
                # Delete old seats
                Seat.objects.filter(schedule=sch).delete()
                # Aircraft save layout logic usually triggers seat creation if properly set up, 
                # but we'll manually trigger it here if it doesn't.
                # In this project, it seems seats are created during schedule save or aircraft logic.
                # Let's just create them using the aircraft's default layout.
                layout = aircraft.get_layout_config()
                for seat_class_config in layout.get('seat_classes', []):
                    sc_id = seat_class_config['class_id']
                    rows = seat_class_config['rows']
                    cols = seat_class_config['columns']
                    start_row = seat_class_config['start_row']
                    
                    for row in range(start_row, start_row + rows):
                        for col_idx in range(cols):
                            col_char = chr(65 + col_idx) # A, B, C...
                            Seat.objects.create(
                                schedule=sch,
                                seat_class_id=sc_id,
                                seat_number=f"{row}{col_char}",
                                row=row,
                                column=col_char,
                                is_available=True
                            )
            print(f"Re-generated seats for all schedules on {r}")

        print("Final standardization complete.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    standardize_ilo_icn()
