from django import template
from django.template.defaultfilters import slugify

register = template.Library()

@register.filter(name='slugify_string')
def slugify_filter(value):
    return slugify(value)