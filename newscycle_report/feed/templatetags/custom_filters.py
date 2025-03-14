import re, html
from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter(name="decode_html_entities")
def decode_html_entities(value):
    """
    Decode HTML entities in the given string.
    """
    if value:
        return html.unescape(value)
    return value

@register.filter
def truncate_long_words(value, length):
    """Truncate words that are longer than the specified length."""
    words = value.split()
    result = []
    for word in words:
        if len(word) > length:
            result.append(word[:length] + "...")
        else:
            result.append(word)
    return " ".join(result)

@register.filter
def highlight_keywords(text, keywords_str):
    if not keywords_str:
        return text
        
    keywords = [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()]
    if not keywords:
        return text
    
    highlighted_text = text
    for keyword in keywords:
        pattern = re.compile(f'({re.escape(keyword)})', re.IGNORECASE)
        highlighted_text = pattern.sub(r'<span class="keyword-highlight">\1</span>', highlighted_text)
    
    return mark_safe(highlighted_text)
