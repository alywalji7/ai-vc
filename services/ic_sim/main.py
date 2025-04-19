"""
Main entry point for the Investment Committee Simulator service.
"""

import os
import logging
import sys
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router

# Load environment variables from .env file if present
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Check for required environment variables
if not os.environ.get("OPENAI_API_KEY"):
    logger.warning("OPENAI_API_KEY environment variable not set. LLM analysis will not work.")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Investment Committee Simulator",
        description="Two-stage investment decision process: rule filtering and LLM-based analysis",
        version="0.1.0",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include the API router
    app.include_router(api_router, prefix="/api")
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """
        Health check endpoint.
        
        Returns:
            Health status
        """
        return {"status": "healthy", "service": "ic_simulator"}
    
    # Add root endpoint
    @app.get("/")
    async def root():
        """
        Root endpoint.
        
        Returns:
            Service information
        """
        return {
            "name": "Investment Committee Simulator",
            "version": "0.1.0",
            "description": "Two-stage investment decision process: rule filtering and LLM analysis",
            "api_docs": "/docs"
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    """
    Run the FastAPI server when script is executed directly.
    """
    port = int(os.environ.get("IC_SIM_PORT", 8060))
    host = os.environ.get("IC_SIM_HOST", "0.0.0.0")
    
    logger.info(f"Starting Investment Committee Simulator server at http://{host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )