from django import template
from django.utils.safestring import mark_safe
import markdown
import bleach

register = template.Library()

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'code', 'blockquote',
    'hr', 'table', 'thead', 'tbody', 'th', 'tr', 'td', 'img'
]

ALLOWED_ATTRIBUTES = dict(bleach.sanitizer.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update({
    'img': ['src', 'alt', 'title', 'width', 'height', 'class'],
    'a': ['href', 'title', 'target', 'rel'],
    'code': ['class'],
    'pre': ['class'],
    'th': ['scope', 'colspan', 'rowspan', 'align'],
    'td': ['colspan', 'rowspan', 'align'],
})

@register.filter(name='markdown_to_html')
def markdown_to_html(text):
    """Convert markdown to safe HTML"""
    if not text:
        return ""
    
    # Convert markdown to HTML
    html = markdown.markdown(
        text,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.toc',
            'markdown.extensions.codehilite',
        ]
    )
    
    # Clean and sanitize HTML
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return mark_safe(clean_html)

@register.filter(name='truncate_content')
def truncate_content(text, length=100):
    """Truncate text to a specified length"""
    if not text:
        return ""
    
    if len(text) <= length:
        return text
    
    truncated = text[:length].rsplit(' ', 1)[0]
    return truncated + '...'
