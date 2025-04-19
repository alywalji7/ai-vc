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


# Create all tables in the database
def create_tables():
    """
    Create all tables in the database if they don't exist.
    """
    Base.metadata.create_all(bind=engine)


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