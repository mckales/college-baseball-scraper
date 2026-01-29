"""
College Baseball Scraper
Scrapes individual player game logs from college baseball team websites.
"""

from .scraper_api import get_player_stats, get_player_stats_json
from .config import SCHOOLS, DEFAULT_SEASON

__version__ = "2.0.0"
__all__ = ["get_player_stats", "get_player_stats_json", "SCHOOLS", "DEFAULT_SEASON"]
