"""
Main module for the Graph Ingest Service.

This is the entry point for the Graph Ingest Service.
"""

import os
import logging
import threading
import uvicorn
from dotenv import load_dotenv
from prometheus_client import start_http_server

from app.db import init_db
# Import the API directly from the module since there's a directory conflict
from app.api import api
from app.scheduler import start_scheduler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    """
    Main entry point for the Graph Ingest Service.
    """
    logger.info("Starting Graph Ingest Service")
    
    # Initialize the database
    try:
        init_db()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return 1
    
    # Start the metrics server
    metrics_port = int(os.environ.get("METRICS_PORT", 8091))
    start_http_server(metrics_port)
    logger.info(f"Metrics server started on port {metrics_port}")
    
    # Start the scheduler in a background thread
    scheduler_thread = start_scheduler()
    logger.info(f"Scheduler started in thread {scheduler_thread.name}")
    
    # Start the API server
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting API server on port {port}")
    
    uvicorn.run(
        "main:api",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True
    )
    
    return 0

if __name__ == "__main__":
    main()