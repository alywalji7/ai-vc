import os
import stripe
import logging
from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from models import initialize_db
from repository import get_db, get_user_subscription, create_user_subscription, update_subscription_status
from repository import increment_api_usage, create_invoice
from stripe_service import (
    SubscriptionTier, SubscriptionStatus, create_checkout_session, 
    get_tier_details, handle_webhook_event
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI.VC Billing Service")

# Initialize the database
initialize_db()

# Get the Stripe webhook secret from environment variables
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Define the Pydantic models
class CheckoutSessionRequest(BaseModel):
    tier: SubscriptionTier
    email: str
    success_url: str
    cancel_url: str

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    status: str
    current_period_end: datetime
    daily_api_limit: int
    daily_api_usage: int

class ApiUsageResponse(BaseModel):
    allowed: bool
    daily_api_usage: int
    daily_api_limit: int

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

@app.get("/subscription/{user_id}")
def get_subscription(user_id: str, db: Session = Depends(get_db)):
    """Get subscription details for a user"""
    subscription = get_user_subscription(db, user_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        status=subscription.status,
        current_period_end=subscription.current_period_end,
        daily_api_limit=subscription.daily_api_limit,
        daily_api_usage=subscription.daily_api_usage
    )

@app.post("/check-api-limit/{user_id}")
def check_and_increment_api_usage(user_id: str, db: Session = Depends(get_db)):
    """Check if the user can make an API call and increment usage"""
    subscription = get_user_subscription(db, user_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Check if subscription is active
    if subscription.status != SubscriptionStatus.ACTIVE:
        # If past due, allow limited usage
        if subscription.status == SubscriptionStatus.PAST_DUE:
            # Force limit to 10/day for past_due subscriptions
            subscription.daily_api_limit = 10
            
        # For other statuses (canceled, unpaid), deny access
        elif subscription.daily_api_usage >= subscription.daily_api_limit:
            return ApiUsageResponse(
                allowed=False,
                daily_api_usage=subscription.daily_api_usage,
                daily_api_limit=subscription.daily_api_limit
            )
    
    # Increment usage and check if limit is reached
    allowed = increment_api_usage(db, user_id)
    subscription = get_user_subscription(db, user_id)  # Refresh
    
    return ApiUsageResponse(
        allowed=allowed,
        daily_api_usage=subscription.daily_api_usage,
        daily_api_limit=subscription.daily_api_limit
    )

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
    
    if not all([customer_id, subscription_id, user_id]):
        logger.error("Missing required data in checkout session")
        return
    
    # Get subscription details from Stripe
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Extract period start/end
        current_period_start = datetime.fromtimestamp(subscription.current_period_start)
        current_period_end = datetime.fromtimestamp(subscription.current_period_end)
        
        # Extract plan details
        plan_id = subscription.items.data[0].price.id if subscription.items.data else None
        
        if not plan_id:
            logger.error("No plan ID found in subscription")
            return
        
        # Determine API limit based on plan
        daily_api_limit = 100  # Default
        if "pro" in plan_id.lower():
            daily_api_limit = 500
        elif "enterprise" in plan_id.lower():
            daily_api_limit = 10000  # "Unlimited"
        
        # Store subscription in database
        db = next(get_db())
        existing_sub = get_user_subscription(db, user_id)
        
        if existing_sub:
            # Update existing subscription
            update_subscription_status(db, user_id, {
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": subscription_id,
                "status": SubscriptionStatus.ACTIVE,
                "current_period_start": current_period_start,
                "current_period_end": current_period_end,
                "daily_api_limit": daily_api_limit
            })
        else:
            # Create new subscription
            # Note: For simplicity, we're using the price ID as the plan ID
            create_user_subscription(
                db=db,
                user_id=user_id,
                plan_id=plan_id,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                daily_api_limit=daily_api_limit
            )
        
        logger.info(f"Successfully created/updated subscription for user {user_id}")
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
        subscriptions = db.query(UserSubscription).filter_by(stripe_customer_id=customer_id).all()
        
        for subscription in subscriptions:
            # Update subscription status to past_due
            update_subscription_status(db, subscription.user_id, SubscriptionStatus.PAST_DUE)
            
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
            
            logger.info(f"Updated subscription status to past_due for user {subscription.user_id}")
    except Exception as e:
        logger.error(f"Error processing invoice payment failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8300)