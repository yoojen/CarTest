# your_app/templatetags/custom_filters.py

from django import template

register = template.Library()


@register.filter
def is_error(tags):
    return tags == 'error'

@register.filter
def is_success(tags):
    return tags=='success'