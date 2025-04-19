from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from .router import router


def create_app() -> FastAPI:
    """Create the FastAPI application"""
    # Initialize database
    init_db()
    
    # Create FastAPI app
    app = FastAPI(
        title="Data Ingestion & Knowledge Graph Service",
        description="Service for ingesting data from various sources and building a knowledge graph",
        version="0.1.0",
    )
    
    # CORS configuration
    origins = [
        "http://localhost:5000",  # Frontend service
        "http://localhost:3000",  # Development frontend
        "http://frontend:5000",   # Docker frontend service
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(router, prefix="/api")
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "Data Ingestion & Knowledge Graph Service",
            "version": "0.1.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    return app