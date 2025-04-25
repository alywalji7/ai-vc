import os
import stripe
import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field

from models import initialize_db, SubscriptionTierLimits, UserSubscription
from repository import (
    get_db, get_user_subscription, get_lp_subscription, create_user_subscription, 
    update_user_subscription, update_subscription_status, add_lp_seat, remove_lp_seat,
    get_lp_seats, count_lp_seats, track_api_usage, get_api_usage, 
    get_total_api_usage, check_api_limit, create_invoice
)
from stripe_service import (
    SubscriptionTier, SubscriptionStatus, UsageType, create_checkout_session, 
    get_tier_details, handle_webhook_event, report_usage, get_subscription_tier,
    retrieve_subscription, TIER_LIMITS, PRICE_IDS
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI.VC Billing Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database
initialize_db()

# Get the Stripe webhook secret from environment variables
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Define the Pydantic models
class CheckoutSessionRequest(BaseModel):
    tier: SubscriptionTier
    email: str
    lp_id: str  # LP (Limited Partner) ID
    success_url: str
    cancel_url: str

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    lp_id: str
    status: str
    plan_tier: str
    current_period_end: datetime
    seat_limit: int
    api_limit_daily: int

class ApiUsageResponse(BaseModel):
    allowed: bool
    usage: int
    limit: int

class SeatResponse(BaseModel):
    id: int
    lp_id: str
    user_id: str
    role: str
    created_at: datetime

class SeatRequest(BaseModel):
    lp_id: str
    user_id: str
    role: str

class APIUsageRequest(BaseModel):
    lp_id: str
    service: str
    count: int = 1

# Define the API routes
@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "AI.VC Billing Service API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/tiers")
def get_subscription_tiers():
    """Get all available subscription tiers"""
    return get_tier_details()

