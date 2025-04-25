from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import os
from datetime import datetime

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
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship with user subscriptions
    subscriptions = relationship("UserSubscription", back_populates="plan")

class UserSubscription(Base):
    """Model for user subscriptions"""
    __tablename__ = "user_subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    plan_id = Column(String, ForeignKey("subscription_plans.id"), nullable=False)
    stripe_customer_id = Column(String, nullable=False)
    stripe_subscription_id = Column(String, nullable=False)
    status = Column(String, nullable=False)  # active, past_due, canceled, unpaid
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # API usage limits
    daily_api_limit = Column(Integer, default=100)
    daily_api_usage = Column(Integer, default=0)
    last_api_reset = Column(DateTime, default=func.now())
    
    # Relationship with subscription plan
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

class Invoice(Base):
    """Model for invoices"""
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    stripe_invoice_id = Column(String, nullable=False)
    stripe_customer_id = Column(String, nullable=False)
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # paid, open, uncollectible, void
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Create the tables
def initialize_db():
    """Create all tables if they don't exist"""
    Base.metadata.create_all(engine)