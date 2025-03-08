from django import template

register = template.Library()

@register.filter
def split_techs(value):
    """Splits a comma-separated string and removes extra spaces."""
    if not value:
        return []
    return [tech.strip() for tech in value.split(",")]