from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtract the argument from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except:
            return 0

@register.filter
def filter_by_type(passengers, passenger_type):
    """Filter passengers by type"""
    if not passengers:
        return []
    return [p for p in passengers if p.get('type', '').lower() == passenger_type.lower()]

@register.filter
def filter_met(requirements, met_status):
    """Filter requirements by met status"""
    if not requirements:
        return []
    return [req for req in requirements if req.get('met') == met_status]

@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        # Handle both single values and lists
        if hasattr(value, '__len__') and not isinstance(value, str):
            value = len(value)
        if hasattr(arg, '__len__') and not isinstance(arg, str):
            arg = len(arg)
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def replace(value, arg):
    """Replace characters in string"""
    if not value or not arg:
        return value
    try:
        old, new = arg.split(',')
        return value.replace(old, new)
    except (ValueError, AttributeError):
        return value

@register.filter
def first(value):
    """Get first item from iterable"""
    try:
        if hasattr(value, 'items'):
            return next(iter(value.items()))
        elif hasattr(value, '__getitem__'):
            return value[0] if value else None
        else:
            return None
    except (StopIteration, IndexError, TypeError):
        return None

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None

@register.filter
def count_met_requirements(requirements):
    """Count how many requirements were met"""
    if not requirements:
        return 0
    return len([req for req in requirements if req.get('met')])

@register.filter
def calculate_percentage(met_count, total_count):
    """Calculate percentage"""
    try:
        if hasattr(met_count, '__len__') and not isinstance(met_count, str):
            met_count = len(met_count)
        if hasattr(total_count, '__len__') and not isinstance(total_count, str):
            total_count = len(total_count)
        return (float(met_count) / float(total_count)) * 100
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
    
@register.filter
def is_passenger_complete(passenger):
    """Check if passenger has complete information"""
    if not passenger:
        return False
    
    required_fields = ['name', 'date_of_birth', 'gender']
    for field in required_fields:
        if not passenger.get(field):
            return False
    
    # Check if date of birth is valid
    dob = passenger.get('date_of_birth')
    if dob and hasattr(dob, 'year'):  # It's a date object
        return True
    elif dob and isinstance(dob, str) and len(dob) > 0:  # It's a string
        return True
    
    return False

@register.filter
def filter_complete_passengers(passengers):
    """Filter only complete passengers"""
    if not passengers:
        return []
    return [p for p in passengers if p|is_passenger_complete]

@register.filter
def filter_incomplete_passengers(passengers):
    """Filter only incomplete passengers"""
    if not passengers:
        return []
    return [p for p in passengers if not p|is_passenger_complete]    


@register.filter
def percentage(value):
    """Convert decimal to percentage (e.g., 0.20 -> 20%)"""
    try:
        return f"{float(value) * 100:.0f}%"
    except (ValueError, TypeError):
        return "0%"

@register.filter
def percentage_one_decimal(value):
    """Convert decimal to percentage with one decimal (e.g., 0.205 -> 20.5%)"""
    try:
        return f"{float(value) * 100:.1f}%"
    except (ValueError, TypeError):
        return "0.0%"

@register.filter
def floatvalue(value):
    """Convert to float for calculations"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

@register.filter
def calculate_category_percentage(earned, possible):
    """Calculate percentage for a specific category"""
    try:
        if possible == 0:
            return 0.0
        return (float(earned) / float(possible)) * 100
    except (ValueError, TypeError):
        return 0.0