"""
Utility functions for RedBus scraper
"""

import logging
import yaml
import os
import re
from typing import Dict, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config/config.yaml') -> Dict:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
    
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Load environment variables
        if 'DB_PASSWORD' in os.environ:
            config['database']['password'] = os.environ['DB_PASSWORD']
        
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def setup_logging(log_level: str = 'INFO', log_file: str = 'logs/app.log'):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (INFO, DEBUG, WARNING, ERROR)
        log_file: Path to log file
    """
    # Create logs directory if not exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger.info("Logging configured successfully")


def validate_bus_data(bus_data: Dict) -> Tuple[bool, str]:
    """
    Validate bus data before storage
    
    Args:
        bus_data: Dictionary with bus information
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['route_name', 'busname', 'departing_time', 'reaching_time', 'price']
    
    # Check required fields
    for field in required_fields:
        value = bus_data.get(field)
        if not value or value == 'N/A':
            return False, f"Missing required field: {field}"
    
    # Validate rating
    if bus_data.get('star_rating') and bus_data['star_rating'] != 'N/A':
        try:
            rating = float(bus_data['star_rating'])
            if rating < 0 or rating > 5:
                return False, "Invalid rating range (must be 0-5)"
        except:
            return False, "Invalid rating format"
    
    # Validate time format
    time_pattern = r'^\d{1,2}:\d{2}$'
    if not re.match(time_pattern, bus_data['departing_time']):
        return False, "Invalid departing time format (should be HH:MM)"
    
    if not re.match(time_pattern, bus_data['reaching_time']):
        return False, "Invalid reaching time format (should be HH:MM)"
    
    return True, "Valid"


def parse_price(price_str: str) -> Optional[int]:
    """
    Normalize price string to integer
    
    Args:
        price_str: Price string like '₹1,200' or '1200'
    
    Returns:
        Integer price or None if not parseable
    """
    if not price_str or price_str == 'N/A':
        return None
    try:
        cleaned = re.sub(r'[₹,\s]', '', str(price_str))
        return int(float(cleaned))
    except Exception:
        return None


def parse_duration_to_minutes(duration_str: str) -> Optional[int]:
    """
    Convert duration like '12h 30m' to integer minutes
    
    Args:
        duration_str: Duration string
    
    Returns:
        Integer minutes or None if not parseable
    """
    if not duration_str or duration_str == 'N/A':
        return None
    
    try:
        m = re.search(r"(?:(\d+)h)?\s*(?:(\d+)m)?", duration_str)
        if not m:
            return None
        hours = int(m.group(1)) if m.group(1) else 0
        mins = int(m.group(2)) if m.group(2) else 0
        return hours * 60 + mins
    except Exception:
        return None


def detect_bustype(container_text: str) -> str:
    """
    Try to infer bus type from container text
    
    Args:
        container_text: Text content from bus container
    
    Returns:
        Bus type string
    """
    text = container_text.lower()
    
    # Priority order for detection
    if 'sleeper' in text:
        if 'ac' in text and 'non' not in text:
            return 'AC Sleeper'
        elif 'non-ac' in text or 'non ac' in text:
            return 'Non-AC Sleeper'
        return 'Sleeper'
    
    if 'seater' in text:
        if 'ac' in text and 'non' not in text:
            return 'AC Seater'
        elif 'non-ac' in text or 'non ac' in text:
            return 'Non-AC Seater'
        return 'Seater'
    
    if 'volvo' in text:
        return 'Volvo'
    
    if 'ac' in text and 'non' not in text:
        return 'AC'
    
    if 'non-ac' in text or 'non ac' in text:
        return 'Non-AC'
    
    return 'N/A'


def sanitize_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text
    
    Returns:
        Cleaned text
    """
    if not text:
        return 'N/A'
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\-.,()&]', '', text)
    
    return text.strip()


def create_route_url(source: str, destination: str) -> str:
    """
    Helper function to create RedBus URL from source and destination
    
    Args:
        source: Source city name
        destination: Destination city name
    
    Returns:
        RedBus URL for the route
    """
    source = source.lower().replace(' ', '-')
    destination = destination.lower().replace(' ', '-')
    return f"https://www.redbus.in/bus-tickets/{source}-to-{destination}"


def save_screenshot(driver, filename: str, output_dir: str = 'output'):
    """
    Save screenshot with error handling
    
    Args:
        driver: Selenium WebDriver instance
        filename: Screenshot filename
        output_dir: Output directory
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")


# Decorators
def retry_on_failure(max_retries: int = 3, delay: int = 5):
    """
    Decorator to retry function on failure
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed")
                        raise
        return wrapper
    return decorator
