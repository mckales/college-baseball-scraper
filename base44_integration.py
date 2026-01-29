"""
Base44 Integration Module.
Fetches player list from Base44, scrapes stats, and pushes results back to Base44.
"""

import requests
import json
import logging
import os
from datetime import datetime
from scraper.scraper_api import get_player_stats

logger = logging.getLogger(__name__)

# Base44 API Configuration
# Set these environment variables or update directly:
BASE44_API_URL = os.getenv('BASE44_API_URL', 'https://your-base44-app.com')
BASE44_API_KEY = os.getenv('BASE44_API_KEY', 'YOUR_API_KEY_HERE')

# API Endpoints
PLAYERS_ENDPOINT = f"{BASE44_API_URL}/api/getPlayersToScrape"
STATS_WEBHOOK = f"{BASE44_API_URL}/api/receivePlayerStats"


def fetch_players_from_base44():
    """
    Fetch the list of players to scrape from Base44.
    
    Returns:
        list: List of player dictionaries with id, name, number, school, season
    """
    try:
        headers = {
            'x-api-key': BASE44_API_KEY
        }
        
        response = requests.get(
            PLAYERS_ENDPOINT,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        players = response.json()
        
        logger.info(f"Fetched {len(players)} players from Base44")
        return players
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch players from Base44: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching players: {str(e)}")
        return []


def push_stats_to_base44(player, stats_result):
    """
    Push scraped stats back to Base44 webhook.
    
    Args:
        player (dict): Player metadata from Base44 (with id)
        stats_result (dict): Result from get_player_stats containing 'games' list
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Prepare payload matching Base44 webhook expectations
        payload = {
            "playerId": player['id'],
            "name": player['name'],
            "number": str(player['number']),
            "school": player['school'],
            "season": str(player.get('season', '2026')),
            "games": stats_result.get('games', []),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': BASE44_API_KEY
        }
        
        response = requests.post(
            STATS_WEBHOOK,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        
        logger.info(f"Successfully pushed stats for {player['name']} (ID: {player['id']}) to Base44")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Failed to push stats to Base44 for {player.get('name', 'unknown')}: {str(e)}")
        if hasattr(e.response, 'text'):
            logger.error(f"Response: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error pushing stats: {str(e)}")
        return False


def run_sync():
    """
    Main sync function:
    1. Fetch players from Base44
    2. Scrape stats for each player
    3. Push stats back to Base44
    
    Returns:
        dict: Summary with success_count, error_count, total
    """
    logger.info("Starting Base44 sync...")
    
    # Fetch players
    players = fetch_players_from_base44()
    
    if not players:
        logger.warning("No players to scrape")
        return {"success_count": 0, "error_count": 0, "total": 0}
    
    success_count = 0
    error_count = 0
    
    for player in players:
        try:
            logger.info(f"Scraping: {player['name']} #{player['number']} from {player['school']} ({player.get('season', '2026')})")
            
            # Call the scraper
            result = get_player_stats(
                player_name=player['name'],
                jersey_number=str(player['number']),
                school=player['school'],
                season=str(player.get('season', '2026'))
            )
            
            if result and result.get('games'):
                # Push to Base44
                if push_stats_to_base44(player, result):
                    success_count += 1
                else:
                    error_count += 1
            else:
                logger.warning(f"No stats found for {player['name']}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"Error processing {player.get('name', 'unknown')}: {str(e)}")
            error_count += 1
    
    logger.info(f"Sync complete. Success: {success_count}, Errors: {error_count}, Total: {len(players)}")
    
    return {
        "success_count": success_count,
        "error_count": error_count,
        "total": len(players)
    }


def save_to_json_fallback(player, stats_result):
    """
    Fallback: Save stats to JSON file if API fails.
    Useful for debugging or as backup.
    
    Args:
        player (dict): Player metadata
        stats_result (dict): Scraped stats result
    """
    try:
        filename = f"output/{player['name'].replace(' ', '_')}_{player['school']}.json"
        
        os.makedirs('output', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump({
                "player": player,
                "stats": stats_result,
                "timestamp": datetime.utcnow().isoformat()
            }, f, indent=2)
        
        logger.info(f"Saved fallback JSON to {filename}")
        
    except Exception as e:
        logger.error(f"Failed to save fallback JSON: {str(e)}")


if __name__ == "__main__":
    # For testing: run sync once
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    run_sync()
