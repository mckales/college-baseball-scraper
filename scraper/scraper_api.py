"""
Main API for Base44 integration.
Universal stat extraction for all NCAA divisions.
"""
import json
import logging
from datetime import datetime
from .find_player_url import find_player_url
from .parse_game_log import scrape_game_log
from .config import DEFAULT_SEASON
from .schools_database import get_school_config
from .error_handler import log_error, ScraperError
from .data_cleaner import clean_stat_value, normalize_date

logger = logging.getLogger(__name__)

def get_player_stats(player_name, jersey_number, school, season=DEFAULT_SEASON, sport="baseball"):
    """
    Scrapes stats for ANY player from ANY NCAA school.
    """
    # 1. Dynamic School Config
    school_config = get_school_config(school, sport)
    school_name = school_config.get('name', school)
    
    logger.info(f"=== Universal Scrape: {player_name} ({school_name}) ===")
    
    # 2. Find Player URL (Works for all schools now)
    try:
        player_url, platform_type = find_player_url(player_name, jersey_number, school, sport)
    except Exception as e:
        return {"error": f"Player find failed: {str(e)}", "success": False}
        
    # 3. Scrape Game Log (Universal Table Extractor)
    try:
        raw_games = scrape_game_log(player_url, season, platform_type)
        
        # Data Normalization for Base44
        cleaned_games = []
        for game in raw_games:
            cleaned = {k: (clean_stat_value(v) if k != 'date' else normalize_date(v)) for k, v in game.items()}
            cleaned_games.append(cleaned)
            
        return {
            "player_name": player_name,
            "school": school_name,
            "sport": sport,
            "games": cleaned_games,
            "success": True,
            "player_url": player_url
        }
    except Exception as e:
        return {"error": f"Stat extraction failed: {str(e)}", "success": False}
