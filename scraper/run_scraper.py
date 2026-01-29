"""
CLI interface for the scraper.
Can be run directly from command line or imported by Base44.
"""

import sys
import json
import csv
from pathlib import Path
from .scraper_api import get_player_stats
from .config import DEFAULT_SEASON


def save_to_csv(result, output_dir="output"):
    """Save game stats to CSV file."""
    if "error" in result:
        print(f"Error: {result['error']}")
        return None
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Create filename
    player_name_clean = result['player_name'].replace(' ', '_').lower()
    filename = f"{output_dir}/{player_name_clean}_{result['school'].lower()}_{result['season']}.csv"
    
    if not result['games']:
        print(f"No games to save for {result['player_name']}")
        return None
    
    # Write CSV
    with open(filename, 'w', newline='') as f:
        if result['games']:
            # Get all possible field names from all games
            fieldnames = set()
            for game in result['games']:
                fieldnames.update(game.keys())
            fieldnames = sorted(list(fieldnames))
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(result['games'])
    
    print(f"✓ Saved CSV: {filename}")
    return filename


def save_to_json(result, output_dir="output"):
    """Save complete result to JSON file."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Create filename
    if "error" in result:
        player_name_clean = result['player_name'].replace(' ', '_').lower()
        filename = f"{output_dir}/{player_name_clean}_error.json"
    else:
        player_name_clean = result['player_name'].replace(' ', '_').lower()
        filename = f"{output_dir}/{player_name_clean}_{result['school'].lower()}_{result['season']}.json"
    
    # Write JSON
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✓ Saved JSON: {filename}")
    return filename


def main():
    """CLI entry point."""
    if len(sys.argv) < 4:
        print("\nUsage: python -m scraper.run_scraper <player_name> <jersey_number> <school> [season]")
        print("\nExample:")
        print('  python -m scraper.run_scraper "Charlie Davis" 8 Belmont')
        print('  python -m scraper.run_scraper "Charlie Davis" 8 Belmont 2025')
        print("\nAvailable schools:")
        from .config import SCHOOLS
        for school in SCHOOLS.keys():
            print(f"  - {school}")
        sys.exit(1)
    
    player_name = sys.argv[1]
    jersey_number = sys.argv[2]
    school = sys.argv[3]
    season = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_SEASON
    
    # Get stats
    result = get_player_stats(player_name, jersey_number, school, season)
    
    # Save to files
    save_to_json(result)
    if "error" not in result:
        save_to_csv(result)
    
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
