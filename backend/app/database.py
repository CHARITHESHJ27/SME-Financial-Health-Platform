from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine.url import make_url
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set."
    )

# DEBUG: Show what Render is actually using
url = make_url(DATABASE_URL)

logger.info("=" * 50)
logger.info(f"DB USER: {url.username}")
logger.info(f"DB HOST: {url.host}")
logger.info(f"DB PORT: {url.port}")
logger.info(f"DB DATABASE: {url.database}")
logger.info("=" * 50)


def create_database_engine():
    """Create PostgreSQL database engine"""

    try:
        logger.info("Using PostgreSQL database")

        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            future=True
        )

        # Test database connection
        with engine.connect():
            logger.info("Database connection successful")

        return engine

    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


# Create engine
engine = create_database_engine()

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base model
Base = declarative_base()


def get_db():
    """Database session dependency"""
    db = SessionLocal()

    try:
        yield db

    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise

    finally:
        db.close()