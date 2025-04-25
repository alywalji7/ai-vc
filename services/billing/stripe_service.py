import os
import stripe
from enum import Enum
from typing import Dict, Any, Optional, Tuple

# Initialize the stripe client with your API key
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Define subscription tiers
class SubscriptionTier(str, Enum):
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

# Define subscription statuses
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"

# Price IDs for each tier
# In a production environment, you would store these in a database
PRICE_IDS = {
    SubscriptionTier.STARTER: "price_starter",  # Replace with actual price IDs from your Stripe dashboard
    SubscriptionTier.PRO: "price_pro",
    SubscriptionTier.ENTERPRISE: "price_enterprise",
}

# Price amounts in USD
PRICE_AMOUNTS = {
    SubscriptionTier.STARTER: 500,  # $500
    SubscriptionTier.PRO: 1000,     # $1,000
    SubscriptionTier.ENTERPRISE: 2000,  # $2,000
}

def get_tier_details() -> Dict[str, Dict[str, Any]]:
    """Get details for all subscription tiers"""
    return {
        SubscriptionTier.STARTER: {
            "name": "Starter",
            "price": PRICE_AMOUNTS[SubscriptionTier.STARTER],
            "price_id": PRICE_IDS[SubscriptionTier.STARTER],
            "features": [
                "Basic dashboard access",
                "Up to 10 companies in Radar",
                "1 dataroom per month",
                "Basic API access (100 calls/day)"
            ]
        },
        SubscriptionTier.PRO: {
            "name": "Pro",
            "price": PRICE_AMOUNTS[SubscriptionTier.PRO],
            "price_id": PRICE_IDS[SubscriptionTier.PRO],
            "features": [
                "Full dashboard access",
                "Up to 50 companies in Radar",
                "5 datarooms per month",
                "Advanced API access (500 calls/day)",
                "Priority support"
            ]
        },
        SubscriptionTier.ENTERPRISE: {
            "name": "Enterprise",
            "price": PRICE_AMOUNTS[SubscriptionTier.ENTERPRISE],
            "price_id": PRICE_IDS[SubscriptionTier.ENTERPRISE],
            "features": [
                "Full dashboard access",
                "Unlimited companies in Radar",
                "Unlimited datarooms",
                "Unlimited API access",
                "Dedicated support",
                "Custom integrations"
            ]
        }
    }

def create_checkout_session(tier: SubscriptionTier, customer_email: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
    """
    Create a Stripe Checkout session for the specified tier
    
    Args:
        tier: The subscription tier
        customer_email: The customer's email
        success_url: URL to redirect to after successful payment
        cancel_url: URL to redirect to if the customer cancels
        
    Returns:
        Dict containing the session ID and checkout URL
    """
    try:
        # Create the checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": PRICE_AMOUNTS[tier] * 100,  # Convert to cents
                        "product_data": {
                            "name": f"AI.VC {get_tier_details()[tier]['name']} Plan",
                            "description": "Monthly subscription",
                        },
                    },
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
        )
        
        return {
            "id": session.id,
            "url": session.url,
        }
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        raise

def retrieve_subscription(subscription_id: str) -> Dict[str, Any]:
    """
    Retrieve subscription details from Stripe
    
    Args:
        subscription_id: The Stripe subscription ID
        
    Returns:
        Dict containing the subscription details
    """
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription
    except Exception as e:
        print(f"Error retrieving subscription: {str(e)}")
        raise

def update_subscription_status(subscription_id: str, status: SubscriptionStatus) -> Dict[str, Any]:
    """
    Update a subscription's status in Stripe
    
    Args:
        subscription_id: The Stripe subscription ID
        status: The new status
        
    Returns:
        Dict containing the updated subscription details
    """
    try:
        if status == SubscriptionStatus.CANCELED:
            subscription = stripe.Subscription.cancel(subscription_id)
        else:
            # For other status changes, you would need to implement
            # appropriate Stripe API calls
            pass
        
        return subscription
    except Exception as e:
        print(f"Error updating subscription: {str(e)}")
        raise

def handle_webhook_event(payload: Dict[str, Any], sig_header: str, webhook_secret: str) -> Tuple[str, Dict[str, Any]]:
    """
    Verify and process a webhook event from Stripe
    
    Args:
        payload: The webhook payload
        sig_header: The Stripe signature header
        webhook_secret: The webhook signing secret
        
    Returns:
        Tuple of (event_type, event_data)
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        
        # Return the event type and data
        return event.type, event.data.object
    except stripe.error.SignatureVerificationError:
        print("Invalid signature")
        raise
    except Exception as e:
        print(f"Error handling webhook: {str(e)}")
        raise

def get_invoice_details(invoice_id: str) -> Dict[str, Any]:
    """
    Get details of a specific invoice
    
    Args:
        invoice_id: The Stripe invoice ID
        
    Returns:
        Dict containing the invoice details
    """
    try:
        invoice = stripe.Invoice.retrieve(invoice_id)
        return invoice
    except Exception as e:
        print(f"Error retrieving invoice: {str(e)}")
        raise