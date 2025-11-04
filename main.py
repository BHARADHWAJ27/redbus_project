"""
RedBus Project - Main Orchestrator
Entry point for the entire application
"""

import argparse
import sys
import os
import subprocess
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scraper.bus_scraper import BusScraper
from database.db_manager import DatabaseManager
from scraper.utils import load_config, setup_logging

import logging
logger = logging.getLogger(__name__)


def run_scraper(config):
    """
    Run the web scraper
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*60)
    print("🚌 REDBUS DATA SCRAPER")
    print("="*60 + "\n")
    
    try:
        # Initialize database
        print("📊 Connecting to database...")
        db = DatabaseManager(config['database'])
        
        if not db.test_connection():
            print("❌ Database connection failed!")
            return False
        
        print("✅ Database connected successfully\n")
        
        # Ask for confirmation
        print("This will scrape bus data from 10 state transport websites.")
        print("This may take 30-60 minutes depending on your internet speed.\n")
        
        response = input("Do you want to continue? (yes/no): ").lower()
        if response not in ['yes', 'y']:
            print("Operation cancelled.")
            return False
        
        # Initialize scraper
        print("\n🔍 Initializing scraper...")
        scraper = BusScraper(config, db)
        print("✅ Scraper initialized\n")
        
        # Start scraping
        print("🚀 Starting scraping process...")
        print("-" * 60)
        
        start_time = datetime.now()
        total_buses = scraper.scrape_all_states()
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds() / 60
        
        print("-" * 60)
        print(f"\n✅ Scraping completed successfully!")
        print(f"📊 Total buses scraped: {total_buses}")
        print(f"⏱️  Time taken: {duration:.1f} minutes")
        print(f"💾 Data saved to database: {config['database']['database']}")
        
        # Cleanup
        scraper.close()
        db.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error in scraper: {e}")
        print(f"\n❌ Error occurred: {e}")
        return False


def run_app(config):
    """
    Launch Streamlit application
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*60)
    print("🚌 LAUNCHING REDBUS STREAMLIT APP")
    print("="*60 + "\n")
    
    try:
        # Check database connection
        print("📊 Checking database connection...")
        db = DatabaseManager(config['database'])
        
        if not db.test_connection():
            print("❌ Database connection failed!")
            print("Please run the scraper first or check your database settings.")
            return False
        
        # Check if data exists
        stats = db.get_statistics()
        total_buses = stats.get('total_buses', 0)
        
        if total_buses == 0:
            print("⚠️  Warning: No data found in database!")
            print("Please run the scraper first using: python main.py --mode scrape")
            response = input("\nDo you want to launch the app anyway? (yes/no): ").lower()
            if response not in ['yes', 'y']:
                return False
        else:
            print(f"✅ Database connected successfully")
            print(f"📊 Found {total_buses} buses in database\n")
        
        db.close()
        
        # Launch Streamlit
        print("🚀 Launching Streamlit application...")
        print("📱 The app will open in your default browser")
        print("Press Ctrl+C to stop the application\n")
        
        app_path = os.path.join('src', 'streamlit_app', 'app.py')
        subprocess.run(['streamlit', 'run', app_path])
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
        return True
    except Exception as e:
        logger.error(f"Error launching app: {e}")
        print(f"\n❌ Error occurred: {e}")
        return False


def show_statistics(config):
    """
    Display database statistics
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*60)
    print("📊 REDBUS DATABASE STATISTICS")
    print("="*60 + "\n")
    
    try:
        db = DatabaseManager(config['database'])
        
        if not db.test_connection():
            print("❌ Database connection failed!")
            return False
        
        stats = db.get_statistics()
        
        if stats.get('total_buses', 0) == 0:
            print("⚠️  No data found in database!")
            print("Run the scraper first using: python main.py --mode scrape")
            return False
        
        print("✅ Database connected successfully\n")
        print("=" * 60)
        print(f"📊 Total Buses:        {stats.get('total_buses', 0):,}")
        print(f"🛣️  Total Routes:       {stats.get('total_routes', 0):,}")
        print(f"💰 Average Price:      ₹{stats.get('avg_price', 0):.2f}")
        print(f"💵 Minimum Price:      ₹{stats.get('min_price', 0):.2f}")
        print(f"💸 Maximum Price:      ₹{stats.get('max_price', 0):.2f}")
        print(f"⭐ Average Rating:     {stats.get('avg_rating', 0):.2f}/5.0")
        print(f"💺 Average Seats:      {stats.get('avg_seats', 0):.1f}")
        print("=" * 60)
        
        # Get route distribution
        print("\n📍 Routes Available:")
        routes = db.get_all_routes()
        print(f"   Total unique routes: {len(routes)}")
        if len(routes) <= 10:
            for route in routes:
                print(f"   - {route}")
        else:
            for route in routes[:10]:
                print(f"   - {route}")
            print(f"   ... and {len(routes) - 10} more routes")
        
        # Get bus type distribution
        print("\n🚍 Bus Types Available:")
        bustypes = db.get_all_bustypes()
        for bustype in bustypes:
            print(f"   - {bustype}")
        
        db.close()
        print("\n")
        return True
        
    except Exception as e:
        logger.error(f"Error showing statistics: {e}")
        print(f"\n❌ Error occurred: {e}")
        return False


def setup_database(config):
    """
    Setup database tables
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*60)
    print("🔧 DATABASE SETUP")
    print("="*60 + "\n")
    
    try:
        print("📊 Connecting to database...")
        db = DatabaseManager(config['database'])
        
        if not db.test_connection():
            print("❌ Database connection failed!")
            print("Please check your MySQL server and credentials.")
            return False
        
        print("✅ Database connected successfully\n")
        print("🔧 Creating tables...")
        
        db.create_tables()
        
        print("✅ Database setup complete!\n")
        print("You can now run the scraper using: python main.py --mode scrape")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        print(f"\n❌ Error occurred: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='RedBus Data Scraping and Analysis Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode setup   # Setup database
  python main.py --mode scrape  # Run web scraper
  python main.py --mode app     # Launch Streamlit app
  python main.py --mode stats   # Show database statistics
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['setup', 'scrape', 'app', 'stats'],
        help='Operation mode: setup, scrape, app, or stats'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        print("Make sure config/config.yaml exists and .env is configured")
        return 1
    
    # Display header
    print("\n" + "="*60)
    print("🚌 REDBUS DATA SCRAPING & ANALYSIS PLATFORM")
    print("="*60)
    
    # Execute based on mode
    if args.mode == 'setup':
        success = setup_database(config)
    elif args.mode == 'scrape':
        success = run_scraper(config)
    elif args.mode == 'app':
        success = run_app(config)
    elif args.mode == 'stats':
        success = show_statistics(config)
    else:
        print(f"❌ Unknown mode: {args.mode}")
        return 1
    
    # Return appropriate exit code
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
