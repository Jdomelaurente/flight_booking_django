from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get a dictionary item by key in templates"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
