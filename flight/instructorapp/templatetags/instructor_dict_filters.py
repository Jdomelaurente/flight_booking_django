from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.filter
def get_addon_by_id(addon_list, addon_id):
    if not addon_list:
        return None
    for addon in addon_list:
        if addon['addon_id'] == addon_id:
            return addon
    return None