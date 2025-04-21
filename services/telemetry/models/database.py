"""
Database models for the Portfolio Telemetry service.
"""
import os
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

# Get DATABASE_URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PortfolioCompany(Base):
    """
    Represents a company in the VC portfolio.
    """
    __tablename__ = "portfolio_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    sector = Column(String, index=True)
    funding_stage = Column(String)
    investment_date = Column(DateTime(timezone=True))
    investment_amount = Column(Float)
    ownership_percentage = Column(Float)
    valuation_at_investment = Column(Float)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    financial_metrics = relationship("FinancialMetric", back_populates="company")
    follow_on_decisions = relationship("FollowOnDecision", back_populates="company")
    
    def __repr__(self):
        return f"<PortfolioCompany {self.name}>"

class FinancialMetric(Base):
    """
    Financial metrics for a portfolio company, collected over time.
    """
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("portfolio_companies.company_id"), index=True)
    date = Column(DateTime(timezone=True), index=True)
    
    # Cash metrics
    cash_balance = Column(Float)
    cash_burn_rate = Column(Float)
    runway_months = Column(Float)
    
    # Growth metrics
    revenue = Column(Float)
    revenue_growth_rate = Column(Float)
    customer_count = Column(Integer)
    customer_growth_rate = Column(Float)
    
    # Churn metrics
    churn_rate = Column(Float)
    customer_acquisition_cost = Column(Float)
    lifetime_value = Column(Float)
    
    # Comparison metrics
    growth_vs_peers = Column(Float)  # Standard deviations from peer median
    
    # Source metadata
    data_source = Column(String)  # 'banking_csv', 'stripe_api', etc.
    raw_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    company = relationship("PortfolioCompany", back_populates="financial_metrics")
    
    def __repr__(self):
        return f"<FinancialMetric for {self.company_id} on {self.date}>"

class FollowOnDecision(Base):
    """
    Represents a decision on whether to make a follow-on investment.
    """
    __tablename__ = "follow_on_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("portfolio_companies.company_id"), index=True)
    decision_date = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Trigger information
    trigger_type = Column(String)  # 'runway', 'growth', 'manual'
    trigger_value = Column(Float)  # The actual value that triggered the decision
    
    # Decision details
    decision = Column(String)  # 'pending', 'approved', 'rejected'
    recommended_amount = Column(Float)
    recommended_valuation = Column(Float)
    pro_rata_amount = Column(Float)
    super_pro_rata = Column(Boolean, default=False)  # True if recommended > pro_rata
    
    # Rationale and metadata
    rationale = Column(Text)
    financial_snapshot = Column(JSONB)
    decision_maker = Column(String, nullable=True)  # Who made the final decision
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("PortfolioCompany", back_populates="follow_on_decisions")
    
    def __repr__(self):
        return f"<FollowOnDecision for {self.company_id} on {self.decision_date}>"


# Create all tables if they don't exist
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()