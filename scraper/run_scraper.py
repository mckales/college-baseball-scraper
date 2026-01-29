"""
Main CLI script to run the scraper.

Usage:
    python -m scraper.run_scraper <team_key>
    
Example:
    python -m scraper.run_scraper example_team
"""

import sys
import os
import json
import csv
from pathlib import Path
from typing import List, Dict

from .config import TEAMS
from .fetch_html import fetch_html
from .parse_sidearm import parse_game_stats


def save_to_csv(data: List[Dict], filepath: str) -> None:
    """
    Save data to CSV file.
    
    Args:
        data: List of dictionaries to save
        filepath: Output file path
    """
    if not data:
        print("Warning: No data to save to CSV")
        return
    
    # Get all unique keys from all dictionaries
    fieldnames = list(data[0].keys())
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✓ Saved CSV: {filepath}")


def save_to_json(data: List[Dict], filepath: str) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: List of dictionaries to save
        filepath: Output file path
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved JSON: {filepath}")


def run_scraper(team_key: str) -> None:
    """
    Run the scraper for a specific team.
    
    Args:
        team_key: Key from TEAMS config dictionary
    """
    # Validate team key
    if team_key not in TEAMS:
        print(f"Error: Team '{team_key}' not found in config.")
        print(f"Available teams: {', '.join(TEAMS.keys())}")
        sys.exit(1)
    
    team_config = TEAMS[team_key]
    print(f"\n{'='*60}")
    print(f"Scraping: {team_config['name']}")
    print(f"URL: {team_config['stats_url']}")
    print(f"{'='*60}\n")
    
    try:
        # Fetch HTML
        html = fetch_html(team_config['stats_url'])
        
        # Parse based on type
        if team_config['type'] == 'sidearm':
            games = parse_game_stats(html, team_config['table_selector'])
        else:
            print(f"Error: Unsupported platform type '{team_config['type']}'")
            sys.exit(1)
        
        # Prepare output directory
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Save results
        csv_path = output_dir / f"{team_key}_games.csv"
        json_path = output_dir / f"{team_key}_games.json"
        
        save_to_csv(games, str(csv_path))
        save_to_json(games, str(json_path))
        
        print(f"\n{'='*60}")
        print(f"✓ Successfully scraped {len(games)} games")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        sys.exit(1)


def main():
    """
    Main entry point for CLI.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m scraper.run_scraper <team_key>")
        print(f"\nAvailable teams:")
        for key, config in TEAMS.items():
            print(f"  - {key}: {config['name']}")
        sys.exit(1)
    
    team_key = sys.argv[1]
    run_scraper(team_key)


if __name__ == '__main__':
    main()
