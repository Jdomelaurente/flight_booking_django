# Flight App Dynamic Pricing & Base Predictor

This document outlines how flight prices are calculated in our system. The pricing model relies on a **two-step calculation**: 
1. **Base Price Prediction** (Machine Learning)
2. **Dynamic Multipliers** (Business Logic / Real-time Context)

---

## 1. The Base Price Prediction (Machine Learning)
**File location:** `flightapp/ml/predictor.py`

The system uses a pre-trained **XGBoost Algorithm** (`flight_xgb.pkl`) to supply the initial flight base price. It does not pull prices from an external API; rather, it makes intelligent predictions based on Historical Data Patterns.

### Features evaluated by the ML Model:
When a user searches for a flight, the `prepare_features` method creates a DataFrame evaluating the following logic:
- **Total Stops**: More stops generally lower the base fare.
- **Date Information**: Journey day and month (`Journey_day`, `Journey_month`).
- **Time Information**: Departure hour/minute and Arrival hour/minute. 
- **Flight Duration**: Total duration in hours and minutes.
- **Flight Specifics**: The Airline, Origin, and Destination (all One-Hot Encoded).

### Code Snippet (`predictor.py`):
```python
def predict_price(self, flight_data):
    features_df = self.prepare_features(flight_data)
    # XGBoost base prediction based on historical feature factors
    predicted_price = self.model.predict(features_df)[0]
    return float(predicted_price)
```

---

## 2. Dynamic Price Fluctuations 
**File location:** `flightapp/ml/dynamic_pricing.py`

Once the ML model spits out the base price, the `DynamicPricingService` steps in to fluctuate that price to match **real-time scenarios** like Holidays, Fiestas, Supply/Demand, and User Behavior.

The calculation works like this:
```text
Final Price = Base Price * User Factor * Session Factor * Demand Factor * Time Factor * Inventory Factor * Randomization 
```

### A. The Time Factor (Holidays, Fiestas, Peak Hours)
This represents seasonality. During city fiestas (e.g., peak local months), weekends, or major holidays like December, the system manually forces a multiplicative spike.

**Code Snippet (`dynamic_pricing.py` - `get_time_factor`):**
```python
# If the flight departs between 7-9 AM or 5-7 PM (Rush Hours)
if 7 <= departure.hour <= 9 or 17 <= departure.hour <= 19:
    factor *= 1.12  # +12% increase

# If the flight is on a Weekend
if departure.weekday() >= 5:
    factor *= 1.08  # +8% increase

# If the flight is in a peak vacation month (e.g. Fiestas in Oct, Summer in Mar, Holidays in Dec)
if departure.month in [12, 3, 10]:
    factor *= 1.20  # +20% increase

# SPECIFIC HOLIDAY/FIESTA SPIKE (e.g., Dec 20 onwards)
if departure.month == 12 and departure.day >= 20:
    factor *= 1.30  # +30% massive increase
```

### B. The Demand & Days-to-Departure Factor
Prices dramatically rise depending on how urgently a user is booking or how many people are searching for the exact same flight simultaneously.

**Code Snippet (`dynamic_pricing.py` - `get_demand_factor`):**
```python
# Demand based on how many users recently searched for THIS flight number
search_count = cache.get(flight_key, 0)
if search_count > 100: factor *= 1.15  # Surging popularity (+15%)
elif search_count > 50: factor *= 1.08 

# Demand based on urgency (days left until takeoff)
days_until = (departure - datetime.now()).days
if days_until < 3: factor *= 1.25      # Emergency booking (+25%)
elif days_until < 7: factor *= 1.15    # Late booking (+15%)
elif days_until > 60: factor *= 0.90   # Early bird discount (-10%)
```

### C. The Inventory / Occupancy Factor
Basic Supply vs. Demand. If a plane is almost full, the remaining seats become significantly more expensive.

**Code Snippet (`dynamic_pricing.py` - `get_inventory_factor`):**
```python
occupancy_rate = 1 - (available_seats / total_seats)

if occupancy_rate > 0.8:     # Plane is 80%+ full
    return 1.20              # Increase price by 20%
elif occupancy_rate > 0.6:   # Plane is 60%+ full
    return 1.10
elif occupancy_rate < 0.2:   # Plane is empty
    return 0.90              # Discount by 10%
```

### D. Psychological Rounding
To make prices look pleasing and to mimic standard airline rules (like Cebu Pacific), everything rounds to neat psychology numbers at the end (e.g., ending in 99).

**Code snippet (`dynamic_pricing.py` - `round_price`):**
```python
if price_int < 10000:
    # Turns a price like 2341.50 into 2499 or 1999
    base = int(round(price_int / 500) * 500)
    return base - 1 
```

---

