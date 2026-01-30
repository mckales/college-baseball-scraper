import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

PLATFORMS = {
    'sidearm': ['sidearmsports.com', 'sidearmstats.com', 'asics.com'],
    'presto': ['prestosports.com', 'presto-stats.com'],
    'genius': ['geniussports.com', 'ncaa.org'],
    'statbroadcast': ['statbroadcast.com'],
    'ncaa': ['ncaa.com', 'ncaa.org'],
    'stretch': ['stretchinternet.com', 'hudl.com'],
    'wmt': ['wmt.digital'],
    'revel': ['revelxp.com'],
    'd3sports': ['d3baseball.com', 'd3sports.com']
}

def detect_platform(url, html=None):
    """
    Detects the athletic platform (Sidearm, Presto, etc.) for a given school URL.
    This is crucial for reaching a 99% success rate across D1, D2, and D3.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    # Check domain patterns
    for platform, patterns in PLATFORMS.items():
        if any(pattern in domain for pattern in patterns):
            return platform
    
    # Check HTML markers if available (more reliable for white-labeled domains)
    if html:
        html_lower = html.lower()
        if 'sidearm sports' in html_lower or 'sidearmstats' in html_lower:
            return 'sidearm'
        if 'prestosports' in html_lower or 'presto stats' in html_lower:
            return 'presto'
        if 'genius sports' in html_lower:
            return 'genius'
        if 'wmt digital' in html_lower:
            return 'wmt'
        if 'stretch internet' in html_lower:
            return 'stretch'
        if 'statbroadcast' in html_lower:
            return 'statbroadcast'
    
    # Check URL path patterns
    path = parsed_url.path.lower()
    if '/sidearmstats/' in path:
        return 'sidearm'
    if '/stats/' in path and 'ncaa' in domain:
        return 'ncaa'
            
    # Default to generic if unknown
    return 'generic'

def get_base_url(url):
    """Extracts base URL (e.g., https://belmontbruins.com)"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
