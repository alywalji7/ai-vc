"""
Upload Service API - Main application
"""
import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.models.db import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Portfolio Upload Service",
    description="API for secure file upload and portfolio parsing",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    Create database tables if they don't exist.
    """
    logger.info("Starting up the upload service...")
    create_tables()
    logger.info("Database tables initialized")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

# Run application if called directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8400))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)