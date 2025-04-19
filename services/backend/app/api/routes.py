"""
Main API routes module.

This module aggregates all API routers and makes them available under a common prefix.
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.api.dataroom import router as dataroom_router
from app.api.due_diligence import router as dd_router

# Create the main API router
router = APIRouter(prefix="/api")

# Include all sub-routers
router.include_router(dataroom_router)
router.include_router(dd_router)


@router.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Welcome to the API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "services": {
            "api": "up",
            "database": "up",
        }
    }