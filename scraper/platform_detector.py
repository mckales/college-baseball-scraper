import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

PLATFORMS = {
    'sidearm': ['sidearmsports.com', 'sidearmstats.com'],
    'presto': ['prestosports.com'],
    'genius': ['geniussports.com'],
    'statbroadcast': ['statbroadcast.com'],
    'ncaa': ['ncaa.com', 'ncaa.org']
}

def detect_platform(url, html=None):
    """
    Detects the athletic platform (Sidearm, Presto, etc.) for a given school URL.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    # Check domain patterns
    for platform, patterns in PLATFORMS.items():
        if any(pattern in domain for pattern in patterns):
            return platform
            
    # Check HTML markers if available
    if html:
        html_lower = html.lower()
        if 'sidearm sports' in html_lower:
            return 'sidearm'
        if 'prestosports' in html_lower:
            return 'presto'
        if 'genius sports' in html_lower:
            return 'genius'
            
    # Default to generic/manual if unknown
    return 'generic'

def get_base_url(url):
    """Extracts base URL (e.g., https://belmontbruins.com)"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
