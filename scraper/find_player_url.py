"""
Find a player's individual page URL by searching the team roster.
"""

import requests
from bs4 import BeautifulSoup
from .config import SCHOOLS
import re


def normalize_name(name):
    """Normalize player name for matching (lowercase, remove extra spaces)."""
    return re.sub(r'\s+', ' ', name.lower().strip())


def find_player_url(player_name, jersey_number, school):
    """
    Find a player's individual page URL from the roster.
    
    Args:
        player_name (str): Player's full name (e.g., "Charlie Davis")
        jersey_number (str or int): Jersey number (e.g., "8" or 8)
        school (str): School name (e.g., "Belmont")
    
    Returns:
        str: Full URL to player's individual page
        
    Raises:
        ValueError: If school not found in config or player not found on roster
    """
    
    # Validate school
    if school not in SCHOOLS:
        raise ValueError(f"School '{school}' not found in config. Available schools: {list(SCHOOLS.keys())}")
    
    school_config = SCHOOLS[school]
    roster_url = school_config["roster_url"]
    
    print(f"Searching for {player_name} #{jersey_number} at {school}...")
    print(f"Roster URL: {roster_url}")
    
    # Fetch roster page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(roster_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch roster page: {e}")
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Normalize search terms
    normalized_name = normalize_name(player_name)
    jersey_str = str(jersey_number).strip()
    
    # Find all player links on roster
    # Sidearm sites typically have roster items with player links
    player_links = soup.find_all('a', href=re.compile(r'/sports/baseball/roster/'))
    
    print(f"Found {len(player_links)} players on roster")
    
    # Search through players
    for link in player_links:
        link_text = link.get_text(strip=True)
        link_normalized = normalize_name(link_text)
        
        # Check if name matches
        name_match = normalized_name in link_normalized or link_normalized in normalized_name
        
        # Try to find jersey number near this link
        parent = link.find_parent(['li', 'div', 'tr'])
        if parent:
            parent_text = parent.get_text()
            number_match = jersey_str in parent_text or f"#{jersey_str}" in parent_text
        else:
            number_match = False
        
        # If name matches (and optionally number matches), return URL
        if name_match:
            if number_match or not jersey_number:  # Number match or no number provided
                player_path = link.get('href')
                
                # Build full URL
                if player_path.startswith('http'):
                    full_url = player_path
                else:
                    full_url = f"https://{school_config['domain']}{player_path}"
                
                print(f"✓ Found player: {full_url}")
                return full_url
    
    # If we get here, player wasn't found
    raise ValueError(
        f"Could not find player '{player_name}' #{jersey_number} on {school} roster. "
        "Check spelling and make sure player is on current roster."
    )
