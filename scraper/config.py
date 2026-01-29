"""
Configuration file for team URLs and parsing settings.

To add a new team:
1. Add an entry to the TEAMS dictionary
2. Provide the team name, stats URL, and CSS selectors
3. Run: python -m scraper.run_scraper your_team_key
"""

TEAMS = {
    "example_team": {
        "name": "Example Team",
        # Replace with actual team stats URL
        "stats_url": "https://lsusports.net/sports/baseball/stats/2025",
        # CSS selector for the main stats table
        "table_selector": {"class": "sidearm-table"},
        # Type of website platform (for future multi-platform support)
        "type": "sidearm"
    },
    
    # Example: LSU Tigers
    "lsu": {
        "name": "LSU Tigers",
        "stats_url": "https://lsusports.net/sports/baseball/stats/2025",
        "table_selector": {"class": "sidearm-table"},
        "type": "sidearm"
    },
    
    # Add more teams here following the same pattern:
    # "team_key": {
    #     "name": "Team Name",
    #     "stats_url": "https://...",
    #     "table_selector": {"class": "..."},
    #     "type": "sidearm"
    # },
}

# User-Agent header for HTTP requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Request timeout in seconds
REQUEST_TIMEOUT = 30
