# flightapp/ml/predictor.py
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from decimal import Decimal
import json
import os
import sys
import random
from pathlib import Path

class FlightPricePredictor:
    """Service to predict flight prices using trained XGBoost model"""
    
    # Class-level singleton instance and cached model
    _instance = None
    _model = None
    _feature_mapping = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - only one instance ever created"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize only once"""
        if not FlightPricePredictor._initialized:
            self.model = None
            self.feature_mapping = None
            
            # Check if we should skip loading (migrations only)
            if not self._is_migration_command():
                self.load_model()
                self.load_feature_mapping()
                # Cache at class level
                FlightPricePredictor._model = self.model
                FlightPricePredictor._feature_mapping = self.feature_mapping
            else:
                print("[CONFIG] Running migration command - skipping model load")
            
            FlightPricePredictor._initialized = True
        else:
            # Restore from class-level cache
            self.model = FlightPricePredictor._model
            self.feature_mapping = FlightPricePredictor._feature_mapping

    def _is_migration_command(self):
        """Check if we're running a database migration command that could conflict"""
        migration_commands = [
            'makemigrations',
            'migrate',
            'sqlmigrate',
            'sqlflush',
            'sqlsequencereset',
        ]
        return any(cmd in sys.argv for cmd in migration_commands)
    
    def load_model(self):
        """Load the trained XGBoost model from the correct path"""
        try:
            # Construct path relative to this file's parent or BASE_DIR
            # The model is usually in the fbs_backend root
            base_dir = Path(__file__).resolve().parent.parent.parent
            model_path = base_dir / 'flight_xgb.pkl'
            
            print(f"[MODEL] Attempting to load XGBoost model from: {model_path}")
            
            if not model_path.exists():
                # Try relative to CWD as fallback
                model_path = Path('flight_xgb.pkl')
                print(f"[WARN] Not found at primary path, trying fallback: {model_path.absolute()}")
            
            with open(model_path, 'rb') as file:
                self.model = pickle.load(file)
                # Cache at class level
                FlightPricePredictor._model = self.model
            
            print("[SUCCESS] XGBoost Model loaded successfully!")
            print(f"   Model type: {type(self.model)}")
            
            # Try to get XGBoost specific info
            try:
                if hasattr(self.model, 'get_params'):
                    params = self.model.get_params()
                    print(f"   XGBoost parameters: {params.get('n_estimators', 'N/A')} trees")
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load XGBoost model: {e}")
            # Try to use cached model if available
            if FlightPricePredictor._model:
                self.model = FlightPricePredictor._model
                print("[INFO] Using cached model from previous instance")
                return True
            self.model = None
            return False

    def load_feature_mapping(self):
        """Load feature column mappings from feature_mapping.json"""
        try:
            mapping_path = Path(__file__).parent / 'feature_mapping.json'
            
            if mapping_path.exists():
                with open(mapping_path, 'r') as file:
                    self.feature_mapping = json.load(file)
                    # Cache at class level
                    FlightPricePredictor._feature_mapping = self.feature_mapping
                print("[SUCCESS] Feature mapping loaded from feature_mapping.json")
                print(f"   Loaded {len(self.feature_mapping.get('feature_columns', []))} feature columns")
            else:
                print(f"[ERROR] Feature mapping file not found at: {mapping_path}")
                self.feature_mapping = FlightPricePredictor._feature_mapping
                
        except Exception as e:
            print(f"[ERROR] Failed to load feature mapping: {e}")
            self.feature_mapping = FlightPricePredictor._feature_mapping
    
    def prepare_features(self, flight_data):
        """
        Convert flight data into feature vector for prediction
        Uses feature_mapping.json for column mapping
        """
        # Restore from cache if needed
        if not self.model and FlightPricePredictor._model:
            self.model = FlightPricePredictor._model
        if not self.feature_mapping and FlightPricePredictor._feature_mapping:
            self.feature_mapping = FlightPricePredictor._feature_mapping
        
        if not self.model or not self.feature_mapping:
            return None
        
        try:
            # Create feature vector with zeros
            features = {col: 0 for col in self.feature_mapping['feature_columns']}
            
            # 1. Total Stops
            features['Total_Stops'] = flight_data.get('total_stops', 0)
            
            # 2. Journey day/month from departure time
            dep_time = flight_data.get('departure_time')
            if isinstance(dep_time, str):
                dep_time = datetime.fromisoformat(dep_time.replace('Z', '+00:00'))
            
            features['Journey_day'] = dep_time.day
            features['Journey_month'] = dep_time.month
            
            # 3. Departure hour/minute
            features['Dep_hour'] = dep_time.hour
            features['Dep_min'] = dep_time.minute
            
            # 4. Arrival hour/minute
            arr_time = flight_data.get('arrival_time')
            if isinstance(arr_time, str):
                arr_time = datetime.fromisoformat(arr_time.replace('Z', '+00:00'))
            
            features['Arrival_hour'] = arr_time.hour
            features['Arrival_min'] = arr_time.minute
            
            # 5. Duration
            duration = arr_time - dep_time
            features['Duration_hours'] = duration.seconds // 3600
            features['Duration_mins'] = (duration.seconds % 3600) // 60
            
            # 6. Airline one-hot encoding
            airline_name = flight_data.get('airline_name', '')
            for airline_key, airline_col in self.feature_mapping['airline_codes'].items():
                if airline_key.lower() in airline_name.lower() or airline_name.lower() in airline_key.lower():
                    if airline_col in features:
                        features[airline_col] = 1
                        break
            
            # 7. Source one-hot encoding
            origin = flight_data.get('origin', '')
            for source_key, source_col in self.feature_mapping['source_codes'].items():
                if source_key in origin or origin in source_key:
                    if source_col in features:
                        features[source_col] = 1
                        break
            
            # 8. Destination one-hot encoding
            destination = flight_data.get('destination', '')
            for dest_key, dest_col in self.feature_mapping['destination_codes'].items():
                if dest_key in destination or destination in dest_key:
                    if dest_col in features:
                        features[dest_col] = 1
                        break
            
            # Convert to DataFrame for prediction
            df = pd.DataFrame([features])
            
            # Ensure columns are in the right order
            df = df[self.feature_mapping['feature_columns']]
            
            return df
            
        except Exception as e:
            print(f"[ERROR] Error preparing features: {e}")
            return None
    
    def predict_price(self, flight_data):
        """
        Predict base price for a flight using XGBoost
        Returns RAW prediction - NO ROUNDING!
        """
        # Restore from cache if needed
        if not self.model and FlightPricePredictor._model:
            self.model = FlightPricePredictor._model
        if not self.feature_mapping and FlightPricePredictor._feature_mapping:
            self.feature_mapping = FlightPricePredictor._feature_mapping
        
        if not self.model:
            return 0.0
        
        try:
            features_df = self.prepare_features(flight_data)
            if features_df is None:
                return 0.0
            
            # XGBoost prediction - RAW value
            predicted_price = self.model.predict(features_df)[0]
            
            # XGBoost sometimes returns weird types
            if hasattr(predicted_price, 'item'):
                predicted_price = predicted_price.item()
            
            # Ensure positive price
            predicted_price = max(predicted_price, 0)
            
            # Print raw prediction (remove in production)
            # print(f"[PRICE] XGBoost: PHP {predicted_price:.2f}")
            
            return float(predicted_price)
            
        except Exception as e:
            print(f"[ERROR] XGBoost prediction error: {e}")
            return 0.0

    def predict_prices_batch(self, flight_data_list):
        """
        Predict base prices for a list of flights using XGBoost in BATCH
        Returns a list of floats
        """
        if not self.model or not flight_data_list:
            return [0.0] * len(flight_data_list)
            
        try:
            # Prepare all feature vectors
            all_features = []
            for data in flight_data_list:
                df = self.prepare_features(data)
                if df is not None:
                    all_features.append(df)
                else:
                    # Fallback for failed feature preparation
                    all_features.append(pd.DataFrame(np.zeros((1, len(self.feature_mapping['feature_columns']))), 
                                                 columns=self.feature_mapping['feature_columns']))
            
            if not all_features:
                return [0.0] * len(flight_data_list)
                
            # Combine into one large DataFrame
            batch_df = pd.concat(all_features, ignore_index=True)
            
            # Batch prediction
            predictions = self.model.predict(batch_df)
            
            # Convert to standard Python floats and ensure positive
            return [max(float(p), 0.0) for p in predictions]
            
        except Exception as e:
            print(f"[ERROR] Batch XGBoost prediction error: {e}")
            return [0.0] * len(flight_data_list)
    
    def predict_seat_class_price(self, base_price, seat_class_name):
        """Predict price with seat class adjustment"""
        multipliers = {
            'economy': 1.0,
            'premium_economy': 1.35,
            'business': 1.8,
            'first': 2.4,
            'business_class': 1.8,
            'first_class': 2.4,
            'economy class': 1.0,
            'premium economy': 1.35,
            'comfort': 1.2,
            'deluxe': 1.6,
            'executive': 2.0,
        }
        
        key = seat_class_name.lower().replace(' ', '_')
        multiplier = multipliers.get(key, 1.0)
        
        return float(base_price * multiplier)

# Singleton instance
predictor = FlightPricePredictor()