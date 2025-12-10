# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Import settings so tests can access app.database.settings
from app.core.config import get_settings
settings = get_settings()

# Check if we're in test mode
USE_TEST_DB = os.getenv("TESTING") == "true"

if USE_TEST_DB:
    print("⚠️ USING TEST DATABASE")
    DATABASE_URL = "sqlite:///./test.db"
else:
    # Use settings.DATABASE_URL for production
    DATABASE_URL = settings.DATABASE_URL if hasattr(settings, 'DATABASE_URL') else "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_engine():
    """Return the database engine."""
    return engine

def get_sessionmaker(engine_param=None):
    """Return the sessionmaker for the given engine, or the default SessionLocal."""
    if engine_param is None:
        return SessionLocal
    return sessionmaker(autocommit=False, autoflush=False, bind=engine_param)

# ----------- TEST DATABASE FOR PYTEST -----------
TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)