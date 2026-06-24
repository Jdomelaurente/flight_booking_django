

# ============================================================
# PRICING CONFIGURATION
# ============================================================

@admin.register(PricingConfiguration)
class PricingConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for dynamic pricing configuration"""
    
    list_display = ('id', 'updated_at', 'anonymous_user_factor', 'loyal_user_factor')
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('User Factors', {
            'fields': (
                'anonymous_user_factor',
                'new_user_factor',
                'returning_user_factor',
                'loyal_user_factor',
            ),
            'description': 'Price multipliers based on user booking history'
        }),
        ('Demand Factors - Search Thresholds', {
            'fields': (
                'search_threshold_high',
                'search_threshold_medium',
                'search_threshold_low',
            ),
            'description': 'Search count thresholds for demand-based pricing'
        }),
        ('Demand Factors - Multipliers', {
            'fields': (
                'demand_factor_high',
                'demand_factor_medium',
                'demand_factor_low',
            ),
        }),
        ('Days Until Departure - Thresholds', {
            'fields': (
                'days_departure_critical',
                'days_departure_near',
                'days_departure_medium',
                'days_departure_far',
            ),
        }),
        ('Days Until Departure - Multipliers', {
            'fields': (
                'days_factor_critical',
                'days_factor_near',
                'days_factor_medium',
                'days_factor_far',
            ),
        }),
        ('Time-Based Factors', {
            'fields': (
                'peak_hour_factor',
                'weekend_factor',
                'peak_month_factor',
                'holiday_factor',
            ),
            'description': 'Multipliers for peak hours, weekends, and holidays'
        }),
        ('Inventory Factors - Occupancy Thresholds', {
            'fields': (
                'occupancy_high_threshold',
                'occupancy_medium_threshold',
                'occupancy_low_threshold',
            ),
        }),
        ('Inventory Factors - Multipliers', {
            'fields': (
                'occupancy_factor_high',
                'occupancy_factor_medium',
                'occupancy_factor_low',
            ),
        }),
        ('Metadata', {
            'fields': ('updated_at',),
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent creating multiple configurations (singleton pattern)"""
        return not PricingConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the configuration"""
        return False
