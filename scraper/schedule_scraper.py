import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from .platform_detector import detect_platform
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

async def fetch_schedule(session, team_url):
    """Fetch the schedule page for a team."""
    try:
        async with session.get(team_url, timeout=15) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        logger.error(f"Error fetching schedule from {team_url}: {e}")
    return ""

def parse_schedule(html, platform, base_url):
    """Parse the schedule HTML based on the platform with universal fallback."""
    soup = BeautifulSoup(html, 'html.parser')
    games = []

    if platform == 'sidearm':
        # Sidearm specific parsing
        game_elements = soup.select('.sidearm-schedule-game')
        for element in game_elements:
            try:
                # Extract date
                date_el = element.select_one('.sidearm-schedule-game-opponent-date span')
                date_str = date_el.text.strip() if date_el else ""
                
                # Extract box score link
                box_link = element.find('a', text=lambda t: t and ('Box Score' in t or 'Stats' in t))
                if not box_link:
                    box_link = element.select_one('a[aria-label*="Box Score"], a[aria-label*="Stats"]')
                
                box_url = ""
                if box_link and box_link.get('href'):
                    box_url = urljoin(base_url, box_link['href'])
                
                if date_str:
                    games.append({'date': date_str, 'box_score_url': box_url})
            except Exception as e:
                continue

    elif platform == 'presto':
        # Presto specific parsing (often tables)
        rows = soup.select('tr.event-row, .schedule-game')
        for row in rows:
            try:
                date_el = row.select_one('.date, .event-date')
                date_str = date_el.text.strip() if date_el else ""
                
                box_link = row.find('a', text=lambda t: t and ('Box' in t or 'Stats' in t))
                box_url = urljoin(base_url, box_link['href']) if box_link and box_link.get('href') else ""
                
                if date_str:
                    games.append({'date': date_str, 'box_score_url': box_url})
            except:
                continue

    # Universal Fallback: Look for any table containing 'Date' and links with 'Box' or 'Stats'
    if not games:
        tables = soup.find_all('table')
        for table in tables:
            headers = [th.text.lower().strip() for th in table.find_all('th')]
            rows = table.find_all('tr')
            
            idx_map = {}
            for i, h in enumerate(headers):
                if 'date' in h: idx_map['date'] = i
                if 'opponent' in h: idx_map['opponent'] = i
            
            if 'date' in idx_map:
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) > max(idx_map.values(), default=-1):
                        date_str = cells[idx_map['date']].get_text(strip=True)
                        
                        box_link = row.find('a', text=lambda t: t and ('Box' in t or 'Stats' in t or 'Links' in t))
                        if not box_link:
                            # Try finding by href pattern
                            box_link = row.find('a', href=lambda h: h and ('box' in h.lower() or 'stats' in h.lower()))
                            
                        box_url = urljoin(base_url, box_link['href']) if box_link and box_link.get('href') else ""
                        
                        if date_str and len(date_str) > 3:
                            games.append({'date': date_str, 'box_score_url': box_url})
                if games: break

    return games

async def scrape_team_schedule(session, team_url):
    """Entry point for the schedule system."""
    html = await fetch_schedule(session, team_url)
    if not html: return []

    from urllib.parse import urlparse
    parsed = urlparse(team_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    platform = detect_platform(team_url, html)
    return parse_schedule(html, platform, base_url)
