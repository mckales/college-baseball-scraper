"""
Configuration for college baseball scraper.
Maps school names to their website domains and roster URLs.
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

# Default season to scrape
DEFAULT_SEASON = "2026"

# Selenium settings
SELENIUM_HEADLESS = True  # Set to False to see browser during scraping
SELENIUM_TIMEOUT = 10  # Seconds to wait for elements to load
