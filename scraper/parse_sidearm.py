"""
Parser for Sidearm Sports websites.

Extracts game-by-game statistics from HTML tables.
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from .utils import clean_text, parse_date, extract_home_away


def parse_game_stats(html: str, table_selector: Dict) -> List[Dict]:
    """
    Parse game statistics from Sidearm Sports HTML.
    
    Args:
        html: HTML content as string
        table_selector: Dictionary with CSS selector info (e.g., {"class": "sidearm-table"})
        
    Returns:
        List of dictionaries, each representing a game with stats
    """
    soup = BeautifulSoup(html, 'lxml')
    games = []
    
    # Find the stats table
    table = soup.find('table', table_selector)
    
    if not table:
        print("Warning: Could not find stats table with selector:", table_selector)
        return games
    
    # Find header row to map column names
    headers = []
    header_row = table.find('thead')
    if header_row:
        headers = [clean_text(th.get_text()) for th in header_row.find_all('th')]
    else:
        # Try first row if no thead
        first_row = table.find('tr')
        if first_row:
            headers = [clean_text(th.get_text()) for th in first_row.find_all(['th', 'td'])]
    
    if not headers:
        print("Warning: Could not find table headers")
        return games
    
    print(f"Found headers: {headers}")
    
    # Create column index mapping
    col_map = create_column_mapping(headers)
    
    # Find data rows (skip header rows)
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
    else:
        rows = table.find_all('tr')[1:]  # Skip first row if no tbody
    
    print(f"Found {len(rows)} data rows")
    
    # Parse each row
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) < 2:
            continue  # Skip empty or invalid rows
        
        game_data = parse_row(cells, col_map)
        
        # Only add if we got meaningful data
        if game_data and (game_data.get('opponent') or game_data.get('date')):
            games.append(game_data)
    
    print(f"Successfully parsed {len(games)} games")
    return games


def create_column_mapping(headers: List[str]) -> Dict[str, int]:
    """
    Map common stat abbreviations to column indices.
    
    Args:
        headers: List of column header names
        
    Returns:
        Dictionary mapping stat names to column indices
    """
    col_map = {}
    
    # Common mappings (case-insensitive)
    mappings = {
        'date': ['date', 'dt'],
        'opponent': ['opponent', 'opp', 'vs'],
        'result': ['result', 'score', 'w/l'],
        'ab': ['ab', 'at-bats'],
        'h': ['h', 'hits'],
        'r': ['r', 'runs'],
        'rbi': ['rbi', "rbi's"],
        'bb': ['bb', 'walks'],
        'k': ['k', 'so', 'strikeouts'],
        'tb': ['tb', 'total bases'],
        'player': ['player', 'name'],
        'number': ['#', 'no', 'num', 'jersey'],
        # Pitching stats
        'ip': ['ip', 'innings'],
        'h_allowed': ['h', 'hits allowed'],
        'er': ['er', 'earned runs'],
    }
    
    for idx, header in enumerate(headers):
        header_lower = header.lower().strip()
        
        for key, variants in mappings.items():
            if header_lower in variants or any(v in header_lower for v in variants):
                col_map[key] = idx
                break
    
    return col_map


def parse_row(cells: List, col_map: Dict[str, int]) -> Optional[Dict]:
    """
    Parse a single table row into a game data dictionary.
    
    Args:
        cells: List of BeautifulSoup cell elements
        col_map: Column name to index mapping
        
    Returns:
        Dictionary with game stats or None if invalid
    """
    def get_cell(key: str, default="") -> str:
        """Safely get cell value by key."""
        idx = col_map.get(key)
        if idx is not None and idx < len(cells):
            return clean_text(cells[idx].get_text())
        return default
    
    def get_int(key: str) -> Optional[int]:
        """Get integer value from cell."""
        value = get_cell(key)
        try:
            return int(value) if value else None
        except ValueError:
            return None
    
    # Extract basic game info
    date_raw = get_cell('date')
    opponent = get_cell('opponent')
    result = get_cell('result')
    
    # Parse date
    date_str = parse_date(date_raw)
    
    # Determine home/away
    home_or_away = extract_home_away(opponent, result)
    
    # Build game data dictionary
    game_data = {
        'date': date_str,
        'opponent': opponent.replace('@', '').replace('vs', '').strip(),
        'home_or_away': home_or_away,
        'result': result,
        'ab': get_int('ab'),
        'h': get_int('h'),
        'r': get_int('r'),
        'rbi': get_int('rbi'),
        'bb': get_int('bb'),
        'k': get_int('k'),
        'tb': get_int('tb'),
        'player_name': get_cell('player'),
        'jersey_number': get_cell('number'),
    }
    
    return game_data
