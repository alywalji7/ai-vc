"""
SQLAlchemy models for the Portfolio Telemetry service.
"""
import os
from typing import Generator

from .database import (
    Base, PortfolioCompany, FinancialMetric, FollowOnDecision, 
    CompanyStage, CompanySector, initialize_db
)

from sqlalchemy.orm import Session

# Initialize database
engine, SessionLocal = initialize_db(os.environ.get("DATABASE_URL"))

def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()