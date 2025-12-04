# bookingapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return []

@register.filter
def get_item_str(dictionary, key):
    """Get item from dictionary by string key"""
    if dictionary and str(key) in dictionary:
        return dictionary[str(key)]
    return []