"""
Main entry point for the backend service.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.db import engine, get_db
from app.api.routes import router as api_router
from app.observability import setup_observability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create database tables
logger.info("Creating database tables")
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="AI.VC Backend API", version="1.0.0")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:8000",
    "http://localhost",
    "https://localhost",
    "*"  # Allow all origins in development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up observability (tracing and metrics)
setup_observability(
    app=app,
    db_engine=engine,
    service_name="backend"
)

logger.info("Backend service initialized with observability")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Polyglot Monorepo Backend API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 8000)), 
        reload=True
    )