#!/usr/bin/env python3
"""
Test script to demonstrate the schedule scraping functionality.
Shows how to retrieve games by date for D1, D2, D3 baseball and D1 softball.
"""

import asyncio
import json
from datetime import datetime, timedelta
from scraper_api import get_team_games_by_date

# Test schools across divisions and sports
TEST_TEAMS = [
    # D1 Baseball
    {
        "name": "Belmont Baseball (D1)",
        "url": "https://belmontbruins.com/sports/baseball/schedule",
        "sport": "baseball"
    },
    # D2 Baseball
    {
        "name": "Young Harris College Baseball (D2)",
        "url": "https://yhcathletics.com/sports/baseball/schedule",
        "sport": "baseball"
    },
    # D3 Baseball
    {
        "name": "Rhodes College Baseball (D3)",
        "url": "https://rhodeslynx.com/sports/baseball/schedule",
        "sport": "baseball"
    },
    # D1 Softball
    {
        "name": "Belmont Softball (D1)",
        "url": "https://belmontbruins.com/sports/softball/schedule",
        "sport": "softball"
    }
]

async def test_schedule_scraper():
    """Test the schedule scraper with multiple schools."""
    print("=" * 80)
    print("SCHEDULE SCRAPER TEST")
    print("Testing D1/D2/D3 Baseball + D1 Softball")
    print("=" * 80)
    
    # Get today's date for filtering
    today = datetime.now().strftime("%m/%d/%Y")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%m/%d/%Y")
    
    for team in TEST_TEAMS:
        print(f"\n{'='*60}")
        print(f"Team: {team['name']}")
        print(f"URL: {team['url']}")
        print(f"{'='*60}")
        
        try:
            # Fetch all games (no date filter)
            result = await get_team_games_by_date(
                team_schedule_url=team['url'],
                target_dates=None,  # Get all games
                sport=team['sport']
            )
            
            if result.get('success'):
                print(f"✓ Successfully fetched {result['total_games']} games")
                
                # Display first 3 games as examples
                for i, game in enumerate(result['games'][:3]):
                    print(f"\n  Game {i+1}:")
                    print(f"    Date: {game.get('date', 'N/A')}")
                    print(f"    Box Score URL: {game.get('box_score_url', 'N/A')}")
                    if game.get('box_score_data'):
                        print(f"    Box Score Data: {len(game['box_score_data'])} player records")
                
                if result['total_games'] > 3:
                    print(f"\n  ... and {result['total_games'] - 3} more games")
            else:
                print(f"✗ Error: {result.get('error')}")
                
        except Exception as e:
            print(f"✗ Exception: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_schedule_scraper())
