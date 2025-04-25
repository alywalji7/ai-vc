from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from models import Base, SubscriptionPlan, UserSubscription, Invoice
import os
import uuid

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Subscription plan functions
def get_subscription_plan(db, plan_id):
    """Get a subscription plan by ID"""
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()

def get_all_subscription_plans(db):
    """Get all subscription plans"""
    return db.query(SubscriptionPlan).all()

def create_subscription_plan(db, name, description, price, stripe_price_id):
    """Create a new subscription plan"""
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"
    new_plan = SubscriptionPlan(
        id=plan_id,
        name=name,
        description=description,
        price=price,
        stripe_price_id=stripe_price_id
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

# User subscription functions
def get_user_subscription(db, user_id):
    """Get a user's subscription"""
    return db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()

def create_user_subscription(
    db, user_id, plan_id, stripe_customer_id, stripe_subscription_id, 
    status, current_period_start, current_period_end, daily_api_limit=100
):
    """Create a new user subscription"""
    subscription_id = f"sub_{uuid.uuid4().hex[:8]}"
    new_subscription = UserSubscription(
        id=subscription_id,
        user_id=user_id,
        plan_id=plan_id,
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
        status=status,
        current_period_start=current_period_start,
        current_period_end=current_period_end,
        daily_api_limit=daily_api_limit
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

def update_user_subscription(db, user_id, updates):
    """Update a user's subscription"""
    subscription = get_user_subscription(db, user_id)
    if not subscription:
        return None
    
    for key, value in updates.items():
        setattr(subscription, key, value)
    
    db.commit()
    db.refresh(subscription)
    return subscription

def update_subscription_status(db, user_id, status):
    """Update a user's subscription status"""
    return update_user_subscription(db, user_id, {"status": status})

def increment_api_usage(db, user_id):
    """Increment a user's API usage"""
    subscription = get_user_subscription(db, user_id)
    if not subscription:
        return False
    
    # Check if we need to reset daily usage
    now = datetime.utcnow()
    last_reset = subscription.last_api_reset
    if now.date() > last_reset.date():
        subscription.daily_api_usage = 0
        subscription.last_api_reset = now
    
    # Increment usage
    subscription.daily_api_usage += 1
    
    db.commit()
    return subscription.daily_api_usage <= subscription.daily_api_limit

# Invoice functions
def create_invoice(
    db, user_id, stripe_invoice_id, stripe_customer_id,
    amount_due, amount_paid, status, invoice_date, due_date
):
    """Create a new invoice"""
    invoice_id = f"inv_{uuid.uuid4().hex[:8]}"
    new_invoice = Invoice(
        id=invoice_id,
        user_id=user_id,
        stripe_invoice_id=stripe_invoice_id,
        stripe_customer_id=stripe_customer_id,
        amount_due=amount_due,
        amount_paid=amount_paid,
        status=status,
        invoice_date=invoice_date,
        due_date=due_date
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice

def get_user_invoices(db, user_id):
    """Get all invoices for a user"""
    return db.query(Invoice).filter(Invoice.user_id == user_id).all()