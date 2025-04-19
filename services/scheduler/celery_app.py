"""
Celery application configuration for the scheduler service.

This module creates and configures the Celery application for processing
data ingestion tasks.
"""
import os
import time
import functools
from typing import Callable, Any

import celery
import prometheus_client as pc

# Environment variables
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
app = celery.Celery("scheduler")
app.conf.broker_url = REDIS_URL
app.conf.result_backend = REDIS_URL
app.conf.task_routes = {"services.scheduler.tasks.*": {"queue": "scheduler"}}

# Define Prometheus metrics
TASK_LATENCY = pc.Histogram(
    "task_latency_seconds",
    "Task execution time in seconds",
    ["task_name"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0),
)
TASKS_TOTAL = pc.Counter(
    "tasks_total",
    "Total number of tasks processed",
    ["task_name", "status"],
)


def track_task_metrics(task_func: Callable) -> Callable:
    """
    Decorator to track task execution metrics using Prometheus.
    
    Args:
        task_func: The Celery task function to wrap with metrics tracking
        
    Returns:
        Wrapped function with metrics tracking
    """
    @functools.wraps(task_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        task_name = task_func.__name__
        start_time = time.time()
        
        try:
            result = task_func(*args, **kwargs)
            TASKS_TOTAL.labels(task_name=task_name, status="success").inc()
            return result
        except Exception as e:
            TASKS_TOTAL.labels(task_name=task_name, status="failure").inc()
            raise e
        finally:
            execution_time = time.time() - start_time
            TASK_LATENCY.labels(task_name=task_name).observe(execution_time)
    
    return wrapper


# Import tasks to ensure they're registered with the Celery app
import services.scheduler.tasks  # noqa: E402, F401