from django import template

register = template.Library()

@register.filter
def times(number):
    """Return a list of integers from 0 to number - 1"""
    return range(number)