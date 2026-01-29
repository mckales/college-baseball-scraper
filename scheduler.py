"""
Scheduled scraper for Base44 integration.
Runs at: 9 AM, then every hour from 12 PM to 12 AM (14 times daily).
"""

import schedule
import time
import logging
from datetime import datetime
import pytz
from scraper.scraper_api import scrape_player
from base44_integration import send_to_base44
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_schedule.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Central Time Zone
CENTRAL_TZ = pytz.timezone('America/Chicago')

def run_scraper_job():
    """
    Main scraper job that runs on schedule.
    Scrapes all configured players and sends data to Base44.
    """
    current_time = datetime.now(CENTRAL_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')
    logger.info(f"Starting scheduled scraper run at {current_time}")
    
    try:
        # Load player list from configuration
        with open('players_to_track.json', 'r') as f:
            players = json.load(f)
        
        success_count = 0
        error_count = 0
        
        for player in players:
            try:
                player_name = player['name']
                jersey_number = player['number']
                school = player['school']
                sport = player.get('sport', 'baseball')
                
                logger.info(f"Scraping: {player_name} #{jersey_number} from {school} ({sport})")
                
                # Run the scraper
                stats = scrape_player(
                    player_name=player_name,
                    jersey_number=jersey_number,
                    school=school,
                    sport=sport,
                    season="2026",
                    output_format="json"
                )
                
                # Send to Base44
                if stats:
                    send_to_base44(stats, player)
                    success_count += 1
                    logger.info(f"Successfully updated {player_name}")
                else:
                    logger.warning(f"No stats found for {player_name}")
                    error_count += 1
                
                # Small delay between players to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error scraping {player.get('name', 'unknown')}: {str(e)}")
        
        logger.info(f"Scraper run complete. Success: {success_count}, Errors: {error_count}")
        
    except FileNotFoundError:
        logger.error("players_to_track.json not found. Please create this file with player configuration.")
    except Exception as e:
        logger.error(f"Fatal error in scraper job: {str(e)}")

def schedule_jobs():
    """
    Set up the schedule:
    - 9:00 AM
    - Every hour from 12:00 PM to 12:00 AM (midnight)
    """
    # Morning update
    schedule.every().day.at("09:00").do(run_scraper_job)
    
    # Hourly updates from noon to midnight
    schedule.every().day.at("12:00").do(run_scraper_job)
    schedule.every().day.at("13:00").do(run_scraper_job)
    schedule.every().day.at("14:00").do(run_scraper_job)
    schedule.every().day.at("15:00").do(run_scraper_job)
    schedule.every().day.at("16:00").do(run_scraper_job)
    schedule.every().day.at("17:00").do(run_scraper_job)
    schedule.every().day.at("18:00").do(run_scraper_job)
    schedule.every().day.at("19:00").do(run_scraper_job)
    schedule.every().day.at("20:00").do(run_scraper_job)
    schedule.every().day.at("21:00").do(run_scraper_job)
    schedule.every().day.at("22:00").do(run_scraper_job)
    schedule.every().day.at("23:00").do(run_scraper_job)
    schedule.every().day.at("00:00").do(run_scraper_job)
    
    logger.info("Scheduler configured with 14 daily runs:")
    logger.info("  - 9:00 AM")
    logger.info("  - Every hour from 12:00 PM to 12:00 AM")

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Base44 College Baseball/Softball Scraper Scheduler")
    logger.info("=" * 50)
    
    # Set up schedule
    schedule_jobs()
    
    # Run immediately on start
    logger.info("Running initial scrape...")
    run_scraper_job()
    
    # Keep running
    logger.info("Scheduler is now running. Press Ctrl+C to stop.")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            time.sleep(60)
