"""
HTML fetching module.

Handles HTTP requests to retrieve webpage content.
"""

import requests
from .config import USER_AGENT, REQUEST_TIMEOUT


def fetch_html(url: str) -> str:
    """
    Fetch HTML content from a URL.
    
    Args:
        url: The URL to fetch
        
    Returns:
        HTML content as a string
        
    Raises:
        Exception: If the request fails or returns non-200 status
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        # Check for successful response
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch page. Status code: {response.status_code}. "
                f"URL: {url}"
            )
        
        print(f"Successfully fetched {len(response.text)} characters")
        return response.text
        
    except requests.exceptions.Timeout:
        raise Exception(f"Request timed out after {REQUEST_TIMEOUT} seconds. URL: {url}")
    
    except requests.exceptions.ConnectionError:
        raise Exception(f"Connection error. Please check your internet connection. URL: {url}")
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}. URL: {url}")
