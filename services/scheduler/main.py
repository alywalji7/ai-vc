"""
Main entry point for the scheduler service.

This module starts all components of the scheduler service:
1. FastAPI server for API endpoints
2. Celery worker for task execution
3. Prometheus metrics exporter
4. Task scheduler
"""

import os
import subprocess
import threading
import time
import logging
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set default Redis URL if not provided in environment
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Define processes to start
processes = []

def start_api_server():
    """Start the FastAPI server."""
    api_cmd = ['python', '-m', 'uvicorn', 'api:app', '--host', '0.0.0.0', '--port', '8000']
    logger.info(f"Starting API server: {' '.join(api_cmd)}")
    return subprocess.Popen(api_cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

def start_celery_worker():
    """Start the Celery worker."""
    worker_cmd = [
        'celery', '-A', 'tasks', 'worker',
        '--loglevel=INFO',
        '--concurrency=4',
        '--without-gossip',  # Disable gossip for better performance
        '--without-mingle',  # Disable mingle for better performance
        '--without-heartbeat'  # Disable heartbeat for better performance
    ]
    logger.info(f"Starting Celery worker: {' '.join(worker_cmd)}")
    return subprocess.Popen(worker_cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

def start_flower():
    """Start Flower for monitoring Celery tasks."""
    flower_cmd = [
        'celery', '-A', 'tasks', 'flower',
        '--port=5555',
        '--broker=' + REDIS_URL
    ]
    logger.info(f"Starting Flower: {' '.join(flower_cmd)}")
    return subprocess.Popen(flower_cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

def start_scheduler():
    """Start the task scheduler."""
    scheduler_cmd = ['python', 'scheduler.py']
    logger.info(f"Starting scheduler: {' '.join(scheduler_cmd)}")
    return subprocess.Popen(scheduler_cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

def start_prometheus():
    """Start Prometheus server."""
    # In production, you would typically run Prometheus as a separate service
    # This is a placeholder for local development
    prometheus_cmd = ['echo', 'Prometheus server would start here']
    logger.info("Prometheus metrics exporter already started by scheduler")
    return None

def start_grafana():
    """Start Grafana server."""
    # In production, you would typically run Grafana as a separate service
    # This is a placeholder for local development
    grafana_cmd = ['echo', 'Grafana server would start here']
    logger.info("Grafana would start here in a real deployment")
    return None

def cleanup(signum, frame):
    """Clean up processes on exit."""
    logger.info(f"Received signal {signum}, shutting down services...")
    
    for proc in processes:
        if proc and proc.poll() is None:  # If process is still running
            logger.info(f"Terminating process with PID {proc.pid}")
            proc.terminate()
    
    # Wait for processes to terminate gracefully
    time.sleep(2)
    
    # Force kill any remaining processes
    for proc in processes:
        if proc and proc.poll() is None:
            logger.info(f"Force killing process with PID {proc.pid}")
            proc.kill()
    
    logger.info("All services shut down")
    sys.exit(0)

def start_services():
    """Start all scheduler services."""
    global processes
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    
    try:
        # Start all components
        processes = [
            start_api_server(),
            start_celery_worker(),
            start_flower(),
            start_scheduler(),
            start_prometheus(),
            start_grafana()
        ]
        
        # Filter out None processes
        processes = [p for p in processes if p is not None]
        
        logger.info("All services started")
        
        # Keep the main thread alive
        while all(p.poll() is None for p in processes if p is not None):
            time.sleep(1)
        
        # If we get here, at least one process has exited
        for p in processes:
            if p and p.poll() is not None:
                logger.error(f"Process with PID {p.pid} exited with code {p.returncode}")
        
        # Cleanup all processes
        cleanup(signal.SIGTERM, None)
        
    except Exception as e:
        logger.error(f"Error starting services: {e}")
        cleanup(signal.SIGTERM, None)

if __name__ == "__main__":
    logger.info("Starting scheduler services")
    start_services()