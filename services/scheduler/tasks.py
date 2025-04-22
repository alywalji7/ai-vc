"""
Task definitions for scheduler service.

This module contains the Celery task functions that will be executed
according to the crontab schedule.
"""
import os
import time
import json
import sys
import logging
from typing import Dict, Any, List
from datetime import datetime

import httpx

from celery_app import app, track_task_metrics

# Set up logger
logger = logging.getLogger(__name__)

# Environment variables
GRAPH_INGEST_API_URL = os.environ.get("GRAPH_INGEST_API_URL", "http://localhost:8080")
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000")
COMPLIANCE_API_URL = os.environ.get("COMPLIANCE_API_URL", "http://localhost:8050")


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


@app.task(bind=True, name="services.scheduler.tasks.build_dataroom")
@track_task_metrics
def build_dataroom(self, company_id: str, score: float = 0.0) -> Dict[str, Any]:
    """
    Task to build a data room for a green-lit company.
    
    This task:
    1. Scrapes the company's website for PDF decks
    2. Compiles KPIs into a markdown summary
    3. Generates JSON data and provides a download link
    
    Args:
        company_id: ID of the company
        score: Radar score (0-1)
        
    Returns:
        Dictionary with data room build results
    """
    self.logger.info(f"Building data room for company {company_id} with score {score:.2f}")
    
    try:
        # Import necessary modules
        import os
        import trafilatura
        from urllib.parse import urlparse
        from bs4 import BeautifulSoup
        
        # Create data room directory for this company
        data_room_dir = f"data/datarooms/{company_id}"
        os.makedirs(data_room_dir, exist_ok=True)
        
        # 1. Get company details from database
        # For demo purposes, use mock data based on company_id
        if company_id.startswith("c"):
            company_num = int(company_id[1:])
            company_details = {
                "id": company_id,
                "name": f"Company {company_num}",
                "website": f"https://company{company_num}.example.com",
                "founding_date": "2018-01-15",
                "github_stars": 2450 + company_num * 100,
                "commit_velocity": 8.7 + company_num * 0.5,
                "investor_count": 3 + company_num % 5,
                "founder_exit_count": company_num % 3,
                "social_traction": 567 + company_num * 50,
                "funding_amount": 1500000 + company_num * 200000,
                "radar_score": score
            }
        else:
            # Fallback for non-standard IDs
            company_details = {
                "id": company_id,
                "name": f"Company {company_id}",
                "website": "https://example.com",
                "founding_date": "2020-01-01",
                "github_stars": 1000,
                "commit_velocity": 5.0,
                "investor_count": 2,
                "founder_exit_count": 0,
                "social_traction": 500,
                "funding_amount": 1000000,
                "radar_score": score
            }
            
        # 2. Scrape company website (simulated)
        website_content = f"Mock website content for {company_details['name']}"
        
        # 3. Save JSON data
        with open(f"{data_room_dir}/company_data.json", "w") as f:
            json.dump(company_details, f, indent=2)
            
        # 4. Generate PDF links (simulated)
        pdf_links = [
            f"https://example.com/{company_id}_deck.pdf",
            f"https://example.com/{company_id}_financials.pdf"
        ]
        
        # 5. Create markdown summary
        summary_md = f"""# {company_details['name']} Data Room
        
## Company Overview
- **ID**: {company_details['id']}
- **Website**: [{company_details['website']}]({company_details['website']})
- **Founded**: {company_details['founding_date']}
- **Radar Score**: {score:.2f}

## Key Performance Indicators
| Metric | Value |
|--------|-------|
| GitHub Stars | {company_details['github_stars']} |
| Commit Velocity | {company_details['commit_velocity']:.1f} |
| Investor Count | {company_details['investor_count']} |
| Founder Exit Count | {company_details['founder_exit_count']} |
| Social Traction | {company_details['social_traction']} |
| Funding Amount | ${company_details['funding_amount']:,} |

## Documents
- [Company Deck]({pdf_links[0]})
- [Financial Summary]({pdf_links[1]})

## API Access
Raw JSON data is available at `/api/dataroom/{company_id}/data`

*Data room generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 6. Save markdown summary
        with open(f"{data_room_dir}/summary.md", "w") as f:
            f.write(summary_md)
            
        # 7. Update database to mark data room as available
        # In a real implementation, we would update a database record
        
        return {
            "task": "build_dataroom",
            "status": "success",
            "company_id": company_id,
            "data_room_path": data_room_dir,
            "files_created": ["summary.md", "company_data.json"]
        }
    
    except Exception as e:
        self.logger.error(f"Error building data room for company {company_id}: {str(e)}")
        return {
            "task": "build_dataroom",
            "status": "error",
            "company_id": company_id,
            "error": str(e)
        }


@app.task(bind=True, name="services.scheduler.tasks.update_ofac_sanctions")
@track_task_metrics
def update_ofac_sanctions(self) -> Dict[str, Any]:
    """
    Task to update the OFAC sanctions list.
    
    This task:
    1. Fetches the latest SDN list from treasury.gov
    2. Processes the data and updates the cache
    3. Records the update timestamp
    
    Returns:
        Dictionary with update results
    """
    self.logger.info("Scheduled update of OFAC sanctions list started")
    
    try:
        # Try to import the necessary module
        try:
            from libs.compliance import sanctions
        except ImportError:
            # If the direct import fails, try to add the root directory to the path
            import sys
            from pathlib import Path
            root_dir = Path(__file__).parent.parent.parent.parent  # Go up four levels to the root
            sys.path.append(str(root_dir))
            from libs.compliance import sanctions
        
        # Trigger the sanctions cache update
        sanctions._update_sanctions_cache()
        
        # Get the updated sanctions list info
        sanctions_info = sanctions.get_latest_sanctions_list()
        
        return {
            "task": "update_ofac_sanctions",
            "status": "success",
            "updated_at": datetime.now().isoformat(),
            "sanctions_lists": sanctions_info
        }
    
    except Exception as e:
        self.logger.error(f"Error updating OFAC sanctions list: {str(e)}")
        
        # Retry with exponential backoff if it's a temporary issue
        self.retry(exc=e, countdown=60 * 30, max_retries=3)  # Retry after 30 minutes
        
        return {
            "task": "update_ofac_sanctions",
            "status": "error",
            "error": str(e)
        }