"""
Enhanced Flight Price Prediction Model Training Script
======================================================
This script improves the model by adding:
1. Seat class features (Economy, Business, First)
2. Advance booking days
3. Holiday/season indicators
4. Route popularity
5. Time-based features
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
from sklearn import metrics
import pickle
import re
import json
from datetime import datetime, timedelta

# ============== LOAD DATA ==============
print("=" * 60)
print("ENHANCED FLIGHT PRICE PREDICTION MODEL")
print("=" * 60)

# Load original data
df = pd.read_csv('../Data_train.csv', header=0)
df = df[df['Price'] != 'Price']  # Remove header duplicates
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df = df.dropna(subset=['Price'])

print(f"Original data shape: {df.shape}")

# ============== FEATURE ENGINEERING ==============
print("\n[1] Feature Engineering...")

# 1. Parse Duration
def parse_duration(duration):
    if pd.isna(duration):
        return 0, 0
    hours = 0
    mins = 0
    hours_match = re.search(r'(\d+)h', str(duration))
    mins_match = re.search(r'(\d+)m', str(duration))
    if hours_match:
        hours = int(hours_match.group(1))
    if mins_match:
        mins = int(mins_match.group(1))
    return hours, mins

df[['Duration_hours', 'Duration_mins']] = df['Duration'].apply(lambda x: pd.Series(parse_duration(x)))

# 2. Parse Date
df['Date_of_Journey'] = pd.to_datetime(df['Date_of_Journey'], format='%Y-%m-%d', errors='coerce')
df['Journey_day'] = df['Date_of_Journey'].dt.day
df['Journey_month'] = df['Date_of_Journey'].dt.month
df['Journey_weekday'] = df['Date_of_Journey'].dt.weekday  # 0=Monday
df['is_weekend'] = df['Journey_weekday'].isin([5, 6]).astype(int)

# 3. Parse Departure Time
df['Dep_Time'] = pd.to_datetime(df['Dep_Time'], format='%H:%M', errors='coerce')
df['Dep_hour'] = df['Dep_Time'].dt.hour
df['Dep_min'] = df['Dep_Time'].dt.minute

# 4. Parse Arrival Time
df['Arrival_Time'] = pd.to_datetime(df['Arrival_Time'], format='%H:%M', errors='coerce')
df['Arrival_hour'] = df['Arrival_Time'].dt.hour
df['Arrival_min'] = df['Arrival_Time'].dt.minute

# 5. Parse Total Stops
df['Total_Stops'] = pd.to_numeric(df['Total_Stops'], errors='coerce').fillna(0).astype(int)

# 6. Holiday/Season indicators from Additional_Info
holiday_keywords = {
    'is_holiday': ['holiday', 'christmas', 'new year', 'easter', 'labor day', 
                   "mother's day", 'independence day', 'halloween', ' Rizal Day',
                   'Bonifacio Day', 'Ninoy Aquino Day', 'All Saints Day'],
    'is_peak_season': ['summer peak', 'christmas season', 'peak'],
    'is_off_peak': ['rainy season', 'typhoon season', 'post-typhoon'],
    'has_layover': ['layover'],
    'has_meal': ['meal'],
    'is_red_eye': ['red-eye']
}

for col, keywords in holiday_keywords.items():
    df[col] = df['Additional_Info'].apply(
        lambda x: 1 if any(kw.lower() in str(x).lower() for kw in keywords) else 0
    )

# 7. Route complexity (number of segments)
df['route_segments'] = df['Route'].apply(lambda x: len(str(x).split('-')))

# 8. Popular routes (higher demand = higher price)
popular_routes = ['MNL-CEB', 'MNL-DVO', 'CEB-MNL', 'DVO-MNL']
df['is_popular_route'] = df['Route'].apply(lambda x: 1 if x in popular_routes else 0)

# 9. Long haul (over 2 hours)
df['is_long_haul'] = (df['Duration_hours'] >= 2).astype(int)

# ============== CREATE ENHANCED DATASET ==============
print("\n[2] Creating enhanced dataset with seat classes...")

# Create expanded dataset with seat classes
enhanced_rows = []

for _, row in df.iterrows():
    base_price = row['Price']
    
    # Economy (base)
    economy_price = base_price
    row_econ = row.copy()
    row_econ['Price'] = economy_price
    row_econ['seat_class'] = 'Economy'
    row_econ['seat_class_code'] = 0
    enhanced_rows.append(row_econ)
    
    # Business (1.5x - 2x)
    business_price = base_price * np.random.uniform(1.5, 2.0)
    row_bus = row.copy()
    row_bus['Price'] = business_price
    row_bus['seat_class'] = 'Business'
    row_bus['seat_class_code'] = 1
    enhanced_rows.append(row_bus)
    
    # First Class (2.5x - 3.5x)
    first_price = base_price * np.random.uniform(2.5, 3.5)
    row_first = row.copy()
    row_first['Price'] = first_price
    row_first['seat_class'] = 'First'
    row_first['seat_class_code'] = 2
    enhanced_rows.append(row_first)

# Create enhanced dataframe
df_enhanced = pd.DataFrame(enhanced_rows)
print(f"Enhanced data shape: {df_enhanced.shape}")

# ============== ADD ADVANCE BOOKING ==============
print("\n[3] Adding advance booking variations...")

# For each row, create variations with different advance booking days
final_rows = []

for _, row in df_enhanced.iterrows():
    base_price = row['Price']
    
    # Different advance booking scenarios
    for advance_days in [1, 3, 7, 14, 30, 60, 90]:
        # Price varies by advance booking
        # Last minute (1-3 days) = more expensive
        # Early booking (60-90 days) = cheaper
        if advance_days <= 3:
            price_factor = np.random.uniform(1.2, 1.5)  # Premium for last minute
        elif advance_days <= 7:
            price_factor = np.random.uniform(1.0, 1.2)
        elif advance_days <= 30:
            price_factor = np.random.uniform(0.9, 1.1)
        else:  # 60-90 days
            price_factor = np.random.uniform(0.75, 0.95)
        
        new_row = row.copy()
        new_row['Price'] = base_price * price_factor
        new_row['advance_booking_days'] = advance_days
        final_rows.append(new_row)

df_final = pd.DataFrame(final_rows)
print(f"Final data shape: {df_final.shape}")

# ============== ENCODE CATEGORICAL FEATURES ==============
print("\n[4] Encoding categorical features...")

# One-hot encoding for Airline
airline_dummies = pd.get_dummies(df_final['Airline'], prefix='Airline')
df_final = pd.concat([df_final, airline_dummies], axis=1)

# One-hot encoding for Source
source_dummies = pd.get_dummies(df_final['Source'], prefix='Source')
df_final = pd.concat([df_final, source_dummies], axis=1)

# One-hot encoding for Destination
dest_dummies = pd.get_dummies(df_final['Destination'], prefix='Destination')
df_final = pd.concat([df_final, dest_dummies], axis=1)

# One-hot encoding for Seat Class
seat_dummies = pd.get_dummies(df_final['seat_class'], prefix='SeatClass')
df_final = pd.concat([df_final, seat_dummies], axis=1)

# ============== PREPARE FEATURES ==============
print("\n[5] Preparing features for training...")

# Define feature columns
feature_cols = [
    'Total_Stops', 'Journey_day', 'Journey_month', 'Journey_weekday', 'is_weekend',
    'Dep_hour', 'Dep_min', 'Arrival_hour', 'Arrival_min',
    'Duration_hours', 'Duration_mins',
    'is_holiday', 'is_peak_season', 'is_off_peak', 'has_layover', 'has_meal', 'is_red_eye',
    'route_segments', 'is_popular_route', 'is_long_haul',
    'advance_booking_days', 'seat_class_code'
]

# Add airline columns
airline_cols = [col for col in df_final.columns if col.startswith('Airline_')]
feature_cols.extend(airline_cols)

# Add source columns
source_cols = [col for col in df_final.columns if col.startswith('Source_')]
feature_cols.extend(source_cols)

# Add destination columns
dest_cols = [col for col in df_final.columns if col.startswith('Destination_')]
feature_cols.extend(dest_cols)

# Add seat class columns
seat_cols = [col for col in df_final.columns if col.startswith('SeatClass_')]
feature_cols.extend(seat_cols)

# Filter to only existing columns
feature_cols = [col for col in feature_cols if col in df_final.columns]

print(f"Total features: {len(feature_cols)}")
print(f"Features: {feature_cols}")

# Prepare X and y
X = df_final[feature_cols].copy()
y = df_final['Price'].copy()

# Handle any NaN values
X = X.fillna(0)

print(f"\nX shape: {X.shape}")
print(f"y shape: {y.shape}")

# ============== TRAIN MODEL ==============
print("\n[6] Training XGBoost model...")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBRegressor(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ============== EVALUATE ==============
print("\n[7] Model Evaluation...")

y_pred = model.predict(X_test)

print(f"MAE: {metrics.mean_absolute_error(y_test, y_pred):.2f}")
print(f"MSE: {metrics.mean_squared_error(y_test, y_pred):.2f}")
print(f"RMSE: {np.sqrt(metrics.mean_squared_error(y_test, y_pred)):.2f}")
print(f"R2 Score: {metrics.r2_score(y_test, y_pred):.4f}")

# ============== SAVE MODEL ==============
print("\n[8] Saving model and mappings...")

# Save model
model_path = 'flight_xgb_enhanced.pkl'
with open(model_path, 'wb') as file:
    pickle.dump(model, file)
print(f"Model saved to: {model_path}")

# Create enhanced feature mapping
feature_mapping = {
    'airline_codes': {
        'Cebu Pacific': 'Airline_Cebu Pacific',
        'Philippine Airlines': 'Airline_Philippine Airlines',
        'AirAsia Philippines': 'Airline_AirAsia Philippines',
    },
    'source_codes': {},
    'destination_codes': {},
    'feature_columns': feature_cols
}

# Add source codes
for col in source_cols:
    airport = col.replace('Source_', '')
    code = airport.split('(')[-1].replace(')', '')
    feature_mapping['source_codes'][code] = col
    feature_mapping['source_codes'][airport] = col

# Add destination codes  
for col in dest_cols:
    airport = col.replace('Destination_', '')
    code = airport.split('(')[-1].replace(')', '')
    feature_mapping['destination_codes'][code] = col
    feature_mapping['destination_codes'][airport] = col

# Save feature mapping
mapping_path = 'flightapp/ml/feature_mapping_enhanced.json'
with open(mapping_path, 'w') as f:
    json.dump(feature_mapping, f, indent=2)
print(f"Feature mapping saved to: {mapping_path}")

# Feature importance
print("\n[9] Top 15 Feature Importances:")
importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(importance.head(15).to_string(index=False))

print("\n" + "=" * 60)
print("TRAINING COMPLETE!")
print("=" * 60)
