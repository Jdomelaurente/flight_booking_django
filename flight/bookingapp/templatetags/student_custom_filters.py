# bookingapp/templatetags/custom_filters.py
from django import template
from django.template.defaultfilters import floatformat
from decimal import Decimal

register = template.Library()

@register.filter(name='get_item')
@register.filter(name='get_item_by_id')
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary and isinstance(dictionary, dict):
        # Try string key first
        str_key = str(key)
        if str_key in dictionary:
            return dictionary[str_key]
        # Try the key as-is
        elif key in dictionary:
            return dictionary[key]
    return None

@register.filter(name='get_list_item')
def get_list_item(dictionary, key):
    """Get item from dictionary by key, return empty list if not found"""
    if dictionary and isinstance(dictionary, dict):
        str_key = str(key)
        if str_key in dictionary:
            result = dictionary[str_key]
            return result if isinstance(result, list) else [result]
        elif key in dictionary:
            result = dictionary[key]
            return result if isinstance(result, list) else [result]
    return []

@register.filter
def format_currency(value):
    """Format decimal as currency"""
    try:
        if value is None:
            return "₱0.00"
        return f"₱{float(value):,.2f}"
    except (ValueError, TypeError):
        return f"₱{value}"

@register.filter
def is_in_list(value, the_list):
    """Check if a value is in a list"""
    try:
        if not the_list:
            return False
        str_value = str(value)
        # Handle list of strings
        if isinstance(the_list, list):
            return any(str(item) == str_value for item in the_list)
        # Handle string
        elif isinstance(the_list, str):
            return str_value == the_list
        return False
    except:
        return False

@register.filter
def intcomma_custom(value):
    """Custom integer comma formatter"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value

# ============================================================
# NEW FILTERS FOR BOOKING SUMMARY
# ============================================================

@register.filter
def list_total(value, field_name=None):
    """
    Calculate total of a list of dictionaries by field name or list of numbers.
    Usage: {{ passenger.selected_addons|list_total:'price' }}
           {{ numbers_list|list_total }}
    """
    try:
        if not value:
            return Decimal('0.00')
        
        total = Decimal('0.00')
        
        # If field_name is provided, sum that field from list of dicts
        if field_name:
            for item in value:
                # Handle dictionary items
                if isinstance(item, dict):
                    field_value = item.get(field_name)
                # Handle object items with attributes
                elif hasattr(item, field_name):
                    field_value = getattr(item, field_name)
                else:
                    field_value = None
                
                if field_value:
                    try:
                        total += Decimal(str(field_value))
                    except (ValueError, TypeError):
                        pass
        else:
            # If no field_name, assume value is a list of numbers
            for item in value:
                try:
                    total += Decimal(str(item))
                except (ValueError, TypeError):
                    pass
        
        return total
    except Exception as e:
        print(f"Error in list_total filter: {e}")
        return Decimal('0.00')

@register.filter
def select_attr(value, attr_name):
    """
    Select items from a list where attribute exists and is truthy.
    Usage: {{ passengers|select_attr:'selected_addons' }}
    """
    try:
        if not value:
            return []
        
        result = []
        for item in value:
            # Check if item is a dictionary
            if isinstance(item, dict):
                if item.get(attr_name):
                    result.append(item)
            # Check if item is an object
            elif hasattr(item, attr_name):
                attr_value = getattr(item, attr_name, None)
                if attr_value:
                    result.append(item)
        
        return result
    except:
        return []

@register.filter
def add_lists(value1, value2):
    """
    Add two lists together or add numbers.
    Usage: {{ list1|add_lists:list2 }}
           {{ value1|add_lists:value2 }}
    """
    try:
        # Handle lists
        if isinstance(value1, list) and isinstance(value2, list):
            return value1 + value2
        # Handle numbers
        else:
            return Decimal(str(value1 or 0)) + Decimal(str(value2 or 0))
    except:
        return value1 or 0

@register.filter
def get_length(value):
    """Get length of list, dictionary, or string"""
    try:
        if hasattr(value, '__len__'):
            return len(value)
        return 0
    except:
        return 0

@register.filter
def format_percentage(value, decimals=1):
    """Format decimal as percentage"""
    try:
        if value is None:
            return "0%"
        return f"{float(value)*100:.{decimals}f}%"
    except:
        return "0%"

@register.filter
def multiply(value, multiplier):
    """Multiply value by multiplier"""
    try:
        if value is None or multiplier is None:
            return Decimal('0.00')
        return Decimal(str(value)) * Decimal(str(multiplier))
    except:
        return Decimal('0.00')

@register.filter
def divide(value, divisor):
    """Divide value by divisor"""
    try:
        if value is None or divisor is None or Decimal(str(divisor)) == 0:
            return Decimal('0.00')
        return Decimal(str(value)) / Decimal(str(divisor))
    except:
        return Decimal('0.00')

@register.filter
def subtract(value, subtrahend):
    """Subtract subtrahend from value"""
    try:
        if value is None:
            value = Decimal('0.00')
        if subtrahend is None:
            subtrahend = Decimal('0.00')
        return Decimal(str(value)) - Decimal(str(subtrahend))
    except:
        return Decimal('0.00')

@register.filter
def calculate_tax_per_passenger(taxes, num_passengers):
    """Calculate tax per passenger"""
    try:
        if taxes is None or num_passengers is None or num_passengers == 0:
            return Decimal('0.00')
        return Decimal(str(taxes)) / Decimal(str(num_passengers))
    except:
        return Decimal('0.00')

@register.filter
def has_insurance(passenger):
    """Check if passenger has insurance add-ons"""
    try:
        if not passenger:
            return False
        
        # Handle dictionary passenger
        if isinstance(passenger, dict):
            addons = passenger.get('selected_addons', [])
            for addon in addons:
                # Check if addon has is_insurance attribute
                if isinstance(addon, dict) and addon.get('is_insurance'):
                    return True
                elif hasattr(addon, 'is_insurance') and addon.is_insurance:
                    return True
        
        # Handle object passenger
        elif hasattr(passenger, 'selected_addons'):
            for addon in passenger.selected_addons:
                if isinstance(addon, dict) and addon.get('is_insurance'):
                    return True
                elif hasattr(addon, 'is_insurance') and addon.is_insurance:
                    return True
        
        return False
    except:
        return False

@register.filter
def get_insurance_plan(passenger):
    """Get insurance plan from passenger's add-ons"""
    try:
        if not passenger:
            return None
        
        # Handle dictionary passenger
        if isinstance(passenger, dict):
            addons = passenger.get('selected_addons', [])
            for addon in addons:
                if isinstance(addon, dict) and addon.get('is_insurance'):
                    return addon.get('insurance_plan')
                elif hasattr(addon, 'is_insurance') and addon.is_insurance:
                    return getattr(addon, 'insurance_plan', None)
        
        # Handle object passenger
        elif hasattr(passenger, 'selected_addons'):
            for addon in passenger.selected_addons:
                if isinstance(addon, dict) and addon.get('is_insurance'):
                    return addon.get('insurance_plan')
                elif hasattr(addon, 'is_insurance') and addon.is_insurance:
                    return getattr(addon, 'insurance_plan', None)
        
        return None
    except:
        return None

