"""
Utility functions for data cleaning and processing.
"""

import re
from datetime import datetime
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters.
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()


def parse_date(date_str: str) -> str:
    """
    Parse date string into ISO format (YYYY-MM-DD).
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        ISO formatted date string or original if parsing fails
    """
    if not date_str:
        return ""
    
    date_str = clean_text(date_str)
    
    # Common date formats in college sports websites
    formats = [
        '%m/%d/%Y',      # 03/04/2025
        '%m/%d/%y',      # 03/04/25
        '%m-%d-%Y',      # 03-04-2025
        '%Y-%m-%d',      # 2025-03-04
        '%b %d, %Y',     # Mar 04, 2025
        '%B %d, %Y',     # March 04, 2025
        '%m.%d.%Y',      # 03.04.2025
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # If no format matches, return original
    return date_str


def extract_home_away(opponent: str, result: str = "") -> str:
    """
    Determine if game is home or away based on opponent string.
    
    Args:
        opponent: Opponent string (may contain @ or vs)
        result: Result string (alternative source for home/away)
        
    Returns:
        "home", "away", or "neutral"
    """
    text = (opponent + " " + result).lower()
    
    if '@' in text or 'at ' in text:
        return "away"
    elif 'vs' in text or 'vs.' in text:
        return "home"
    else:
        return "neutral"


def safe_int(value: str, default: Optional[int] = None) -> Optional[int]:
    """
    Safely convert string to integer.
    
    Args:
        value: String value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer or default value
    """
    if not value:
        return default
    
    try:
        # Remove common non-numeric characters
        cleaned = re.sub(r'[^0-9.-]', '', str(value))
        return int(float(cleaned)) if cleaned else default
    except (ValueError, TypeError):
        return default
