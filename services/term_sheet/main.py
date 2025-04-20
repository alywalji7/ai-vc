"""
Main entry point for the Term Sheet Generator & Negotiator Bot service.

This service provides:
1. Generation of NVCA model documents using docxtpl templates
2. WebSocket API for real-time term sheet negotiations using GPT-4o
3. Lane guards with Slack escalation for extreme counter-offers
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import endpoints as api_endpoints

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Term Sheet Generator & Negotiator Bot",
    description="API for generating NVCA model documents and negotiating term sheets",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific frontend origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_endpoints.router, prefix="/api")


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with service information."""
    return {
        "service": "Term Sheet Generator & Negotiator Bot",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "generate_term_sheet": "/api/generate",
            "download_document": "/api/download/{document_path}",
            "create_negotiation_session": "/api/negotiate/session",
            "get_negotiation_session": "/api/negotiate/session/{session_id}",
            "negotiate_chat_websocket": "/api/negotiate/chat/{session_id}",
        }
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    # Check if required environment variables are set
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set. GPT integration will not function.")
        
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for the application."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8070"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Term Sheet Generator & Negotiator Bot server at http://{host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )