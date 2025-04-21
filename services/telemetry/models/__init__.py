"""
Database models package for the Portfolio Telemetry service.
"""
import os
import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models.database import Base, PortfolioCompany, FinancialMetric, FollowOnDecision, CompanySector, CompanyStage, TriggerType

# Configure logging
logger = logging.getLogger(__name__)

# Get database connection string from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create database engine
engine = create_engine(DATABASE_URL) if DATABASE_URL else None

if engine:
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
else:
    logger.warning("No DATABASE_URL provided, database connection not initialized")
    # Create dummy session factory for testing
    SessionLocal = None

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get a database session.
    
    Returns:
        Database session
    """
    if SessionLocal is None:
        raise RuntimeError("Database connection not initialized")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

__all__ = ["PortfolioCompany", "FinancialMetric", "FollowOnDecision", "CompanySector", "CompanyStage", "TriggerType", "get_db"]