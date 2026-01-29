"""
Base44 Integration Module.
Fetches player list from Base44, scrapes stats, and pushes results back to Base44.
"""
import json
import logging
import os
from datetime import datetime

import requests

from scraper.scraper_api import get_player_stats

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


def fetch_players_from_base44():
    """
    Fetch the list of players to scrape from Base44.

    Returns:
        list: List of player dictionaries with id, name, number, school, season
    """
    try:
        headers = {
            "x-api-key": BASE44_API_KEY
        }

        response = requests.get(
            PLAYERS_ENDPOINT,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        players = response.json()

        if not isinstance(players, list):
            logger.error(f"Expected list of players, got: {type(players).__name__}")
            return []

        logger.info(f"Fetched {len(players)} players from Base44")
        return players

    except requests.Timeout as e:
        logger.error(f"Timeout fetching players from Base44: {e}")
        return []
    except requests.RequestException as e:
        logger.error(f"HTTP error fetching players from Base44: {e}")
        resp = getattr(e, "response", None)
        if resp is not None:
            logger.error(f"Response status: {resp.status_code}, body: {resp.text}")
        return []
    except ValueError as e:
        logger.error(f"Failed to parse JSON from Base44: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching players: {e}")
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
        payload = {
            "playerId": player["id"],
            "name": player["name"],
            "number": str(player["number"]),
            "school": player["school"],
            "season": str(player.get("season", "2026")),
            "games": stats_result.get("games", []),
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": BASE44_API_KEY,
        }

        response = requests.post(
            STATS_WEBHOOK,
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        logger.info(
            f"Successfully pushed stats for {player['name']} "
            f"(ID: {player['id']}) to Base44"
        )
        return True

    except requests.RequestException as e:
        logger.error(
            f"Failed to push stats to Base44 for {player.get('name', 'unknown')}: {e}"
        )
        resp = getattr(e, "response", None)
        if resp is not None:
            body = resp.text
            if len(body) > 1000:
                body = body[:1000] + "... [truncated]"
            logger.error(f"Response status: {resp.status_code}, body: {body}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error pushing stats: {e}")
        return False


def save_to_json_fallback(player, stats_result):
    """
    Fallback: Save stats to JSON file if API fails.
    Useful for debugging or as backup.

    Args:
        player (dict): Player metadata
        stats_result (dict): Scraped stats result
    """
    try:
        safe_name = player.get("name", "unknown").replace(" ", "_")
        safe_school = player.get("school", "unknown").replace(" ", "_")
        filename = f"output/{safe_name}_{safe_school}.json"

        os.makedirs("output", exist_ok=True)

        with open(filename, "w") as f:
            json.dump(
                {
                    "player": player,
                    "stats": stats_result,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                f,
                indent=2,
            )

        logger.info(f"Saved fallback JSON to {filename}")
    except Exception as e:
        logger.error(f"Failed to save fallback JSON: {e}")


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

    players = fetch_players_from_base44()

    if not players:
        logger.warning("No players to scrape")
        return {"success_count": 0, "error_count": 0, "total": 0}

    success_count = 0
    error_count = 0

    required_keys = {"id", "name", "number", "school"}

    for player in players:
        if not required_keys.issubset(player):
            logger.error(f"Skipping player with missing keys: {player}")
            error_count += 1
            continue

        try:
            logger.info(
                f"Scraping: {player['name']} #{player['number']} from "
                f"{player['school']} ({player.get('season', '2026')})"
            )

            result = get_player_stats            (
                player_name=player["name"],
                jersey_number=str(player["number"]),
                school=player["school"],
                season=str(player.get("season", "2026",
                sport=str(player.get("sport", "baseball")),

            if result and result.get("games"):
                if push_stats_to_base44(player, result):
                    success_count += 1
                else:
                    logger.warning(
                        f"API push failed, saving fallback JSON for {player['name']}"
                    )
                    save_to_json_fallback(player, result)
                    error_count += 1
            else:
                logger.warning(f"No stats found for {player['name']}")
                error_count += 1

        except Exception as e:
            logger.error(
                f"Error processing {player.get('name', 'unknown')}: {e}"
            )
            error_count += 1

    logger.info(
        f"Sync complete. Success: {success_count}, "
        f"Errors: {error_count}, Total: {len(players)}"
    )

    return {
        "success_count": success_count,
        "error_count": error_count,
        "total": len(players),
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    summary = run_sync()
    # Non-zero exit if there were errors (useful for cron / CI)
    if summary["error_count"] > 0:
        raise SystemExit(1)
