"""
Main entry point for the Deal-Flow Radar service.
"""
import logging
import os
import uvicorn
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def main():
    """
    Start the Deal-Flow Radar API server.
    """
    # Configure the server
    host = os.environ.get("RADAR_HOST", "0.0.0.0")
    port = int(os.environ.get("RADAR_PORT", 8095))
    
    logger.info(f"Starting Deal-Flow Radar server at http://{host}:{port}")
    
    # Start the server
    uvicorn.run(
        "app.app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()