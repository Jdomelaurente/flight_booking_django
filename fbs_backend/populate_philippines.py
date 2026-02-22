
import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Airline, Route, Flight, Schedule, Aircraft, Country

def run():
    print("Starting Philippine data population...")
    
    # 1. Ensure Country
    ph, _ = Country.objects.get_or_create(name="Philippines", code="PH")
    
    # 2. Ensure Airlines
    airlines = []
    for name, code in [("Philippine Airlines", "PR"), ("Cebu Pacific", "5J"), ("AirAsia Philippines", "Z2")]:
        airline, _ = Airline.objects.get_or_create(name=name, code=code)
        airlines.append(airline)
        
    # 3. Ensure Aircraft
    aircraft_models = ["Airbus A320", "Airbus A321", "ATR 72-600", "Boeing 737"]
    aircrafts = []
    for model_name in aircraft_models:
        for airline in airlines:
            ac, _ = Aircraft.objects.get_or_create(
                model=model_name,
                airline=airline,
                defaults={'capacity': 180}
            )
            aircrafts.append(ac)
            
    # 4. Detailed PH Airports with Coordinates
    ph_airports = [
        ("MNL", "Ninoy Aquino International", 14.5086, 121.0194),
        ("CEB", "Mactan-Cebu International", 10.3075, 123.9794),
        ("DVO", "Francisco Bangoy International", 7.1253, 125.6453),
        ("PPS", "Puerto Princesa International", 9.7421, 118.7588),
        ("ILO", "Iloilo International", 10.8328, 122.4933),
        ("BCD", "Bacolod-Silay", 10.7767, 123.0133),
        ("CGY", "Laguindingan", 8.4153, 124.4697),
        ("ZAM", "Zamboanga International", 6.9214, 122.0594),
        ("BXU", "Bancasi (Butuan)", 8.9515, 125.4770),
        ("TAG", "Bohol-Panglao International", 9.6486, 123.8500),
        ("MPH", "Godofredo P. Ramos (Caticlan)", 11.9250, 121.9500),
        ("KLO", "Kalibo International", 11.5933, 122.3789),
        ("USU", "Francisco B. Reyes (Busuanga)", 12.1214, 120.2000),
        ("TAC", "Daniel Z. Romualdez (Tacloban)", 11.2269, 125.0281),
        ("LAO", "Laoag International", 18.1812, 120.5317),
        ("CBO", "Awang (Cotabato)", 7.1644, 124.2144),
        ("PAG", "Pagadian", 7.8283, 123.4683),
        ("DPL", "Dipolog", 8.6019, 123.3444),
        ("TUG", "Tuguegarao", 17.6414, 121.7308),
        ("WNP", "Naga", 11.7850, 123.9933)
    ]
    
    airports = []
    for code, name, lat, lng in ph_airports:
        airport, created = Airport.objects.get_or_create(
            code=code,
            defaults={'name': name, 'city': name.split()[0], 'country': ph, 'airport_type': 'domestic'}
        )
        airport.latitude = lat
        airport.longitude = lng
        airport.city = name.split()[0]
        airport.save()
        airports.append(airport)
        
    print(f"Ensured {len(airports)} airports with coordinates.")
    
    # 5. Routes & Flights & Schedules (Create 20)
    now = timezone.now()
    
    # Clear existing schedules
    Schedule.objects.all().delete()
    
    for i in range(20):
        origin, destination = random.sample(airports, 2)
        route, _ = Route.objects.get_or_create(origin_airport=origin, destination_airport=destination)
        
        airline = random.choice(airlines)
        airline_aircrafts = [ac for ac in aircrafts if ac.airline == airline]
        aircraft = random.choice(airline_aircrafts)
        
        flight_num = f"{airline.code}{2000 + i}"
        
        # Flight fields are: flight_number, airline, aircraft, route
        flight, _ = Flight.objects.get_or_create(
            flight_number=flight_num,
            defaults={
                'airline': airline,
                'aircraft': aircraft,
                'route': route,
            }
        )
        
        # Schedule
        if i < 12:
            status = 'On Flight'
            dep = now - timedelta(minutes=random.randint(20, 120))
            arr = now + timedelta(minutes=random.randint(15, 60))
        elif i < 16:
            status = 'Closed'
            dep = now + timedelta(minutes=random.randint(5, 20))
            arr = now + timedelta(hours=1, minutes=30)
        else:
            status = 'Scheduled'
            dep = now + timedelta(hours=random.randint(2, 5))
            arr = dep + timedelta(hours=1, minutes=20)
            
        Schedule.objects.create(
            flight=flight,
            departure_time=dep,
            arrival_time=arr,
            price=random.randint(1500, 8000),
            status=status
        )
        print(f"Created schedule {i+1}: {flight_num} {origin.code}->{destination.code} ({status})")

    print("Successfully populated 20 Philippine data points.")

if __name__ == "__main__":
    run()
