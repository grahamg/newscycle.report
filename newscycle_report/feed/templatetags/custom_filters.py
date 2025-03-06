import re
from django import template
from django.utils.html import mark_safe

register = template.Library()

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
