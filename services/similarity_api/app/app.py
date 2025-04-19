"""
FastAPI application factory.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.api import router as api_router

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI application instance
    """
    # Create FastAPI app
    app = FastAPI(
        title="Similarity API",
        description="API for vector similarity search using Qdrant",
        version="0.1.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, you'd restrict this to your frontend domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add routers
    app.include_router(api_router, prefix="/api/v1")
    
    # Root endpoint
    @app.get("/", tags=["general"])
    async def root():
        """Root endpoint with service information."""
        return {
            "name": "Similarity API",
            "version": "0.1.0",
            "description": "API for vector similarity search using Qdrant",
        }
    
    # Health check endpoint
    @app.get("/health", tags=["general"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
        }
    
    return app