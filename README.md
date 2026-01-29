# College Baseball Stats Scraper

A Python-based web scraper for college baseball team statistics. Designed for easy extension to multiple teams with minimal coding required.

## Features

- Scrapes game-by-game stats from college baseball team websites
- Currently supports Sidearm Sports website structure
- Outputs clean CSV and JSON files
- Easy configuration for adding new teams
- Built for non-coders to extend

## Project Structure

```
college-baseball-scraper/
  README.md
  requirements.txt
  .gitignore
  scraper/
    __init__.py
    config.py          # Team URLs and selectors
    fetch_html.py      # HTTP request handling
    parse_sidearm.py   # Sidearm Sports parser
    run_scraper.py     # Main CLI script
    utils.py           # Helper functions
  output/
    (generated CSV/JSON files)
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/mckales/college-baseball-scraper.git
cd college-baseball-scraper
```

### 2. Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Running the Scraper

To scrape stats for a team:

```bash
python -m scraper.run_scraper example_team
```

This will create two files in the `output/` folder:
- `example_team_games.csv`
- `example_team_games.json`

### Adding a New Team

1. Open `scraper/config.py`
2. Add a new entry to the `TEAMS` dictionary:

```python
TEAMS = {
    "example_team": {
        "name": "Example Team",
        "stats_url": "https://example.com/sports/baseball/stats/2025",
        "table_selector": {"class": "sidearm-table"},
        "type": "sidearm"
    },
    "my_new_team": {  # Add your new team here
        "name": "My New Team",
        "stats_url": "https://mynewteam.com/sports/baseball/stats/2025",
        "table_selector": {"class": "sidearm-table"},
        "type": "sidearm"
    }
}
```

3. Run the scraper with your new team key:

```bash
python -m scraper.run_scraper my_new_team
```

## Output Format

The scraper extracts the following fields from each game:

- `date`: Game date
- `opponent`: Opposing team name
- `home_or_away`: "home" or "away" (derived from vs/@ indicators)
- `result`: Win/Loss and score (e.g., "W, 5-3")
- `ab`: At-bats
- `h`: Hits
- `r`: Runs
- `rbi`: Runs batted in
- `bb`: Walks
- `k`: Strikeouts
- `tb`: Total bases
- `player_name`: Player name (if available)
- `jersey_number`: Player number (if available)

**Note:** Fields may vary based on the specific team website structure. Missing data is represented as `None` or empty strings.

## Customizing Selectors

If a team's website has a different table structure:

1. Open the team's stats page in your browser
2. Right-click the stats table and select "Inspect"
3. Find the table element and note its class or id
4. Update the `table_selector` in `config.py`:

```python
"table_selector": {"class": "your-table-class"}  # or
"table_selector": {"id": "your-table-id"}
```

## Troubleshooting

### "Team not found" Error

Make sure the team key you're using matches exactly what's in `config.py`.

### "Failed to fetch" Error

The website may be down or blocking automated requests. Try accessing the URL in your browser first.

### Empty Output Files

The table selector may be incorrect. Inspect the website HTML and update `table_selector` in `config.py`.

### Missing Data in Output

Some columns may not be present on all team websites. The scraper will skip missing columns gracefully.

## Future Enhancements

- Support for additional website platforms (Presto Sports, PrestoSports, etc.)
- Pitcher-specific stats parsing
- Season summary statistics
- Automated scheduling for regular updates

## Requirements

- Python 3.8 or higher
- Internet connection
- See `requirements.txt` for Python package dependencies

## License

MIT License - feel free to use and modify for your projects.

## Support

For issues or questions, please open an issue on GitHub.
