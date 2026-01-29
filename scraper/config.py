"""
Configuration for college baseball/softball scraper.Maps school names to their website domains and roster URLs.
Supports multiple platforms: SIDEARM, PrestoSports, NCAA.com, and more.
"""

SCHOOLS = {
    "Belmont": {
        "domain": "belmontbruins.com",
        "roster_url": "https://belmontbruins.com/sports/baseball/roster",
        "type": "sidearm"
    },
    "Tennessee": {
        "domain": "utsports.com",
        "roster_url": "https://utsports.com/sports/baseball/roster",
        "type": "sidearm"
    },
    "Vanderbilt": {
        "domain": "vucommodores.com",
        "roster_url": "https://vucommodores.com/sports/baseball/roster",
        "type": "sidearm"
    },
    "Lipscomb": {
        "domain": "lipscombsports.com",
        "roster_url": "https://lipscombsports.com/sports/baseball/roster",
        "type": "sidearm"
    },
    # Add more schools as needed - all Sidearm Sports sites follow same structure
}

# Platform-specific selectors for different website types
PLATFORM_SELECTORS = {
    "sidearm": {
        "roster_card": "div.sidearm-roster-player",
        "player_name": ".sidearm-roster-player-name",
        "player_number": ".sidearm-roster-player-jersey-number",
        "player_link": "a.sidearm-roster-player-link",
        "stats_tab": "a[href*='#sidearm-roster-player-stats']",
        "season_dropdown": "select, .season-select",
        "stats_table": "table",
        "game_log_headers": ["Date", "Opponent", "W/L", "GS", "AB", "R", "H", "RBI", "2B", "3B", "HR", "BB", "IBB", "SB", "SBA", "CS", "HBP", "SH", "SF"],
    },
    "prestosports": {
        "roster_card": "div.player_card, tr.roster_row",
        "player_name": ".player_name, td.player-name",
        "player_number": ".jersey_number, td.jersey",
        "player_link": "a[href*='/player/']",
        "stats_tab": "a[href*='stats'], #stats-tab",
        "season_dropdown": "select#season",
        "stats_table": "table.stats_table",
        "game_log_headers": ["Date", "Opponent", "Result", "AB", "R", "H", "RBI", "2B", "3B", "HR", "BB", "SO", "SB"],
    },
    "ncaa": {
        "roster_card": "div.roster-player",
        "player_name": ".player-name",
        "player_number": ".jersey-number",
        "player_link": "a.player-link",
        "stats_tab": "button[data-tab='stats']",
        "season_dropdown": "select.season-select",
        "stats_table": "table.stats-table",
        "game_log_headers": ["Date", "Opponent", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO"],
    },
    "generic": {
        # Fallback selectors that work across many sites
        "roster_card": "div[class*='player'], div[class*='roster'], tr[class*='player']",
        "player_name": "[class*='name'], h3, h4, strong",
        "player_number": "[class*='number'], [class*='jersey']",
        "player_link": "a[href*='player'], a[href*='roster']",
        "stats_tab": "a[href*='stats'], button[data-tab*='stats'], #stats",
        "season_dropdown": "select",
        "stats_table": "table",
        "game_log_headers": ["Date", "Opponent", "AB", "R", "H", "RBI", "2B", "3B", "HR"],
    }
}

# Auto-detect platform based on domain patterns
PLATFORM_DOMAINS = {
    "sidearm": ["sidearmdev", "sidearmsports", ".com"],  # Most college sites use SIDEARM
    "prestosports": ["prestosports.com", "prestosports"],
    "ncaa": ["ncaa.com"],
}

def detect_platform(domain):
    """
    Auto-detect which platform a website uses based on domain.
    Returns platform type or 'generic' if unknown.
    """
    domain_lower = domain.lower()
    
    for platform, patterns in PLATFORM_DOMAINS.items():
        for pattern in patterns:
            if pattern in domain_lower:
                return platform
    
    return "generic"

def get_school_config(school_name):
    """
    Get configuration for a specific school.
    Returns school config dict or None if not found.
    """
    return SCHOOLS.get(school_name)

def get_platform_selectors(platform_type):
    """
    Get CSS selectors for a specific platform.
    Returns selector dict.
    """
    return PLATFORM_SELECTORS.get(platform_type, PLATFORM_SELECTORS["generic"])


def get_roster_url(school_name, sport="baseball"):
    """
    Get roster URL for a specific school and sport.
    
    Args:
        school_name (str): School name (e.g., "Belmont")
        sport (str): Sport name ("baseball" or "softball")
    
    Returns:
        str: Full roster URL
    """
    school_config = SCHOOLS.get(school_name)
    if not school_config:
        raise ValueError(f"School '{school_name}' not found in configuration. Available schools: {list(SCHOOLS.keys())}")
    
    # Default to baseball if sport not recognized
    sport_path = sport.lower() if sport.lower() in ["baseball", "softball"] else "baseball"
    domain = school_config["domain"]
    
    return f"https://{domain}/sports/{sport_path}/roster"
