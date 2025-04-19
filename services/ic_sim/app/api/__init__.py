"""
API routes for the Investment Committee Simulator.
"""

from fastapi import APIRouter
from app.api.endpoints import router as ic_router

# Create API router
api_router = APIRouter()

# Include the investment committee routes
api_router.include_router(ic_router, tags=["ic_simulator"])