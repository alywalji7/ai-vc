#!/usr/bin/env python3
"""
Startup script for the Portfolio Telemetry & Follow-On Engine service.

This script initializes and starts the FastAPI application for
the Portfolio Telemetry service.
"""
import os
import uvicorn
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    """
    Main entry point for the service.
    """
    logger.info("Starting Portfolio Telemetry & Follow-On Engine service")
    
    # Get configuration from environment
    port = int(os.environ.get("PORT", 8100))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Service will be available at http://{host}:{port}")
    
    # Start the service
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )

if __name__ == "__main__":
    main()