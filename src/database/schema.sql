-- RedBus Database Schema for PostgreSQL
-- Note: Run this after creating the database or let the application create tables

-- Main bus routes table
CREATE TABLE IF NOT EXISTS bus_routes (
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

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_route_name ON bus_routes (route_name);
CREATE INDEX IF NOT EXISTS idx_bustype ON bus_routes (bustype);
CREATE INDEX IF NOT EXISTS idx_price ON bus_routes (price);
CREATE INDEX IF NOT EXISTS idx_rating ON bus_routes (star_rating);
CREATE INDEX IF NOT EXISTS idx_departure ON bus_routes (departing_time);
CREATE INDEX IF NOT EXISTS idx_seats ON bus_routes (seats_available);
CREATE INDEX IF NOT EXISTS idx_scraped ON bus_routes (scraped_at);

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists and create new one
DROP TRIGGER IF EXISTS update_bus_routes_updated_at ON bus_routes;
CREATE TRIGGER update_bus_routes_updated_at
BEFORE UPDATE ON bus_routes
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Table for storing scraping logs
CREATE TABLE IF NOT EXISTS scraping_logs (
    id SERIAL PRIMARY KEY,
    route_url TEXT,
    status VARCHAR(20),
    buses_scraped INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);

-- Create indexes for scraping_logs
CREATE INDEX IF NOT EXISTS idx_status ON scraping_logs (status);
CREATE INDEX IF NOT EXISTS idx_started ON scraping_logs (started_at);

-- View for quick statistics
CREATE OR REPLACE VIEW bus_statistics AS
SELECT 
    bustype,
    COUNT(*) as total_buses,
    AVG(price) as avg_price,
    AVG(star_rating) as avg_rating,
    AVG(seats_available) as avg_seats
FROM bus_routes
GROUP BY bustype;
