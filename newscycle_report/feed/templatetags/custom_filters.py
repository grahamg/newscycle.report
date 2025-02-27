from django import template
import html

register = template.Library()

@register.filter(name="truncate_long_words")
def truncate_long_words(value, max_length=10):
    """
    Truncate words in the string that are longer than max_length characters.
    """
    words = value.split()
    truncated_words = [word if len(word) <= max_length else word[:max_length] + "..." for word in words]
    return " ".join(truncated_words)

@register.filter(name="decode_html_entities")
def decode_html_entities(value):
    """
    Decode HTML entities in the given string.
    """
    if value:
        return html.unescape(value)
    return value

