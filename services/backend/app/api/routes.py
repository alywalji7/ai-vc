"""
Main API router.

This module combines all the API routers from different modules.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.api.dataroom import router as dataroom_router
from app.api.due_diligence import router as dd_router

# Main API router
router = APIRouter()

# Include all sub-routers
router.include_router(dataroom_router)
router.include_router(dd_router)


@router.get("/", tags=["root"])
async def api_root():
    """
    Root endpoint for the API.
    """
    return {
        "message": "API is running",
        "version": "1.0.0",
        "endpoints": [
            "/api/dataroom",
            "/api/dd"
        ]
    }