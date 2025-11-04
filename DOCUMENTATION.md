# RedBus Data Scraping & Analysis Platform - Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Installation Guide](#installation-guide)
4. [Code Structure](#code-structure)
5. [Data Collection Process](#data-collection-process)
6. [Database Design](#database-design)
7. [Application Usage](#application-usage)
8. [API Reference](#api-reference)

---

## Project Overview

### Purpose
This project is a comprehensive bus transportation data platform that scrapes, stores, and analyzes bus route information from RedBus, providing users with an interactive web interface to search and filter bus services.

### Key Features
- **Automated Web Scraping**: Selenium-based scraper for 10 state transport services
- **PostgreSQL Database**: Robust data storage with indexing for performance
- **Interactive Dashboard**: Streamlit-based web application with filtering and visualization
- **Data Analysis**: Statistical insights on pricing, ratings, and availability

### Technology Stack
- **Language**: Python 3.12
- **Web Scraping**: Selenium WebDriver, BeautifulSoup4
- **Database**: PostgreSQL with psycopg2
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly

---

## Architecture

### System Design
```
┌─────────────────┐
│   RedBus.in     │  (Data Source)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Web Scraper    │  (Selenium + BeautifulSoup)
│  bus_scraper.py │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  (Data Storage)
│   redbus_db     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit App  │  (User Interface)
│     app.py      │
└─────────────────┘
```

### Component Interaction
1. **Scraper Module** (`src/scraper/`):
   - Connects to RedBus website
   - Extracts bus route data
   - Validates and cleans data
   - Stores in database

2. **Database Module** (`src/database/`):
   - Manages connections (connection pooling)
   - CRUD operations
   - Query optimization
   - Statistics generation

3. **Streamlit Module** (`src/streamlit_app/`):
   - User interface
   - Data filtering
   - Visualizations
   - CSV export

---

## Installation Guide

### Prerequisites
```bash
- Python 3.12+
- PostgreSQL 12+
- Chrome Browser (for Selenium)
- Git
```

### Step-by-Step Setup

#### 1. Clone Repository
```bash
git clone <repository-url>
cd redbus_project
```

#### 2. Create Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
Create `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=redbus_db
LOG_LEVEL=INFO
```

#### 5. Setup Database
```bash
python main.py --mode setup
```

#### 6. Run Scraper
```bash
python main.py --mode scrape
```

#### 7. Launch Application
```bash
python main.py --mode app
```

---

## Code Structure

### Directory Layout
```
redbus_project/
├── main.py                 # Main orchestrator
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── config/
│   └── config.yaml        # Application configuration
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py  # Database operations
│   │   └── schema.sql     # Database schema
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── bus_scraper.py # Web scraping logic
│   │   └── utils.py       # Helper functions
│   └── streamlit_app/
│       ├── __init__.py
│       └── app.py         # Streamlit application
├── data/
│   ├── raw/               # Raw scraped data
│   └── processed/         # Processed data
├── logs/                  # Application logs
├── output/                # Screenshots
└── tests/                 # Unit tests
```

### Module Descriptions

#### 1. main.py
**Purpose**: Entry point and orchestrator for all operations

**Functions**:
- `run_scraper(config)`: Executes web scraping
- `run_app(config)`: Launches Streamlit application
- `show_statistics(config)`: Displays database statistics
- `setup_database(config)`: Creates database tables

**Usage**:
```python
python main.py --mode [setup|scrape|app|stats]
```

#### 2. src/database/db_manager.py
**Purpose**: Database connection and operations management

**Key Classes**:
- `DatabaseManager`: Handles all database operations

**Key Methods**:
```python
def __init__(self, config: Dict)
    """Initialize with connection pooling"""

def create_tables(self)
    """Create database tables from schema.sql"""

def insert_bus_data(self, bus_data: Dict) -> bool
    """Insert single bus record"""

def bulk_insert(self, bus_list: List[Dict]) -> Tuple[int, int]
    """Insert multiple records efficiently"""

def filter_buses(self, filters: Dict) -> List[Dict]
    """Filter buses based on criteria"""

def get_statistics(self) -> Dict
    """Get summary statistics"""
```

**Design Patterns**:
- Connection Pooling: Efficient resource management
- Context Manager: Safe connection handling
- Error Handling: Comprehensive exception management

#### 3. src/scraper/bus_scraper.py
**Purpose**: Web scraping implementation

**Key Classes**:
- `BusScraper`: Main scraping logic

**Key Methods**:
```python
def setup_driver(self)
    """Configure Selenium WebDriver with anti-detection"""

def scrape_all_states(self) -> int
    """Scrape all configured state transport services"""

def scrape_route(self, route: str) -> int
    """Scrape single bus route"""

def _parse_bus_data(self, container) -> Dict
    """Extract data from HTML element"""
```

**Scraping Strategy**:
1. Navigate to state transport page
2. Extract route links
3. For each route:
   - Load route page
   - Wait for dynamic content
   - Extract bus information
   - Validate data
   - Save to database

**Anti-Detection Measures**:
- User-Agent rotation
- Random delays
- ChromeDriver options for stealth

#### 4. src/scraper/utils.py
**Purpose**: Utility functions and helpers

**Key Functions**:
```python
def load_config(config_path: str) -> Dict
    """Load YAML configuration with environment variables"""

def setup_logging(log_level: str, log_file: str)
    """Configure logging system"""

def validate_bus_data(bus_data: Dict) -> Tuple[bool, str]
    """Validate scraped data before storage"""

def parse_time(time_str: str) -> str
    """Parse and standardize time format"""

def parse_price(price_str: str) -> float
    """Extract price from string"""

def calculate_duration_minutes(duration_str: str) -> int
    """Convert duration to minutes"""
```

#### 5. src/streamlit_app/app.py
**Purpose**: Interactive web application

**Key Sections**:
1. **Configuration**: Page setup and styling
2. **Database Connection**: Connection management
3. **Filters**: Six filter categories
4. **Data Display**: Formatted bus listing
5. **Visualizations**: Charts and graphs
6. **Statistics**: Summary dashboard

**Features**:
- Route selection dropdown
- Bus type multi-select
- Price range slider
- Rating filter
- Seats availability filter
- Departure time range
- Real-time filtering
- CSV export
- Interactive charts

---

## Data Collection Process

### Scraping Workflow

#### Phase 1: Initialization
```python
# Configure WebDriver
driver = setup_driver()
driver.get(state_transport_url)
```

#### Phase 2: Route Extraction
```python
# Find all route links on landing page
route_links = driver.find_elements(By.CLASS_NAME, "route_link")

# Extract route information
for link in route_links:
    route_name = link.text
    route_url = link.get_attribute("href")
```

#### Phase 3: Bus Data Extraction
```python
# Navigate to route page
driver.get(route_url)

# Wait for dynamic content
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "bus-item"))
)

# Extract bus details
buses = driver.find_elements(By.CLASS_NAME, "bus-item")
for bus in buses:
    data = extract_bus_data(bus)
```

#### Phase 4: Data Validation
```python
def validate_bus_data(bus_data):
    required_fields = ['route_name', 'busname', 'departing_time', 
                       'reaching_time', 'price']
    
    for field in required_fields:
        if not bus_data.get(field):
            return False, f"Missing {field}"
    
    # Validate data types and ranges
    if not (0 <= bus_data.get('star_rating', 0) <= 5):
        return False, "Invalid rating"
    
    return True, "Valid"
```

#### Phase 5: Data Storage
```python
# Bulk insert for efficiency
success, failed = db.bulk_insert(validated_buses)
logger.info(f"Inserted {success} buses, {failed} failed")
```

### Data Fields Collected

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| route_name | TEXT | Origin to destination | "Hyderabad to Vijayawada" |
| route_link | TEXT | RedBus URL | "https://..." |
| busname | TEXT | Bus operator name | "APSRTC" |
| bustype | VARCHAR(50) | Bus category | "AC Sleeper" |
| departing_time | TIME | Departure time | "14:30:00" |
| duration | VARCHAR(20) | Journey duration | "6h 30m" |
| duration_minutes | INT | Duration in minutes | 390 |
| reaching_time | TIME | Arrival time | "21:00:00" |
| star_rating | FLOAT | User rating (0-5) | 4.2 |
| price | DECIMAL(10,2) | Ticket price | 650.00 |
| seats_available | INT | Available seats | 28 |
| scraped_at | TIMESTAMP | Scraping timestamp | "2025-11-04 07:17:19" |

### Data Quality Measures
1. **Validation**: Required field checks
2. **Cleaning**: Remove invalid characters
3. **Normalization**: Standardize formats
4. **Deduplication**: Prevent duplicate entries
5. **Error Logging**: Track scraping issues

---

## Database Design

### Schema Overview

#### Table: bus_routes
**Purpose**: Store bus route and service information

```sql
CREATE TABLE bus_routes (
    id SERIAL PRIMARY KEY,
    route_name TEXT NOT NULL,
    route_link TEXT NOT NULL,
    busname TEXT NOT NULL,
    bustype VARCHAR(50),
    departing_time TIME NOT NULL,
    duration VARCHAR(20),
    duration_minutes INT,
    reaching_time TIME NOT NULL,
    star_rating FLOAT CHECK (star_rating >= 0 AND star_rating <= 5),
    price DECIMAL(10, 2) NOT NULL,
    seats_available INT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_route_name`: Fast route search
- `idx_bustype`: Filter by bus type
- `idx_price`: Price range queries
- `idx_rating`: Rating filters
- `idx_departure`: Departure time filters
- `idx_seats`: Seat availability
- `idx_scraped`: Temporal queries

#### Table: scraping_logs
**Purpose**: Track scraping operations

```sql
CREATE TABLE scraping_logs (
    id SERIAL PRIMARY KEY,
    route_url TEXT,
    status VARCHAR(20),
    buses_scraped INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);
```

**Indexes**:
- `idx_status`: Filter by status
- `idx_started`: Temporal analysis

#### View: bus_statistics
**Purpose**: Aggregate statistics by bus type

```sql
CREATE VIEW bus_statistics AS
SELECT 
    bustype,
    COUNT(*) as total_buses,
    AVG(price) as avg_price,
    AVG(star_rating) as avg_rating,
    AVG(seats_available) as avg_seats
FROM bus_routes
GROUP BY bustype;
```

### Database Operations

#### Connection Pooling
```python
from psycopg2 import pool

self.pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    host=config['host'],
    port=config['port'],
    database=config['database'],
    user=config['user'],
    password=config['password']
)
```

**Benefits**:
- Reduced connection overhead
- Better resource management
- Improved performance

#### Query Optimization
```python
# Use parameterized queries
query = "SELECT * FROM bus_routes WHERE price BETWEEN %s AND %s"
cursor.execute(query, (min_price, max_price))

# Batch inserts
query = "INSERT INTO bus_routes (...) VALUES %s"
execute_values(cursor, query, data_list)
```

---

## Application Usage

### Command Line Interface

#### 1. Database Setup
```bash
python main.py --mode setup
```
**Output**:
- Creates database tables
- Sets up indexes
- Creates views
- Initializes triggers

#### 2. Run Scraper
```bash
python main.py --mode scrape
```
**Output**:
- Scrapes 10 state transport services
- Extracts ~30 routes per state
- Collects bus information
- Saves to database
- Duration: 30-60 minutes

#### 3. View Statistics
```bash
python main.py --mode stats
```
**Output**:
```
📊 Total Buses:        815
🛣️  Total Routes:       61
💰 Average Price:      ₹665.96
💵 Minimum Price:      ₹50.00
💸 Maximum Price:      ₹5555.00
⭐ Average Rating:     3.92/5.0
💺 Average Seats:      29.0
```

#### 4. Launch Web Application
```bash
python main.py --mode app
```
**Output**:
- Starts Streamlit server
- Opens browser at http://localhost:8501
- Provides interactive interface

### Web Application Features

#### Filter Options
1. **Route Filter**: Select origin-destination pair
2. **Bus Type Filter**: Choose AC/Non-AC, Seater/Sleeper
3. **Price Range**: Slider for min-max price
4. **Rating Filter**: Minimum star rating
5. **Seats Filter**: Minimum available seats
6. **Departure Time**: Time range selection

#### Visualizations
1. **Price Distribution**: Bar chart by bus type
2. **Rating Analysis**: Average ratings comparison
3. **Availability Trends**: Seat availability patterns

#### Data Export
- **CSV Download**: Export filtered results
- **Format**: Includes all fields
- **Usage**: Further analysis in Excel/Python

---

## API Reference

### DatabaseManager Class

#### Methods

##### `__init__(config: Dict)`
Initialize database manager with configuration.

**Parameters**:
- `config` (Dict): Database configuration
  - `host` (str): Database host
  - `port` (int): Database port
  - `database` (str): Database name
  - `user` (str): Username
  - `password` (str): Password

**Example**:
```python
config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'redbus_db',
    'user': 'postgres',
    'password': 'password'
}
db = DatabaseManager(config)
```

##### `filter_buses(filters: Dict) -> List[Dict]`
Filter buses based on criteria.

**Parameters**:
- `filters` (Dict): Filter criteria
  - `route_name` (str, optional): Route name
  - `bustype` (List[str], optional): Bus types
  - `min_price` (float, optional): Minimum price
  - `max_price` (float, optional): Maximum price
  - `min_rating` (float, optional): Minimum rating
  - `min_seats` (int, optional): Minimum seats
  - `departure_start` (str, optional): Start time
  - `departure_end` (str, optional): End time

**Returns**:
- List[Dict]: Filtered bus records

**Example**:
```python
filters = {
    'route_name': 'Hyderabad to Vijayawada',
    'bustype': ['AC Sleeper'],
    'min_price': 500,
    'max_price': 1000,
    'min_rating': 4.0
}
buses = db.filter_buses(filters)
```

### BusScraper Class

#### Methods

##### `__init__(config: Dict, db_manager: DatabaseManager)`
Initialize scraper with configuration and database.

**Parameters**:
- `config` (Dict): Scraping configuration
- `db_manager` (DatabaseManager): Database manager instance

##### `scrape_all_states() -> int`
Scrape all configured states.

**Returns**:
- int: Total buses scraped

**Example**:
```python
scraper = BusScraper(config, db)
total = scraper.scrape_all_states()
print(f"Scraped {total} buses")
```

---

## Performance Optimization

### Database Optimizations
1. **Indexing**: Strategic indexes on filter columns
2. **Connection Pooling**: Reuse connections
3. **Bulk Operations**: Batch inserts
4. **Query Optimization**: Efficient WHERE clauses

### Scraping Optimizations
1. **Wait Strategies**: Explicit waits vs. implicit
2. **Parallel Processing**: Multiple routes simultaneously (future)
3. **Caching**: Store intermediate results
4. **Error Recovery**: Retry failed requests

### Application Optimizations
1. **Caching**: @st.cache_data for database queries
2. **Lazy Loading**: Load data on demand
3. **Pagination**: Display results in chunks (future)

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
**Error**: `connection to server at "localhost" failed`

**Solutions**:
- Verify PostgreSQL is running
- Check credentials in `.env`
- Verify port number (5432)

#### 2. Scraper Timeout
**Error**: `TimeoutException: Page load timeout`

**Solutions**:
- Increase timeout in config.yaml
- Check internet connection
- Verify RedBus website accessibility

#### 3. No Data in Application
**Error**: `No buses found matching your criteria`

**Solutions**:
- Run scraper: `python main.py --mode scrape`
- Check database: `python main.py --mode stats`
- Relax filter criteria

---

## Best Practices

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Keep functions small and focused

### Error Handling
```python
try:
    # Operation
    result = perform_operation()
except SpecificError as e:
    logger.error(f"Error: {e}")
    # Handle error
finally:
    # Cleanup
    cleanup_resources()
```

### Logging
```python
# Use appropriate log levels
logger.debug("Detailed information")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error messages")
```

### Testing
```python
def test_function():
    """Test function behavior"""
    # Arrange
    input_data = prepare_data()
    
    # Act
    result = function(input_data)
    
    # Assert
    assert result == expected_output
```

---

## Future Enhancements

1. **Booking Integration**: Direct booking from app
2. **Real-time Updates**: Live availability
3. **Price Predictions**: ML-based price forecasting
4. **User Authentication**: Personalized experience
5. **Mobile App**: React Native/Flutter
6. **API**: RESTful API for third-party integration
7. **Advanced Analytics**: Trend analysis, demand prediction
8. **Multi-language Support**: Hindi, Telugu, Tamil, etc.

---

## License
This project is for educational purposes.

## Contact
For questions or issues, please contact the development team.

---

*Last Updated: November 4, 2025*
