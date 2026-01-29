# College Baseball Stats Scraper

A Python scraper that extracts game-by-game statistics for individual college baseball players. Designed for integration with Base44 app.

## Features

- ✅ Find players by name, number, and school (no URLs needed)
- ✅ Scrapes individual player game logs from college websites  
- ✅ Handles JavaScript-heavy Sidearm Sports sites with Selenium
- ✅ Outputs clean CSV and JSON files
- ✅ Easy integration with Base44 backend
- ✅ Configurable for 2026 season (or any season)
- ✅ Easily extensible to add more schools

## Installation

```bash
git clone https://github.com/mckales/college-baseball-scraper.git
cd college-baseball-scraper
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Note: Selenium requires Chrome browser to be installed on your system.

## Quick Start

### Command Line Usage

```bash
# Basic usage
python -m scraper.run_scraper "Charlie Davis" 8 Belmont

# Specify season
python -m scraper.run_scraper "Charlie Davis" 8 Belmont 2025

# Output will be saved to output/ folder
```

### Python API Usage (For Base44 Integration)

See full README at the repository for complete Base44 integration guide, examples, and documentation for:
- Direct Python import
- Scheduled cron jobs  
- Adding more schools
- Output formats
- Troubleshooting

```python
from scraper import get_player_stats

# Get player stats
result = get_player_stats(
    player_name="Charlie Davis",
    jersey_number="8",
    school="Belmont",
    season="2026"  # Optional, defaults to 2026
)

# Use in Base44 backend to update player stats
for game in result['games']:
    # Update database with game stats
    pass
```

## Project Structure

```
college-baseball-scraper/
├── README.md
├── requirements.txt
├── scraper/
│   ├── __init__.py
│   ├── config.py              # School mappings & settings
│   ├── find_player_url.py     # Find player page from roster
│   ├── parse_game_log.py      # Selenium scraper for game logs
│   ├── scraper_api.py         # Main API for Base44
│   └── run_scraper.py         # CLI interface
└── output/                    # Generated CSV/JSON files
```

## Available Schools

- Belmont
- Tennessee
- Vanderbilt
- Lipscomb

*All Sidearm Sports websites follow the same structure, making it easy to add more schools via configuration!*
