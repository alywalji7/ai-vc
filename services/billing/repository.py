from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, and_
from datetime import datetime, timedelta, date
from models import Base, SubscriptionPlan, UserSubscription, Invoice, LPSeat, ApiUsage, SubscriptionTierLimits
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

def create_subscription_plan(db, name, description, price, stripe_price_id, seat_limit=1, api_limit_daily=100):
    """Create a new subscription plan"""
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"
    new_plan = SubscriptionPlan(
        id=plan_id,
        name=name,
        description=description,
        price=price,
        stripe_price_id=stripe_price_id,
        seat_limit=seat_limit,
        api_limit_daily=api_limit_daily
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

# User subscription functions
def get_user_subscription(db, user_id):
    """Get a user's subscription"""
    return db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()

def get_lp_subscription(db, lp_id):
    """Get an LP's subscription"""
    return db.query(UserSubscription).filter(UserSubscription.lp_id == lp_id).first()

def create_user_subscription(
    db, user_id, lp_id, plan_id, stripe_customer_id, stripe_subscription_id, 
    status, current_period_start, current_period_end
):
    """Create a new user subscription"""
    subscription_id = f"sub_{uuid.uuid4().hex[:8]}"
    new_subscription = UserSubscription(
        id=subscription_id,
        user_id=user_id,
        lp_id=lp_id,
        plan_id=plan_id,
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
        status=status,
        current_period_start=current_period_start,
        current_period_end=current_period_end
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

# LP Seat management
def add_lp_seat(db, lp_id, user_id, role):
    """Add a new LP seat"""
    # Check if this seat already exists
    existing_seat = db.query(LPSeat).filter(
        LPSeat.lp_id == lp_id,
        LPSeat.user_id == user_id
    ).first()
    
    if existing_seat:
        return existing_seat
    
    # Get the LP's subscription to check seat limits
    subscription = get_lp_subscription(db, lp_id)
    if not subscription:
        return None
    
    # Get the plan to check seat limits
    plan = get_subscription_plan(db, subscription.plan_id)
    if not plan:
        return None
    
    # Count current seats
    current_seats = db.query(LPSeat).filter(LPSeat.lp_id == lp_id).count()
    
    # Check if seat limit is reached
    if current_seats >= plan.seat_limit:
        return None
    
    # Add the new seat
    new_seat = LPSeat(
        lp_id=lp_id,
        user_id=user_id,
        role=role
    )
    db.add(new_seat)
    db.commit()
    db.refresh(new_seat)
    return new_seat

def remove_lp_seat(db, lp_id, user_id):
    """Remove an LP seat"""
    seat = db.query(LPSeat).filter(
        LPSeat.lp_id == lp_id,
        LPSeat.user_id == user_id
    ).first()
    
    if seat:
        db.delete(seat)
        db.commit()
        return True
    return False

def get_lp_seats(db, lp_id):
    """Get all seats for an LP"""
    return db.query(LPSeat).filter(LPSeat.lp_id == lp_id).all()

def count_lp_seats(db, lp_id):
    """Count the number of seats for an LP"""
    return db.query(LPSeat).filter(LPSeat.lp_id == lp_id).count()

# API Usage tracking
def track_api_usage(db, lp_id, service, count=1):
    """Track API usage for an LP"""
    today = date.today()
    
    # Get or create an API usage record for today
    usage = db.query(ApiUsage).filter(
        ApiUsage.lp_id == lp_id,
        ApiUsage.service == service,
        ApiUsage.date == today
    ).first()
    
    if usage:
        # Update existing record
        usage.count += count
        db.commit()
        db.refresh(usage)
    else:
        # Create new record
        usage = ApiUsage(
            lp_id=lp_id,
            service=service,
            count=count,
            date=today
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
    
    return usage

def get_api_usage(db, lp_id, service, usage_date=None):
    """Get API usage for an LP on a specific date"""
    if usage_date is None:
        usage_date = date.today()
        
    return db.query(ApiUsage).filter(
        ApiUsage.lp_id == lp_id,
        ApiUsage.service == service,
        ApiUsage.date == usage_date
    ).first()

def get_total_api_usage(db, lp_id, service, start_date=None, end_date=None):
    """Get total API usage for an LP over a date range"""
    query = db.query(func.sum(ApiUsage.count).label('total')).filter(
        ApiUsage.lp_id == lp_id,
        ApiUsage.service == service
    )
    
    if start_date:
        query = query.filter(ApiUsage.date >= start_date)
    
    if end_date:
        query = query.filter(ApiUsage.date <= end_date)
    
    result = query.first()
    return result.total if result and result.total else 0

def check_api_limit(db, lp_id, service):
    """Check if an LP has reached their API limit for a service"""
    # Get the LP's subscription
    subscription = get_lp_subscription(db, lp_id)
    if not subscription:
        return False
    
    # Get the plan to check API limits
    plan = get_subscription_plan(db, subscription.plan_id)
    if not plan:
        return False
    
    # Get today's usage
    today = date.today()
    usage = get_api_usage(db, lp_id, service, today)
    
    # If no usage record exists yet, they're under the limit
    if not usage:
        return True
    
    # Check if they've exceeded their daily limit
    return usage.count < plan.api_limit_daily

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