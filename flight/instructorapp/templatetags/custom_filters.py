# instructorapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []

@register.filter
def get_addon_by_id(addon_list, addon_id):
    """Get addon from list by id"""
    if not addon_list:
        return None
    
    # Convert addon_id to string for comparison if needed
    addon_id_str = str(addon_id)
    
    for addon in addon_list:
        # Check if addon is a dictionary with 'addon_id' key
        if isinstance(addon, dict) and str(addon.get('addon_id')) == addon_id_str:
            return addon
    return None