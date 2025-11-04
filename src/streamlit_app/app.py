"""
RedBus Data Analysis - Streamlit Application
Interactive web interface for filtering and analyzing bus data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from scraper.utils import load_config

# Page configuration
st.set_page_config(
    page_title="RedBus Bus Search & Analysis",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
    }
    h1 {
        color: #d84e55;
    }
    .filter-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    try:
        config = load_config()
        st.session_state.db = DatabaseManager(config['database'])
        st.session_state.config_loaded = True
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        st.session_state.config_loaded = False

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🚌 RedBus Bus Search & Analysis")
    st.markdown("Find and analyze bus routes across India")
with col2:
    st.image("https://img.icons8.com/color/96/000000/bus.png", width=80)

st.markdown("---")

# Check database connection
if not st.session_state.config_loaded:
    st.error("⚠️ Database not connected. Please check configuration.")
    st.stop()

db = st.session_state.db

# Verify connection
if not db.test_connection():
    st.error("❌ Database connection failed. Please check your database settings.")
    st.stop()

# Sidebar - Filters
st.sidebar.header("🔍 Filter Options")
st.sidebar.markdown("---")

# Get filter options from database
routes = ["All"] + db.get_all_routes()
bustypes = db.get_all_bustypes()
min_price_db, max_price_db = db.get_price_range()

# Filter 1: Route Selection
st.sidebar.subheader("📍 Route")
selected_route = st.sidebar.selectbox(
    "Select Route",
    routes,
    help="Choose a specific route or 'All' for all routes"
)

# Filter 2: Bus Type
st.sidebar.subheader("🚍 Bus Type")
selected_bustypes = st.sidebar.multiselect(
    "Select Bus Types",
    bustypes,
    default=[],
    help="Select one or more bus types"
)

# Filter 3: Price Range
st.sidebar.subheader("💰 Price Range")
price_range = st.sidebar.slider(
    "Select Price Range (₹)",
    min_value=int(min_price_db),
    max_value=int(max_price_db),
    value=(int(min_price_db), int(max_price_db)),
    step=50,
    help="Filter buses by ticket price"
)

# Filter 4: Star Rating
st.sidebar.subheader("⭐ Minimum Rating")
min_rating = st.sidebar.slider(
    "Minimum Star Rating",
    min_value=0.0,
    max_value=5.0,
    value=0.0,
    step=0.5,
    help="Filter buses by minimum passenger rating"
)

# Filter 5: Seat Availability
st.sidebar.subheader("💺 Seat Availability")
min_seats = st.sidebar.number_input(
    "Minimum Seats Available",
    min_value=0,
    max_value=50,
    value=0,
    step=1,
    help="Filter buses by minimum available seats"
)

# Additional filters
st.sidebar.subheader("🕐 Departure Time (Optional)")
use_time_filter = st.sidebar.checkbox("Filter by departure time")

departure_time_start = None
departure_time_end = None

if use_time_filter:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        departure_time_start = st.time_input("From", value=None)
    with col2:
        departure_time_end = st.time_input("To", value=None)

st.sidebar.markdown("---")

# Apply Filters Button
apply_filters = st.sidebar.button("🔍 Apply Filters", type="primary", use_container_width=True)

# Reset Filters Button
if st.sidebar.button("🔄 Reset Filters", use_container_width=True):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use filters to narrow down your search and find the perfect bus!")

# Main Content Area
if apply_filters:
    # Prepare filter dictionary
    filters = {
        'route_name': selected_route if selected_route != "All" else None,
        'bustype': selected_bustypes if selected_bustypes else None,
        'min_price': price_range[0],
        'max_price': price_range[1],
        'min_rating': min_rating,
        'min_seats': min_seats,
        'departure_time_start': departure_time_start.strftime("%H:%M") if departure_time_start else None,
        'departure_time_end': departure_time_end.strftime("%H:%M") if departure_time_end else None
    }
    
    # Get filtered data
    with st.spinner("🔍 Searching for buses..."):
        df = db.filter_buses(filters)
    
    # Display results
    if len(df) == 0:
        st.warning("😕 No buses found matching your criteria. Try adjusting the filters.")
    else:
        # Statistics Section
        st.subheader("📊 Search Results Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Buses",
                len(df),
                help="Number of buses matching your filters"
            )
        
        with col2:
            avg_price = df['price'].mean()
            st.metric(
                "Avg Price",
                f"₹{avg_price:.0f}",
                help="Average ticket price"
            )
        
        with col3:
            avg_rating = df['star_rating'].mean()
            st.metric(
                "Avg Rating",
                f"{avg_rating:.1f} ⭐",
                help="Average passenger rating"
            )
        
        with col4:
            unique_routes = df['route_name'].nunique()
            st.metric(
                "Routes",
                unique_routes,
                help="Number of unique routes"
            )
        
        with col5:
            avg_seats = df['seats_available'].mean()
            st.metric(
                "Avg Seats",
                f"{avg_seats:.0f}",
                help="Average seats available"
            )
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Price Distribution")
            fig_price = px.histogram(
                df,
                x='price',
                nbins=20,
                title="Distribution of Bus Prices",
                labels={'price': 'Price (₹)', 'count': 'Number of Buses'},
                color_discrete_sequence=['#d84e55']
            )
            fig_price.update_layout(showlegend=False)
            st.plotly_chart(fig_price, use_container_width=True)
        
        with col2:
            st.subheader("🚍 Buses by Type")
            bustype_counts = df['bustype'].value_counts().reset_index()
            bustype_counts.columns = ['Bus Type', 'Count']
            
            fig_bustype = px.bar(
                bustype_counts,
                x='Bus Type',
                y='Count',
                title="Number of Buses by Type",
                color='Count',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_bustype, use_container_width=True)
        
        st.markdown("---")
        
        # Data Table
        st.subheader("📋 Bus Listings")
        
        # Sorting options
        col1, col2 = st.columns([2, 1])
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                ["Departure Time", "Price (Low to High)", "Price (High to Low)", "Rating (High to Low)"]
            )
        
        # Apply sorting
        if sort_by == "Departure Time":
            df = df.sort_values('departing_time')
        elif sort_by == "Price (Low to High)":
            df = df.sort_values('price')
        elif sort_by == "Price (High to Low)":
            df = df.sort_values('price', ascending=False)
        elif sort_by == "Rating (High to Low)":
            df = df.sort_values('star_rating', ascending=False)
        
        # Format dataframe for display
        display_df = df[[
            'busname', 'bustype', 'departing_time', 'reaching_time',
            'duration', 'price', 'star_rating', 'seats_available', 'route_name'
        ]].copy()
        
        display_df.columns = [
            'Bus Name', 'Type', 'Departure', 'Arrival',
            'Duration', 'Price (₹)', 'Rating', 'Seats', 'Route'
        ]
        
        # Display with custom formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            column_config={
                "Price (₹)": st.column_config.NumberColumn(
                    format="₹%.0f"
                ),
                "Rating": st.column_config.NumberColumn(
                    format="%.1f ⭐"
                )
            }
        )
        
        # Export functionality
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"redbus_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.button("🔄 Refresh Data", use_container_width=True)

else:
    # Initial view - Show overall statistics
    st.info("👈 Use the filters in the sidebar to search for buses")
    
    # Get overall statistics
    stats = db.get_statistics()
    
    if stats:
        st.subheader("📊 Overall Database Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Buses", f"{stats.get('total_buses', 0):,}")
        
        with col2:
            st.metric("Total Routes", f"{stats.get('total_routes', 0):,}")
        
        with col3:
            avg_price = stats.get('avg_price', 0)
            st.metric("Avg Price", f"₹{avg_price:.0f}")
        
        with col4:
            avg_rating = stats.get('avg_rating', 0)
            st.metric("Avg Rating", f"{avg_rating:.1f} ⭐")
        
        st.markdown("---")
        
        # Quick stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Price Range")
            min_p = stats.get('min_price', 0)
            max_p = stats.get('max_price', 0)
            st.write(f"Minimum: ₹{min_p:.0f}")
            st.write(f"Maximum: ₹{max_p:.0f}")
        
        with col2:
            st.subheader("💺 Average Seats")
            avg_s = stats.get('avg_seats', 0)
            st.write(f"Average: {avg_s:.0f} seats per bus")
    
    # Recent buses
    st.markdown("---")
    st.subheader("🕒 Recently Added Buses")
    
    recent_query = "SELECT * FROM bus_routes ORDER BY scraped_at DESC LIMIT 10"
    try:
        with db.get_connection() as conn:
            recent_df = pd.read_sql(recent_query, conn)
        
        if len(recent_df) > 0:
            display_recent = recent_df[[
                'busname', 'bustype', 'departing_time', 'price', 'star_rating', 'route_name'
            ]].copy()
            display_recent.columns = ['Bus Name', 'Type', 'Departure', 'Price (₹)', 'Rating', 'Route']
            st.dataframe(display_recent, use_container_width=True)
        else:
            st.info("No buses in database yet. Run the scraper first!")
    
    except Exception as e:
        st.error(f"Error loading recent buses: {e}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🚌 RedBus Data Analysis Platform | Built with Streamlit & Selenium</p>
        <p>Data scraped from <a href='https://www.redbus.in' target='_blank'>RedBus.in</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