## How to Easily Explain This to the Panelist:

1. **Step 1:** *"Our system doesn't rely on random guessing. First, we use an **XGBoost Machine Learning model**. The model looks at historical flight data, travel duration, the number of stops, and airlines to establish a statistically accurate base fare."*
2. **Step 2:** *"Once we have the Base Fare, our **Dynamic Pricing Engine** steps in to mimic real-world airline economics. It applies percentage multipliers sequentially."*
3. **Step 3:** *"For example, during a **City Fiesta or Holiday**, our `get_time_factor()` function detects if the departure month falls into a peak season like December or October. If true, it multiplies the base price by up to 1.30 (a 30% surge)."*
4. **Step 4:** *"We also evaluate **occupancy and urgency**. If a user tries to book just 3 days before a flight (`days_until < 3`), or if the plane is already 80% full, the price scales up drastically just like real-world airlines do. Finally, we round the price psychologically to end in 99 so it looks authentic."*



How to Explain This to the Panelist 🎙️
"Our flight pricing engine does not rely on static numbers or random guessing. It operates in a two-step process: First, an AI predicts a Base Fare based on historical data. Second, a Dynamic Pricing Algorithm fluctuates that base fare to mimic real-world supply, demand, and seasonality like holidays or fiestas."

Step 1: The Base Price Prediction (The Machine Learning)
Location: 

ml/predictor.py

When a user searches for a flight, your system feeds flight details into a trained XGBoost Machine Learning Model. The model has learned historical flight data patterns and looks at:

How many Stops the flight has
The Journey Day & Month
Time of Departure/Arrival and total Duration
The specific Airline, Origin, and Destination
It then spits out an initial, realistic 

base_price
 for that route.

The Code:

python
def predict_price(self, flight_data):
    # Prepares the features (Stops, Airline, Date, Duration)
    features_df = self.prepare_features(flight_data)
    
    # The XGBoost ML model predicts the raw base price based on history
    predicted_price = self.model.predict(features_df)[0]
    return float(predicted_price)
Step 2: Dynamic Price Fluctuations
Location: 

ml/dynamic_pricing.py

Once the ML model provides the Base Price, your 

DynamicPricingService
 applies series of multipliers sequentially to simulate real airline economics:

Final Price = Base Price * User Loyalty * Demand * Time (Holidays) * Inventory * Randomization

A. Fiestas, Holidays, and Peak Hours (

get_time_factor
)
If the flight occurs during a city fiesta, a peak holiday month, or rush hour, the system adds a percentage markup. For example, if the flight departs very close to Christmas, the base price surges by 30%.

python
# During peak months (Oct for fiestas, Dec for holidays, Mar for summer)
if departure.month in [12, 3, 10]:
    factor *= 1.20  # +20% price surge
# Massive surge for specific Holiday/Christmas week (Dec 20 onwards)
if departure.month == 12 and departure.day >= 20: 
    factor *= 1.30  # +30% massive price surge
    
# Rush hour peaks (7-9 AM or 5-7 PM)
if 7 <= departure.hour <= 9 or 17 <= departure.hour <= 19:
    factor *= 1.12  # +12% increase
B. Supply & Demand Urgency (

get_demand_factor
 & 

get_inventory_factor
)
Like real airlines, your system punishes last-minute bookers. It checks how many days are left until the flight takes off. It also checks how many seats are left; if the plane is almost full, the remaining seats become incredibly expensive.

python
# 1. URGENCY: How soon is the flight?
days_until = (departure - datetime.now()).days
if days_until < 3: factor *= 1.25      # Emergency booking (+25% surge)
elif days_until < 7: factor *= 1.15    # Late booking (+15% surge)
elif days_until > 60: factor *= 0.90   # Early bird discount (-10% off)
# 2. INVENTORY: Is the plane almost full?
occupancy_rate = 1 - (available_seats / total_seats)
if occupancy_rate > 0.8:     # Plane is 80%+ full
    return 1.20              # Supply is low, increase price by 20%
elif occupancy_rate < 0.2:   # Plane is practically empty
    return 0.90              # Discount price by 10%
C. Psychological Rounding (

round_price
)
To make it look extremely realistic—exactly like how Cebu Pacific or Philippine Airlines does it—the system uses "Psychological Pricing". It takes the final mathematical number and forces it to end in a 9.

python
if price_int < 10000:
    # Turns a raw calculated price like "P 2341.50" immediately into "P 2499.00"
    base = int(round(price_int / 500) * 500)
    return base - 1
To summarize to your panelist: "First, our Machine Learning calculates what the flight should cost based on history. Then, our dynamic algorithm checks if it's a holiday, if the user is booking last minute, and if the plane is almost full—surging the price automatically before rounding it to look like a real corporate airline ticket."