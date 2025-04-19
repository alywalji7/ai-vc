"""
Main entry point for the similarity API service.
"""

import sys
import argparse
import logging
import uvicorn

from app.app import create_app
from app.config import API_HOST, API_PORT, API_DEBUG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Parse command-line arguments and start the application."""
    parser = argparse.ArgumentParser(description="Similarity API Service")
    parser.add_argument(
        "--host", 
        type=str, 
        default=API_HOST,
        help=f"Host to bind the server to. Default: {API_HOST}"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=API_PORT,
        help=f"Port to bind the server to. Default: {API_PORT}"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        default=API_DEBUG,
        help="Run the server in debug mode. Default: False"
    )
    
    args = parser.parse_args()
    
    app = create_app()
    
    logger.info(f"Starting similarity API server at http://{args.host}:{args.port}")
    uvicorn.run(
        app, 
        host=args.host, 
        port=args.port,
        reload=args.debug
    )


if __name__ == "__main__":
    main()