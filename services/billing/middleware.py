"""
Subscription Middleware Module for AI.VC Platform

This module provides middleware functionality to enforce subscription-based
access control across the platform's services.
"""

import logging
from typing import Callable, Dict, Any, Optional
from functools import wraps

from fastapi import Request, Response, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from subscription_service import SubscriptionService, AccessMode, SubscriptionStatus

logger = logging.getLogger(__name__)

def get_operation_type_from_path(path: str, method: str) -> str:
    """
    Determine the operation type based on the request path and method.
    
    Args:
        path: The request path
        method: The HTTP method
    
    Returns:
        str: The determined operation type
    """
    if method == "GET":
        return "get" if "/id/" in path or path.endswith("/details") else "list"
    elif method == "POST":
        if "/search" in path:
            return "search"
        elif "/export" in path:
            return "export"
        elif "/import" in path or "/upload" in path:
            return "upload"
        else:
            return "create"
    elif method == "PUT" or method == "PATCH":
        return "update"
    elif method == "DELETE":
        return "delete"
    else:
        return "unknown"

async def subscription_middleware(
    request: Request,
    call_next: Callable,
    db: Session = Depends(get_db)
) -> Response:
    """
    Middleware to enforce subscription-based access control.
    
    Args:
        request: The incoming request
        call_next: The next middleware or endpoint handler
        db: Database session
    
    Returns:
        Response: The response after access control
    """
    # Paths that should bypass subscription check
    bypass_paths = [
        "/api/health",
        "/api/docs",
        "/api/openapi.json",
        "/api/auth",
        "/api/login",
        "/api/register",
        "/api/webhook",
        "/api/create-checkout-session",
        "/api/create-customer-portal"
    ]
    
    path = request.url.path
    
    # Skip middleware for bypass paths
    if any(path.startswith(bp) for bp in bypass_paths):
        return await call_next(request)
    
    # Get user ID from the request (either from token or header)
    user_id = None
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        # Extract user ID from token (simplified)
        # In a real implementation, this would decode and validate the token
        token = auth_header.replace("Bearer ", "")
        user_id = "mock_user_id_for_demo"  # In production, extract from token
    
    if not user_id:
        # No user ID found, deny access
        logger.warning(f"No user ID found in request to {path}")
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Determine operation type from the request
    operation_type = get_operation_type_from_path(path, request.method)
    
    # Check if the user has access to perform this operation
    has_access = SubscriptionService.check_access_for_operation(
        user_id=user_id,
        operation_type=operation_type,
        db=db
    )
    
    if not has_access:
        logger.warning(f"User {user_id} denied access to {operation_type} operation on {path}")
        if operation_type in ["create", "update", "delete", "import", "upload"]:
            # If this is a write operation, return subscription required error
            raise HTTPException(
                status_code=403,
                detail="Your current subscription does not allow this operation. Please upgrade your plan."
            )
        else:
            # Otherwise, continue with the request
            # This allows read operations for canceled subscriptions
            pass
    
    # Continue processing the request
    response = await call_next(request)
    return response

def require_active_subscription(db: Session = Depends(get_db)):
    """
    Dependency to require an active subscription for a specific endpoint.
    
    Args:
        db: Database session
    
    Returns:
        Callable: A dependency function that checks for an active subscription
    """
    def dependency(request: Request):
        # Get user ID from the request (simplified)
        user_id = "mock_user_id_for_demo"  # In production, extract from token
        
        # Check if the user exists and has an active subscription
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.subscription_id:
            raise HTTPException(
                status_code=403,
                detail="Subscription required to access this feature"
            )
        
        # Check subscription status
        subscription = db.query(Subscription).filter(Subscription.id == user.subscription_id).first()
        if not subscription or subscription.status != SubscriptionStatus.ACTIVE:
            raise HTTPException(
                status_code=403,
                detail="Active subscription required to access this feature"
            )
        
        return True
    
    return dependency