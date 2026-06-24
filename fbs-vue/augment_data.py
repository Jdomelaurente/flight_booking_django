import csv
import random
from datetime import datetime, timedelta
import math

# Philippine Airports info
AIRPORTS = {
    'MNL': 'Manila (MNL)',
    'CEB': 'Cebu (CEB)',
    'DVO': 'Davao (DVO)',
    'PPS': 'Puerto Princesa (PPS)',
    'ILO': 'Iloilo (ILO)',
    'KLO': 'Kalibo (KLO)',
    'BCD': 'Bacolod (BCD)',
    'CGY': 'Cagayan de Oro (CGY)',
    'TAC': 'Tacloban (TAC)',
    'GES': 'General Santos (GES)',
    'MPH': 'Caticlan (MPH)',
    'CRK': 'Clark (CRK)',
    'ZAM': 'Zamboanga (ZAM)',
    'LGP': 'Legazpi (LGP)'
}

AIRLINES = ['Philippine Airlines', 'Cebu Pacific', 'AirAsia Philippines']

# National Holiday Peaks (from dynamic_pricing.py)
PH_HOLIDAY_PEAKS = [
    (1, 1, 1, 5, 1.40, "New Year"),
    (2, 14, 2, 16, 1.15, "Valentine's Day"),
    (2, 23, 2, 26, 1.20, "EDSA Anniversary"),
    (3, 28, 4, 1, 1.50, "Holy Week"), # 2024 Holy week was Mar 24-31
    (4, 8, 4, 10, 1.25, "Araw ng Kagitingan"),
    (5, 1, 5, 1, 1.30, "Labor Day"),
    (6, 12, 6, 12, 1.25, "Independence Day"),
    (8, 21, 8, 21, 1.20, "Ninoy Aquino Day"),
    (8, 26, 8, 30, 1.20, "National Heroes Day"),
    (11, 1, 11, 2, 1.35, "Undas"),
    (11, 30, 11, 30, 1.20, "Bonifacio Day"),
    (12, 8, 12, 8, 1.15, "Immaculate Conception"),
    (12, 20, 12, 31, 1.60, "Christmas/Rizal Day")
]

# Regional Festival Surges
PH_FESTIVAL_SURGES = [
    (1, 15, 1, 20, ['CEB'], 1.35, "Sinulog Festival"),
    (1, 16, 1, 20, ['KLO', 'MPH'], 1.30, "Ati-Atihan Festival"),
    (1, 23, 1, 27, ['ILO'], 1.30, "Dinagyang Festival"),
    (8, 17, 8, 23, ['DVO'], 1.25, "Kadayawan Festival"),
    (10, 19, 10, 25, ['BCD'], 1.25, "MassKara Festival"),
]

def is_date_in_range(d, sm, sd, em, ed):
    year = d.year
    start = datetime(year, sm, sd)
    end = datetime(year, em, ed)
    if start <= end:
        return start <= d <= end
    else: # Year wrap
        end = datetime(year + 1, em, ed)
        return start <= d <= end

