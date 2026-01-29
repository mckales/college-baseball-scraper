import logging
import json
import traceback
from datetime import datetime
import os

logger = logging.getLogger(__name__)

ERROR_LOG_PATH = "output/scraper_errors.json"

class ScraperError(Exception):
    """Base class for scraper exceptions"""
    def __init__(self, message, player_id=None, school=None, url=None):
        super().__init__(message)
        self.player_id = player_id
        self.school = school
        self.url = url
        self.timestamp = datetime.now().isoformat()

def log_error(error):
    """Logs structured error information to a file"""
    error_data = {
        "timestamp": datetime.now().isoformat(),
        "message": str(error),
        "traceback": traceback.format_exc(),
        "player_id": getattr(error, 'player_id', None),
        "school": getattr(error, 'school', None),
        "url": getattr(error, 'url', None)
    }
    
    logger.error(f"Scraper Error: {error_data['message']} | School: {error_data['school']}")
    
    # Append to JSON log file
    os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
    
    try:
        errors = []
        if os.path.exists(ERROR_LOG_PATH):
            with open(ERROR_LOG_PATH, 'r') as f:
                errors = json.load(f)
        
        errors.append(error_data)
        
        # Keep only last 100 errors
        errors = errors[-100:]
        
        with open(ERROR_LOG_PATH, 'w') as f:
            json.dump(errors, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to write to error log: {e}")

def handle_retry(func):
    """Decorator to retry functions on failure"""
    def wrapper(*args, **kwargs):
        retries = 3
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if i == retries - 1:
                    log_error(e)
                    raise
                logger.warning(f"Retry {i+1}/{retries} for {func.__name__}")
    return wrapper
