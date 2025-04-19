"""
Task definitions for scheduler service.

This module contains the Celery task functions that will be executed
according to the crontab schedule.
"""

import os
import httpx
import logging
from celery_app import app, track_task_metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API base URL for the Graph Ingest Service
GRAPH_INGEST_API_URL = os.environ.get('GRAPH_INGEST_API_URL', 'http://localhost:8080')

@app.task
@track_task_metrics
def ingest_github(org_or_user):
    """
    Task to ingest GitHub data for an organization or user.
    
    Args:
        org_or_user: GitHub organization or username to ingest
        
    Returns:
        Dictionary with ingestion results
    """
    logger.info(f"Starting GitHub ingestion for: {org_or_user}")
    
    try:
        # Determine if this is an organization or user based on some heuristic
        # This is a simplified example - in reality, you might need to check first
        is_org = not org_or_user.startswith('user_')
        
        # Prepare the request payload
        payload = {
            "source": "github",
            "org": org_or_user if is_org else None,
            "user": None if is_org else org_or_user,
        }
        
        # Make POST request to the Graph Ingest API
        with httpx.Client(timeout=300.0) as client:  # 5-minute timeout
            response = client.post(f"{GRAPH_INGEST_API_URL}/api/ingest", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"GitHub ingestion completed for {org_or_user}. " 
                      f"Entities: {result.get('entities_count', 0)}, " 
                      f"Relationships: {result.get('relationships_count', 0)}")
            
            return result
    except Exception as e:
        logger.error(f"Error ingesting GitHub data for {org_or_user}: {e}")
        raise


@app.task
@track_task_metrics
def ingest_crunchbase(company_or_person):
    """
    Task to ingest Crunchbase data for a company or person.
    
    Args:
        company_or_person: Crunchbase company or person permalink to ingest
        
    Returns:
        Dictionary with ingestion results
    """
    logger.info(f"Starting Crunchbase ingestion for: {company_or_person}")
    
    try:
        # Determine if this is a company or person based on some heuristic
        # This is a simplified example - in reality, you might need to check first
        is_company = not company_or_person.startswith('person_')
        
        # Prepare the request payload
        payload = {
            "source": "crunchbase",
            "company": company_or_person if is_company else None,
            "person": None if is_company else company_or_person,
        }
        
        # Make POST request to the Graph Ingest API
        with httpx.Client(timeout=300.0) as client:  # 5-minute timeout
            response = client.post(f"{GRAPH_INGEST_API_URL}/api/ingest", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Crunchbase ingestion completed for {company_or_person}. " 
                      f"Entities: {result.get('entities_count', 0)}, " 
                      f"Relationships: {result.get('relationships_count', 0)}")
            
            return result
    except Exception as e:
        logger.error(f"Error ingesting Crunchbase data for {company_or_person}: {e}")
        raise


@app.task
@track_task_metrics
def cleanup_old_data(days_to_keep):
    """
    Task to clean up data older than a certain number of days.
    
    Args:
        days_to_keep: Number of days of data to retain
        
    Returns:
        Dictionary with cleanup results
    """
    logger.info(f"Starting data cleanup. Keeping {days_to_keep} days of data.")
    
    try:
        # In a real implementation, you would make a request to an API endpoint
        # that handles the actual cleanup operation
        
        # This is a placeholder implementation
        cleanup_stats = {
            "entities_removed": 0,
            "relationships_removed": 0,
            "status": "success"
        }
        
        logger.info(f"Data cleanup completed. "
                  f"Entities removed: {cleanup_stats['entities_removed']}, "
                  f"Relationships removed: {cleanup_stats['relationships_removed']}")
        
        return cleanup_stats
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        raise