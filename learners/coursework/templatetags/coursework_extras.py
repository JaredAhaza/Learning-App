from django import template
import re

register = template.Library()

@register.filter
def get_video_embed_url(url):
    """
    Convert various video platform URLs to their embed URLs.
    Supports YouTube, Vimeo, TikTok, Facebook, Instagram, and other platforms.
    """
    if not url:
        return None
        
    # YouTube URLs
    youtube_regex = (
        r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)'
        r'([^"&?\/\s]{11})'
    )
    
    # Vimeo URLs
    vimeo_regex = r'(?:vimeo\.com\/)(\d+)'
    
    # TikTok URLs
    tiktok_regex = r'(?:tiktok\.com\/@[\w.-]+\/video\/)(\d+)'
    
    # Facebook URLs (both video and post)
    facebook_regex = r'(?:facebook\.com\/)(?:.*?\/videos\/|.*?\/posts\/|.*?\/)(\d+)'
    
    # Instagram URLs
    instagram_regex = r'(?:instagram\.com\/p\/)([\w-]+)'
    
    # Check for YouTube
    youtube_match = re.search(youtube_regex, url)
    if youtube_match:
        return f'https://www.youtube.com/embed/{youtube_match.group(1)}'
    
    # Check for Vimeo
    vimeo_match = re.search(vimeo_regex, url)
    if vimeo_match:
        return f'https://player.vimeo.com/video/{vimeo_match.group(1)}'
    
    # Check for TikTok
    tiktok_match = re.search(tiktok_regex, url)
    if tiktok_match:
        return f'https://www.tiktok.com/embed/v2/{tiktok_match.group(1)}'
    
    # Check for Facebook
    facebook_match = re.search(facebook_regex, url)
    if facebook_match:
        return f'https://www.facebook.com/plugins/video.php?href={url}&show_text=false'
    
    # Check for Instagram
    instagram_match = re.search(instagram_regex, url)
    if instagram_match:
        return f'https://www.instagram.com/p/{instagram_match.group(1)}/embed'
    
    # If the URL is already an embed URL, return it as is
    if 'embed' in url or 'player' in url:
        return url
        
    # For other platforms that use standard iframe embedding, return the URL as is
    return url

@register.filter
def get_video_platform(url):
    """
    Determine the video platform from the URL.
    """
    if not url:
        return None
        
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'vimeo.com' in url:
        return 'vimeo'
    elif 'tiktok.com' in url:
        return 'tiktok'
    elif 'facebook.com' in url:
        return 'facebook'
    elif 'instagram.com' in url:
        return 'instagram'
    else:
        return 'other'

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

@register.filter
def get_item(dictionary, key):
    """Template filter to get an item from a dictionary using a key."""
    return dictionary.get(key) 