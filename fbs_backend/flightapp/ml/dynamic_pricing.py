# flightapp/ml/dynamic_pricing.py
import random
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

class DynamicPricingService:
    """Dynamic pricing based on user, session, and real-time factors"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - only one instance ever created"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize only once"""
        if not DynamicPricingService._initialized:
            self._predictor = None
            DynamicPricingService._initialized = True
    
    @property
    def predictor(self):
        """Lazy load predictor - uses singleton pattern"""
        if self._predictor is None:
            try:
                from .predictor import predictor
                self._predictor = predictor
                # Silently check if model is loaded - no warning
                if self._predictor and self._predictor.model:
                    # Only log once at startup
                    if not hasattr(self, '_logged_connected'):
                        print("? DynamicPricing: ML model connected")
                        self._logged_connected = True
            except ImportError:
                self._predictor = None
        return self._predictor

    def get_config(self):
        """Get pricing configuration with caching"""
        try:
            from app.models import PricingConfiguration
            return PricingConfiguration.load()
        except:
            return None


    def get_price_for_user(self, flight_data, user=None, session_id=None, context=None):
        """
        Generate different prices for different users/sessions
        'context' can contain pre-fetched factors to avoid DB lookups:
        {
            'config': PricingConfiguration object,
            'user_factor': float,
            'occupancy_factor': float,
            'base_price': float (if already predicted)
        }
        """
        context = context or {}
        
        # 1. Get base ML prediction (use pre-computed if available)
        base_price = context.get('base_price')
        if base_price is None:
            base_price = self.get_base_ml_price(flight_data)
        
        # 2. Apply dynamic factors
        price = base_price
        
        # DEBUG: Print base price (commented for performance)
        # print(f"? Base price: ?{base_price:.2f}")
        
        # User-specific factors
        user_factor = context.get('user_factor')
        if user_factor is None:
            user_factor = self.get_user_factor(user, flight_data)
        price *= user_factor
        
        # Session-specific factors
        session_factor = self.get_session_factor(session_id, flight_data)
        price *= session_factor
        
        # Real-time demand factor
        demand_factor = self.get_demand_factor(flight_data)
        price *= demand_factor
        
        # Time-based factor
        time_factor = self.get_time_factor(flight_data)
        price *= time_factor
        
        # Inventory factor
        inventory_factor = context.get('occupancy_factor')
        if inventory_factor is None:
            inventory_factor = self.get_inventory_factor(flight_data)
        price *= inventory_factor
        
        # Randomization
        random_factor = self.get_randomization_factor(session_id)
        price *= random_factor
        
        # 4. Round to nice number
        final_price = self.round_price(price)
        
        return {
            'base_price': float(base_price),
            'final_price': float(final_price),
            'factors_applied': {
                'user_factor': float(user_factor),
                'session_factor': float(session_factor),
                'demand_factor': float(demand_factor),
                'time_factor': float(time_factor),
                'inventory_factor': float(inventory_factor),
                'randomization': float(random_factor)
            }
        }
    
    def get_base_ml_price(self, flight_data):
        """Get base price from ML model - returns 0 if fails"""
        if self.predictor and self.predictor.model:
            try:
                return self.predictor.predict_price(flight_data)
            except Exception:
                pass
        return 0.0  # ? Return 0 instead of fallback price

    def _fallback_base_price(self, flight_data):
        """Fallback base price calculation - now returns 0"""
        return 0.0
    
    def get_user_factor(self, user, flight_data):
        """Different prices based on user history/loyalty"""
        config = self.get_config()
        
        if not user or user.is_anonymous:
            return float(config.anonymous_user_factor) if config else 1.05
        
        try:
            from app.models import Booking
            previous_bookings = Booking.objects.filter(user=user).count()
            
            if config:
                if previous_bookings == 0:
                    return float(config.new_user_factor)
                elif previous_bookings >= 5:
                    return float(config.loyal_user_factor)
                elif previous_bookings >= 2:
                    return float(config.returning_user_factor)
            else:
                # Fallback logic if config fails
                if previous_bookings == 0:
                    return 1.03
                elif previous_bookings >= 5:
                    return 0.92
                elif previous_bookings >= 2:
                    return 0.97
        except:
            pass
        
        return 1.0
    
    def get_session_factor(self, session_id, flight_data):
        """Different prices for each browsing session"""
        if not session_id:
            return 1.0
        
        hash_input = f"{session_id}_{flight_data.get('flight_number', '')}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        factor = 0.98 + (hash_value % 5) / 100
        
        try:
            from django.core.cache import cache
            cache_key = f"session_flight_{session_id}_{flight_data.get('flight_number', '')}"
            visit_count = cache.get(cache_key, 0)
            
            if visit_count > 0:
                factor *= (1 + (min(visit_count, 5) * 0.01))
            
            cache.set(cache_key, visit_count + 1, 3600)
        except:
            pass
        
        return factor
    
    def get_demand_factor(self, flight_data):
        """Real-time demand pricing based on config"""
        config = self.get_config()
        factor = 1.0
        
        try:
            from django.core.cache import cache
            flight_key = f"flight_demand_{flight_data.get('flight_number', '')}"
            search_count = cache.get(flight_key, 0)
            
            if config:
                if search_count > config.search_threshold_high:
                    factor *= float(config.demand_factor_high)
                elif search_count > config.search_threshold_medium:
                    factor *= float(config.demand_factor_medium)
                elif search_count > config.search_threshold_low:
                    factor *= float(config.demand_factor_low)
            else:
                # Fallback
                if search_count > 100:
                    factor *= 1.15
                elif search_count > 50:
                    factor *= 1.08
                elif search_count > 20:
                    factor *= 1.03
        except:
            pass
        
        try:
            departure = flight_data.get('departure_time')
            if isinstance(departure, str):
                departure = datetime.fromisoformat(departure.replace('Z', '+00:00'))
            
            days_until = (departure - datetime.now()).days
            
            if config:
                if days_until < config.days_departure_critical:
                    factor *= float(config.days_factor_critical)
                elif days_until < config.days_departure_near:
                    factor *= float(config.days_factor_near)
                elif days_until < config.days_departure_medium:
                    factor *= float(config.days_factor_medium)
                elif days_until > config.days_departure_far:
                    factor *= float(config.days_factor_far)
            else:
                # Fallback
                if days_until < 3:
                    factor *= 1.25
                elif days_until < 7:
                    factor *= 1.15
                elif days_until < 14:
                    factor *= 1.05
                elif days_until > 60:
                    factor *= 0.90
        except:
            pass
        
        return factor
    
    def get_time_factor(self, flight_data):
        """Time-based pricing based on config"""
        config = self.get_config()
        factor = 1.0
        
        try:
            departure = flight_data.get('departure_time')
            if isinstance(departure, str):
                departure = datetime.fromisoformat(departure.replace('Z', '+00:00'))
            
            # Peak hours
            if config:
                if 7 <= departure.hour <= 9 or 17 <= departure.hour <= 19:
                    factor *= float(config.peak_hour_factor)
                
                if departure.weekday() >= 5:
                    factor *= float(config.weekend_factor)
                
                if departure.month in [12, 3, 10]:
                    factor *= float(config.peak_month_factor)
                
                if departure.month == 12 and departure.day >= 20:
                    factor *= float(config.holiday_factor)
            else:
                # Fallback
                if 7 <= departure.hour <= 9 or 17 <= departure.hour <= 19:
                    factor *= 1.12
                
                if departure.weekday() >= 5:
                    factor *= 1.08
                
                if departure.month in [12, 3, 10]:
                    factor *= 1.20
                
                if departure.month == 12 and departure.day >= 20:
                    factor *= 1.30
        except:
            pass
        
        return factor
    
    def get_inventory_factor(self, flight_data):
        """Inventory-based pricing based on config"""
        try:
            from app.models import Seat
            config = self.get_config()
            
            schedule_id = flight_data.get('schedule_id')
            if schedule_id:
                available_seats = Seat.objects.filter(
                    schedule_id=schedule_id,
                    is_available=True
                ).count()
                
                total_seats = Seat.objects.filter(
                    schedule_id=schedule_id
                ).count()
                
                if total_seats > 0:
                    occupancy_rate = 1 - (available_seats / total_seats)
                    
                    if config:
                        if occupancy_rate > float(config.occupancy_high_threshold):
                            return float(config.occupancy_factor_high)
                        elif occupancy_rate > float(config.occupancy_medium_threshold):
                            return float(config.occupancy_factor_medium)
                        elif occupancy_rate < float(config.occupancy_low_threshold):
                            return float(config.occupancy_factor_low)
                    else:
                        # Fallback
                        if occupancy_rate > 0.8:
                            return 1.20
                        elif occupancy_rate > 0.6:
                            return 1.10
                        elif occupancy_rate < 0.2:
                            return 0.90
        except:
            pass
        
        return 1.0
    
    def get_randomization_factor(self, session_id):
        """Add small randomization to prevent price matching"""
        if not session_id:
            return 1.0 + (random.random() * 0.04 - 0.02)
        
        hash_input = f"random_{session_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        return 0.98 + (hash_value % 5) / 100
    

    def round_price(self, price):
        """
        Round to psychological price points
        Philippine Airlines / Cebu Pacific style:
        - 999, 1499, 1999, 2499, 2999, etc.
        """
        if price <= 0:
            return 0
            
        price_int = int(round(price))
        
        if price_int < 1000:
            # 999, 899, 799, 699, etc.
            base = int(round(price_int / 100) * 100)
            return max(base - 1, 0)
        
        elif price_int < 10000:
            # 1499, 1999, 2499, 2999, 3499, etc.
            base = int(round(price_int / 500) * 500)
            return base - 1
        
        elif price_int < 20000:
            # 9999, 10999, 11999, 12999, etc.
            base = int(round(price_int / 1000) * 1000)
            return base - 1
        
        else:
            # 19999, 24999, 29999, 34999, etc.
            base = int(round(price_int / 5000) * 5000)
            return base - 1

    def round_seat_class_price(self, price):
        """
        Special rounding for seat classes - cleaner numbers
        Business/First class should round to nice numbers
        """
        if price <= 0:
            return 0
            
        price_int = int(round(price))
        
        if price_int < 5000:
            # Round to nearest 100
            return int(round(price_int / 100) * 100)
        elif price_int < 10000:
            # Round to nearest 500
            return int(round(price_int / 500) * 500)
        elif price_int < 20000:
            # Round to nearest 1000
            return int(round(price_int / 1000) * 1000)
        else:
            # Round to nearest 5000
            return int(round(price_int / 5000) * 5000)

# Singleton instance
dynamic_pricing = DynamicPricingService()