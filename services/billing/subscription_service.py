"""
Subscription Service Module for AI.VC Platform

This module provides functions for managing user subscriptions, 
including handling subscription cancellations and enforcing
read-only mode for canceled subscriptions.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session

from models import Subscription, User
from repository import get_subscription_by_id, update_subscription_status

logger = logging.getLogger(__name__)

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    UNPAID = "unpaid"

class AccessMode(str, Enum):
    FULL = "full"
    READ_ONLY = "read_only"
    NONE = "none"

class SubscriptionService:
    """Service for managing subscription-related operations."""

    @staticmethod
    def get_access_mode(subscription_status: SubscriptionStatus) -> AccessMode:
        """
        Determine access mode based on subscription status.
        
        Args:
            subscription_status: The current status of the subscription
            
        Returns:
            AccessMode: The appropriate access mode for the subscription
        """
        if subscription_status == SubscriptionStatus.ACTIVE or subscription_status == SubscriptionStatus.TRIALING:
            return AccessMode.FULL
        elif subscription_status == SubscriptionStatus.CANCELED:
            # Canceled subscriptions still have read-only access until the end of the billing period
            return AccessMode.READ_ONLY
        else:
            # All other statuses (past_due, incomplete, etc.) have no access
            return AccessMode.NONE

    @staticmethod
    def handle_subscription_canceled(db: Session, subscription_id: str) -> None:
        """
        Handle a subscription cancellation.
        
        Args:
            db: Database session
            subscription_id: ID of the canceled subscription
        """
        logger.info(f"Processing subscription cancellation for subscription {subscription_id}")
        
        # Update subscription status in database
        subscription = get_subscription_by_id(db, subscription_id)
        if not subscription:
            logger.error(f"Subscription {subscription_id} not found")
            return
        
        update_subscription_status(db, subscription_id, SubscriptionStatus.CANCELED)
        logger.info(f"Subscription {subscription_id} marked as canceled")

    @staticmethod
    def check_access_for_operation(user_id: str, operation_type: str, db: Session) -> bool:
        """
        Check if a user has access to perform a specific operation.
        
        Args:
            user_id: ID of the user
            operation_type: Type of operation being performed
            db: Database session
            
        Returns:
            bool: True if the user has access, False otherwise
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.subscription_id:
            logger.warning(f"User {user_id} has no subscription")
            return False
        
        subscription = get_subscription_by_id(db, user.subscription_id)
        if not subscription:
            logger.warning(f"Subscription {user.subscription_id} not found for user {user_id}")
            return False
        
        access_mode = SubscriptionService.get_access_mode(SubscriptionStatus(subscription.status))
        
        # Define which operations are allowed for each access mode
        read_operations = ["get", "list", "view", "export", "search"]
        write_operations = ["create", "update", "delete", "import", "upload"]
        
        if access_mode == AccessMode.FULL:
            # Full access can do all operations
            return True
        elif access_mode == AccessMode.READ_ONLY:
            # Read-only access can only do read operations
            return operation_type.lower() in read_operations
        else:
            # No access can't do any operations
            return False

    @staticmethod
    def update_subscription_seats(
        db: Session, 
        subscription_id: str, 
        seats_used: int
    ) -> None:
        """
        Update the number of seats used in a subscription.
        
        Args:
            db: Database session
            subscription_id: ID of the subscription
            seats_used: Number of seats currently in use
        """
        subscription = get_subscription_by_id(db, subscription_id)
        if not subscription:
            logger.error(f"Subscription {subscription_id} not found")
            return
        
        subscription.seats_used = seats_used
        db.commit()
        logger.info(f"Updated seats used for subscription {subscription_id} to {seats_used}")

    @staticmethod
    def update_api_usage(
        db: Session, 
        subscription_id: str, 
        api_calls_today: int
    ) -> None:
        """
        Update the API usage for a subscription.
        
        Args:
            db: Database session
            subscription_id: ID of the subscription
            api_calls_today: Number of API calls made today
        """
        subscription = get_subscription_by_id(db, subscription_id)
        if not subscription:
            logger.error(f"Subscription {subscription_id} not found")
            return
        
        subscription.api_calls_today = api_calls_today
        db.commit()
        logger.info(f"Updated API usage for subscription {subscription_id} to {api_calls_today} calls today")