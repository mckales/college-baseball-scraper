"""
Base44 Integration Module.
Fetches player list from Base44, scrapes stats, and pushes results back to Base44.
"""
import json
import logging
import os
import asyncio
from datetime import datetime
import requests
import aiohttp
from scraper.scraper_api import get_player_stats
from scraper.error_handler import log_error
from scraper.schedule_scraper import scrape_team_schedule
from scraper.config import get_schedule_url

logger = logging.getLogger(__name__)

# Base44 API Configuration – require explicit env vars
BASE44_API_URL = os.getenv("BASE44_API_URL")
BASE44_API_KEY = os.getenv("BASE44_API_KEY")

if not BASE44_API_URL or not BASE44_API_KEY:
    raise RuntimeError("BASE44_API_URL and BASE44_API_KEY must be set in environment")

# Normalize URL (no trailing slash)
BASE44_API_URL = BASE44_API_URL.rstrip("/")

# API Endpoints
PLAYERS_ENDPOINT = f"{BASE44_API_URL}/api/getPlayersToScrape"
STATS_WEBHOOK = f"{BASE44_API_URL}/api/receivePlayerStats"
UPCOMING_GAMES_WEBHOOK = f"{BASE44_API_URL}/api/receiveUpcomingGames"

def fetch_players_from_base44():
    """Fetch the list of players to scrape from Base44."""
    try:
        headers = {"x-api-key": BASE44_API_KEY}
        response = requests.get(PLAYERS_ENDPOINT, headers=headers, timeout=30)
        response.raise_for_status()
        players = response.json()
        if not isinstance(players, list):
            logger.error(f"Expected list of players, got: {type(players).__name__}")
            return []
        logger.info(f"Fetched {len(players)} players from Base44")
        return players
    except Exception as e:
        logger.error(f"Error fetching players: {e}")
        return []

def push_stats_to_base44(player, stats_result):
    """Push scraped stats back to Base44 webhook."""
    try:
        payload = {
            "playerId": player["id"],
            "name": player["name"],
            "number": str(player["number"]),
            "school": stats_result.get("school", player["school"]),
            "season": str(player.get("season", "2026")),
            "sport": str(player.get("sport", "baseball")),
            "games": stats_result.get("games", []),
            "success": stats_result.get("success", True),
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }
        headers = {
            "Content-Type": "application/json",
            "x-api-key": BASE44_API_KEY,
        }
        response = requests.post(STATS_WEBHOOK, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully pushed stats for {player['name']} (ID: {player['id']})")
        return True
    except Exception as e:
        logger.error(f"Failed to push stats for {player.get('name', 'unknown')}: {e}")
        return False

def push_upcoming_games_to_base44(school_name, games):
    """Push upcoming games for a team to Base44."""
    try:
        payload = {
            "school": school_name,
            "upcomingGames": games,
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }
        headers = {
            "Content-Type": "application/json",
            "x-api-key": BASE44_API_KEY,
        }
        response = requests.post(UPCOMING_GAMES_WEBHOOK, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully pushed {len(games)} upcoming games for {school_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to push upcoming games for {school_name}: {e}")
        return False

async def process_player(player):
    """Async wrapper for get_player_stats and push."""
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: get_player_stats(
                player_name=player["name"],
                jersey_number=str(player["number"]),
                school=player["school"],
                season=str(player.get("season", "2026")),
                sport=str(player.get("sport", "baseball"))
            )
        )
        
        if result and (result.get("success") or result.get("games")):
            push_stats_to_base44(player, result)
            return True
        return False
    except Exception as e:
        logger.error(f"Error in process_player for {player.get('name')}: {e}")
        return False

async def sync_schedules(players):
    """Sync schedules for all unique schools in the player list."""
    schools = list(set(p["school"] for p in players))
    logger.info(f"Syncing schedules for {len(schools)} schools...")
    
    async with aiohttp.ClientSession() as session:
        for school in schools:
            schedule_url = get_schedule_url(school)
            if schedule_url:
                upcoming_games = await scrape_team_schedule(session, schedule_url)
                if upcoming_games:
                    push_upcoming_games_to_base44(school, upcoming_games)

async def run_sync_async(concurrency=5):
    """Main sync function with concurrency control."""
    logger.info("Starting Base44 sync...")
    players = fetch_players_from_base44()
    if not players:
        return
    
    # Sync upcoming games
    await sync_schedules(players)
    
    semaphore = asyncio.Semaphore(concurrency)
    
    async def sem_process(player):
        async with semaphore:
            return await process_player(player)
    
    tasks = [sem_process(p) for p in players]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(1 for r in results if r)
    logger.info(f"Sync complete. Success: {success_count}/{len(players)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    asyncio.run(run_sync_async())
