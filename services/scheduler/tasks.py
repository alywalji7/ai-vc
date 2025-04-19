"""
Task definitions for scheduler service.

This module contains the Celery task functions that will be executed
according to the crontab schedule.
"""
import os
from typing import Dict, Any

import httpx

from services.scheduler.celery_app import app, track_task_metrics

# Environment variables
GRAPH_INGEST_API_URL = os.environ.get("GRAPH_INGEST_API_URL", "http://localhost:8080")


@app.task(bind=True, name="services.scheduler.tasks.ingest_github")
@track_task_metrics
def ingest_github(self, org_or_user: str) -> Dict[str, Any]:
    """
    Task to ingest GitHub data for an organization or user.
    
    Args:
        org_or_user: GitHub organization or username to ingest
        
    Returns:
        Dictionary with ingestion results
    """
    # Determine if this is an organization or a user
    if "/" in org_or_user:
        # This is a repository
        org, repo = org_or_user.split("/", 1)
        url = f"{GRAPH_INGEST_API_URL}/api/ingest/github?org={org}&repo={repo}"
    elif org_or_user.startswith("@"):
        # This is a user
        user = org_or_user[1:]  # Remove the @ prefix
        url = f"{GRAPH_INGEST_API_URL}/api/ingest/github?user={user}"
    else:
        # This is an organization
        url = f"{GRAPH_INGEST_API_URL}/api/ingest/github?org={org_or_user}"
    
    try:
        response = httpx.post(url)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        self.retry(exc=e, countdown=60, max_retries=3)
        return {"status": "error", "message": f"Request error: {str(e)}"}
    except httpx.HTTPStatusError as e:
        if e.response.status_code >= 500:
            self.retry(exc=e, countdown=60, max_retries=3)
            return {"status": "error", "message": f"Server error: {str(e)}"}
        else:
            # Client error, don't retry
            return {"status": "error", "message": f"Client error: {str(e)}"}


@app.task(bind=True, name="services.scheduler.tasks.ingest_crunchbase")
@track_task_metrics
def ingest_crunchbase(self, company_or_person: str) -> Dict[str, Any]:
    """
    Task to ingest Crunchbase data for a company or person.
    
    Args:
        company_or_person: Crunchbase company or person permalink to ingest
        
    Returns:
        Dictionary with ingestion results
    """
    # Determine if this is a company or a person
    if company_or_person.startswith("@"):
        # This is a person
        person = company_or_person[1:]  # Remove the @ prefix
        url = f"{GRAPH_INGEST_API_URL}/api/ingest/crunchbase?person={person}"
    else:
        # This is a company
        url = f"{GRAPH_INGEST_API_URL}/api/ingest/crunchbase?company={company_or_person}"
    
    try:
        response = httpx.post(url)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        self.retry(exc=e, countdown=60, max_retries=3)
        return {"status": "error", "message": f"Request error: {str(e)}"}
    except httpx.HTTPStatusError as e:
        if e.response.status_code >= 500:
            self.retry(exc=e, countdown=60, max_retries=3)
            return {"status": "error", "message": f"Server error: {str(e)}"}
        else:
            # Client error, don't retry
            return {"status": "error", "message": f"Client error: {str(e)}"}


@app.task(bind=True, name="services.scheduler.tasks.cleanup_old_data")
@track_task_metrics
def cleanup_old_data(self, days_to_keep: int) -> Dict[str, Any]:
    """
    Task to clean up data older than a certain number of days.
    
    Args:
        days_to_keep: Number of days of data to retain
        
    Returns:
        Dictionary with cleanup results
    """
    url = f"{GRAPH_INGEST_API_URL}/api/maintenance/cleanup?days_to_keep={days_to_keep}"
    
    try:
        response = httpx.post(url)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        self.retry(exc=e, countdown=60, max_retries=3)
        return {"status": "error", "message": f"Request error: {str(e)}"}
    except httpx.HTTPStatusError as e:
        if e.response.status_code >= 500:
            self.retry(exc=e, countdown=60, max_retries=3)
            return {"status": "error", "message": f"Server error: {str(e)}"}
        else:
            # Client error, don't retry
            return {"status": "error", "message": f"Client error: {str(e)}"}