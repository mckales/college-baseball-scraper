"""
Parse individual player game logs using Selenium to handle dynamic content.
Supports multiple platforms: SIDEARM (100% optimized), PrestoSports, NCAA.com, and generic sites.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
from .config import SELENIUM_HEADLESS, SELENIUM_TIMEOUT, DEFAULT_SEASON, get_platform_selectors


def setup_driver():
    """Initialize and return a Selenium WebDriver."""
    chrome_options = Options()
    
    if SELENIUM_HEADLESS:
        chrome_options.add_argument('--headless')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


def parse_sidearm_game_log(driver, player_url, season=DEFAULT_SEASON):
    """
    Parse game log from SIDEARM Sports sites (100% optimized for accuracy).
    This is the primary parser for most D1, D2, D3 college baseball sites.
    """
    driver.get(player_url)
    wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
    
    # Wait for page to load
    time.sleep(2)
    
    # Click on Stats tab
    try:
        stats_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='#sidearm-roster-player-stats']")))
        driver.execute_script("arguments[0].click();", stats_tab)
        time.sleep(2)
    except Exception as e:
        raise ValueError(f"Could not find or click Stats tab on SIDEARM page: {str(e)}")
    
    # Select season
    try:
        season_dropdown = driver.find_element(By.CSS_SELECTOR, "select")
        for option in season_dropdown.find_elements(By.TAG_NAME, "option"):
            if season in option.text:
                option.click()
                time.sleep(2)
                break
    except:
        pass  # Season selector might not exist if only one season available
    
    # Get page HTML after JavaScript has loaded
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find the game-by-game stats table
    game_log = []
    
    # Look for tables containing "Hitting Statistics" header
    tables = soup.find_all('table')
    
    for table in tables:
        # Check if this is the game log table (has "Date" and "Opponent" headers)
        headers = [th.get_text().strip() for th in table.find_all('th')]
        
        if 'Date' in headers and 'Opponent' in headers:
            # Found the game log table!
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 3:  # Skip rows that don't have enough data
                    continue
                
                game_data = {}
                for i, header in enumerate(headers):
                    if i < len(cells):
                        game_data[header] = cells[i].get_text().strip()
                
                # Only add games that have actual data (not season totals)
                if game_data.get('Date') and 'Total' not in game_data.get('Date', ''):
                    game_log.append(game_data)
    
    if not game_log:
        raise ValueError(f"No game log data found on SIDEARM page for {season} season")
    
    return game_log


def parse_prestosports_game_log(driver, player_url, season=DEFAULT_SEASON):
    """
    Parse game log from PrestoSports sites.
    """
    driver.get(player_url)
    wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
    time.sleep(2)
    
    # Try to click stats tab
    try:
        stats_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='stats'], #stats-tab")))
        stats_tab.click()
        time.sleep(2)
    except:
        pass  # Stats might be default view
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    game_log = []
    
    # Find stats table
    tables = soup.find_all('table', class_=lambda x: x and 'stats' in x.lower() if x else False)
    
    for table in tables:
        headers = [th.get_text().strip() for th in table.find_all('th')]
        
        if 'Date' in headers or 'Opponent' in headers:
            rows = table.find_all('tr')[1:]
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue
                
                game_data = {}
                for i, header in enumerate(headers):
                    if i < len(cells):
                        game_data[header] = cells[i].get_text().strip()
                
                if game_data.get('Date'):
                    game_log.append(game_data)
    
    return game_log


def parse_generic_game_log(driver, player_url, season=DEFAULT_SEASON):
    """
    Generic parser that works across various platforms.
    Falls back to this if platform-specific parser fails.
    """
    driver.get(player_url)
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    game_log = []
    
    # Find any table that looks like game log
    tables = soup.find_all('table')
    
    for table in tables:
        headers = [th.get_text().strip() for th in table.find_all('th')]
        
        # Check if this looks like a game log table
        if any(keyword in ' '.join(headers).lower() for keyword in ['date', 'opponent', 'game']):
            rows = table.find_all('tr')[1:]
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    game_data = {}
                    for i, header in enumerate(headers):
                        if i < len(cells):
                            game_data[header] = cells[i].get_text().strip()
                    
                    if game_data:
                        game_log.append(game_data)
    
    return game_log


def parse_game_log(player_url, platform_type, season=DEFAULT_SEASON):
    """
    Main function to parse game log based on platform type.
    
    Args:
        player_url (str): URL to player's profile page
        platform_type (str): Platform type ('sidearm', 'prestosports', 'ncaa', 'generic')
        season (str): Season to scrape (e.g., '2026')
    
    Returns:
        list: List of game dictionaries with stats
    """
    driver = setup_driver()
    
    try:
        # Route to platform-specific parser
        if platform_type == 'sidearm':
            game_log = parse_sidearm_game_log(driver, player_url, season)
        elif platform_type == 'prestosports':
            game_log = parse_prestosports_game_log(driver, player_url, season)
        else:
            # Use generic parser for unknown platforms
            game_log = parse_generic_game_log(driver, player_url, season)
        
        return game_log
    
    except Exception as e:
        # If platform-specific parser fails, try generic as fallback
        try:
            if platform_type != 'generic':
                print(f"Platform-specific parser failed, trying generic parser: {str(e)}")
                game_log = parse_generic_game_log(driver, player_url, season)
                return game_log
            else:
                raise
        except:
            raise ValueError(f"Failed to parse game log from {player_url}: {str(e)}")
    
    finally:
        driver.quit()
