"""
Parse individual player game logs using Selenium to handle dynamic content.
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
from .config import SELENIUM_HEADLESS, SELENIUM_TIMEOUT, DEFAULT_SEASON


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


def scrape_game_log(player_url, season=DEFAULT_SEASON):
    """
    Scrape a player's game-by-game stats using Selenium.
    
    Args:
        player_url (str): Full URL to player's page
        season (str): Season year (e.g., "2026")
    
    Returns:
        list: List of dicts, each containing game stats
    """
    
    print(f"Scraping game log from: {player_url}")
    print(f"Season: {season}")
    
    driver = None
    try:
        driver = setup_driver()
        driver.get(player_url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
        
        # Click on "Stats" tab
        print("Looking for Stats tab...")
        stats_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Stats') or contains(@href, 'stats')]"))
        )
        stats_tab.click()
        time.sleep(2)  # Wait for content to load
        
        # Select season from dropdown
        print(f"Selecting {season} season...")
        try:
            # Find and click season dropdown
            season_dropdown = driver.find_element(By.XPATH, f"//select[contains(@id, 'season') or contains(@aria-label, 'Season')]")
            season_dropdown.click()
            time.sleep(1)
            
            # Select the desired season
            season_option = driver.find_element(By.XPATH, f"//option[contains(text(), '{season}')]")
            season_option.click()
            time.sleep(2)  # Wait for data to load
        except Exception as e:
            print(f"Note: Could not change season (may already be on {season}): {e}")
        
        # Get page HTML after JavaScript has loaded
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        
        # Find the game log table
        game_log_table = None
        
        # Try to find table by looking for common patterns
        headings = soup.find_all(['h2', 'h3', 'h4'], string=re.compile(r'Hitting Statistics|Game Log', re.I))
        for heading in headings:
            # Find next table after this heading
            table = heading.find_next('table')
            if table:
                # Check if table has Date column (indicates game log)
                headers = [th.get_text(strip=True) for th in table.find_all('th')]
                if 'Date' in headers or 'Opponent' in headers:
                    game_log_table = table
                    break
        
        if not game_log_table:
            # Fallback: find any table with Date and Opponent columns
            for table in soup.find_all('table'):
                headers = [th.get_text(strip=True) for th in table.find_all('th')]
                if 'Date' in headers and 'Opponent' in headers:
                    game_log_table = table
                    break
        
        if not game_log_table:
            print("Warning: Could not find game log table. Page may not have loaded correctly or player has no games yet.")
            return []
        
        # Parse the table
        games = parse_game_table(game_log_table)
        
        print(f"✓ Scraped {len(games)} games")
        return games
        
    except Exception as e:
        print(f"Error scraping game log: {e}")
        raise
    
    finally:
        if driver:
            driver.quit()


def parse_game_table(table):
    """
    Parse the game log table into a list of game dicts.
    
    Args:
        table: BeautifulSoup table element
    
    Returns:
        list: List of game dicts
    """
    
    # Get headers
    headers = []
    header_row = table.find('thead')
    if header_row:
        headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
    else:
        # Try first row if no thead
        first_row = table.find('tr')
        if first_row:
            headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
    
    print(f"Table headers: {headers}")
    
    # Get data rows
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
    else:
        rows = table.find_all('tr')[1:]  # Skip header row
    
    games = []
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) < 3:  # Skip empty or summary rows
            continue
        
        game = {}
        for i, cell in enumerate(cells):
            if i < len(headers):
                header = headers[i]
                value = cell.get_text(strip=True)
                
                # Handle special cases
                if header == 'Opponent' and cell.find('a'):
                    # Extract just opponent name, not the link
                    value = cell.find('a').get_text(strip=True)
                
                # Store with cleaned header name
                clean_header = header.lower().replace('/', '_').replace(' ', '_')
                game[clean_header] = value
        
        if game:  # Only add if we got data
            games.append(game)
    
    return games
