from django import template
import re

register = template.Library()

@register.filter
def github_username(github_link):
    """
    Extracts the GitHub username from a given repository link.
    Example: "https://github.com/nexgenclub/nxgen-website" → "nexgenclub"
    """
    match = re.match(r'https?://github\.com/([^/]+)', github_link)
    return match.group(1) if match else None
