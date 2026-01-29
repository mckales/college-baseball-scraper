"""
Main API for Base44 integration.
This is the primary function Base44 will call.
"""

import json
from .find_player_url import find_player_url
from .parse_game_log import scrape_game_log
from .config import DEFAULT_SEASON


def get_player_stats(player_name, jersey_number, school, season=DEFAULT_SEASON):
    """
    Complete workflow: Find player and scrape their stats.
    This is the main function Base44 should call.
    
    Args:
        player_name (str): Player's full name (e.g., "Charlie Davis")
        jersey_number (str or int): Jersey number (e.g., "8")
        school (str): School name (e.g., "Belmont")
        season (str, optional): Season year (default: "2026")
    
    Returns:
        dict: Contains 'player_info' and 'games' list
        
    Example return:
        {
            "player_name": "Charlie Davis",
            "jersey_number": "8",
            "school": "Belmont",
            "season": "2026",
            "player_url": "https://belmontbruins.com/sports/baseball/roster/charlie-davis/4763",
            "games_count": 12,
            "games": [
                {
                    "date": "2/14/2026",
                    "opponent": "Georgia State",
                    "w_l": "L",
                    "ab": "4",
                    "r": "1",
                    "h": "2",
                    "rbi": "1",
                    ...
                },
                ...
            ]
        }
    """
    
    print(f"\n=== Scraping Stats for {player_name} #{jersey_number} ({school}) ===\n")
    
    # Step 1: Find player URL
    try:
        player_url = find_player_url(player_name, jersey_number, school)
    except ValueError as e:
        return {
            "error": str(e),
            "player_name": player_name,
            "jersey_number": jersey_number,
            "school": school
        }
    
    # Step 2: Scrape game log
    try:
        games = scrape_game_log(player_url, season)
    except Exception as e:
        return {
            "error": f"Failed to scrape game log: {str(e)}",
            "player_name": player_name,
            "jersey_number": jersey_number,
            "school": school,
            "player_url": player_url
        }
    
    # Step 3: Return structured data
    result = {
        "player_name": player_name,
        "jersey_number": str(jersey_number),
        "school": school,
        "season": season,
        "player_url": player_url,
        "games_count": len(games),
        "games": games
    }
    
    print(f"\n✓ Successfully scraped {len(games)} games for {player_name}")
    
    return result


def get_player_stats_json(player_name, jersey_number, school, season=DEFAULT_SEASON):
    """
    Same as get_player_stats but returns JSON string instead of dict.
    Useful for APIs that expect JSON response.
    """
    result = get_player_stats(player_name, jersey_number, school, season)
    return json.dumps(result, indent=2)
