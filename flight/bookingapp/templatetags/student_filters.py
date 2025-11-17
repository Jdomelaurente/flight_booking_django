from django import template

register = template.Library()

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