"""
Scheduler service that reads a crontab.yml file and schedules Celery tasks.

This module defines a scheduler that:
1. Reads a crontab.yml configuration file
2. Schedules tasks at specified intervals using the Celery beat service
3. Exposes metrics via Prometheus for monitoring
"""

import os
import time
import yaml
import logging
from datetime import datetime, timedelta
from croniter import croniter
from celery import Celery
import prometheus_client
from prometheus_client import Counter, Gauge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set default Redis URL if not provided in environment
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Get the path to the crontab.yml file
CRONTAB_PATH = os.environ.get('CRONTAB_PATH', 'services/scheduler/crontab.yml')

# Create metrics
SCHEDULER_TASK_NEXT_RUN = Gauge(
    'scheduler_task_next_run_seconds',
    'Time in seconds until the next scheduled run of each task',
    ['task_name']
)

SCHEDULER_LAST_LOAD_SUCCESS = Gauge(
    'scheduler_last_load_success',
    'Whether the last crontab load was successful (1=success, 0=failure)'
)

SCHEDULER_TASK_SCHEDULED = Counter(
    'scheduler_task_scheduled_total',
    'Number of times a task has been scheduled',
    ['task_name']
)

class Scheduler:
    """
    Service that reads a crontab.yml file and schedules Celery tasks.
    """
    
    def __init__(self, crontab_path, app):
        """
        Initialize the scheduler.
        
        Args:
            crontab_path: Path to the crontab.yml configuration file
            app: Celery application
        """
        self.crontab_path = crontab_path
        self.app = app
        self.scheduled_tasks = {}
        self.last_check_time = datetime.now()
        # Start with failure until we successfully load
        SCHEDULER_LAST_LOAD_SUCCESS.set(0)
    
    def load_crontab(self):
        """
        Load the crontab configuration from the YAML file.
        
        Returns:
            Dictionary containing the task configurations
        """
        try:
            logger.info(f"Loading crontab from {self.crontab_path}")
            with open(self.crontab_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Set success metric
            SCHEDULER_LAST_LOAD_SUCCESS.set(1)
            return config
        except Exception as e:
            logger.error(f"Error loading crontab: {e}")
            # Set failure metric
            SCHEDULER_LAST_LOAD_SUCCESS.set(0)
            raise
    
    def calculate_next_run(self, cron_expr):
        """
        Calculate the next run time based on a cron expression.
        
        Args:
            cron_expr: Cron expression string
            
        Returns:
            Datetime object representing the next run time
        """
        iter = croniter(cron_expr, datetime.now())
        return iter.get_next(datetime)
    
    def seconds_until_next_run(self, next_run):
        """
        Calculate the number of seconds until the next run.
        
        Args:
            next_run: Datetime object representing the next run time
            
        Returns:
            Number of seconds until the next run
        """
        now = datetime.now()
        return max(0, (next_run - now).total_seconds())
    
    def schedule_task(self, task_config):
        """
        Schedule a single task based on its configuration.
        
        Args:
            task_config: Dictionary containing the task configuration
            
        Returns:
            None
        """
        task_name = task_config['name']
        cron_expr = task_config['cron']
        task_path = task_config['task']
        args = task_config.get('args', [])
        kwargs = task_config.get('kwargs', {})
        
        # Calculate next run time
        next_run = self.calculate_next_run(cron_expr)
        
        # Update metric for next run time
        seconds_until_next = self.seconds_until_next_run(next_run)
        SCHEDULER_TASK_NEXT_RUN.labels(task_name=task_name).set(seconds_until_next)
        
        logger.info(f"Task {task_name} scheduled to run in {seconds_until_next:.2f} seconds")
        
        # Get the task function
        task_func = self.app.tasks[task_path]
        
        # Schedule the task
        self.app.send_task(
            task_path,
            args=args,
            kwargs=kwargs,
            eta=next_run,
            task_id=f"{task_name}-{next_run.isoformat()}"
        )
        
        # Increment the scheduled counter
        SCHEDULER_TASK_SCHEDULED.labels(task_name=task_name).inc()
        
        # Store the next run time
        self.scheduled_tasks[task_name] = {
            'config': task_config,
            'next_run': next_run
        }
    
    def run(self):
        """
        Main loop for the scheduler.
        
        This method:
        1. Loads the crontab configuration
        2. Identifies tasks that need to be scheduled
        3. Schedules those tasks
        4. Updates metrics
        5. Sleeps until the next check
        
        Returns:
            None
        """
        logger.info("Starting scheduler service")
        
        while True:
            try:
                # Load the crontab configuration
                config = self.load_crontab()
                
                # Get the current time
                now = datetime.now()
                
                # Process each task in the configuration
                for task_config in config.get('tasks', []):
                    task_name = task_config['name']
                    
                    # Skip tasks that are not enabled
                    if not task_config.get('enabled', True):
                        logger.debug(f"Skipping disabled task: {task_name}")
                        continue
                    
                    # Check if the task needs to be scheduled
                    if (task_name not in self.scheduled_tasks or
                            now >= self.scheduled_tasks[task_name]['next_run']):
                        self.schedule_task(task_config)
                
                # Update the last check time
                self.last_check_time = now
                
                # Sleep for a bit before checking again
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                time.sleep(60)  # Sleep longer on error
                

def start_scheduler():
    """
    Start the scheduler service.
    
    This function:
    1. Creates a Celery application
    2. Creates a Scheduler instance
    3. Starts the Prometheus metrics exporter
    4. Runs the scheduler
    
    Returns:
        None
    """
    # Create Celery application
    app = Celery('scheduler',
                broker=REDIS_URL,
                backend=REDIS_URL)
    
    # Start Prometheus metrics server
    prometheus_client.start_http_server(9090)
    
    # Create and run scheduler
    scheduler = Scheduler(CRONTAB_PATH, app)
    scheduler.run()


if __name__ == "__main__":
    start_scheduler()