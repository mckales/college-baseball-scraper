import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from .platform_detector import detect_platform
from .data_cleaner import clean_stat_value

logger = logging.getLogger(__name__)

async def fetch_box_score(session, box_url):
    """Fetch box score HTML from a URL."""
    try:
        async with session.get(box_url, timeout=15) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        logger.error(f"Error fetching box score from {box_url}: {e}")
    return ""

def parse_box_score(html, platform):
    """Universal box score parser - extracts player stats tables."""
    soup = BeautifulSoup(html, 'html.parser')
    teams_data = []

    if platform == 'sidearm':
        # Sidearm box scores typically use specific classes
        tables = soup.select('table.sidearm-table, table.box-score-table')
    elif platform == 'presto':
        # Presto uses standard table structures
        tables = soup.select('table.stats-table, table.linescore')
    else:
        # Universal fallback: find all tables
        tables = soup.find_all('table')

    for table in tables:
        # Check if this table contains player stats
        headers = [th.text.strip().lower() for th in table.find_all('th')]
        
        # Look for common stat headers
        if any(header in headers for header in ['player', 'name', 'ab', 'r', 'h', 'rbi']):
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    player_data = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            key = headers[i]
                            value = clean_stat_value(cell.text.strip())
                            player_data[key] = value
                    
                    if player_data:
                        teams_data.append(player_data)

    return teams_data

async def scrape_box_score(session, box_url):
    """Main entry point for box score scraping."""
    html = await fetch_box_score(session, box_url)
    if not html:
        return []

    platform = detect_platform(box_url, html)
    return parse_box_score(html, platform)
