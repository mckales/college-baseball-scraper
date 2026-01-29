"""
Find a player's individual page URL by searching the team roster.
Supports multiple platforms: SIDEARM, PrestoSports, NCAA.com, and generic sites.
"""

import requests
from bs4 import BeautifulSoup
from .config import SCHOOLS, get_platform_selectors, detect_platform
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
        tuple: (player_url, platform_type) or (None, None) if not found
    
    Raises:
        ValueError: If school not found in config or player not found on roster
    """
    # Get school configuration
    school_config = SCHOOLS.get(school)
    if not school_config:
        raise ValueError(f"School '{school}' not found in configuration. Available schools: {list(SCHOOLS.keys())}")
    
    roster_url = school_config["roster_url"]
    platform_type = school_config.get("type", "generic")
    
    # Auto-detect platform if not specified
    if platform_type == "generic":
        platform_type = detect_platform(school_config["domain"])
    
    # Get platform-specific selectors
    selectors = get_platform_selectors(platform_type)
    
    # Fetch the roster page
    try:
        response = requests.get(roster_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch roster from {roster_url}: {str(e)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Normalize inputs
    normalized_player = normalize_name(player_name)
    jersey_str = str(jersey_number).strip()
    
    # Find all player cards/rows on the roster
    player_cards = soup.select(selectors["roster_card"])
    
    if not player_cards:
        raise ValueError(f"No players found on roster page {roster_url}. Check platform selectors for '{platform_type}'.")
    
    # Search for the player
    for card in player_cards:
        # Extract player name
        name_elem = card.select_one(selectors["player_name"])
        if not name_elem:
            continue
        
        card_name = normalize_name(name_elem.get_text())
        
        # Extract jersey number
        number_elem = card.select_one(selectors["player_number"])
        card_number = number_elem.get_text().strip() if number_elem else ""
        
        # Match by name AND number for accuracy
        name_match = normalized_player in card_name or card_name in normalized_player
        number_match = jersey_str == card_number
        
        if name_match and number_match:
            # Find the player's profile link
            link_elem = card.select_one(selectors["player_link"])
            if not link_elem:
                link_elem = card.find_parent('a') or card.find('a')
            
            if link_elem and link_elem.get('href'):
                player_url = link_elem['href']
                
                # Make URL absolute if it's relative
                if player_url.startswith('/'):
                    base_url = f"https://{school_config['domain']}"
                    player_url = base_url + player_url
                elif not player_url.startswith('http'):
                    player_url = roster_url.rsplit('/', 1)[0] + '/' + player_url
                
                return player_url, platform_type
    
    # Player not found
    raise ValueError(
        f"Player '{player_name}' (#{jersey_number}) not found on {school} roster. "
        f"Found {len(player_cards)} players on page. Check spelling and number."
    )
