"""
Base44 Integration Module.
Handles sending scraped stats to Base44 platform via API/Webhook.
"""

import requests
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Base44 API Configuration
# Set these environment variables or update directly:
BASE44_API_URL = os.getenv('BASE44_API_URL', 'https://your-base44-app.com/api/player-stats')
BASE44_API_KEY = os.getenv('BASE44_API_KEY', 'YOUR_API_KEY_HERE')


def send_to_base44(stats_data, player_info):
    """
    Send player stats to Base44 via API webhook.
    
    Args:
        stats_data (dict): Scraped stats data from scraper
        player_info (dict): Player metadata (name, number, school, etc.)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Prepare payload
        payload = {
            "player": {
                "name": player_info['name'],
                "number": player_info['number'],
                "school": player_info['school'],
                "sport": player_info.get('sport', 'baseball')
            },
            "stats": stats_data,
            "last_updated": datetime.utcnow().isoformat(),
            "season": "2026"
        }
        
        # Send to Base44 API
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {BASE44_API_KEY}'
        }
        
        response = requests.post(
            BASE44_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        
        logger.info(f"Successfully sent stats for {player_info['name']} to Base44")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Failed to send to Base44: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in Base44 integration: {str(e)}")
        return False


def save_to_json_fallback(stats_data, player_info):
    """
    Fallback: Save stats to JSON file if API fails.
    Useful for debugging or as backup.
    
    Args:
        stats_data (dict): Scraped stats data
        player_info (dict): Player metadata
    """
    try:
        filename = f"output/{player_info['name'].replace(' ', '_')}_{player_info['school']}.json"
        
        os.makedirs('output', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump({
                "player": player_info,
                "stats": stats_data,
                "timestamp": datetime.utcnow().isoformat()
            }, f, indent=2)
        
        logger.info(f"Saved fallback JSON to {filename}")
        
    except Exception as e:
        logger.error(f"Failed to save fallback JSON: {str(e)}")


def send_batch_to_base44(players_stats):
    """
    Send multiple players' stats in a single batch request.
    More efficient for multiple players.
    
    Args:
        players_stats (list): List of (stats_data, player_info) tuples
    
    Returns:
        int: Number of successful updates
    """
    try:
        batch_payload = []
        
        for stats_data, player_info in players_stats:
            batch_payload.append({
                "player": {
                    "name": player_info['name'],
                    "number": player_info['number'],
                    "school": player_info['school'],
                    "sport": player_info.get('sport', 'baseball')
                },
                "stats": stats_data,
                "last_updated": datetime.utcnow().isoformat()
            })
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {BASE44_API_KEY}'
        }
        
        response = requests.post(
            f"{BASE44_API_URL}/batch",
            json={"players": batch_payload},
            headers=headers,
            timeout=60
        )
        
        response.raise_for_status()
        
        logger.info(f"Successfully sent batch of {len(batch_payload)} players to Base44")
        return len(batch_payload)
        
    except requests.RequestException as e:
        logger.error(f"Failed to send batch to Base44: {str(e)}")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error in batch update: {str(e)}")
        return 0
