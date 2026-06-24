from datetime import date, timedelta

class PhilippineCalendar:
    """
    Helper for Philippine-specific pricing factors like holidays and festivals.
    """
    
    @staticmethod
    def get_holiday_impact(target_date):
        """
        Returns a dictionary of holiday impacts for a specific date.
        """
        holiday_name = None
        is_fiesta = False
        is_long_weekend = False
        is_payday = False
        impact_score = 0
        
        # Hardcoded 2025 Holidays & Festivals (for demonstration/testing)
        # In production, this would use a more robust holiday database
        holidays_2025 = {
            (1, 1): "New Year's Day",
            (1, 15): "Sinulog Festival",
            (2, 25): "EDSA Revolution Anniversary",
            (4, 9): "Araw ng Kagitingan",
            (4, 17): "Maundy Thursday",
            (4, 18): "Good Friday",
            (5, 1): "Labor Day",
            (6, 12): "Independence Day",
            (8, 21): "Ninoy Aquino Day",
            (8, 25): "National Heroes Day",
            (11, 1): "All Saints' Day",
            (11, 2): "All Souls' Day",
            (11, 30): "Bonifacio Day",
            (12, 8): "Feast of the Immaculate Conception",
            (12, 24): "Christmas Eve",
            (12, 25): "Christmas Day",
            (12, 30): "Rizal Day",
            (12, 31): "New Year's Eve",
        }
        
        month_day = (target_date.month, target_date.day)
        
        if month_day in holidays_2025:
            holiday_name = holidays_2025[month_day]
            impact_score = 0.3  # Base impact for holiday
            
            if "Sinulog" in holiday_name:
                is_fiesta = True
                impact_score = 0.5
            
            if "Christmas" in holiday_name or "New Year" in holiday_name:
                impact_score = 0.6
        
        # Long Weekend Check (Friday/Monday/Holiday proximity)
        # Simplified: check for Sat/Sun/Mon/Fri
        is_weekend = target_date.weekday() >= 4 # Fri, Sat, Sun
        if is_weekend:
            is_long_weekend = True
            impact_score = max(impact_score, 0.2)
            
        # Payday Check (15th and 30th/31st)
        if target_date.day in [14, 15, 16, 29, 30, 31]:
            is_payday = True
            impact_score = max(impact_score, 0.15)
            
        return {
            'holiday_name': holiday_name,
            'is_fiesta': is_fiesta,
            'is_long_weekend': is_long_weekend,
            'is_payday': is_payday,
            'impact_score': impact_score
        }

    @staticmethod
    def get_route_fiesta_factor(origin, destination, target_date):
        """
        Returns a pricing multiplier based on route-specific festival impact.
        """
        impact = PhilippineCalendar.get_holiday_impact(target_date)
        factor = 1.0
        
        if impact['is_fiesta']:
            # Example: Sinulog impact for Cebu flights
            if destination == 'CEB' or origin == 'CEB':
                factor = 1.5
        
        return factor
