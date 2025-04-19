"""
Celery application configuration for the scheduler service.

This module creates and configures the Celery application for processing
data ingestion tasks.
"""

import os
import time
from functools import wraps
from celery import Celery
from prometheus_client import Counter, Histogram

# Set default Redis URL if not provided in environment
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery application
app = Celery('scheduler',
             broker=REDIS_URL,
             backend=REDIS_URL)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Define Prometheus metrics
TASK_LATENCY = Histogram(
    'task_latency_seconds',
    'Task execution time in seconds',
    ['task_name']
)

TASK_COUNT = Counter(
    'tasks_total',
    'Number of tasks processed',
    ['task_name', 'status']
)

def track_task_metrics(task_func):
    """
    Decorator to track task execution metrics using Prometheus.
    
    Args:
        task_func: The Celery task function to wrap with metrics tracking
        
    Returns:
        Wrapped function with metrics tracking
    """
    @wraps(task_func)
    def wrapper(*args, **kwargs):
        task_name = task_func.__name__
        start_time = time.time()
        
        try:
            # Execute the task
            result = task_func(*args, **kwargs)
            
            # Record success
            TASK_COUNT.labels(task_name=task_name, status='success').inc()
            
            return result
        except Exception as e:
            # Record failure
            TASK_COUNT.labels(task_name=task_name, status='failure').inc()
            
            # Re-raise the exception to let Celery handle it
            raise
        finally:
            # Record task latency
            latency = time.time() - start_time
            TASK_LATENCY.labels(task_name=task_name).observe(latency)
    
    return wrapper