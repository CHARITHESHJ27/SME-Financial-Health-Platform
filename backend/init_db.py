#!/usr/bin/env python3
"""
Database initialization script for SME Financial Health Platform
Run this to create all required tables
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine
from app.models.schemas import Base
from app.database import DATABASE_URL

def init_database():
    """Initialize database with all tables"""
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = ['companies', 'financial_statements', 'financial_assessments', 'industry_benchmarks']
    
    for table in expected_tables:
        if table in tables:
            print(f"✅ Table '{table}' exists")
        else:
            print(f"❌ Table '{table}' missing")

if __name__ == "__main__":
    init_database()