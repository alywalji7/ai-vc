"""
FastAPI application for the Deal-Flow Radar service.
"""
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .database import create_tables
from .routes.api import router as api_router

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI app instance
    """
    app = FastAPI(
        title="Deal-Flow Radar",
        description="Investment opportunity scoring service using ML to identify promising companies",
        version="0.1.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    app.include_router(api_router)
    
    # Create default route
    @app.get("/", tags=["Status"])
    async def root():
        """
        Root endpoint - return basic service info.
        """
        return {
            "service": "Deal-Flow Radar",
            "version": "0.1.0",
            "status": "operational",
            "endpoints": {
                "daily_shortlist": "/radar/daily_shortlist",
                "model_metadata": "/radar/model_metadata",
            }
        }
    
    @app.get("/health", tags=["Status"])
    async def health_check():
        """
        Health check endpoint.
        """
        return {"status": "ok"}
    
    # Create database tables on startup
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning(f"Could not create database tables: {str(e)}")
    
    return app


app = create_app()