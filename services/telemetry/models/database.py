"""
Database models for the Portfolio Telemetry service.

This module defines SQLAlchemy models representing portfolio companies,
their financial metrics, and follow-on investment decisions.
"""
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Text, Enum, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class CompanyStage(enum.Enum):
    """Enumeration of possible company stages."""
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D_PLUS = "series_d_plus"
    GROWTH = "growth"
    PRE_IPO = "pre_ipo"

class CompanySector(enum.Enum):
    """Enumeration of possible company sectors."""
    SAAS = "saas"
    FINTECH = "fintech"
    HEALTH = "health"
    AI = "ai"
    HARDWARE = "hardware"
    CONSUMER = "consumer"
    MARKETPLACE = "marketplace"
    ENTERPRISE = "enterprise"
    OTHER = "other"

class PortfolioCompany(Base):
    """Model representing a portfolio company."""
    __tablename__ = "portfolio_companies"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sector = Column(Enum(CompanySector), nullable=False)
    stage = Column(Enum(CompanyStage), nullable=False)
    investment_date = Column(DateTime, default=datetime.utcnow)
    investment_amount = Column(Float, nullable=False)
    ownership_percentage = Column(Float, nullable=False)
    valuation_at_investment = Column(Float, nullable=False)
    
    # Relationships
    financial_metrics = relationship("FinancialMetric", back_populates="company")
    follow_on_decisions = relationship("FollowOnDecision", back_populates="company")
    
    def __repr__(self):
        return f"<PortfolioCompany(id='{self.id}', name='{self.name}', sector={self.sector})>"

class FinancialMetric(Base):
    """Model representing financial metrics for a portfolio company."""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(50), ForeignKey("portfolio_companies.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Cash metrics
    cash_balance = Column(Float)
    burn_rate = Column(Float)
    runway_months = Column(Float)
    
    # Revenue metrics
    mrr = Column(Float)  # Monthly Recurring Revenue
    arr = Column(Float)  # Annual Recurring Revenue
    revenue_growth = Column(Float)  # Month-over-month percentage
    
    # Customer metrics
    customer_count = Column(Integer)
    new_customers = Column(Integer)
    churned_customers = Column(Integer)
    churn_rate = Column(Float)
    
    # Efficiency metrics
    cac = Column(Float)  # Customer Acquisition Cost
    ltv = Column(Float)  # Lifetime Value
    ltv_cac_ratio = Column(Float)
    
    # Relationship
    company = relationship("PortfolioCompany", back_populates="financial_metrics")
    
    def __repr__(self):
        return f"<FinancialMetric(company_id='{self.company_id}', date='{self.date}')>"

class FollowOnDecision(Base):
    """Model representing a follow-on investment decision."""
    __tablename__ = "follow_on_decisions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(50), ForeignKey("portfolio_companies.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Decision details
    trigger_type = Column(String(50), nullable=False)  # 'runway', 'growth', 'opportunity', etc.
    recommended_amount = Column(Float, nullable=False)
    super_pro_rata = Column(Boolean, default=False)
    expected_runway_extension = Column(Float)  # Additional months of runway
    expected_ownership_increase = Column(Float)  # Percentage points
    
    # Decision rationale
    analysis = Column(Text)
    
    # Decision status
    approved = Column(Boolean, default=None, nullable=True)
    executed = Column(Boolean, default=False)
    execution_date = Column(DateTime, nullable=True)
    actual_amount = Column(Float, nullable=True)
    
    # Relationship
    company = relationship("PortfolioCompany", back_populates="follow_on_decisions")
    
    def __repr__(self):
        return f"<FollowOnDecision(company_id='{self.company_id}', trigger_type='{self.trigger_type}', recommended_amount={self.recommended_amount})>"

def initialize_db(db_url: str):
    """
    Initialize the database connection.
    
    Args:
        db_url: Database connection URL
        
    Returns:
        A tuple containing the engine and session factory
    """
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    return engine, SessionLocal