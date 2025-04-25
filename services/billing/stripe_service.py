import os
import stripe
from enum import Enum
from typing import Dict, Any, Optional, Tuple, List
import logging
from datetime import datetime

# Initialize logging
logger = logging.getLogger(__name__)

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

# Define usage types
class UsageType(str, Enum):
    SEATS = "seats"
    API_CALLS = "api_calls"
    RADAR_CALLS = "radar_calls"
    SIMILARITY_CALLS = "similarity_calls"

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

# Metered Usage IDs for each tier
# These would be created in Stripe dashboard and associated with your subscription products
USAGE_ITEM_IDS = {
    SubscriptionTier.STARTER: {
        UsageType.SEATS: "si_starter_seats",  # Replace with actual IDs from your Stripe dashboard
        UsageType.API_CALLS: "si_starter_api_calls",
        UsageType.RADAR_CALLS: "si_starter_radar_calls",
        UsageType.SIMILARITY_CALLS: "si_starter_similarity_calls",
    },
    SubscriptionTier.PRO: {
        UsageType.SEATS: "si_pro_seats",
        UsageType.API_CALLS: "si_pro_api_calls",
        UsageType.RADAR_CALLS: "si_pro_radar_calls",
        UsageType.SIMILARITY_CALLS: "si_pro_similarity_calls",
    },
    SubscriptionTier.ENTERPRISE: {
        UsageType.SEATS: "si_enterprise_seats",
        UsageType.API_CALLS: "si_enterprise_api_calls",
        UsageType.RADAR_CALLS: "si_enterprise_radar_calls",
        UsageType.SIMILARITY_CALLS: "si_enterprise_similarity_calls",
    },
}

# Subscription tier limits
TIER_LIMITS = {
    SubscriptionTier.STARTER: {
        "seats": 1,
        "api_calls_daily": 50,
        "radar_calls_daily": 50,
        "similarity_calls_daily": 50,
    },
    SubscriptionTier.PRO: {
        "seats": 3,
        "api_calls_daily": 500,
        "radar_calls_daily": 500,
        "similarity_calls_daily": 500,
    },
    SubscriptionTier.ENTERPRISE: {
        "seats": 999,  # Practically unlimited
        "api_calls_daily": 10000,  # Practically unlimited
        "radar_calls_daily": 10000,
        "similarity_calls_daily": 10000,
    },
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
                f"{TIER_LIMITS[SubscriptionTier.STARTER]['seats']} LP seat",
                f"{TIER_LIMITS[SubscriptionTier.STARTER]['api_calls_daily']} API calls/day"
            ],
            "limits": TIER_LIMITS[SubscriptionTier.STARTER]
        },
        SubscriptionTier.PRO: {
            "name": "Pro",
            "price": PRICE_AMOUNTS[SubscriptionTier.PRO],
            "price_id": PRICE_IDS[SubscriptionTier.PRO],
            "features": [
                "Full dashboard access",
                "Up to 50 companies in Radar",
                "5 datarooms per month",
                f"{TIER_LIMITS[SubscriptionTier.PRO]['seats']} LP seats",
                f"{TIER_LIMITS[SubscriptionTier.PRO]['api_calls_daily']} API calls/day",
                "Priority support"
            ],
            "limits": TIER_LIMITS[SubscriptionTier.PRO]
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
                "Unlimited LP seats",
                "Dedicated support",
                "Custom integrations"
            ],
            "limits": TIER_LIMITS[SubscriptionTier.ENTERPRISE]
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
        logger.error(f"Error creating checkout session: {str(e)}")
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
        logger.error(f"Error retrieving subscription: {str(e)}")
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
            subscription = stripe.Subscription.delete(subscription_id)
        else:
            # For other status changes, you would need to implement
            # appropriate Stripe API calls
            subscription = stripe.Subscription.retrieve(subscription_id)
        
        return subscription
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")
        raise