@register.filter
def format_duration(minutes):
    """Format minutes as hours:minutes"""
    try:
        if minutes is None:
            return "0h 0m"
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return f"{hours}h {mins}m"
    except:
        return "0h 0m"

@register.filter
def get_seat_class_name(seat_class):
    """Get seat class name from seat class object or dict"""
    try:
        if not seat_class:
            return "Economy"
        
        if isinstance(seat_class, dict):
            return seat_class.get('name', 'Economy')
        elif hasattr(seat_class, 'name'):
            return seat_class.name
        
        return "Economy"
    except:
        return "Economy"

@register.filter
def calculate_addon_count(passengers):
    """Calculate total number of add-ons across all passengers"""
    try:
        if not passengers:
            return 0
        
        count = 0
        for passenger in passengers:
            if isinstance(passenger, dict):
                addons = passenger.get('selected_addons', [])
                count += len(addons)
            elif hasattr(passenger, 'selected_addons'):
                count += len(passenger.selected_addons)
        
        return count
    except:
        return 0

@register.filter
def calculate_addon_types(passengers):
    """Calculate number of unique add-on types"""
    try:
        if not passengers:
            return 0
        
        types = set()
        for passenger in passengers:
            if isinstance(passenger, dict):
                addons = passenger.get('selected_addons', [])
                for addon in addons:
                    if isinstance(addon, dict):
                        type_name = addon.get('type')
                    elif hasattr(addon, 'type'):
                        type_name = addon.type.name if addon.type else None
                    if type_name:
                        types.add(str(type_name))
            elif hasattr(passenger, 'selected_addons'):
                for addon in passenger.selected_addons:
                    if hasattr(addon, 'type') and addon.type:
                        types.add(str(addon.type.name))
        
        return len(types)
    except:
        return 0

@register.filter
def get_addon_types(passengers):
    """Get list of unique add-on types"""
    try:
        if not passengers:
            return []
        
        types = set()
        for passenger in passengers:
            if isinstance(passenger, dict):
                addons = passenger.get('selected_addons', [])
                for addon in addons:
                    if isinstance(addon, dict):
                        type_name = addon.get('type')
                    elif hasattr(addon, 'type'):
                        type_name = addon.type.name if addon.type else None
                    if type_name:
                        types.add(str(type_name))
            elif hasattr(passenger, 'selected_addons'):
                for addon in passenger.selected_addons:
                    if hasattr(addon, 'type') and addon.type:
                        types.add(str(addon.type.name))
        
        return sorted(list(types))
    except:
        return []

@register.filter
def get_addon_count_by_type(passengers, type_name):
    """Count add-ons of a specific type"""
    try:
        if not passengers or not type_name:
            return 0
        
        count = 0
        for passenger in passengers:
            if isinstance(passenger, dict):
                addons = passenger.get('selected_addons', [])
                for addon in addons:
                    if isinstance(addon, dict):
                        addon_type = addon.get('type')
                    elif hasattr(addon, 'type'):
                        addon_type = addon.type.name if addon.type else None
                    
                    if str(addon_type) == str(type_name):
                        count += 1
            elif hasattr(passenger, 'selected_addons'):
                for addon in passenger.selected_addons:
                    if hasattr(addon, 'type') and addon.type and str(addon.type.name) == str(type_name):
                        count += 1
        
        return count
    except:
        return 0

# Simple alias for template compatibility
@register.filter
def floatformat(value, decimal_places=2):
    """Simple float formatting filter"""
    try:
        return floatformat(value, decimal_places)
    except:
        return value