"""
Main API for Base44 integration.
This is the primary function Base44 will call.
"""
import json
import logging
from datetime import datetime
from .find_player_url import find_player_url
from .parse_game_log import scrape_game_log
from .config import DEFAULT_SEASON
from .schools_database import get_school_info
from .error_handler import log_error, ScraperError
from .data_cleaner import clean_stat_value, normalize_date

logger = logging.getLogger(__name__)

def get_player_stats(player_name, jersey_number, school, season=DEFAULT_SEASON, sport="baseball"):
    """
    Complete workflow: Find player and scrape their stats.
    This is the main function Base44 should call.
    """
    
    # Step 0: Normalize school
    school_info = get_school_info(school)
    school_name = school_info['name'] if school_info else school
    
    logger.info(f"=== Scraping Stats for {player_name} #{jersey_number} ({school_name} {sport}) ===")
    
    # Step 1: Find player URL
    try:
        player_url, platform_type = find_player_url(player_name, jersey_number, school_name, sport)
    except Exception as e:
        err = ScraperError(f"Player search failed: {str(e)}", school=school_name)
        log_error(err)
        return {
            "error": str(err),
            "player_name": player_name,
            "jersey_number": jersey_number,
            "school": school_name,
            "sport": sport,
            "success": False
        }
    
    # Step 2: Scrape game log
    try:
        raw_games = scrape_game_log(player_url, season)
        
        # Step 2.5: Clean game stats
        cleaned_games = []
        for game in raw_games:
            cleaned_game = {}
            for k, v in game.items():
                if k == 'date':
                    cleaned_game[k] = normalize_date(v)
                elif k in ['ab', 'r', 'h', 'rbi', 'bb', 'k', 'hr', '2b', '3b', 'sb', 'cs', 'hbp', 'sh', 'sf', 'avg', 'obp', 'slg', 'ops', 'ip', 'er', 'bb', 'k', 'era']:
                    cleaned_game[k] = clean_stat_value(v)
                else:
                    cleaned_game[k] = v
            cleaned_games.append(cleaned_game)
            
    except Exception as e:
        err = ScraperError(f"Scrape failed: {str(e)}", school=school_name, url=player_url)
        log_error(err)
        return {
            "error": f"Failed to scrape game log: {str(e)}",
            "player_name": player_name,
            "jersey_number": jersey_number,
            "school": school_name,
            "sport": sport,
            "player_url": player_url,
            "success": False
        }
    
    # Step 3: Return structured data
    result = {
        "player_name": player_name,
        "jersey_number": str(jersey_number),
        "school": school_name,
        "season": season,
        "sport": sport,
        "player_url": player_url,
        "games_count": len(cleaned_games),
        "games": cleaned_games,
        "success": True,
        "last_updated": datetime.now().isoformat()
    }
    
    logger.info(f"✓ Successfully scraped {len(cleaned_games)} games for {player_name}")
    
    return result

def get_player_stats_json(player_name, jersey_number, school, season=DEFAULT_SEASON, sport="baseball"):
    """
    Same as get_player_stats but returns JSON string instead of dict.
    Useful for APIs that expect JSON response.
    """
    result = get_player_stats(player_name, jersey_number, school, season, sport)
    return json.dumps(result, indent=2, default=str)