def calculate_price(airline, journey_date, dep_time, source_code, dest_code, stops):
    # Base price by airline reputation
    base = 2500
    if airline == 'Philippine Airlines':
        base = 3800
    elif airline == 'Cebu Pacific':
        base = 2800
    else:
        base = 2400
        
    # Factor for distance/route (simplified)
    popular_to_manila = ['CEB', 'DVO', 'PPS']
    if source_code == 'MNL' or dest_code == 'MNL':
        base += 500
    
    # Duration factor
    if stops > 0:
        base += (stops * 1500)
    
    price = base
    
    # Holiday Factor
    best_holiday_mult = 1.0
    info = "No info"
    for sm, sd, em, ed, mult, label in PH_HOLIDAY_PEAKS:
        if is_date_in_range(journey_date, sm, sd, em, ed):
            if mult > best_holiday_mult:
                best_holiday_mult = mult
                info = label
    
    price *= best_holiday_mult
    
    # Festival Factor
    for sm, sd, em, ed, airports, mult, label in PH_FESTIVAL_SURGES:
        if is_date_in_range(journey_date, sm, sd, em, ed):
            if source_code in airports or dest_code in airports:
                price *= mult
                if info == "No info":
                    info = label
                else:
                    info += f", {label}"
                break
                
    # Weekend Factor
    if journey_date.weekday() >= 5: # Sat, Sun
        price *= 1.10
        
    # Time of Day Factor
    hour = dep_time.hour
    if (7 <= hour <= 9) or (17 <= hour <= 19): # Peak hours
        price *= 1.12
    elif (0 <= hour <= 5): # Red eye
        price *= 0.85
        
    # Small randomization
    price *= (0.95 + random.random() * 0.1)
    
    return int(round(price)), info

def generate_data(num_rows, start_date, end_date, include_price=True):
    rows = []
    delta = end_date - start_date
    days = delta.days
    
    for _ in range(num_rows):
        airline = random.choice(AIRLINES)
        random_days = random.randint(0, days)
        journey_date = start_date + timedelta(days=random_days)
        
        # Source/Dest
        s_code, d_code = random.sample(list(AIRPORTS.keys()), 2)
        source = AIRPORTS[s_code]
        dest = AIRPORTS[d_code]
        
        # Route
        stops = random.choices([0, 1, 2], weights=[0.8, 0.15, 0.05])[0]
        if stops == 0:
            route = f"{s_code}-{d_code}"
            duration_mins = random.randint(45, 150)
        else:
            layover = random.choice([k for k in AIRPORTS.keys() if k not in [s_code, d_code]])
            if stops == 1:
                route = f"{s_code}-{layover}-{d_code}"
                duration_mins = random.randint(180, 400)
            else:
                layover2 = random.choice([k for k in AIRPORTS.keys() if k not in [s_code, d_code, layover]])
                route = f"{s_code}-{layover}-{layover2}-{d_code}"
                duration_mins = random.randint(400, 700)
        
        # Dep/Arrival Time
        dep_hour = random.randint(0, 23)
        dep_min = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        dep_time = datetime(2024, 1, 1, dep_hour, dep_min)
        
        arr_time_dt = dep_time + timedelta(minutes=duration_mins)
        dep_time_str = dep_time.strftime("%H:%M")
        arr_time_str = arr_time_dt.strftime("%H:%M")
        if arr_time_dt.day > dep_time.day:
            arr_time_str += " +1 day"
            
        duration_str = f"{duration_mins // 60}h {duration_mins % 60}m"
        
        row = [
            airline,
            journey_date.strftime("%Y-%m-%d"),
            source,
            dest,
            route,
            dep_time_str,
            arr_time_str,
            duration_str,
            stops,
        ]
        
        if include_price:
            price, info = calculate_price(airline, journey_date, dep_time, s_code, d_code, stops)
            row.append(info)
            row.append(price)
        else:
            _, info = calculate_price(airline, journey_date, dep_time, s_code, d_code, stops)
            row.append(info)
            
        rows.append(row)
        
    return rows

if __name__ == "__main__":
    import os
    
    # Generate for Training
    print("Generating training data...")
    train_start = datetime(2024, 1, 1)
    train_end = datetime(2024, 12, 31)
    new_train_rows = generate_data(3000, train_start, train_end, include_price=True)
    
    with open('Data_train.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_train_rows)
    print(f"Added 3000 rows to Data_train.csv")
    
    # Generate for Test
    print("Generating test data...")
    test_start = datetime(2024, 1, 1)
    test_end = datetime(2024, 6, 30)
    new_test_rows = generate_data(1500, test_start, test_end, include_price=False)
    
    with open('Test_set.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_test_rows)
    print(f"Added 1500 rows to Test_set.csv")
