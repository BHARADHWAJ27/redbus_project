# 🚌 RedBus Data Scraping & Analysis Platform

A comprehensive data platform for scraping, storing, and analyzing bus transportation data from RedBus across 10 Indian state transport services.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

## 📋 Table of Contents
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Usage](#-usage)
- [Technologies](#-technologies)
- [Project Deliverables](#-project-deliverables)
- [Guidelines Compliance](#-guidelines-compliance)

## ✨ Features

### 🔍 Web Scraping
- Automated scraping from 10 state transport services
- Selenium WebDriver with anti-detection measures
- Dual parsing strategy (container & element-based)
- Error recovery and retry mechanism
- Screenshot capture for debugging

### 💾 Database Management
- PostgreSQL with connection pooling
- Optimized indexes for fast queries
- Data validation and cleaning
- Transaction management

### 📊 Interactive Dashboard
- 6 filter categories (Route, Bus Type, Price, Rating, Seats, Time)
- Real-time data filtering
- Interactive visualizations (Plotly charts)
- CSV export functionality
- Responsive design

### 📈 Analytics
- Summary statistics dashboard
- Price and rating analysis
- Availability tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- Chrome Browser
- Git

### Installation

```bash
# 1. Navigate to project
cd "e:\PROJECTS\scrapper (RB)\redbus_project"

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (.env file)
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=redbus_db

# 5. Setup database
python main.py --mode setup

# 6. Run scraper
python main.py --mode scrape

# 7. Launch app
python main.py --mode app
```

## 📁 Project Structure

```
redbus_project/
├── main.py                      # Main orchestrator & CLI
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
├── README.md                   # Project overview
├── DOCUMENTATION.md            # Technical documentation
│
├── config/
│   └── config.yaml             # Application configuration
│
├── src/
│   ├── database/
│   │   ├── db_manager.py       # Database operations
│   │   └── schema.sql          # PostgreSQL schema
│   ├── scraper/
│   │   ├── bus_scraper.py      # Web scraping logic
│   │   └── utils.py            # Utility functions
│   └── streamlit_app/
│       └── app.py              # Streamlit application
│
├── data/                        # Data storage
├── logs/                        # Application logs
├── output/                      # Screenshots
└── tests/                       # Unit tests
```

## 📖 Usage

### Command Line Interface

```bash
# Setup database tables
python main.py --mode setup

# Run web scraper (30-60 minutes)
python main.py --mode scrape

# Launch Streamlit app
python main.py --mode app

# View statistics
python main.py --mode stats
```

### Current Project Status

✅ **Database Setup**: Completed
✅ **Web Scraper**: Successfully collected 815 buses from 61 routes
✅ **Streamlit App**: Fully functional at http://localhost:8501
✅ **Statistics**: Working dashboard

### States Covered
1. APSRTC (Andhra Pradesh)
2. TSRTC (Telangana)
3. KSRTC Kerala (Kerala)
4. RSRTC (Rajasthan)
5. UPSRTC (Uttar Pradesh)
6. PEPSU (Punjab)
7. HRTC (Himachal Pradesh)
8. ASTC (Assam)
9. WBTC (West Bengal)
10. KAAC (Meghalaya)

### Database Statistics
```
📊 Total Buses:        815
🛣️  Total Routes:       61
💰 Average Price:      ₹665.96
💵 Minimum Price:      ₹50.00
💸 Maximum Price:      ₹5555.00
⭐ Average Rating:     3.92/5.0
💺 Average Seats:      29.0
```

## � Technologies

- **Python 3.12**: Core language
- **Selenium 4.15**: Web scraping
- **PostgreSQL 12+**: Database
- **Streamlit 1.28**: Web framework
- **Pandas 2.1**: Data processing
- **Plotly 5.17**: Visualizations
- **psycopg2 2.9**: PostgreSQL adapter
- **BeautifulSoup4 4.12**: HTML parsing

## � Project Deliverables

### ✅ 1. Source Code
- **Python scripts for data scraping** (`src/scraper/bus_scraper.py`)
  - 450+ lines with complete scraping logic
  - Selenium-based with anti-detection
  - Dual parsing strategies
  - Error handling and logging

- **SQL database interaction** (`src/database/db_manager.py`)
  - 500+ lines with database operations
  - Connection pooling implementation
  - CRUD operations
  - Query optimization

- **Streamlit application** (`src/streamlit_app/app.py`)
  - 380+ lines interactive dashboard
  - 6 filter categories
  - Interactive visualizations
  - CSV export functionality

### ✅ 2. Documentation
- **README.md**: Quick start guide, features, usage
- **DOCUMENTATION.md**: Comprehensive technical documentation
  - Architecture overview
  - Data collection process
  - Database design details
  - API reference
  - Code explanations
  - Best practices
  - Troubleshooting guide

- **Inline Comments**: Throughout all source files
- **Docstrings**: All functions and classes documented
  ```python
  def function_name(param: Type) -> ReturnType:
      """
      Brief description of function.
      
      Args:
          param (Type): Description of parameter
      
      Returns:
          ReturnType: Description of return value
      """
  ```

### ✅ 3. Database Schema
- **schema.sql** (`src/database/schema.sql`)
  - Complete PostgreSQL schema
  - Table definitions:
    - `bus_routes`: 14 fields with constraints
    - `scraping_logs`: Scraping audit trail
    - `bus_statistics`: Aggregated view
  - 7 indexes for optimization
  - Triggers for automatic updates
  - Fully documented with comments

### ✅ 4. Streamlit Application
- **Live Application**: http://localhost:8501
- **Features Demonstrated**:
  - Data filtering with 6 categories
  - Real-time search results
  - Interactive charts and graphs
  - Statistics dashboard
  - CSV export
  
- **Screenshots Available**: `output/` directory
  - Scraping process
  - Bus data display
  - Filter functionality
  - Visualizations

## 🏗 Project Guidelines Compliance

### ✅ Coding Standards (PEP 8)

#### Followed Guidelines:
1. **Naming Conventions**:
   - Functions/Variables: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPERCASE`
   ```python
   class DatabaseManager:  # PascalCase
       def get_statistics(self):  # snake_case
           MAX_RETRIES = 3  # UPPERCASE constant
   ```

2. **Line Length**: Max 88 characters (Black formatter compatible)
3. **Imports**: Organized and grouped properly
4. **Whitespace**: Consistent spacing around operators
5. **Indentation**: 4 spaces (no tabs)
6. **Comments**: Clear, concise explanations

#### Code Quality Features:
- Type hints for function parameters and returns
- Comprehensive docstrings (Google style)
- Error handling with specific exceptions
- Logging throughout application
- No unused imports or variables

### ✅ Version Control (Git)

#### Git Best Practices:
1. **Regular Commits**: Incremental changes tracked
2. **Descriptive Messages**: Clear commit descriptions
3. **.gitignore**: Excludes:
   - `__pycache__/`
   - `*.pyc`
   - `.env`
   - `venv/`
   - `.vscode/`
   - `logs/`

4. **Branch Structure** (if using):
   - `main`: Production-ready code
   - `develop`: Integration branch
   - `feature/*`: Feature branches

### ✅ Best Practices

#### 1. Modular Code
- Separated concerns: scraper, database, UI
- Each module has single responsibility
- Reusable functions in utils.py

#### 2. Reusable Code
```python
# Example: Utility functions
def parse_time(time_str: str) -> str:
    """Reusable time parsing function"""
    pass

def parse_price(price_str: str) -> float:
    """Reusable price parsing function"""
    pass
```

#### 3. Comments & Docstrings
- **Module-level**: Purpose and usage
- **Class-level**: Description and attributes
- **Function-level**: Parameters, returns, raises
- **Inline**: Complex logic explanation

Example:
```python
"""
Database Manager Module
Handles all database operations for RedBus project
"""

class DatabaseManager:
    """
    Manages all database operations for RedBus data
    
    Features:
    - Connection pooling
    - CRUD operations
    - Filtering and querying
    - Transaction management
    """
    
    def filter_buses(self, filters: Dict) -> List[Dict]:
        """
        Filter buses based on multiple criteria
        
        Args:
            filters (Dict): Dictionary containing filter criteria
                - route_name (str, optional): Route name
                - bustype (List[str], optional): Bus types
                - min_price (float, optional): Minimum price
                - max_price (float, optional): Maximum price
        
        Returns:
            List[Dict]: List of filtered bus records
        
        Raises:
            DatabaseError: If query execution fails
        """
```

#### 4. Error Handling
```python
try:
    # Database operation
    result = db.execute_query(query)
except psycopg2.Error as e:
    logger.error(f"Database error: {e}")
    raise DatabaseError(f"Failed to execute query: {e}")
finally:
    # Cleanup
    if conn:
        db.pool.putconn(conn)
```

#### 5. Configuration Management
- External configuration in `config.yaml`
- Environment variables in `.env`
- No hardcoded credentials
- Easy to modify without code changes

#### 6. Logging
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error messages")
logger.critical("Critical issues")
```

## 📚 Complete Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for:
- Architecture details
- Data collection methodology
- Database design specifications
- API reference
- Performance optimization
- Troubleshooting guide

## 🧪 Testing

### Run Tests
```bash
pytest tests/
```

### Test Coverage
- Database operations
- Data validation
- Configuration loading
- Utility functions

## 🐛 Troubleshooting

### Database Connection
```bash
# Check PostgreSQL service
# Verify credentials in .env
# Test connection manually
```

### Scraper Issues
```bash
# Update Chrome browser
# Check internet connection
# Increase timeout in config.yaml
```

### Application Errors
```bash
# Check logs in logs/app.log
# Verify all dependencies installed
# Ensure database has data
```

## 🤝 Contributing

Contributions welcome! Please:
1. Follow PEP 8 guidelines
2. Add docstrings to functions
3. Include type hints
4. Write unit tests
5. Update documentation

## 📄 License

Educational purposes only. Respect RedBus terms of service.

## 👥 Authors

- **Project Team** - *Initial work*

## 🙏 Acknowledgments

- RedBus for data source
- Selenium community
- Streamlit team
- PostgreSQL community

---

## 📊 Project Metrics

- **Total Lines of Code**: ~2,000+
- **Python Files**: 8
- **Functions**: 50+
- **Classes**: 3
- **Database Tables**: 2 + 1 view
- **States Covered**: 10
- **Buses Scraped**: 815+
- **Routes**: 61+

---

<div align="center">

**Made with ❤️ for the bus travel community**

⭐ **Star this repo if you find it useful!** ⭐

</div>

---

*Last Updated: November 4, 2025*
*Version: 1.0.0*
