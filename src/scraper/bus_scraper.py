"""
Enhanced RedBus Bus Scraper with Database Integration
Scrapes bus data from RedBus and stores in MySQL database
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import re
import os
import logging
import sys
from typing import List, Dict, Optional

# Import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from scraper.utils import (
    parse_price, parse_duration_to_minutes, detect_bustype,
    validate_bus_data, save_screenshot, sanitize_text
)

logger = logging.getLogger(__name__)


class BusScraper:
    """
    Main scraper class for RedBus data
    
    Features:
    - Selenium-based scraping
    - Anti-detection measures
    - Database integration
    - Error handling and logging
    """
    
    def __init__(self, config: Dict, db_manager: DatabaseManager):
        """
        Initialize scraper
        
        Args:
            config: Configuration dictionary
            db_manager: Database manager instance
        """
        self.config = config
        self.db = db_manager
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Initialize Selenium WebDriver with anti-detection"""
        scraping_config = self.config.get('scraping', {})
        
        options = webdriver.ChromeOptions()
        
        # Headless mode
        if scraping_config.get('headless', False):
            options.add_argument('--headless')
        
        # Anti-detection options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={scraping_config.get("window_size", "1920,1080")}')
        options.add_argument('--disable-popup-blocking')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        logger.info("WebDriver initialized successfully")
    
    def wait_for_page_load(self, timeout: int = 10):
        """Wait for page to be fully loaded"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(2)  # Extra buffer
        except TimeoutException:
            logger.warning("Page load timeout")
    
    def scroll_and_load(self, scrolls: int = 5):
        """Scroll page to trigger lazy loading"""
        for i in range(scrolls):
            self.driver.execute_script(f"window.scrollTo(0, {(i+1) * 500});")
            time.sleep(1)
    
    def expand_landing_page_routes(self, landing_url: str) -> List[Dict]:
        """
        Extract all route links from a state transport landing page
        
        Args:
            landing_url: URL of state transport landing page
        
        Returns:
            List of route dictionaries with 'name' and 'url'
        """
        routes = []
        
        try:
            logger.info(f"Expanding routes from landing page: {landing_url}")
            self.driver.get(landing_url)
            self.wait_for_page_load()
            time.sleep(3)
            
            # Find all route links
            anchors = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/bus-tickets/')]")
            logger.info(f"Found {len(anchors)} candidate route links")
            
            for anchor in anchors:
                try:
                    href = anchor.get_attribute('href')
                    text = anchor.text.strip() or href
                    
                    if href and '/bus-tickets/' in href:
                        routes.append({
                            'name': text,
                            'url': href
                        })
                except Exception as e:
                    logger.debug(f"Error extracting route link: {e}")
                    continue
            
            logger.info(f"Extracted {len(routes)} routes from landing page")
            
        except Exception as e:
            logger.error(f"Error expanding landing page routes: {e}")
        
        return routes
    
    def scrape_route(self, route: Dict) -> List[Dict]:
        """
        Scrape all buses for a given route
        
        Args:
            route: Dictionary with 'name' and 'url' keys
        
        Returns:
            List of bus data dictionaries
        """
        all_buses = []
        log_id = None
        
        try:
            logger.info(f"Scraping route: {route['name']}")
            log_id = self.db.log_scraping_job(route['url'], 'STARTED')
            
            # Navigate to route page
            self.driver.get(route['url'])
            self.wait_for_page_load()
            time.sleep(5)
            
            # Check for bus count
            try:
                body_text = self.driver.find_element(By.TAG_NAME, 'body').text
                bus_count_match = re.search(r'(\d+)\s+buses', body_text)
                if bus_count_match:
                    logger.info(f"Found {bus_count_match.group(1)} buses mentioned")
            except Exception:
                pass
            
            # Scroll to load all buses
            self.scroll_and_load(scrolls=5)
            
            # Try container-based parsing first
            buses = self._parse_containers(route)
            
            # Fallback to element-based parsing if needed
            if len(buses) == 0:
                logger.warning("Container parsing failed, trying element-based parsing")
                buses = self._parse_elements(route)
            
            # Validate and filter buses
            for bus in buses:
                is_valid, message = validate_bus_data(bus)
                if is_valid:
                    all_buses.append(bus)
                else:
                    logger.debug(f"Invalid bus data: {message}")
            
            logger.info(f"Scraped {len(all_buses)} valid buses from {route['name']}")
            
            # Update log
            self.db.update_scraping_log(log_id, 'SUCCESS', len(all_buses))
            
            # Save screenshot
            save_screenshot(self.driver, f"{route['name'].replace(' ', '_')}.png")
            
        except Exception as e:
            logger.error(f"Error scraping route {route['name']}: {e}")
            if log_id:
                self.db.update_scraping_log(log_id, 'FAILED', error_message=str(e))
            save_screenshot(self.driver, f"ERROR_{route['name'].replace(' ', '_')}.png")
        
        return all_buses
    
    def _parse_containers(self, route: Dict) -> List[Dict]:
        """Parse using bus container elements (primary method)"""
        buses = []
        
        try:
            containers = self.driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'timeFareBoWrap') or contains(@class, 'bus-item')]"
            )
            logger.info(f"Found {len(containers)} bus containers")
            
            for idx, container in enumerate(containers):
                try:
                    bus_data = self._extract_from_container(container, route, idx)
                    if bus_data:
                        buses.append(bus_data)
                except Exception as e:
                    logger.debug(f"Error parsing container {idx}: {e}")
            
        except Exception as e:
            logger.error(f"Error in container parsing: {e}")
        
        return buses
    
    def _extract_from_container(self, container, route: Dict, idx: int) -> Optional[Dict]:
        """Extract bus data from a single container element"""
        try:
            container_text = container.text
            
            # Extract times
            time_pattern = r'(\d{1,2}:\d{2})'
            times = re.findall(time_pattern, container_text)
            
            if len(times) < 2:
                return None
            
            # Extract price
            price_pattern = r'₹([\d,]+)'
            price_match = re.search(price_pattern, container_text)
            price_val = f"₹{price_match.group(1)}" if price_match else "N/A"
            
            # Extract duration
            duration_pattern = r'(\d+h\s*\d+m|\d+h|\d+m)'
            duration_match = re.search(duration_pattern, container_text)
            duration_val = duration_match.group(1) if duration_match else "N/A"
            
            # Extract seats
            seats_pattern = r'(\d+)\s*Seats?'
            seats_match = re.search(seats_pattern, container_text)
            seats_val = f"{seats_match.group(1)} Seats" if seats_match else "N/A"
            
            # Extract operator name
            try:
                op_el = container.find_element(By.XPATH, ".//div[contains(@class,'travelsName')]")
                operator_val = op_el.text.strip()
            except:
                operator_pattern = r'^([A-Za-z0-9\s\-&!.()]+)'
                op_match = re.search(operator_pattern, container_text)
                operator_val = op_match.group(1).strip() if op_match else f"Bus {idx+1}"
            
            # Extract rating
            rating_pattern = r'(\d\.\d+)'
            rating_match = re.search(rating_pattern, container_text)
            rating_val = rating_match.group(1) if rating_match else "N/A"
            
            # Detect bus type
            bustype_val = detect_bustype(container_text)
            
            # Build bus data dictionary
            bus_data = {
                "route_name": route['name'],
                "route_link": route['url'],
                "busname": sanitize_text(operator_val),
                "bustype": bustype_val,
                "departing_time": times[0],
                "duration": duration_val,
                "duration_minutes": parse_duration_to_minutes(duration_val),
                "reaching_time": times[1] if len(times) > 1 else times[0],
                "star_rating": rating_val,
                "price": price_val,
                "price_numeric": parse_price(price_val),
                "seats_available": seats_val
            }
            
            return bus_data
            
        except Exception as e:
            logger.debug(f"Error extracting from container: {e}")
            return None
    
    def _parse_elements(self, route: Dict) -> List[Dict]:
        """Parse using individual elements (fallback method)"""
        buses = []
        
        try:
            # Get departure times
            departure_times = self.driver.find_elements(
                By.XPATH, "//p[contains(@class, 'boardingTime')]"
            )
            
            # Get arrival times
            arrival_times = self.driver.find_elements(
                By.XPATH, "//p[contains(@class, 'droppingTime')]"
            )
            
            # Get operators
            operators = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'travelsName')]"
            )
            
            # Get prices
            prices = self.driver.find_elements(
                By.XPATH, "//p[contains(@class, 'finalFare') or contains(@class, 'fare')]"
            )
            
            logger.info(f"Element parsing: {len(departure_times)} departures, {len(operators)} operators")
            
            # Combine data
            max_count = min(len(departure_times), len(arrival_times), len(operators))
            
            for i in range(max_count):
                try:
                    bus_data = {
                        "route_name": route['name'],
                        "route_link": route['url'],
                        "busname": sanitize_text(operators[i].text) if i < len(operators) else f"Bus {i+1}",
                        "bustype": "N/A",
                        "departing_time": departure_times[i].text.strip(),
                        "duration": "N/A",
                        "duration_minutes": None,
                        "reaching_time": arrival_times[i].text.strip(),
                        "star_rating": "N/A",
                        "price": prices[i].text.strip() if i < len(prices) else "N/A",
                        "price_numeric": None,
                        "seats_available": "N/A"
                    }
                    buses.append(bus_data)
                except Exception as e:
                    logger.debug(f"Error creating bus data for element {i}: {e}")
            
        except Exception as e:
            logger.error(f"Error in element parsing: {e}")
        
        return buses
    
    def scrape_all_states(self) -> int:
        """
        Scrape all states configured in config
        
        Returns:
            Total number of buses scraped
        """
        total_buses = 0
        states = self.config.get('states', [])
        
        logger.info(f"Starting to scrape {len(states)} states")
        
        for state in states:
            try:
                logger.info(f"Processing state: {state['name']} ({state['state']})")
                
                # First visit homepage to set cookies
                if total_buses == 0:
                    self.driver.get("https://www.redbus.in/")
                    self.wait_for_page_load()
                    time.sleep(3)
                
                # Expand landing page to get all routes
                routes = self.expand_landing_page_routes(state['url'])
                
                if not routes:
                    logger.warning(f"No routes found for {state['name']}")
                    continue
                
                logger.info(f"Found {len(routes)} routes for {state['name']}")
                
                # Scrape each route (limit to first 10 for testing)
                for route in routes[:10]:
                    buses = self.scrape_route(route)
                    
                    if buses:
                        # Insert into database
                        success, failed = self.db.bulk_insert(buses)
                        total_buses += success
                        logger.info(f"Inserted {success} buses, {failed} failed")
                    
                    # Delay between routes
                    delay = self.config.get('scraping', {}).get('delay_between_routes', 5)
                    time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error processing state {state['name']}: {e}")
                continue
        
        logger.info(f"Scraping complete: {total_buses} total buses scraped")
        return total_buses
    
    def close(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")


# Example usage
if __name__ == "__main__":
    from scraper.utils import load_config, setup_logging
    
    # Setup
    setup_logging()
    config = load_config()
    
    # Initialize database
    db = DatabaseManager(config['database'])
    
    # Test connection
    if not db.test_connection():
        logger.error("Database connection failed")
        exit(1)
    
    # Initialize scraper
    scraper = BusScraper(config, db)
    
    # Scrape all states
    try:
        total = scraper.scrape_all_states()
        print(f"\n✅ Scraping complete: {total} buses scraped")
    finally:
        scraper.close()
        db.close()
