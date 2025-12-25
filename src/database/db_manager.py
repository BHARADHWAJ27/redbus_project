"""
Database Manager Module
Handles all database operations for RedBus project
"""

import logging
import psycopg2
from psycopg2 import pool, Error
from typing import List, Dict, Optional, Tuple
import pandas as pd
from datetime import datetime
import os
from contextlib import contextmanager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages all database operations for RedBus data
    
    Features:
    - Connection pooling
    - CRUD operations
    - Filtering and querying
    - Transaction management
    - Error handling
    """
    
    def __init__(self, config: Dict):
        """
        Initialize database manager with configuration
        
        Args:
            config: Dictionary with database configuration
                   {host, port, database, user, password, pool_size}
        """
        self.config = config
        self.pool = None
        self._create_connection_pool()
    
    def _create_connection_pool(self):
        """Create PostgreSQL connection pool"""
        try:
            self.pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=self.config.get('pool_size', 5),
                host=self.config['host'],
                port=self.config.get('port', 5432),
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            logger.info("Database connection pool created successfully")
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
        """
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Error as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                logger.info("Database connection test successful")
                return result[0] == 1
        except Error as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            schema_path = os.path.join(
                os.path.dirname(__file__), 
                'schema.sql'
            )
            
            with open(schema_path, 'r') as f:
                sql_script = f.read()
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Execute the entire script at once for PostgreSQL
                cursor.execute(sql_script)
                conn.commit()
                cursor.close()
                logger.info("Database tables created successfully")
        except Error as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def insert_bus_data(self, bus_data: Dict) -> bool:
        """
        Insert single bus record
        
        Args:
            bus_data: Dictionary with bus information
        
        Returns:
            True if successful, False otherwise
        """
        query = """
            INSERT INTO bus_routes 
            (route_name, route_link, busname, bustype, departing_time, 
             duration, duration_minutes, reaching_time, star_rating, 
             price, seats_available)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Extract and clean data
                values = (
                    bus_data.get('route_name', ''),
                    bus_data.get('route_link', ''),
                    bus_data.get('busname', ''),
                    bus_data.get('bustype', 'N/A'),
                    bus_data.get('departing_time', '00:00'),
                    bus_data.get('duration', 'N/A'),
                    bus_data.get('duration_minutes'),
                    bus_data.get('reaching_time', '00:00'),
                    self._parse_rating(bus_data.get('star_rating')),
                    self._parse_price(bus_data.get('price')),
                    self._parse_seats(bus_data.get('seats_available'))
                )
                
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                logger.debug(f"Inserted bus: {bus_data.get('busname')}")
                return True
                
        except Error as e:
            logger.error(f"Error inserting bus data: {e}")
            return False
    
    def bulk_insert(self, bus_data_list: List[Dict]) -> Tuple[int, int]:
        """
        Bulk insert multiple bus records
        
        Args:
            bus_data_list: List of bus data dictionaries
        
        Returns:
            Tuple of (successful_inserts, failed_inserts)
        """
        query = """
            INSERT INTO bus_routes 
            (route_name, route_link, busname, bustype, departing_time, 
             duration, duration_minutes, reaching_time, star_rating, 
             price, seats_available)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        successful = 0
        failed = 0
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for bus_data in bus_data_list:
                    try:
                        values = (
                            bus_data.get('route_name', ''),
                            bus_data.get('route_link', ''),
                            bus_data.get('busname', ''),
                            bus_data.get('bustype', 'N/A'),
                            bus_data.get('departing_time', '00:00'),
                            bus_data.get('duration', 'N/A'),
                            bus_data.get('duration_minutes'),
                            bus_data.get('reaching_time', '00:00'),
                            self._parse_rating(bus_data.get('star_rating')),
                            self._parse_price(bus_data.get('price')),
                            self._parse_seats(bus_data.get('seats_available'))
                        )
                        
                        cursor.execute(query, values)
                        successful += 1
                        
                    except Error as e:
                        logger.warning(f"Failed to insert bus: {e}")
                        failed += 1
                
                conn.commit()
                cursor.close()
                logger.info(f"Bulk insert complete: {successful} successful, {failed} failed")
                
        except Error as e:
            logger.error(f"Error in bulk insert: {e}")
        
        return successful, failed
    
    def filter_buses(self, filters: Dict) -> pd.DataFrame:
        """
        Filter buses based on criteria
        
        Args:
            filters: Dictionary with filter criteria:
                - route_name: str or None
                - bustype: list or None
                - min_price: float or None
                - max_price: float or None
                - min_rating: float or None
                - min_seats: int or None
                - departure_time_start: str or None (HH:MM)
                - departure_time_end: str or None (HH:MM)
        
        Returns:
            Filtered data as pandas DataFrame
        """
        # Base query
        query = "SELECT * FROM bus_routes WHERE 1=1"
        params = []
        
        # Route name filter
        if filters.get('route_name') and filters['route_name'] != 'All':
            query += " AND route_name LIKE %s"
            params.append(f"%{filters['route_name']}%")
        
        # Bus type filter
        if filters.get('bustype') and len(filters['bustype']) > 0:
            placeholders = ','.join(['%s'] * len(filters['bustype']))
            query += f" AND bustype IN ({placeholders})"
            params.extend(filters['bustype'])
        
        # Price range filter
        if filters.get('min_price') is not None:
            query += " AND price >= %s"
            params.append(filters['min_price'])
        
        if filters.get('max_price') is not None:
            query += " AND price <= %s"
            params.append(filters['max_price'])
        
        # Rating filter
        if filters.get('min_rating') is not None:
            query += " AND star_rating >= %s"
            params.append(filters['min_rating'])
        
        # Seats filter
        if filters.get('min_seats') is not None:
            query += " AND seats_available >= %s"
            params.append(filters['min_seats'])
        
        # Departure time filter
        if filters.get('departure_time_start'):
            query += " AND departing_time >= %s"
            params.append(filters['departure_time_start'])
        
        if filters.get('departure_time_end'):
            query += " AND departing_time <= %s"
            params.append(filters['departure_time_end'])
        
        # Order by
        query += " ORDER BY departing_time ASC"
        
        try:
            with self.get_connection() as conn:
                df = pd.read_sql(query, conn, params=params)
                logger.info(f"Filter returned {len(df)} results")
                return df
        except Error as e:
            logger.error(f"Error filtering buses: {e}")
            return pd.DataFrame()
    
    def get_all_routes(self) -> List[str]:
        """Get list of unique route names"""
        query = "SELECT DISTINCT route_name FROM bus_routes ORDER BY route_name"
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                routes = [row[0] for row in cursor.fetchall()]
                cursor.close()
                return routes
        except Error as e:
            logger.error(f"Error fetching routes: {e}")
            return []
    
    def get_all_bustypes(self) -> List[str]:
        """Get list of unique bus types"""
        query = "SELECT DISTINCT bustype FROM bus_routes WHERE bustype IS NOT NULL ORDER BY bustype"
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                bustypes = [row[0] for row in cursor.fetchall()]
                cursor.close()
                return bustypes
        except Error as e:
            logger.error(f"Error fetching bus types: {e}")
            return []
    
    def get_price_range(self) -> Tuple[float, float]:
        """Get minimum and maximum price from database"""
        query = "SELECT MIN(price), MAX(price) FROM bus_routes"
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()
                return (float(result[0] or 0), float(result[1] or 5000))
        except Error as e:
            logger.error(f"Error fetching price range: {e}")
            return (0.0, 5000.0)
    
    def get_statistics(self) -> Dict:
        """Get summary statistics"""
        query = """
            SELECT 
                COUNT(*) as total_buses,
                COUNT(DISTINCT route_name) as total_routes,
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(star_rating) as avg_rating,
                AVG(seats_available) as avg_seats
            FROM bus_routes
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()
                if result:
                    return {
                        'total_buses': int(result[0] or 0),
                        'total_routes': int(result[1] or 0),
                        'avg_price': float(result[2] or 0),
                        'min_price': float(result[3] or 0),
                        'max_price': float(result[4] or 0),
                        'avg_rating': float(result[5] or 0),
                        'avg_seats': float(result[6] or 0)
                    }
                return {}
        except Error as e:
            logger.error(f"Error fetching statistics: {e}")
            return {}
    
    def log_scraping_job(self, route_url: str, status: str, 
                        buses_scraped: int = 0, error_message: str = None) -> int:
        """
        Log scraping job to database
        
        Returns:
            Log ID
        """
        query = """
            INSERT INTO scraping_logs (route_url, status, buses_scraped, error_message)
            VALUES (%s, %s, %s, %s)
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (route_url, status, buses_scraped, error_message))
                log_id = cursor.lastrowid
                conn.commit()
                cursor.close()
                return log_id
        except Error as e:
            logger.error(f"Error logging scraping job: {e}")
            return -1
    
    def update_scraping_log(self, log_id: int, status: str, 
                           buses_scraped: int = None, error_message: str = None):
        """Update scraping log status"""
        query = """
            UPDATE scraping_logs 
            SET status = %s, buses_scraped = COALESCE(%s, buses_scraped), 
                error_message = %s, completed_at = NOW()
            WHERE id = %s
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (status, buses_scraped, error_message, log_id))
                conn.commit()
                cursor.close()
        except Error as e:
            logger.error(f"Error updating scraping log: {e}")
    
    def clear_all_data(self):
        """Clear all bus data (use with caution!)"""
        query = "DELETE FROM bus_routes"
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                cursor.close()
                logger.warning("All bus data cleared from database")
        except Error as e:
            logger.error(f"Error clearing data: {e}")
    
    # Helper methods
    def _parse_rating(self, rating_str) -> Optional[float]:
        """Parse rating string to float"""
        if not rating_str or rating_str == 'N/A':
            return None
        try:
            rating = float(rating_str)
            return rating if 0 <= rating <= 5 else None
        except:
            return None
    
    def _parse_price(self, price_str) -> Optional[float]:
        """Parse price string to float"""
        if not price_str or price_str == 'N/A':
            return None
        try:
            import re
            cleaned = re.sub(r'[₹,\s]', '', str(price_str))
            return float(cleaned)
        except:
            return None
    
    def _parse_seats(self, seats_str) -> Optional[int]:
        """Parse seats string to int"""
        if not seats_str or seats_str == 'N/A':
            return None
        try:
            import re
            match = re.search(r'(\d+)', str(seats_str))
            return int(match.group(1)) if match else None
        except:
            return None
    
    def close(self):
        """Close all connections in the pool"""
        try:
            if self.pool:
                # Note: MySQL connection pool doesn't have a direct close method
                # Connections will be closed automatically
                logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")


# Example usage
if __name__ == "__main__":
    # Test configuration
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'redbus_db',
        'user': 'redbus_db',
        'password': '992499',
        'pool_size': 5
    }
    
    # Initialize database manager
    db = DatabaseManager(config)
    
    # Test connection
    if db.test_connection():
        print("✅ Database connection successful")
        
        # Test statistics
        stats = db.get_statistics()
        print(f"📊 Statistics: {stats}")
    else:
        print("❌ Database connection failed")
