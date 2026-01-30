import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from .platform_detector import detect_platform

logger = logging.getLogger(__name__)

async def fetch_schedule(session, team_url):
    """Fetch the schedule page for a team."""
    async with session.get(team_url) as response:
        if response.status == 200:
            return await response.text()
        return ""

def parse_schedule(html, platform):
    """Parse the schedule HTML based on the platform."""
    soup = BeautifulSoup(html, 'html.parser')
    games = []
    
    if platform == 'sidearm':
        # Sidearm schedule parsing logic
        game_elements = soup.select('.sidearm-schedule-game')
        for element in game_elements:
            date_str = element.select_one('.sidearm-schedule-game-opponent-date span').text.strip()
            opponent = element.select_one('.sidearm-schedule-game-opponent-name a').text.strip()
            time_str = element.select_one('.sidearm-schedule-game-time span').text.strip()
            
            # Simplified date parsing
            try:
                game_date = datetime.strptime(f"{date_str} 2026", "%b %d %Y")
                games.append({
                    'date': game_date.strftime("%Y-%m-%d"),
                    'opponent': opponent,
                    'time': time_str
                })
            except:
                continue
                
    elif platform == 'presto':
        # Presto schedule parsing logic
        # ... implementation for presto ...
        pass
        
    return games

def get_upcoming_games(games, days=14):
    """Filter games within the next X days."""
    now = datetime.now()
    end_date = now + timedelta(days=days)
    
    upcoming = [
        game for game in games 
        if now.strftime("%Y-%m-%d") <= game['date'] <= end_date.strftime("%Y-%m-%d")
    ]
    return upcoming

async def scrape_team_schedule(session, team_url):
    """Main entry point to scrape a team's schedule."""
    html = await fetch_schedule(session, team_url)
    if not html:
        return []
        
    platform = detect_platform(team_url, html)
    games = parse_schedule(html, platform)
    return get_upcoming_games(games)
