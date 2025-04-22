"""
Scheduler module for the Graph Ingest Service.

This module contains the scheduler for automated data ingestion tasks.
"""

import os
import time
import logging
import threading
from datetime import datetime

import schedule

from app.db import get_session
from app.ingestors import CrunchbaseIngestor, GitHubIngestor
from app.metrics import update_scheduler_timestamp, calculate_and_update_metrics

# Set up logging
logger = logging.getLogger(__name__)

def ingest_crunchbase_companies():
    """
    Scheduled task to ingest updated companies from Crunchbase.
    """
    logger.info("Starting scheduled Crunchbase ingestion")
    
    try:
        # Get database session
        db = get_session()
        
        # Get the last update timestamp
        try:
            result = db.execute("SELECT MAX(updated_at) FROM entities WHERE properties->>'data_source' = 'crunchbase'")
            last_updated = result.scalar()
        except Exception:
            last_updated = None
        
        # Initialize the ingestor
        api_key = os.environ.get("CRUNCHBASE_API_KEY")
        ingestor = CrunchbaseIngestor(db, api_key=api_key)
        
        # Get updated companies
        companies = ingestor.get_updated_companies(last_updated)
        logger.info(f"Found {len(companies)} companies to update from Crunchbase")
        
        # Ingest each company
        success_count = 0
        for permalink in companies:
            try:
                result = ingestor.ingest_company(permalink)
                if result.get("status") == "success":
                    success_count += 1
                    logger.info(f"Successfully ingested Crunchbase company: {permalink}")
                else:
                    logger.warning(f"Failed to ingest Crunchbase company: {permalink}")
            except Exception as e:
                logger.error(f"Error ingesting Crunchbase company {permalink}: {str(e)}")
        
        logger.info(f"Crunchbase ingestion complete: {success_count}/{len(companies)} successful")
        
        # Update metrics
        calculate_and_update_metrics(db)
        
        # Update scheduler timestamp
        update_scheduler_timestamp(time.time())
        
    except Exception as e:
        logger.error(f"Error in Crunchbase ingestion task: {str(e)}")


def ingest_github_repositories():
    """
    Scheduled task to ingest trending repositories from GitHub.
    """
    logger.info("Starting scheduled GitHub ingestion")
    
    try:
        # Get database session
        db = get_session()
        
        # Initialize the ingestor
        api_token = os.environ.get("GITHUB_API_TOKEN")
        ingestor = GitHubIngestor(db, api_token=api_token)
        
        # Get trending repositories for different languages
        languages = ["python", "javascript", "typescript", "go", "rust", "java"]
        repos = []
        
        for language in languages:
            language_repos = ingestor.get_trending_repositories(language=language)
            repos.extend(language_repos)
            logger.info(f"Found {len(language_repos)} trending {language} repositories")
        
        # Deduplicate
        unique_repos = {}
        for repo in repos:
            key = f"{repo['owner']}/{repo['repo']}"
            unique_repos[key] = repo
        
        repos = list(unique_repos.values())
        logger.info(f"Found {len(repos)} unique trending repositories")
        
        # Ingest each repository
        success_count = 0
        for repo_info in repos:
            try:
                owner = repo_info["owner"]
                repo_name = repo_info["repo"]
                
                result = ingestor.ingest_repository(owner, repo_name)
                if result.get("status") == "success":
                    success_count += 1
                    logger.info(f"Successfully ingested GitHub repository: {owner}/{repo_name}")
                else:
                    logger.warning(f"Failed to ingest GitHub repository: {owner}/{repo_name}")
            except Exception as e:
                logger.error(f"Error ingesting GitHub repository {repo_info['owner']}/{repo_info['repo']}: {str(e)}")
        
        logger.info(f"GitHub ingestion complete: {success_count}/{len(repos)} successful")
        
        # Update metrics
        calculate_and_update_metrics(db)
        
        # Update scheduler timestamp
        update_scheduler_timestamp(time.time())
        
    except Exception as e:
        logger.error(f"Error in GitHub ingestion task: {str(e)}")


def setup_scheduler():
    """
    Set up the scheduler with all ingestion tasks.
    """
    logger.info("Setting up Graph Ingest scheduler")
    
    # Schedule Crunchbase ingestion daily at 2 AM
    schedule.every().day.at("02:00").do(ingest_crunchbase_companies)
    logger.info("Scheduled Crunchbase ingestion daily at 02:00")
    
    # Schedule GitHub ingestion daily at 3 AM
    schedule.every().day.at("03:00").do(ingest_github_repositories)
    logger.info("Scheduled GitHub ingestion daily at 03:00")
    
    # Schedule metrics update every 6 hours
    schedule.every(6).hours.do(lambda: calculate_and_update_metrics(get_session()))
    logger.info("Scheduled metrics update every 6 hours")


def run_scheduler():
    """
    Run the scheduler in a loop.
    """
    logger.info("Starting Graph Ingest scheduler")
    
    # Set initial scheduler timestamp
    update_scheduler_timestamp(time.time())
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retrying after an error


def start_scheduler():
    """
    Start the scheduler in a background thread.
    """
    setup_scheduler()
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    logger.info(f"Scheduler started in thread {thread.name}")
    return thread