from django import template
import re

register = template.Library()

@register.filter
def youtube_id(url):
    """
    Extract the YouTube video ID from a YouTube URL.
    Supports both youtube.com and youtu.be URLs.
    """
    if not url:
        return None
        
    # Regular expressions for different YouTube URL formats
    youtube_regex = (
        r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)'
        r'([^"&?\/\s]{11})'
    )
    
    match = re.search(youtube_regex, url)
    if match:
        return match.group(1)
    return None 