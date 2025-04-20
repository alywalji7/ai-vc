"""
Admin override functionality for the compliance system.

This module provides a FastAPI router with administrative override endpoints,
including the kill-switch override that requires GP-level authorization.
"""

import logging
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .models import AdminOverride
from services.backend.app.db import get_db

logger = logging.getLogger(__name__)

# Security scheme for JWT Bearer tokens
security = HTTPBearer()

# Create admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])


def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> str:
    """
    Get the role of the current user from their JWT token.
    
    In a real application, this would validate the JWT token
    and extract the user's role from the claims.
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        User role string
        
    Raises:
        HTTPException: If authentication fails
    """
    # In a real implementation, this would verify the JWT and get the user's role
    # For this example, we'll parse it from the token directly
    
    try:
        token = credentials.credentials
        
        # This is a simplistic check just for demonstration
        # In a real system, you would decode and verify the JWT properly
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token contains role claim
        # Note: In a real application, you would properly parse the JWT
        if "role=GP" in token:
            return "GP"
        elif "role=LP" in token:
            return "LP"
        elif "role=ADMIN" in token:
            return "ADMIN"
        else:
            return "USER"
    
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_gp_role(role: str = Depends(get_current_user_role)):
    """
    Dependency to require a GP role for certain endpoints.
    
    Args:
        role: User role from the get_current_user_role dependency
        
    Returns:
        The role if authorized
        
    Raises:
        HTTPException: If user doesn't have GP role
    """
    if role != "GP":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. GP role required.",
        )
    return role


@admin_router.get("/")
async def admin_root():
    """Admin API root endpoint."""
    return {
        "message": "Admin API",
        "endpoints": [
            "/admin/override",
            "/admin/audit-logs"
        ]
    }


@admin_router.post("/override", response_model=Dict[str, Any])
async def admin_override(
    override_data: Dict[str, Any],
    role: str = Depends(require_gp_role),
    db: Session = Depends(get_db)
):
    """
    Kill-switch admin override endpoint. Requires GP role.
    
    This endpoint allows GPs to override compliance checks and other
    system rules when necessary. All overrides are thoroughly logged.
    
    Args:
        override_data: Data for the override
        role: User role (from dependency)
        db: Database session
        
    Returns:
        Dictionary with override details
    """
    logger.warning(f"ADMIN OVERRIDE INITIATED BY {role} USER: {override_data}")
    
    # Create a record of the override
    override = AdminOverride(
        override_type=override_data.get("type", "general"),
        description=override_data.get("description", ""),
        original_decision_id=override_data.get("original_decision_id"),
        override_data=override_data,
        user_id=override_data.get("user_id", "unknown"),
        user_role=role
    )
    
    # Add to database and commit
    db.add(override)
    db.commit()
    db.refresh(override)
    
    logger.info(f"Admin override logged: ID {override.id}")
    
    return {
        "status": "success",
        "message": "Administrative override applied successfully",
        "override_id": override.id,
        "timestamp": override.created_at,
    }


@admin_router.get("/audit-logs", response_model=List[Dict[str, Any]])
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    role: str = Depends(require_gp_role),
    db: Session = Depends(get_db)
):
    """
    Retrieve audit logs. Requires GP role.
    
    Args:
        limit: Maximum number of logs to return
        offset: Offset for pagination
        role: User role (from dependency)
        db: Database session
        
    Returns:
        List of audit log entries
    """
    from .models import AuditLog
    
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "decision_type": log.decision_type,
            "payload_hash": log.payload_hash,
            "user_id": log.user_id,
            "company_id": log.company_id,
            "created_at": log.created_at,
        }
        for log in logs
    ]