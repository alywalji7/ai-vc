"""
FastAPI server for the scheduler service.

This module provides a RESTful API for interacting with the scheduler service,
including endpoints to:
- Trigger immediate execution of tasks
- View scheduled tasks
- Check service health
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

import fastapi
import pydantic
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from celery.result import AsyncResult

from celery_app import app as celery_app
import tasks

# Create FastAPI app
app = FastAPI(
    title="Scheduler Service API",
    description="API for the Scheduler Service",
    version="0.1.0",
)


class TaskBase(BaseModel):
    """Base model for task configuration."""
    name: str
    description: Optional[str] = None
    cron: str
    task: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
    enabled: bool = True


class TaskCreate(TaskBase):
    """Model for creating a new task."""
    pass


class Task(TaskBase):
    """Model for a task with execution information."""
    next_run: Optional[str] = None
    last_run: Optional[str] = None
    last_status: Optional[str] = None


class TaskResult(BaseModel):
    """Model for a task execution result."""
    task_id: str
    status: str
    result: Optional[Any] = None


@app.get("/", tags=["general"])
async def root():
    """Root endpoint with service information."""
    return {
        "name": "Scheduler Service",
        "version": "0.1.0",
        "description": "Service for scheduling and executing periodic tasks",
    }


@app.get("/health", tags=["general"])
async def health_check():
    """Health check endpoint."""
    # Check if we can communicate with Celery
    try:
        celery_app.control.ping()
        celery_status = "ok"
    except Exception:
        celery_status = "error"
    
    # Load crontab file
    crontab_path = os.environ.get("CRONTAB_PATH", "crontab.yml")
    crontab_status = "ok" if os.path.exists(crontab_path) else "missing"
    
    return {
        "status": "ok" if celery_status == "ok" and crontab_status == "ok" else "error",
        "components": {
            "celery": celery_status,
            "crontab": crontab_status,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/tasks", response_model=List[Task], tags=["tasks"])
async def get_tasks():
    """
    Get all scheduled tasks.
    
    Returns:
        List of task configurations
    """
    # Load crontab file
    crontab_path = os.environ.get("CRONTAB_PATH", "crontab.yml")
    
    if not os.path.exists(crontab_path):
        return []
    
    # This is a simplification - in a real system, tasks would be stored in a database
    # and their status would be tracked persistently
    import yaml
    with open(crontab_path, "r") as f:
        crontab = yaml.safe_load(f)
    
    task_configs = crontab.get("tasks", [])
    
    # Add execution information
    tasks_with_info = []
    for task_config in task_configs:
        # Get task information from Redis (simplified)
        tasks_with_info.append(
            Task(
                name=task_config.get("name", ""),
                description=task_config.get("description", ""),
                cron=task_config.get("cron", ""),
                task=task_config.get("task", ""),
                args=task_config.get("args", []),
                kwargs=task_config.get("kwargs", {}),
                enabled=task_config.get("enabled", True),
                next_run="Not implemented",  # Would require croniter to calculate
                last_run="Unknown",  # Would be stored in Redis/database
                last_status="Unknown",  # Would be stored in Redis/database
            )
        )
    
    return tasks_with_info


@app.get("/tasks/{task_name}", response_model=Task, tags=["tasks"])
async def get_task(task_name: str):
    """
    Get a specific task by name.
    
    Args:
        task_name: Name of the task
        
    Returns:
        Task configuration
    """
    # Load crontab file
    crontab_path = os.environ.get("CRONTAB_PATH", "crontab.yml")
    
    if not os.path.exists(crontab_path):
        raise fastapi.HTTPException(status_code=404, detail="Crontab file not found")
    
    # This is a simplification - in a real system, tasks would be stored in a database
    import yaml
    with open(crontab_path, "r") as f:
        crontab = yaml.safe_load(f)
    
    task_configs = crontab.get("tasks", [])
    
    # Find task by name
    for task_config in task_configs:
        if task_config.get("name") == task_name:
            return Task(
                name=task_config.get("name", ""),
                description=task_config.get("description", ""),
                cron=task_config.get("cron", ""),
                task=task_config.get("task", ""),
                args=task_config.get("args", []),
                kwargs=task_config.get("kwargs", {}),
                enabled=task_config.get("enabled", True),
                next_run="Not implemented",  # Would require croniter to calculate
                last_run="Unknown",  # Would be stored in Redis/database
                last_status="Unknown",  # Would be stored in Redis/database
            )
    
    raise fastapi.HTTPException(status_code=404, detail=f"Task '{task_name}' not found")


@app.post("/tasks/{task_name}/run", response_model=TaskResult, tags=["tasks"])
async def run_task(task_name: str, background_tasks: BackgroundTasks):
    """
    Trigger immediate execution of a task.
    
    Args:
        task_name: Name of the task
        
    Returns:
        Task execution result
    """
    # Load crontab file
    crontab_path = os.environ.get("CRONTAB_PATH", "crontab.yml")
    
    if not os.path.exists(crontab_path):
        raise fastapi.HTTPException(status_code=404, detail="Crontab file not found")
    
    # This is a simplification - in a real system, tasks would be stored in a database
    import yaml
    with open(crontab_path, "r") as f:
        crontab = yaml.safe_load(f)
    
    task_configs = crontab.get("tasks", [])
    
    # Find task by name
    for task_config in task_configs:
        if task_config.get("name") == task_name:
            # Execute task
            task_path = task_config.get("task")
            args = task_config.get("args", [])
            kwargs = task_config.get("kwargs", {})
            
            # Check if task is enabled
            if not task_config.get("enabled", True):
                raise fastapi.HTTPException(
                    status_code=400,
                    detail=f"Task '{task_name}' is disabled",
                )
            
            # Apply Celery task
            task = celery_app.signature(task_path, args=args, kwargs=kwargs)
            result = task.apply_async()
            
            return TaskResult(
                task_id=result.id,
                status="pending",
                result=None,
            )
    
    raise fastapi.HTTPException(status_code=404, detail=f"Task '{task_name}' not found")


@app.get("/tasks/results/{task_id}", response_model=TaskResult, tags=["tasks"])
async def get_task_result(task_id: str):
    """
    Get the result of a task execution.
    
    Args:
        task_id: ID of the task execution
        
    Returns:
        Task execution result
    """
    # Get AsyncResult from Celery
    result = AsyncResult(task_id, app=celery_app)
    
    # Check task status
    if result.status == "PENDING":
        return TaskResult(
            task_id=task_id,
            status="pending",
            result=None,
        )
    elif result.status == "SUCCESS":
        return TaskResult(
            task_id=task_id,
            status="success",
            result=result.get(),
        )
    elif result.status == "FAILURE":
        return TaskResult(
            task_id=task_id,
            status="failure",
            result=str(result.result),
        )
    else:
        return TaskResult(
            task_id=task_id,
            status=result.status.lower(),
            result=None,
        )


def start_api():
    """
    Start the FastAPI application.
    
    This function is the entry point for the API server.
    """
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_api()