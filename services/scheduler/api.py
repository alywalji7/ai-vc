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
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import yaml
import json
from celery.result import AsyncResult
from celery_app import app as celery_app

# Path to the crontab.yml file
CRONTAB_PATH = os.environ.get('CRONTAB_PATH', 'services/scheduler/crontab.yml')

# Create FastAPI application
app = FastAPI(
    title="ETL Scheduler API",
    description="API for managing scheduled ETL tasks",
    version="0.1.0"
)

# Define data models
class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    cron: str
    task: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
    enabled: bool = True

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    next_run: Optional[str] = None
    last_run: Optional[str] = None
    last_status: Optional[str] = None

class TaskResult(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None

# API endpoints
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "ETL Scheduler",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    """
    Get all scheduled tasks.
    
    Returns:
        List of task configurations
    """
    try:
        with open(CRONTAB_PATH, 'r') as f:
            config = yaml.safe_load(f)
        
        tasks = []
        for task_config in config.get('tasks', []):
            tasks.append(Task(**task_config))
        
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading tasks: {str(e)}")

@app.get("/tasks/{task_name}", response_model=Task)
async def get_task(task_name: str):
    """
    Get a specific task by name.
    
    Args:
        task_name: Name of the task
        
    Returns:
        Task configuration
    """
    try:
        with open(CRONTAB_PATH, 'r') as f:
            config = yaml.safe_load(f)
        
        for task_config in config.get('tasks', []):
            if task_config['name'] == task_name:
                return Task(**task_config)
        
        raise HTTPException(status_code=404, detail=f"Task '{task_name}' not found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error getting task: {str(e)}")

@app.post("/tasks/{task_name}/run", response_model=TaskResult)
async def run_task(task_name: str, background_tasks: BackgroundTasks):
    """
    Trigger immediate execution of a task.
    
    Args:
        task_name: Name of the task
        
    Returns:
        Task execution result
    """
    try:
        with open(CRONTAB_PATH, 'r') as f:
            config = yaml.safe_load(f)
        
        for task_config in config.get('tasks', []):
            if task_config['name'] == task_name:
                # Get task path, args, and kwargs
                task_path = task_config['task']
                args = task_config.get('args', [])
                kwargs = task_config.get('kwargs', {})
                
                # Run the task asynchronously
                result = celery_app.send_task(
                    task_path,
                    args=args,
                    kwargs=kwargs,
                    task_id=f"{task_name}-immediate-{os.urandom(4).hex()}"
                )
                
                return TaskResult(
                    task_id=result.id,
                    status="PENDING",
                    result=None
                )
        
        raise HTTPException(status_code=404, detail=f"Task '{task_name}' not found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error running task: {str(e)}")

@app.get("/tasks/results/{task_id}", response_model=TaskResult)
async def get_task_result(task_id: str):
    """
    Get the result of a task execution.
    
    Args:
        task_id: ID of the task execution
        
    Returns:
        Task execution result
    """
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        # Check the task status
        if result.ready():
            if result.successful():
                # Convert to JSON-serializable format
                task_result = result.get()
                if isinstance(task_result, dict):
                    # Ensure result is JSON serializable
                    return TaskResult(
                        task_id=task_id,
                        status="SUCCESS",
                        result=task_result
                    )
                else:
                    # Convert to string if not serializable
                    return TaskResult(
                        task_id=task_id,
                        status="SUCCESS",
                        result=str(task_result)
                    )
            else:
                return TaskResult(
                    task_id=task_id,
                    status="FAILURE",
                    result=str(result.result)
                )
        else:
            return TaskResult(
                task_id=task_id,
                status=result.state,
                result=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task result: {str(e)}")

# Run the FastAPI application
def start_api():
    """
    Start the FastAPI application.
    
    This function is the entry point for the API server.
    """
    import uvicorn
    
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '8000'))
    
    uvicorn.run("api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start_api()