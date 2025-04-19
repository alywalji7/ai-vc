"""
Scheduler service that reads a crontab.yml file and schedules Celery tasks.

This module defines a scheduler that:
1. Reads a crontab.yml configuration file
2. Schedules tasks at specified intervals using the Celery beat service
3. Exposes metrics via Prometheus for monitoring
"""
import os
import time
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml
import croniter
import celery
import prometheus_client as pc
from prometheus_client import start_http_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment variables
CRONTAB_PATH = os.environ.get("CRONTAB_PATH", "crontab.yml")
PROMETHEUS_PORT = int(os.environ.get("PROMETHEUS_PORT", "9090"))


class Scheduler:
    """
    Service that reads a crontab.yml file and schedules Celery tasks.
    """
    
    def __init__(self, crontab_path: str, app: celery.Celery):
        """
        Initialize the scheduler.
        
        Args:
            crontab_path: Path to the crontab.yml configuration file
            app: Celery application
        """
        self.crontab_path = crontab_path
        self.app = app
        self.tasks: List[Dict[str, Any]] = []
        self.last_modified_time = 0
        
        # Define Prometheus metrics
        self.scheduled_tasks = pc.Gauge(
            "scheduled_tasks",
            "Number of tasks scheduled",
            ["task_name"]
        )
        self.crontab_reload_total = pc.Counter(
            "crontab_reload_total",
            "Total number of crontab reloads",
            ["status"]
        )
        self.next_execution_time = pc.Gauge(
            "next_execution_time_seconds",
            "Next execution time in seconds since epoch",
            ["task_name"]
        )
    
    def load_crontab(self) -> Dict[str, Any]:
        """
        Load the crontab configuration from the YAML file.
        
        Returns:
            Dictionary containing the task configurations
        """
        crontab_file = Path(self.crontab_path)
        
        if not crontab_file.exists():
            logger.error("Crontab file not found: %s", self.crontab_path)
            self.crontab_reload_total.labels(status="error").inc()
            return {}
        
        # Check if the file has been modified since the last load
        mod_time = crontab_file.stat().st_mtime
        if mod_time <= self.last_modified_time:
            # File hasn't changed, return cached tasks
            return {"tasks": self.tasks}
        
        try:
            with open(crontab_file, "r") as f:
                crontab = yaml.safe_load(f)
            
            # Update last modified time
            self.last_modified_time = mod_time
            
            # Update tasks cache
            self.tasks = crontab.get("tasks", [])
            
            self.crontab_reload_total.labels(status="success").inc()
            logger.info("Loaded crontab with %d tasks", len(self.tasks))
            
            return crontab
        except Exception as e:
            logger.error("Error loading crontab: %s", str(e))
            self.crontab_reload_total.labels(status="error").inc()
            return {}
    
    def calculate_next_run(self, cron_expr: str) -> datetime.datetime:
        """
        Calculate the next run time based on a cron expression.
        
        Args:
            cron_expr: Cron expression string
            
        Returns:
            Datetime object representing the next run time
        """
        now = datetime.datetime.now()
        cron = croniter.croniter(cron_expr, now)
        return cron.get_next(datetime.datetime)
    
    def seconds_until_next_run(self, next_run: datetime.datetime) -> float:
        """
        Calculate the number of seconds until the next run.
        
        Args:
            next_run: Datetime object representing the next run time
            
        Returns:
            Number of seconds until the next run
        """
        now = datetime.datetime.now()
        return (next_run - now).total_seconds()
    
    def schedule_task(self, task_config: Dict[str, Any]) -> None:
        """
        Schedule a single task based on its configuration.
        
        Args:
            task_config: Dictionary containing the task configuration
            
        Returns:
            None
        """
        name = task_config.get("name")
        cron = task_config.get("cron")
        task = task_config.get("task")
        args = task_config.get("args", [])
        kwargs = task_config.get("kwargs", {})
        enabled = task_config.get("enabled", True)
        
        if not all([name, cron, task]) or not enabled:
            if not enabled:
                logger.info("Task %s is disabled, skipping", name)
            else:
                logger.error("Invalid task configuration: %s", task_config)
            return
        
        # Calculate next run time
        next_run = self.calculate_next_run(cron)
        delay_seconds = self.seconds_until_next_run(next_run)
        
        # Update Prometheus metrics
        self.scheduled_tasks.labels(task_name=name).set(1)
        self.next_execution_time.labels(task_name=name).set(next_run.timestamp())
        
        # Schedule the task
        logger.info(
            "Scheduling task %s (%s) to run in %.2f seconds (at %s)",
            name, task, delay_seconds, next_run.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Apply the task with the given arguments
        task_instance = self.app.signature(task, args=args, kwargs=kwargs)
        result = task_instance.apply_async(countdown=max(0, int(delay_seconds)))
        
        logger.info("Task %s scheduled with ID %s", name, result.id)
    
    def run(self) -> None:
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
                crontab = self.load_crontab()
                tasks = crontab.get("tasks", [])
                
                # Schedule all tasks
                for task_config in tasks:
                    self.schedule_task(task_config)
                
                # Sleep for a while before checking again
                time.sleep(60)
            except Exception as e:
                logger.error("Error in scheduler: %s", str(e))
                time.sleep(60)


def start_scheduler() -> None:
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
    from celery_app import app
    
    # Start Prometheus metrics server
    logger.info("Starting Prometheus metrics server on port %d", PROMETHEUS_PORT)
    start_http_server(PROMETHEUS_PORT)
    
    # Create and run the scheduler
    scheduler = Scheduler(CRONTAB_PATH, app)
    scheduler.run()


if __name__ == "__main__":
    start_scheduler()