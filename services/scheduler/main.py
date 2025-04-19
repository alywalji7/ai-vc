"""
Main entry point for the scheduler service - simplified version.

This module provides a FastAPI server for:
1. Listing scheduled tasks from crontab.yml
2. Viewing task details
3. Triggering manual task execution
"""
import os
import yaml
import logging
import uvicorn
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Scheduler Service API",
    description="API for the Scheduler Service",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you'd restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to crontab file
CRONTAB_PATH = os.environ.get("CRONTAB_PATH", "crontab.yml")


class Task(BaseModel):
    """Model for a task configuration."""
    name: str
    description: Optional[str] = None
    cron: str
    task: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
    enabled: bool = True


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
    crontab_status = "ok" if os.path.exists(CRONTAB_PATH) else "missing"
    
    return {
        "status": "ok",
        "components": {
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
    if not os.path.exists(CRONTAB_PATH):
        return []
    
    try:
        with open(CRONTAB_PATH, "r") as f:
            crontab = yaml.safe_load(f)
        
        task_configs = crontab.get("tasks", {})
        tasks = []
        
        # Iterate through the dictionary items (key, value pairs)
        for task_id, task_config in task_configs.items():
            tasks.append(
                Task(
                    name=task_config.get("name", ""),
                    description=task_config.get("description", ""),
                    cron=task_config.get("cron", ""),
                    task=task_config.get("task", ""),
                    args=task_config.get("args", []),
                    kwargs=task_config.get("kwargs", {}),
                    enabled=task_config.get("enabled", True),
                )
            )
        
        return tasks
    except Exception as e:
        logger.error(f"Error loading crontab: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading crontab: {str(e)}")


@app.get("/tasks/{task_name}", response_model=Task, tags=["tasks"])
async def get_task(task_name: str):
    """
    Get a specific task by name.
    
    Args:
        task_name: Name of the task
        
    Returns:
        Task configuration
    """
    if not os.path.exists(CRONTAB_PATH):
        raise HTTPException(status_code=404, detail="Crontab file not found")
    
    try:
        with open(CRONTAB_PATH, "r") as f:
            crontab = yaml.safe_load(f)
        
        task_configs = crontab.get("tasks", {})
        
        # Search for the task by name
        for task_id, task_config in task_configs.items():
            if task_config.get("name") == task_name:
                return Task(
                    name=task_config.get("name", ""),
                    description=task_config.get("description", ""),
                    cron=task_config.get("cron", ""),
                    task=task_config.get("task", ""),
                    args=task_config.get("args", []),
                    kwargs=task_config.get("kwargs", {}),
                    enabled=task_config.get("enabled", True),
                )
        
        raise HTTPException(status_code=404, detail=f"Task '{task_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading crontab: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading crontab: {str(e)}")


@app.post("/tasks/{task_name}/run", tags=["tasks"])
async def run_task(task_name: str):
    """
    Simulate manual task execution (simplified version).
    
    Args:
        task_name: Name of the task
        
    Returns:
        Task execution result
    """
    if not os.path.exists(CRONTAB_PATH):
        raise HTTPException(status_code=404, detail="Crontab file not found")
    
    try:
        with open(CRONTAB_PATH, "r") as f:
            crontab = yaml.safe_load(f)
        
        task_configs = crontab.get("tasks", {})
        
        # Search for the task by name in dictionary items
        for task_id, task_config in task_configs.items():
            if task_config.get("name") == task_name:
                # Check if task is enabled
                if not task_config.get("enabled", True):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Task '{task_name}' is disabled",
                    )
                
                # In this simplified version, we just simulate task execution
                return {
                    "status": "success",
                    "message": f"Task '{task_name}' execution simulated",
                    "task": task_config,
                }
        
        raise HTTPException(status_code=404, detail=f"Task '{task_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running task: {str(e)}")


def main():
    """Start the FastAPI server."""
    logger.info("Starting scheduler service API")
    uvicorn.run(app, host="0.0.0.0", port=8085)


if __name__ == "__main__":
    main()