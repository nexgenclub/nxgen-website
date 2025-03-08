from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def sub(value, arg):
    return value - arg

# templatetags/custom_filters.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def add_class(field, css_class):
    """Add a CSS class to a Django form field."""
    return field.as_widget(attrs={"class": css_class})

@register.filter
def div(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def sub(value, arg):
    """Subtract the argument from the value."""
    try:
        return int(value) - int(arg)
    except ValueError:
        return 0