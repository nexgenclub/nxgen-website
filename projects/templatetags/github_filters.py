from django import template
import re

register = template.Library()


@register.filter
def github_username(github_link):
    """
    Extracts the GitHub username from a given repository link.
    Example: "https://github.com/nexgenclub/nxgen-website" → "nexgenclub"
    """
    match = re.match(r"https?://github\.com/([^/]+)", github_link)
    return match.group(1) if match else None


@register.filter
def github_profile(github_link):
    """Extracts the GitHub profile URL from a given repository link."""
    match = re.match(r"https?://github\.com/([^/]+)", github_link)
    return f"https://github.com/{match.group(1)}" if match else github_link


@register.filter
def github_repo_details(github_link):
    """
    Extracts the GitHub owner and repository name from the URL.
    Example: "https://github.com/nexgenclub/nxgen-website" → "nexgenclub / nxgen-website"
    """
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)", github_link)
    return f"{match.group(1)}" if match else "Unknown Repository"
