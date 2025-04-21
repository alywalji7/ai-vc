"""
FastAPI application for the Deal-Flow Radar service.
"""
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import threading

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

# ML Pipeline configuration
ENABLE_MLFLOW_SERVER = os.environ.get("ENABLE_MLFLOW_SERVER", "true").lower() == "true"
ENABLE_ML_SCHEDULER = os.environ.get("ENABLE_ML_SCHEDULER", "true").lower() == "true"
RUN_INITIAL_TRAINING = os.environ.get("RUN_INITIAL_TRAINING", "true").lower() == "true"


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
    
    # Start MLflow server and scheduler on app startup
    @app.on_event("startup")
    async def startup_event():
        if ENABLE_MLFLOW_SERVER:
            try:
                from .ml.mlflow_server import start_mlflow_server
                start_mlflow_server(use_thread=True)
                logger.info("MLflow tracking server started")
            except Exception as e:
                logger.warning(f"Failed to start MLflow server: {str(e)}")
        
        if ENABLE_ML_SCHEDULER:
            try:
                from .ml.scheduler import start_scheduler
                start_scheduler()
                logger.info("ML training scheduler started")
            except Exception as e:
                logger.warning(f"Failed to start ML scheduler: {str(e)}")
        
        if RUN_INITIAL_TRAINING:
            try:
                # Run initial training in a separate thread
                from .ml.scheduler import run_initial_training
                threading.Thread(target=run_initial_training, daemon=True).start()
                logger.info("Initial model training started in background")
            except Exception as e:
                logger.warning(f"Failed to start initial model training: {str(e)}")
    
    # Clean up resources on shutdown
    @app.on_event("shutdown")
    async def shutdown_event():
        if ENABLE_MLFLOW_SERVER:
            try:
                from .ml.mlflow_server import stop_mlflow_server
                stop_mlflow_server()
                logger.info("MLflow tracking server stopped")
            except Exception as e:
                logger.warning(f"Error stopping MLflow server: {str(e)}")
    
    return app


app = create_app()