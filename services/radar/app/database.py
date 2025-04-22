"""
Database connection and models for the Radar service.
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Company(Base):
    """
    Company entity model with features used for prediction.
    """
    __tablename__ = "companies"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    founding_date = Column(DateTime, nullable=True)
    github_stars = Column(Integer, default=0)
    commit_velocity = Column(Float, default=0)
    investor_count = Column(Integer, default=0)
    founder_exit_count = Column(Integer, default=0)
    social_traction = Column(Integer, default=0)
    funding_amount = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    investors = relationship("Investor", secondary="company_investors", back_populates="companies")
    founders = relationship("Founder", secondary="company_founders", back_populates="companies")
    
    def __repr__(self):
        return f"<Company(id='{self.id}', name='{self.name}')>"


class Investor(Base):
    """
    Investor entity model.
    """
    __tablename__ = "investors"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)  # VC, Angel, Corporate, etc.
    investment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    companies = relationship("Company", secondary="company_investors", back_populates="investors")
    
    def __repr__(self):
        return f"<Investor(id='{self.id}', name='{self.name}')>"


class Founder(Base):
    """
    Founder entity model.
    """
    __tablename__ = "founders"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    exit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    companies = relationship("Company", secondary="company_founders", back_populates="founders")
    
    def __repr__(self):
        return f"<Founder(id='{self.id}', name='{self.name}')>"


class CompanyInvestor(Base):
    """
    Association table for Company-Investor relationship.
    """
    __tablename__ = "company_investors"

    company_id = Column(String, ForeignKey("companies.id"), primary_key=True)
    investor_id = Column(String, ForeignKey("investors.id"), primary_key=True)
    investment_date = Column(DateTime, nullable=True)
    amount = Column(Float, nullable=True)
    round_type = Column(String, nullable=True)  # Seed, Series A, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CompanyInvestor(company_id='{self.company_id}', investor_id='{self.investor_id}')>"


class CompanyFounder(Base):
    """
    Association table for Company-Founder relationship.
    """
    __tablename__ = "company_founders"

    company_id = Column(String, ForeignKey("companies.id"), primary_key=True)
    founder_id = Column(String, ForeignKey("founders.id"), primary_key=True)
    role = Column(String, nullable=True)  # CEO, CTO, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CompanyFounder(company_id='{self.company_id}', founder_id='{self.founder_id}')>"


class InvestmentOpportunity(Base):
    """
    Investment opportunity model with prediction scores.
    """
    __tablename__ = "investment_opportunities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    score = Column(Float, nullable=False)  # Classifier score (0-1)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    features_used = Column(String, nullable=True)  # JSON string of features used for this prediction
    
    def __repr__(self):
        return f"<InvestmentOpportunity(id={self.id}, company_id='{self.company_id}', score={self.score})>"


class CompanyOutcome(Base):
    """
    Tracks the actual outcome of companies for model training and evaluation.
    """
    __tablename__ = "company_outcomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    exit_event = Column(Boolean, default=False)  # True if company had an exit
    exit_date = Column(DateTime, nullable=True)  # Date of exit (if any)
    exit_amount = Column(Float, nullable=True)  # Amount of exit (if any)
    
    up_round = Column(Boolean, default=False)  # True if company had an up-round
    up_round_date = Column(DateTime, nullable=True)  # Date of up-round (if any)
    up_round_valuation = Column(Float, nullable=True)  # Valuation of up-round (if any)
    previous_valuation = Column(Float, nullable=True)  # Previous valuation
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CompanyOutcome(id={self.id}, company_id='{self.company_id}', exit={self.exit_event}, up_round={self.up_round})>"


class ModelVersion(Base):
    """
    Model version tracking for MLflow integration.
    """
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mlflow_run_id = Column(String, nullable=True)
    model_version = Column(String, nullable=False)
    training_date = Column(DateTime, default=datetime.utcnow)
    auc_score = Column(Float, nullable=False)
    in_production = Column(Boolean, default=False)
    metrics = Column(String, nullable=True)  # JSON string of various metrics
    
    def __repr__(self):
        return f"<ModelVersion(id={self.id}, model_version='{self.model_version}', auc={self.auc_score}, in_production={self.in_production})>"


# Create all tables in the database
def create_tables():
    """
    Create all tables in the database if they don't exist.
    """
    Base.metadata.create_all(bind=engine)


# Function to get SQLAlchemy engine
def get_engine():
    """
    Get the SQLAlchemy engine.
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    return engine


# Dependency to get DB session
def get_db():
    """
    Get a database session.
    
    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()