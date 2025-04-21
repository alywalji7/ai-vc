"""
Database models for the Portfolio Telemetry service.

This module defines the SQLAlchemy models for storing portfolio company data,
financial metrics, and follow-on investment decisions.
"""
import enum
from datetime import datetime
from typing import Optional, List

import sqlalchemy as sa
from sqlalchemy import Column, String, Float, DateTime, Boolean, Enum, Integer, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class CompanySector(enum.Enum):
    """Enumeration of company sectors."""
    SAAS = "SAAS"
    FINTECH = "FINTECH"
    HEALTHTECH = "HEALTHTECH"
    MARKETPLACE = "MARKETPLACE"
    HARDWARE = "HARDWARE"
    AI = "AI"
    CONSUMER = "CONSUMER"
    ENTERPRISE = "ENTERPRISE"
    OTHER = "OTHER"

class CompanyStage(enum.Enum):
    """Enumeration of company funding stages."""
    PRE_SEED = "PRE_SEED"
    SEED = "SEED"
    SERIES_A = "SERIES_A"
    SERIES_B = "SERIES_B"
    SERIES_C = "SERIES_C"
    SERIES_D_PLUS = "SERIES_D_PLUS"

class TriggerType(enum.Enum):
    """Enumeration of follow-on decision trigger types."""
    RUNWAY = "runway"
    GROWTH = "growth"
    STRATEGIC = "strategic"

class PortfolioCompany(Base):
    """Model for portfolio companies."""
    __tablename__ = "portfolio_companies"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    sector = Column(Enum(CompanySector), nullable=False)
    stage = Column(Enum(CompanyStage), nullable=False)
    investment_date = Column(DateTime, nullable=False)
    investment_amount = Column(Float, nullable=False)
    ownership_percentage = Column(Float, nullable=False)
    valuation_at_investment = Column(Float, nullable=False)
    
    # Relationships
    financial_metrics = relationship("FinancialMetric", back_populates="company", cascade="all, delete-orphan")
    follow_on_decisions = relationship("FollowOnDecision", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<PortfolioCompany(id='{self.id}', name='{self.name}', sector={self.sector})>"

class FinancialMetric(Base):
    """Model for company financial metrics."""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(50), ForeignKey("portfolio_companies.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Cash metrics
    cash_balance = Column(Float, nullable=True)
    burn_rate = Column(Float, nullable=True)  # Monthly burn rate
    runway_months = Column(Float, nullable=True)
    
    # Revenue metrics
    mrr = Column(Float, nullable=True)  # Monthly Recurring Revenue
    arr = Column(Float, nullable=True)  # Annual Recurring Revenue
    revenue_growth = Column(Float, nullable=True)  # Month-over-month percentage
    
    # Customer metrics
    customer_count = Column(Integer, nullable=True)
    new_customers = Column(Integer, nullable=True)
    churned_customers = Column(Integer, nullable=True)
    churn_rate = Column(Float, nullable=True)  # Percentage
    
    # Relationships
    company = relationship("PortfolioCompany", back_populates="financial_metrics")
    
    def __repr__(self) -> str:
        return f"<FinancialMetric(id={self.id}, company_id='{self.company_id}', date='{self.date}')>"

class FollowOnDecision(Base):
    """Model for follow-on investment decisions."""
    __tablename__ = "follow_on_decisions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(50), ForeignKey("portfolio_companies.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    trigger_type = Column(Enum(TriggerType), nullable=False)
    recommended_amount = Column(Float, nullable=False)
    super_pro_rata = Column(Boolean, default=False, nullable=False)
    expected_runway_extension = Column(Float, nullable=True)
    expected_ownership_increase = Column(Float, nullable=True)
    analysis = Column(Text, nullable=False)
    
    # Decision status
    approved = Column(Boolean, default=False, nullable=False)
    executed = Column(Boolean, default=False, nullable=False)
    execution_date = Column(DateTime, nullable=True)
    actual_amount = Column(Float, nullable=True)
    
    # Relationships
    company = relationship("PortfolioCompany", back_populates="follow_on_decisions")
    
    def __repr__(self) -> str:
        return f"<FollowOnDecision(id={self.id}, company_id='{self.company_id}', trigger_type={self.trigger_type})>"