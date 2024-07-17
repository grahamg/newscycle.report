from django import template

register = template.Library()

@register.filter(name='truncate_long_words')
def truncate_long_words(value, max_length=10):
    """
    Truncate words in the string that are longer than max_length characters.
    """
    words = value.split()
    truncated_words = [word if len(word) <= max_length else word[:max_length] + '...' for word in words]
    return ' '.join(truncated_words)
