import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def clean_stat_value(value):
    """Converts string stat values to floats or ints, handling '-' and empty strings."""
    if value is None or value == "" or value == "-":
        return 0.0
    
    # Remove any non-numeric characters except decimal and negative sign
    clean_val = re.sub(r'[^\d\.-]', '', str(value))
    
    try:
        if '.' in clean_val:
            return float(clean_val)
        return int(clean_val)
    except ValueError:
        return 0.0

def normalize_date(date_str):
    """Converts various date formats (e.g., 'Feb 15', '2/15/26') to ISO format."""
    if not date_str:
        return None
        
    current_year = datetime.now().year
    
    formats = [
        "%b %d, %Y", # Feb 15, 2026
        "%b %d",     # Feb 15 (assume current year)
        "%m/%d/%y",  # 2/15/26
        "%m/%d/%Y",  # 02/15/2026
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if fmt == "%b %d":
                dt = dt.replace(year=current_year)
            return dt.date().isoformat()
        except ValueError:
            continue
            
    return date_str # Return as is if unknown

def calculate_batting_avg(h, ab):
    """Helper to ensure accurate batting average calculation if missing."""
    if ab == 0:
        return 0.000
    return round(h / ab, 3)

def sanitize_player_name(name):
    """Normalizes player names for fuzzy matching."""
    if not name:
        return ""
    # Remove suffixes, extra spaces, and special characters
    name = name.lower()
    name = re.sub(r'\s+', ' ', name).strip()
    name = re.sub(r'[^a-z\s-]', '', name)
    return name
