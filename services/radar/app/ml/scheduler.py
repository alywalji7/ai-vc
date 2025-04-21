"""
Scheduler for nightly model retraining.
"""
import os
import time
import logging
import threading
import schedule
from datetime import datetime

from .pipeline import run_training_pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
TRAINING_SCHEDULE = os.environ.get("RADAR_TRAINING_SCHEDULE", "02:00")  # Default to 2 AM
DISABLE_SCHEDULER = os.environ.get("DISABLE_RADAR_SCHEDULER", "false").lower() == "true"


def run_threaded(job_func):
    """
    Run job in a separate thread.
    
    Args:
        job_func: Function to run
    """
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
    logger.info(f"Started job thread {job_thread.name}")


def start_scheduler():
    """
    Start the scheduler for nightly model retraining.
    """
    if DISABLE_SCHEDULER:
        logger.info("Radar model training scheduler is disabled")
        return
    
    logger.info(f"Setting up radar model training scheduler to run at {TRAINING_SCHEDULE}")
    
    # Schedule the job
    schedule.every().day.at(TRAINING_SCHEDULE).do(run_threaded, run_training_pipeline)
    logger.info(f"Scheduled model retraining to run daily at {TRAINING_SCHEDULE}")
    
    # Run in a separate thread
    def run_scheduler():
        """Run the scheduler loop."""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info(f"Radar model training scheduler started in thread {scheduler_thread.name}")


def run_initial_training():
    """
    Run initial training at service startup.
    """
    logger.info("Running initial model training at startup")
    try:
        run_training_pipeline()
        logger.info("Initial model training completed successfully")
    except Exception as e:
        logger.error(f"Error during initial model training: {str(e)}")
        # Continue with startup even if initial training fails