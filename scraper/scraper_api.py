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


async def get_team_games_by_date(team_schedule_url, target_dates=None, sport="baseball"):
    """
    Get all games from a team's schedule and optionally filter by date.
    Returns box score URLs and game data.
    
    Args:
        team_schedule_url: URL to team's schedule page
        target_dates: List of date strings to filter (optional, None = all games)
        sport: Sport type (baseball/softball)
    
    Returns:
        List of game dictionaries with dates and box score URLs
    """
    import aiohttp
    from .schedule_scraper import scrape_team_schedule
    from .box_score_scraper import scrape_box_score
    from datetime import datetime
    
    logger.info(f"=== Fetching Schedule: {team_schedule_url} ===")
    
    async with aiohttp.ClientSession() as session:
        # 1. Get schedule with box score URLs
        games = await scrape_team_schedule(session, team_schedule_url)
        
        if not games:
            return {"error": "No games found on schedule", "success": False}
        
        # 2. Filter by date if specified
        if target_dates:
            filtered_games = []
            for game in games:
                game_date = game.get('date', '')
                # Simple date matching (can be enhanced)
                if any(target in game_date for target in target_dates):
                    filtered_games.append(game)
            games = filtered_games
        
        # 3. Optionally fetch box score data for each game
        enriched_games = []
        for game in games:
            box_url = game.get('box_score_url')
            if box_url:
                box_data = await scrape_box_score(session, box_url)
                game['box_score_data'] = box_data
            enriched_games.append(game)
        
        return {
            "team_url": team_schedule_url,
            "sport": sport,
            "games": enriched_games,
            "total_games": len(enriched_games),
            "success": True
        }
