-- Finexri Production DB Initialization
-- Runs automatically on first postgres container start

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for fast text search

-- Performance indexes (tables created by SQLAlchemy on app start)
-- These run after app startup via db_migrate.sh

-- Timezone
SET timezone = 'Asia/Kolkata';
