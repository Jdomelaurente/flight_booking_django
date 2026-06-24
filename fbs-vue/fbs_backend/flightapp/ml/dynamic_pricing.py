# flightapp/ml/dynamic_pricing.py
import random
import hashlib
from datetime import timedelta, date
from decimal import Decimal
import numpy as np
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# 2026 PHILIPPINE FLIGHT PRICING CALENDAR
# =============================================================================

# National Holiday Peaks — (start_month, start_day, end_month, end_day, multiplier, label)
PH_HOLIDAY_PEAKS = [
    # New Year Return Wave
    (1, 1, 1, 5, 1.40, "New Year Return Wave"),
    # Chinese New Year (Feb 17) — 4-day spike
    (2, 15, 2, 18, 1.30, "Chinese New Year"),
    # Eid'l Fitr (Mar 20) — long weekend
    (3, 19, 3, 22, 1.25, "Eid'l Fitr"),
    # Holy Week (Semana Santa)
    (4, 1, 4, 6, 1.50, "Holy Week"),
    # Araw ng Kagitingan (Apr 9) — potential 4-day weekend
    (4, 8, 4, 12, 1.25, "Araw ng Kagitingan"),
    # Labor Day (May 1) — 3-day beach surge
    (4, 30, 5, 3, 1.30, "Labor Day Weekend"),
    # Eid'l Adha (May 27) — mid-week, Mindanao routes
    (5, 26, 5, 28, 1.20, "Eid'l Adha"),
    # Independence Day (Jun 12) — 3-day weekend
    (6, 11, 6, 14, 1.25, "Independence Day"),
    # Ninoy Aquino Day (Aug 21) — 3-day weekend
    (8, 20, 8, 23, 1.20, "Ninoy Aquino Day"),
    # National Heroes Day (Aug 31) — 3-day weekend
    (8, 29, 9, 1, 1.20, "National Heroes Day"),
    # Undas / All Saints & Souls (Oct 31 – Nov 2)
    (10, 29, 11, 3, 1.35, "Undas"),
    # Bonifacio Day (Nov 30) — 3-day weekend
    (11, 28, 11, 30, 1.20, "Bonifacio Day"),
    # Feast of Immaculate Conception (Dec 8)
    (12, 7, 12, 9, 1.15, "Immaculate Conception"),
    # Christmas / Rizal Day EXTREME PEAK (Dec 24 – Jan 3)
    (12, 20, 12, 31, 1.60, "Christmas / Rizal Day Peak"),
]

# Regional Festival Surges — (start_m, start_d, end_m, end_d, airport_codes[], multiplier, label)
# These apply ONLY to flights going TO or FROM the listed airports.
PH_FESTIVAL_SURGES = [
    # Black Nazarene — Manila traffic/hotel spike
    (1, 8, 1, 10, ['MNL'], 1.15, "Black Nazarene"),
    # Sinulog — Cebu City (flights to CEB surge Jan 15–20)
    (1, 15, 1, 20, ['CEB'], 1.35, "Sinulog Festival"),
    # Ati-Atihan — Kalibo (flights to KLO surge)
    (1, 16, 1, 20, ['KLO', 'MPH'], 1.30, "Ati-Atihan Festival"),
    # Dinagyang — Iloilo City
    (1, 23, 1, 27, ['ILO'], 1.30, "Dinagyang Festival"),
    # Panagbenga — Baguio (Feb; flights to BAG/Loakan)
    (2, 1, 2, 28, ['BAG', 'SFS'], 1.15, "Panagbenga"),
    # Kadayawan — Davao City 
    (8, 17, 8, 23, ['DVO'], 1.25, "Kadayawan Festival"),
    # Peñafrancia — Naga City
    (9, 11, 9, 20, ['WNP'], 1.20, "Peñafrancia Festival"),
    # MassKara — Bacolod City
    (10, 19, 10, 25, ['BCD'], 1.25, "MassKara Festival"),
]

