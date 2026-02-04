from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Database URL from environment variable or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sme_financial_health.db")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_engine():
    """Create database engine with proper configuration"""
    try:
        if DATABASE_URL.startswith("sqlite"):
            logger.info("Using SQLite database")
            engine = create_engine(
                DATABASE_URL, 
                connect_args={"check_same_thread": False},
                pool_pre_ping=True
            )
        else:
            logger.info("Using PostgreSQL database")
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=5,
                max_overflow=10
            )
        
        # Test connection
        with engine.connect() as conn:
            logger.info("Database connection successful")
        
        return engine
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.info("Falling back to SQLite")
        fallback_url = "sqlite:///./sme_financial_health.db"
        return create_engine(
            fallback_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True
        )

# Create engine
engine = create_database_engine()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    """Dependency to get DB session with error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise e
    finally:
        db.close()