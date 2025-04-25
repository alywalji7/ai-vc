"""
Database connection and model definitions for the upload service.
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

# Database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

class UploadedFile(Base):
    """Model for tracking uploaded files."""
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    lp_id = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, csv, xlsx
    s3_key = Column(String, nullable=False, unique=True)
    size_bytes = Column(Integer, nullable=False)
    status = Column(String, default="uploaded")  # uploaded, processed, failed
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

class LpHolding(Base):
    """Model for LP direct company holdings."""
    __tablename__ = "lp_holdings"

    id = Column(Integer, primary_key=True, index=True)
    lp_id = Column(String, index=True, nullable=False)
    company_name = Column(String, nullable=False)
    cost_basis = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    acquisition_date = Column(DateTime, nullable=True)
    valuation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"))
    
    uploaded_file = relationship("UploadedFile")

class LpFundPosition(Base):
    """Model for LP fund positions."""
    __tablename__ = "lp_fund_positions"

    id = Column(Integer, primary_key=True, index=True)
    lp_id = Column(String, index=True, nullable=False)
    fund_name = Column(String, nullable=False)
    committed_capital = Column(Float, nullable=False)
    contributed_capital = Column(Float, nullable=False)
    remaining_capital = Column(Float, nullable=True)
    distributed_capital = Column(Float, nullable=True)
    nav = Column(Float, nullable=False)  # Net Asset Value
    vintage_year = Column(Integer, nullable=True)
    currency = Column(String, default="USD")
    valuation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    irr = Column(Float, nullable=True)  # Internal Rate of Return
    tvpi = Column(Float, nullable=True)  # Total Value to Paid In
    dpi = Column(Float, nullable=True)   # Distributions to Paid In
    file_id = Column(Integer, ForeignKey("uploaded_files.id"))
    
    uploaded_file = relationship("UploadedFile")

# Create database engine
engine = create_engine(DATABASE_URL)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)