# Academic Break Spikes — same format as holidays
PH_ACADEMIC_BREAKS = [
    # Mid-Year Break (overlaps Undas)
    (10, 26, 11, 3, 1.20, "Mid-Year School Break"),
    # Academic Year End — graduation trip surge
    (5, 20, 6, 7, 1.15, "Graduation Trip Season"),
    # School Start — return to Manila for university
    (8, 1, 8, 10, 1.15, "Back-to-School Movement"),
]
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


    def get_price_for_user(self, flight_data, user=None, session_id=None, context=None, is_search=False):
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
        session_factor = self.get_session_factor(session_id, flight_data, is_search=is_search)
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
        random_factor = self.get_randomization_factor(session_id, flight_data)
        price *= random_factor
        
        # Festival / regional surge factor (route-specific)
        festival_factor = self.get_festival_factor(flight_data)
        price *= festival_factor
        
        # 4. Get exact price without decimal
        final_price = self.round_price(price)
        
        return {
            'base_price': int(round(base_price)),
            'final_price': int(final_price),
            'factors_applied': {
                'user_factor': float(user_factor),
                'session_factor': float(session_factor),
                'demand_factor': float(demand_factor),
                'time_factor': float(time_factor),
                'inventory_factor': float(inventory_factor),
                'randomization': float(random_factor),
                'festival_factor': float(festival_factor)
            }
        }
    
    def get_base_ml_price(self, flight_data):
        """Get base price from ML model - returns fallback if fails"""
        if self.predictor and self.predictor.model:
            try:
                price = self.predictor.predict_price(flight_data)
                if price > 0:
                    return price
                else:
                    logger.warning(f"ML returned 0, using fallback for flight: {flight_data.get('flight_number')}")
            except Exception as e:
                logger.error(f"ML prediction failed: {e}", exc_info=True)
        return self._fallback_base_price(flight_data)

    def _fallback_base_price(self, flight_data):
        """Fallback base price calculation based on route/duration"""
        try:
            # Check if there is a base price provided by the flight schedule directly
            if 'base_price' in flight_data and flight_data['base_price']:
                try:
                    return float(flight_data['base_price'])
                except (ValueError, TypeError):
                    pass
                    
            duration = flight_data.get('duration_hours', 1.5)
            if isinstance(duration, str):
                import re
                hours = re.findall(r'(\d+)h', duration)
                mins = re.findall(r'(\d+)m', duration)
                duration = int(hours[0]) if hours else 0
                duration += int(mins[0]) / 60 if mins else 0
            
            base = 2500
            if duration > 3:
                base += 1500
            elif duration > 1.5:
                base += 800
            
            origin = flight_data.get('origin', '').upper()
            destination = flight_data.get('destination', '').upper()
            
            # if 'CEB' in origin or 'CEB' in destination:
            #     base += 500
            # if 'MNL' in origin or 'MNL' in destination:
            #     base += 300
                
            return base
        except Exception as e:
            logger.error(f"Fallback price calculation failed: {e}", exc_info=True)
            return 2500 # Ensure a baseline price is always returned
    
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
        except Exception as e:
            logger.warning(f"Error calculating user factor: {e}")
        
        return 1.0
    
    def get_session_factor(self, session_id, flight_data, is_search=False):
        """Different prices for each browsing session"""
        if not session_id:
            return 1.0
        
        hash_input = f"{session_id}_{flight_data.get('flight_number', '')}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        factor = 0.98 + (hash_value % 5) / 100
        
        try:
            from django.core.cache import cache
            flight_num = str(flight_data.get('flight_number', '')).replace(' ', '_')
            cache_key = f"session_flight_{session_id}_{flight_num}"
            
            try:
                if is_search:
                    visit_count = cache.incr(cache_key)
                else:
                    visit_count = cache.get(cache_key)
                    if visit_count is None:
                        visit_count = 1
            except ValueError:
                if is_search:
                    cache.set(cache_key, 1, 3600)
                visit_count = 1
                
            # If visited multiple times, increase the price slightly to create urgency
            if visit_count > 1:
                factor *= (1 + (min(visit_count - 1, 5) * 0.01))
                
        except Exception as e:
            logger.warning(f"Error tracking session views: {e}")
        
        return factor
    
    def get_demand_factor(self, flight_data):
        """Real-time demand pricing based on config"""
        config = self.get_config()
        factor = 1.0
        
        try:
            from django.core.cache import cache
            flight_num = str(flight_data.get('flight_number', '')).replace(' ', '_')
            flight_key = f"flight_demand_{flight_num}"
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
        except Exception as e:
            logger.warning(f"Error fetching demand from cache: {e}")
        
        try:
            departure = self._parse_departure(flight_data)
            if departure is None:
                return factor
                
            days_until = max((departure - timezone.now()).total_seconds() / 86400, 0)
            
            # Continuous Booking Curve (exponential decay)
            # Simulates real-world airline pricing where every single day closer to departure increases the price.
            import math
            
            # Use the config's "critical" factor to scale how aggressive the daily surge gets
            max_surge = 2.80 # default +280% (Allows prices to hit 7k-9k easily on a 2500 base)
            if config and hasattr(config, 'days_factor_critical'):
                config_surge = float(config.days_factor_critical) - 1.0
                max_surge = max(config_surge * 4.0, 1.50)
                
            if days_until <= 30:
                # Math: e^(-0.10 * days) creates a beautifully sharp increase in the last 14 days
                curve = 1.0 + max_surge * math.exp(-0.10 * days_until)
            elif days_until <= 60:
                # Moderate increase between 30 and 60 days
                curve = 1.0 + (max_surge * 0.15) * (1 - (days_until - 30) / 30)
            else:
                # Early bird discount — drops significantly the further out (up to 40% off)
                curve = 0.95 - 0.35 * min((days_until - 60) / 120, 1.0)
                
            factor *= curve
        except Exception as e:
            logger.warning(f"Error calculating days-to-departure curve: {e}")
        
        return factor
    
    def _parse_departure(self, flight_data):
        """Parse departure_time from flight_data into a datetime matching project's TZ setting."""
        departure = flight_data.get('departure_time')
        if departure is None:
            return None
            
        if isinstance(departure, str):
            import dateutil.parser
            try:
                departure = dateutil.parser.isoparse(departure)
            except (ValueError, TypeError):
                return None
                
        # Synchronize awareness with Django settings to avoid subtraction errors
        from django.conf import settings
        if getattr(settings, 'USE_TZ', False):
            if timezone.is_naive(departure):
                departure = timezone.make_aware(departure)
        else:
            if timezone.is_aware(departure):
                departure = timezone.make_naive(departure)
                
        return departure

    def _date_in_range(self, d, sm, sd, em, ed):
        """Check if a date falls within a (month, day) range. Handles year wrap (Dec→Jan)."""
        year = d.year
        try:
            start = date(year, sm, sd)
            end = date(year, em, ed)
        except ValueError:
            return False
        if start <= end:
            return start <= d <= end
        else:
            # Wraps across year boundary (e.g. Dec 20 – Jan 5)
            return d >= start or d <= end

    def get_time_factor(self, flight_data):
        """
        Time-based pricing using the 2026 Philippine Holiday Calendar.
        Checks: peak hours, weekends, national holidays, and academic breaks.
        """
        config = self.get_config()
        factor = 1.0
        
        try:
            departure = self._parse_departure(flight_data)
            if departure is None:
                return factor
            
            dep_date = departure.date()

            # ── Peak Hours ──
            if config:
                if 7 <= departure.hour <= 9 or 17 <= departure.hour <= 19:
                    factor *= float(config.peak_hour_factor)
                if departure.weekday() >= 5:
                    factor *= float(config.weekend_factor)
            else:
                if 7 <= departure.hour <= 9 or 17 <= departure.hour <= 19:
                    factor *= 1.12
                if departure.weekday() >= 5:
                    factor *= 1.08

            # ── National Holiday Peaks ──
            # Find the highest matching holiday multiplier (don't stack them)
            best_holiday_mult = 1.0
            best_holiday_name = None
            for sm, sd, em, ed, mult, label in PH_HOLIDAY_PEAKS:
                if self._date_in_range(dep_date, sm, sd, em, ed):
                    if mult > best_holiday_mult:
                        best_holiday_mult = mult
                        best_holiday_name = label
            
            if best_holiday_mult > 1.0:
                if config and hasattr(config, 'holiday_factor'):
                    # Use config multiplier scaled by the calendar intensity
                    # e.g. Christmas (1.60) is stronger than a 3-day weekend (1.20)
                    intensity = (best_holiday_mult - 1.0) / 0.60  # 0.0 to 1.0 scale
                    config_mult = float(config.holiday_factor)
                    factor *= 1.0 + (config_mult - 1.0) * max(intensity, 0.5)
                else:
                    factor *= best_holiday_mult
                logger.debug(f"Holiday surge: {best_holiday_name} x{best_holiday_mult}")

            # ── Academic Break Spikes ──
            for sm, sd, em, ed, mult, label in PH_ACADEMIC_BREAKS:
                if self._date_in_range(dep_date, sm, sd, em, ed):
                    # Only apply if no stronger holiday is already active
                    if best_holiday_mult < mult:
                        factor *= mult
                        logger.debug(f"Academic break surge: {label} x{mult}")
                    break  # Only match the first academic break

        except Exception as e:
            logger.warning(f"Error calculating time factors: {e}")
        
        return factor
    
    def get_festival_factor(self, flight_data):
        """
        Route-specific festival surge pricing.
        Only applies if the flight origin or destination matches a festival city.
        """
        factor = 1.0
        try:
            departure = self._parse_departure(flight_data)
            if departure is None:
                return factor
            
            dep_date = departure.date()
            origin = flight_data.get('origin', '').upper()
            destination = flight_data.get('destination', '').upper()
            
            best_fest_mult = 1.0
            best_fest_name = None
            
            for sm, sd, em, ed, airports, mult, label in PH_FESTIVAL_SURGES:
                if self._date_in_range(dep_date, sm, sd, em, ed):
                    # Check if origin or destination matches a festival airport
                    if any(code in origin or code in destination for code in airports):
                        if mult > best_fest_mult:
                            best_fest_mult = mult
                            best_fest_name = label
            
            if best_fest_mult > 1.0:
                factor *= best_fest_mult
                logger.debug(f"Festival surge: {best_fest_name} x{best_fest_mult}")
                
        except Exception as e:
            logger.warning(f"Error calculating festival factor: {e}")
        
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
                        # Fallback heuristic
                        if occupancy_rate > 0.90:
                            return 1.80 # 80% markup for strictly last few seats
                        elif occupancy_rate > 0.8:
                            return 1.45 # 45% markup for almost full
                        elif occupancy_rate > 0.6:
                            return 1.20
                        elif occupancy_rate < 0.2:
                            return 0.70 # Empty floor, 30% discount
        except Exception as e:
            logger.warning(f"Error parsing occupancy config or state: {e}")
        
        return 1.0
    
    def get_randomization_factor(self, session_id, flight_data=None):
        """Add small randomization to prevent price matching"""
        flight_number = flight_data.get('flight_number', '') if flight_data else ''
        
        if not session_id:
            # Fully random for anonymous
            return 1.0 + (random.random() * 0.04 - 0.02)
        
        # Include flight_number so that prices fluctuate per-flight organically, not globally
        hash_input = f"random_{session_id}_{flight_number}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        return 0.98 + (hash_value % 5) / 100
    

    def round_price(self, price):
        """
        Return the exact price as integer without psychological rounding
        """
        if price <= 0:
            return 0
            
        return int(round(price))

    def round_seat_class_price(self, price):
        """
        Return the exact price as integer without special rounding
        """
        if price <= 0:
            return 0
            
        return int(round(price))

# Singleton instance
dynamic_pricing = DynamicPricingService()

