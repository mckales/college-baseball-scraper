"""
Scheduled scraper for Base44 integration.
Runs at: 9 AM, then every hour from 12 PM to 12 AM (14 times daily).
"""
import schedule
import time
import logging
import asyncio
from datetime import datetime
import pytz
from base44_integration import run_sync_async

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
    Uses async sync function for high performance.
    """
    current_time = datetime.now(CENTRAL_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')
    logger.info(f"Starting scheduled scraper run at {current_time}")
    
    try:
        # Run the async sync
        asyncio.run(run_sync_async(concurrency=10))
        logger.info("Scraper run complete.")
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
    for hour in range(12, 24):
        time_str = f"{hour:02d}:00"
        schedule.every().day.at(time_str).do(run_scraper_job)
    schedule.every().day.at("00:00").do(run_scraper_job)
    
    logger.info("Scheduler configured for 14 daily runs.")

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
            time.sleep(60) 
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            time.sleep(60)
