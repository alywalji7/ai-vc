from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, create_engine, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import os
from datetime import datetime, date

# Get the database URL from the environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a base class for our models
Base = declarative_base()

class SubscriptionPlan(Base):
    """Model for subscription plans"""
    __tablename__ = "subscription_plans"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stripe_price_id = Column(String, nullable=False)
    # Plan limits
    seat_limit = Column(Integer, default=1)  # Default to 1 seat for Starter plan
    api_limit_daily = Column(Integer, default=100)  # Default to 100 API calls/day
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship with user subscriptions
    subscriptions = relationship("UserSubscription", back_populates="plan")

class UserSubscription(Base):
    """Model for user subscriptions"""
    __tablename__ = "user_subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    lp_id = Column(String, nullable=False, index=True)  # LP (Limited Partner) ID
    plan_id = Column(String, ForeignKey("subscription_plans.id"), nullable=False)
    stripe_customer_id = Column(String, nullable=False)
    stripe_subscription_id = Column(String, nullable=False)
    status = Column(String, nullable=False)  # active, past_due, canceled, unpaid
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship with subscription plan
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

class Invoice(Base):
    """Model for invoices"""
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True, index=True)  # Nullable to allow creation prior to user lookup
    stripe_invoice_id = Column(String, nullable=False)
    stripe_customer_id = Column(String, nullable=False)
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # paid, open, uncollectible, void
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    pdf_url = Column(String, nullable=True)  # URL to the S3 bucket where PDF is stored
    pdf_data = Column(String, nullable=True)  # Base64 encoded PDF data as fallback
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class LPSeat(Base):
    """Model for LP seats"""
    __tablename__ = "lp_seats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lp_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        # Composite unique constraint to prevent duplicates
        {'sqlite_autoincrement': True}
    )

class ApiUsage(Base):
    """Model for API usage tracking"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lp_id = Column(String, nullable=False, index=True)
    service = Column(String, nullable=False, index=True)  # e.g., 'similarity', 'radar'
    count = Column(Integer, default=0)
    date = Column(Date, default=date.today, index=True)
    
    __table_args__ = (
        # Composite unique constraint to prevent duplicates
        {'sqlite_autoincrement': True}
    )

# Subscription tier constants
class SubscriptionTierLimits:
    """Constants for subscription tier limits"""
    STARTER_SEAT_LIMIT = 1
    PRO_SEAT_LIMIT = 3
    ENTERPRISE_SEAT_LIMIT = 999  # Practically unlimited
    
    STARTER_API_LIMIT = 50
    PRO_API_LIMIT = 500
    ENTERPRISE_API_LIMIT = 10000  # Practically unlimited

# Create the tables
def initialize_db():
    """Create all tables if they don't exist"""
    Base.metadata.create_all(engine)