@app.post("/create-checkout-session")
def create_stripe_checkout_session(request: CheckoutSessionRequest):
    """Create a Stripe Checkout session for subscription"""
    try:
        session = create_checkout_session(
            tier=request.tier,
            customer_email=request.email,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
        return session
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscription/user/{user_id}")
def get_user_subscription_details(user_id: str, db: Session = Depends(get_db)):
    """Get subscription details for a user"""
    subscription = get_user_subscription(db, user_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Get the plan to get the seat and API limits
    plan = subscription.plan
    
    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        lp_id=subscription.lp_id,
        status=subscription.status,
        plan_tier=plan.name,
        current_period_end=subscription.current_period_end,
        seat_limit=plan.seat_limit,
        api_limit_daily=plan.api_limit_daily
    )

@app.get("/subscription/lp/{lp_id}")
def get_lp_subscription_details(lp_id: str, db: Session = Depends(get_db)):
    """Get subscription details for an LP"""
    subscription = get_lp_subscription(db, lp_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Get the plan to get the seat and API limits
    plan = subscription.plan
    
    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        lp_id=subscription.lp_id,
        status=subscription.status,
        plan_tier=plan.name,
        current_period_end=subscription.current_period_end,
        seat_limit=plan.seat_limit,
        api_limit_daily=plan.api_limit_daily
    )

@app.post("/api-usage/check")
def check_api_usage(request: APIUsageRequest, db: Session = Depends(get_db)):
    """Check if the LP can make an API call to a specific service"""
    # Check if LP has an active subscription
    subscription = get_lp_subscription(db, request.lp_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="LP subscription not found")
    
    # Check if subscription is active
    if subscription.status != SubscriptionStatus.ACTIVE:
        if subscription.status == SubscriptionStatus.PAST_DUE:
            # Allow limited usage for past_due subscriptions
            plan = subscription.plan
            plan.api_limit_daily = min(plan.api_limit_daily, 10)
        else:
            # For other statuses (canceled, unpaid), deny access
            return ApiUsageResponse(
                allowed=False,
                usage=0,
                limit=0
            )
    
    # Check API limit for the service
    allowed = check_api_limit(db, request.lp_id, request.service)
    
    # If allowed, track this usage
    if allowed:
        usage = track_api_usage(db, request.lp_id, request.service, request.count)
        plan = subscription.plan
        
        return ApiUsageResponse(
            allowed=True,
            usage=usage.count,
            limit=plan.api_limit_daily
        )
    else:
        # Get current usage
        usage = get_api_usage(db, request.lp_id, request.service)
        plan = subscription.plan
        
        return ApiUsageResponse(
            allowed=False,
            usage=usage.count if usage else 0,
            limit=plan.api_limit_daily
        )

@app.get("/seats/{lp_id}")
def get_all_lp_seats(lp_id: str, db: Session = Depends(get_db)):
    """Get all seats for an LP"""
    # Check if LP has an active subscription
    subscription = get_lp_subscription(db, lp_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="LP subscription not found")
    
    seats = get_lp_seats(db, lp_id)
    return [
        SeatResponse(
            id=seat.id,
            lp_id=seat.lp_id,
            user_id=seat.user_id,
            role=seat.role,
            created_at=seat.created_at
        ) for seat in seats
    ]

@app.post("/seats")
def add_new_lp_seat(request: SeatRequest, db: Session = Depends(get_db)):
    """Add a new seat for an LP"""
    # Check if LP has an active subscription
    subscription = get_lp_subscription(db, request.lp_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="LP subscription not found")
    
    # Add the new seat
    seat = add_lp_seat(db, request.lp_id, request.user_id, request.role)
    if not seat:
        # If seat couldn't be added, it's likely because the seat limit is reached
        raise HTTPException(status_code=403, detail="Seat limit reached for this LP subscription")
    
    return SeatResponse(
        id=seat.id,
        lp_id=seat.lp_id,
        user_id=seat.user_id,
        role=seat.role,
        created_at=seat.created_at
    )

@app.delete("/seats/{lp_id}/{user_id}")
def remove_existing_seat(lp_id: str, user_id: str, db: Session = Depends(get_db)):
    """Remove a seat for an LP"""
    success = remove_lp_seat(db, lp_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Seat not found")
    
    return {"success": True}

@app.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """Handle Stripe webhook events"""
    if not STRIPE_WEBHOOK_SECRET:
        logger.warning("STRIPE_WEBHOOK_SECRET is not set")
        return JSONResponse({"success": False, "error": "Webhook secret not configured"}, status_code=500)
    
    try:
        # Get the request body
        payload = await request.body()
        
        # Verify the webhook signature
        event_type, event_data = handle_webhook_event(
            payload=payload,
            sig_header=stripe_signature,
            webhook_secret=STRIPE_WEBHOOK_SECRET
        )
        
        # Handle the event
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(event_data)
        elif event_type == "invoice.payment_failed":
            await handle_invoice_payment_failed(event_data)
        # Add more event handlers as needed
        
        return JSONResponse({"success": True})
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        return JSONResponse({"success": False, "error": "Invalid signature"}, status_code=400)
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def handle_checkout_completed(event_data):
    """Handle checkout.session.completed event"""
    session = event_data
    
    # Get the customer and subscription IDs
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    user_id = session.get("client_reference_id")  # This should be set when creating the session
    lp_id = session.get("metadata", {}).get("lp_id")  # Get LP ID from metadata
    
    if not all([customer_id, subscription_id, user_id]):
        logger.error("Missing required data in checkout session")
        return
    
    # If lp_id is not provided, use user_id as lp_id
    if not lp_id:
        lp_id = user_id
        logger.warning(f"No lp_id in metadata, using user_id {user_id} as lp_id")
    
    # Get subscription details from Stripe
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Extract period start/end
        current_period_start = datetime.fromtimestamp(subscription.current_period_start)
        current_period_end = datetime.fromtimestamp(subscription.current_period_end)
        
        # Extract plan details
        price_id = subscription.items.data[0].price.id if subscription.items.data else None
        
        if not price_id:
            logger.error("No price ID found in subscription")
            return
        
        # Determine tier based on price ID
        tier = None
        for t, price in PRICE_IDS.items():
            if price_id == price:
                tier = t
                break
        
        if not tier:
            logger.error(f"Could not determine tier for price ID {price_id}")
            return
        
        # Get seat and API limits based on tier
        seat_limit = TIER_LIMITS[tier]["seats"]
        api_limit_daily = TIER_LIMITS[tier]["api_calls_daily"]
        
        # Store subscription in database
        db = next(get_db())
        existing_sub = get_lp_subscription(db, lp_id)
        
        if existing_sub:
            # Update existing subscription
            update_user_subscription(db, existing_sub.user_id, {
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": subscription_id,
                "status": SubscriptionStatus.ACTIVE,
                "current_period_start": current_period_start,
                "current_period_end": current_period_end
            })
        else:
            # Create new subscription
            create_user_subscription(
                db=db,
                user_id=user_id,
                lp_id=lp_id,
                plan_id=price_id,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=current_period_start,
                current_period_end=current_period_end
            )
            
            # Add the admin user as the first seat
            add_lp_seat(db, lp_id, user_id, "admin")
        
        logger.info(f"Successfully created/updated subscription for user {user_id}, LP {lp_id}")
    except Exception as e:
        logger.error(f"Error processing checkout session: {str(e)}")

async def handle_invoice_payment_failed(event_data):
    """Handle invoice.payment_failed event"""
    invoice = event_data
    
    # Get customer ID from the invoice
    customer_id = invoice.get("customer")
    if not customer_id:
        logger.error("No customer ID found in invoice")
        return
    
    try:
        # Find the subscription by customer ID
        db = next(get_db())
        subscription = db.query(UserSubscription).filter_by(stripe_customer_id=customer_id).first()
        
        if subscription:
            # Update subscription status to past_due
            update_user_subscription(db, subscription.user_id, {"status": SubscriptionStatus.PAST_DUE})
            
            # Create invoice record
            create_invoice(
                db=db,
                user_id=subscription.user_id,
                stripe_invoice_id=invoice.get("id"),
                stripe_customer_id=customer_id,
                amount_due=invoice.get("amount_due") / 100,  # Convert from cents
                amount_paid=invoice.get("amount_paid") / 100,  # Convert from cents
                status=invoice.get("status"),
                invoice_date=datetime.fromtimestamp(invoice.get("created")),
                due_date=datetime.fromtimestamp(invoice.get("due_date") or invoice.get("created"))
            )
            
            logger.info(f"Successfully processed payment failure for customer {customer_id}")
        else:
            logger.warning(f"Could not find subscription for customer {customer_id}")
    except Exception as e:
        logger.error(f"Error processing invoice payment failure: {str(e)}")

async def report_daily_usage_to_stripe():
    """Report daily usage metrics to Stripe"""
    try:
        logger.info("Starting daily usage reporting to Stripe")
        db = next(get_db())
        
        # Get all active subscriptions
        subscriptions = db.query(UserSubscription).filter_by(status=SubscriptionStatus.ACTIVE).all()
        
        for subscription in subscriptions:
            lp_id = subscription.lp_id
            subscription_id = subscription.stripe_subscription_id
            
            # Get the tier for this subscription
            tier = get_subscription_tier(subscription_id)
            if not tier:
                logger.warning(f"Could not determine tier for subscription {subscription_id}")
                continue
            
            # Report seat count
            seat_count = count_lp_seats(db, lp_id)
            seat_limit = TIER_LIMITS[tier]["seats"]
            
            # Only report seats if they're using seats (reporting 0 might cause issues)
            if seat_count > 0:
                success = report_usage(
                    subscription_id=subscription_id,
                    usage_type=UsageType.SEATS,
                    quantity=seat_count,
                    tier=tier
                )
                if not success:
                    logger.warning(f"Failed to report seat count for subscription {subscription_id}")
            
            # Report API usage
            for service_type in [UsageType.API_CALLS, UsageType.RADAR_CALLS, UsageType.SIMILARITY_CALLS]:
                # Get yesterday's usage (we report the previous day)
                yesterday = date.today() - timedelta(days=1)
                service_usage = get_api_usage(db, lp_id, service_type, yesterday)
                
                if service_usage and service_usage.count > 0:
                    success = report_usage(
                        subscription_id=subscription_id,
                        usage_type=service_type,
                        quantity=service_usage.count,
                        tier=tier
                    )
                    if not success:
                        logger.warning(f"Failed to report {service_type} usage for subscription {subscription_id}")
        
        logger.info("Completed daily usage reporting to Stripe")
    except Exception as e:
        logger.error(f"Error during daily usage reporting: {str(e)}")

def setup_scheduler():
    """Set up the scheduler for daily usage reporting"""
    scheduler = BackgroundScheduler()
    
    # Schedule the usage reporting task to run at 00:05 every day (just after midnight)
    scheduler.add_job(
        lambda: asyncio.run(report_daily_usage_to_stripe()),
        'cron',
        hour=0,
        minute=5
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Started daily usage reporting scheduler")

# Start the scheduler when the app is ready
@app.on_event("startup")
async def on_startup():
    setup_scheduler()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8300))
    uvicorn.run(app, host="0.0.0.0", port=port)