def handle_webhook_event(payload: bytes, sig_header: str, webhook_secret: str) -> Tuple[str, Dict[str, Any]]:
    """
    Verify and process a webhook event from Stripe
    
    Args:
        payload: The webhook payload (as bytes)
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
        logger.error("Invalid signature")
        raise
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
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
        logger.error(f"Error retrieving invoice: {str(e)}")
        raise

def report_usage(subscription_id: str, usage_type: UsageType, quantity: int, tier: SubscriptionTier) -> bool:
    """
    Report metered usage to Stripe
    
    Args:
        subscription_id: The Stripe subscription ID
        usage_type: The type of usage (seats, api_calls, etc.)
        quantity: The amount of usage to report
        tier: The subscription tier
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get subscription items
        subscription = retrieve_subscription(subscription_id)
        
        # Find the ID of the subscription item for this usage type
        item_id = None
        for item in subscription.items.data:
            if item.price.id == USAGE_ITEM_IDS[tier][usage_type]:
                item_id = item.id
                break
        
        if not item_id:
            logger.error(f"Could not find subscription item for usage type {usage_type}")
            return False
        
        # Create usage record
        stripe.SubscriptionItem.create_usage_record(
            item_id,
            quantity=quantity,
            timestamp=int(datetime.now().timestamp()),
            action="set"  # Set usage to the exact quantity
        )
        
        logger.info(f"Reported usage: {quantity} {usage_type} for subscription {subscription_id}")
        return True
    except Exception as e:
        logger.error(f"Error reporting usage: {str(e)}")
        return False

def get_subscription_tier(subscription_id: str) -> Optional[SubscriptionTier]:
    """
    Get the tier for a subscription
    
    Args:
        subscription_id: The Stripe subscription ID
        
    Returns:
        The subscription tier, or None if not found
    """
    try:
        subscription = retrieve_subscription(subscription_id)
        
        # Get the price ID for the subscription
        price_id = subscription.items.data[0].price.id if subscription.items.data else None
        
        if not price_id:
            return None
        
        # Find which tier this price belongs to
        for tier, price in PRICE_IDS.items():
            if price_id == price:
                return tier
        
        return None
    except Exception as e:
        logger.error(f"Error getting subscription tier: {str(e)}")
        return None

def get_subscription_item_ids(subscription_id: str) -> Dict[str, str]:
    """
    Get all subscription item IDs for a subscription
    
    Args:
        subscription_id: The Stripe subscription ID
        
    Returns:
        Dict mapping usage types to subscription item IDs
    """
    try:
        subscription = retrieve_subscription(subscription_id)
        
        result = {}
        for item in subscription.items.data:
            # Find which usage type this item belongs to
            for tier in SubscriptionTier:
                for usage_type, price_id in USAGE_ITEM_IDS[tier].items():
                    if item.price.id == price_id:
                        result[usage_type] = item.id
        
        return result
    except Exception as e:
        logger.error(f"Error getting subscription item IDs: {str(e)}")
        return {}

def create_customer_portal_session(customer_id: str, return_url: str) -> Dict[str, Any]:
    """
    Create a Stripe Customer Portal session for the customer
    
    Args:
        customer_id: The Stripe customer ID
        return_url: URL to redirect to after the customer portal session
        
    Returns:
        Dict containing the customer portal session URL
    """
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
            features={
                "customer_update": {
                    "allowed_updates": ["email", "address", "shipping", "phone", "tax_id"],
                    "enabled": True,
                },
                "invoice_history": {"enabled": True},
                "payment_method_update": {"enabled": True},
                "subscription_cancel": {"enabled": True},
                "subscription_update": {
                    "enabled": True,
                    "default_allowed_updates": ["price", "quantity"],
                    "products": {
                        # Include product mappings as needed
                    }
                }
            }
        )
        
        return {
            "url": session.url
        }
    except Exception as e:
        logger.error(f"Error creating customer portal session: {str(e)}")
        raise