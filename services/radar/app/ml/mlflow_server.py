"""
MLflow server initialization and utilities.
"""
import os
import logging
import subprocess
import threading
import signal
import atexit
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MLflow configuration
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlruns.db")
MLFLOW_PORT = int(os.environ.get("MLFLOW_PORT", 5000))
MLFLOW_HOST = os.environ.get("MLFLOW_HOST", "0.0.0.0")
MLFLOW_BACKEND_STORE_URI = os.environ.get("MLFLOW_BACKEND_STORE_URI", "sqlite:///mlruns.db")
MLFLOW_DEFAULT_ARTIFACT_ROOT = os.environ.get("MLFLOW_DEFAULT_ARTIFACT_ROOT", "./mlruns")

# Process handle for the MLflow server
mlflow_process = None


def start_mlflow_server(use_thread=True):
    """
    Start the MLflow tracking server.
    
    Args:
        use_thread: If True, start the server in a separate thread.
                   If False, start the server in the current process.
    """
    global mlflow_process
    
    # Check if MLflow server is already running
    if mlflow_process:
        logger.info("MLflow server is already running")
        return
    
    try:
        # Prepare command
        cmd = [
            "mlflow", "server",
            "--host", MLFLOW_HOST,
            "--port", str(MLFLOW_PORT),
            "--backend-store-uri", MLFLOW_BACKEND_STORE_URI,
            "--default-artifact-root", MLFLOW_DEFAULT_ARTIFACT_ROOT
        ]
        
        if use_thread:
            # Start MLflow server in a separate thread
            def run_server():
                """Run MLflow server."""
                global mlflow_process
                logger.info(f"Starting MLflow server with command: {' '.join(cmd)}")
                mlflow_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Capture and log output
                while mlflow_process.poll() is None:
                    output = mlflow_process.stderr.readline()
                    if output:
                        logger.info(f"MLflow: {output.strip()}")
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            logger.info(f"MLflow server thread started: {server_thread.name}")
            
            # Wait for server to start
            time.sleep(5)
            
        else:
            # Start MLflow server in the current process
            logger.info(f"Starting MLflow server with command: {' '.join(cmd)}")
            mlflow_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            logger.info("MLflow server started")
        
        # Register cleanup handler
        atexit.register(stop_mlflow_server)
        
    except Exception as e:
        logger.error(f"Error starting MLflow server: {str(e)}")
        raise


def stop_mlflow_server():
    """
    Stop the MLflow tracking server.
    """
    global mlflow_process
    
    if mlflow_process:
        logger.info("Stopping MLflow server")
        try:
            mlflow_process.terminate()
            # Wait for process to terminate
            mlflow_process.wait(timeout=5)
            logger.info("MLflow server stopped")
        except subprocess.TimeoutExpired:
            logger.warning("MLflow server did not terminate gracefully, killing it")
            mlflow_process.kill()
        except Exception as e:
            logger.error(f"Error stopping MLflow server: {str(e)}")
        finally:
            mlflow_process = None
    else:
        logger.info("No MLflow server to stop")


if __name__ == "__main__":
    # Start MLflow server in the current process
    start_mlflow_server(use_thread=False)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping MLflow server")
        stop_mlflow_server()