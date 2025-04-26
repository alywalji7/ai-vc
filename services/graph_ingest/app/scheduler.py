"""
Scheduler module for the Graph Ingest Service.

This module contains job scheduling functionality for the Graph Ingest Service.
"""

import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import schedule

from app.db import get_session
from app.ingestors import CrunchbaseIngestor, GitHubIngestor, AngelListConnector, YCLaunchConnector
from app.metrics import calculate_and_update_metrics, IngestTimer

# Set up logging
logger = logging.getLogger(__name__)

def ingest_crunchbase_updates():
    """
    Ingest updated companies from Crunchbase.
    
    This function retrieves a list of companies updated in the last 24 hours
    and ingests their data into the knowledge graph.
    """
    logger.info("Starting Crunchbase ingestion job")
    
    try:
        # Get database session
        db_session = get_session()
        
        # Create ingestor
        ingestor = CrunchbaseIngestor(db_session)
        
        # Get updated companies from the last 24 hours
        since_date = datetime.now() - timedelta(days=1)
        logger.info(f"Getting companies updated since {since_date.isoformat()}")
        
        with IngestTimer('crunchbase'):
            # Get updated companies
            permalinks = ingestor.get_updated_companies(since_date=since_date)
            
            logger.info(f"Found {len(permalinks)} companies to update")
            
            # Ingest each company
            for permalink in permalinks:
                try:
                    logger.info(f"Ingesting company: {permalink}")
                    result = ingestor.ingest_company(permalink)
                    
                    if result.get("status") == "success":
                        logger.info(f"Successfully ingested company: {result.get('name')} ({result.get('company_id')})")
                    else:
                        logger.error(f"Failed to ingest company {permalink}: {result.get('message')}")
                        
                except Exception as e:
                    logger.error(f"Error ingesting company {permalink}: {str(e)}")
        
        # Update metrics
        calculate_and_update_metrics(db_session)
        
        # Close session
        db_session.close()
        
        logger.info("Completed Crunchbase ingestion job")
        
    except Exception as e:
        logger.error(f"Error in Crunchbase ingestion job: {str(e)}")

def ingest_github_trending():
    """
    Ingest trending repositories from GitHub.
    
    This function retrieves trending repositories from GitHub and ingests their
    data into the knowledge graph.
    """
    logger.info("Starting GitHub trending ingestion job")
    
    try:
        # Get database session
        db_session = get_session()
        
        # Create ingestor
        ingestor = GitHubIngestor(db_session)
        
        with IngestTimer('github'):
            # Get trending repositories
            repos = ingestor.get_trending_repositories(time_period="weekly")
            
            logger.info(f"Found {len(repos)} trending repositories")
            
            # Ingest each repository
            for repo in repos:
                try:
                    owner = repo.get("owner")
                    repo_name = repo.get("repo")
                    
                    if owner and repo_name:
                        logger.info(f"Ingesting repository: {owner}/{repo_name}")
                        result = ingestor.ingest_repository(owner, repo_name)
                        
                        if result.get("status") == "success":
                            logger.info(f"Successfully ingested repository: {result.get('name')} ({result.get('repo_id')})")
                        else:
                            logger.error(f"Failed to ingest repository {owner}/{repo_name}: {result.get('message')}")
                            
                except Exception as e:
                    logger.error(f"Error ingesting repository {repo}: {str(e)}")
        
        # Update metrics
        calculate_and_update_metrics(db_session)
        
        # Close session
        db_session.close()
        
        logger.info("Completed GitHub trending ingestion job")
        
    except Exception as e:
        logger.error(f"Error in GitHub trending ingestion job: {str(e)}")

def run_scheduler():
    """Run the scheduler loop."""
    logger.info("Starting scheduler loop")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            time.sleep(5)  # Sleep longer on error

def ingest_angellist_deals():
    """
    Ingest new deals from AngelList.
    
    This function retrieves new deals from AngelList and ingests their
    data into the knowledge graph.
    """
    logger.info("Starting AngelList deal ingestion job")
    
    try:
        # Get database session
        db_session = get_session()
        
        # Create ingestor
        ingestor = AngelListConnector(db_session)
        
        with IngestTimer('angellist'):
            # Run the ingestion process
            result = ingestor.ingest()
            
            logger.info(f"AngelList ingestion completed: {result.get('entities_created', 0)} entities created, "
                        f"{result.get('relationships_created', 0)} relationships created")
                        
        # Update metrics
        calculate_and_update_metrics(db_session)
        
        # Close session
        db_session.close()
        
        logger.info("Completed AngelList ingestion job")
        
    except Exception as e:
        logger.error(f"Error in AngelList ingestion job: {str(e)}")

def ingest_yc_launches():
    """
    Ingest YC company launches.
    
    This function retrieves YC company launches from the YC RSS feed and creates
    entities and relationships in the knowledge graph.
    """
    logger.info("Starting YC Launch ingestion job")
    
    try:
        # Get database session
        db_session = get_session()
        
        # Create ingestor
        ingestor = YCLaunchConnector(db_session)
        
        with IngestTimer('yc_launch'):
            # Run the ingestion process, looking back 30 days by default
            result = ingestor.ingest()
            
            logger.info(f"YC Launch ingestion completed: {result.get('entities_created', 0)} entities created, "
                        f"{result.get('relationships_created', 0)} relationships created")
                        
        # Update metrics
        calculate_and_update_metrics(db_session)
        
        # Close session
        db_session.close()
        
        logger.info("Completed YC Launch ingestion job")
        
    except Exception as e:
        logger.error(f"Error in YC Launch ingestion job: {str(e)}")

def start_scheduler() -> threading.Thread:
    """
    Start the scheduler in a background thread.
    
    Returns:
        Thread object for the scheduler
    """
    logger.info("Setting up scheduled jobs")
    
    # Schedule Crunchbase ingestion to run daily at 1 AM
    schedule.every().day.at("01:00").do(ingest_crunchbase_updates)
    logger.info("Scheduled Crunchbase ingestion to run daily at 01:00")
    
    # Schedule GitHub trending ingestion to run daily at 2 AM
    schedule.every().day.at("02:00").do(ingest_github_trending)
    logger.info("Scheduled GitHub trending ingestion to run daily at 02:00")
    
    # Schedule AngelList deals ingestion to run daily at 3 AM
    schedule.every().day.at("03:00").do(ingest_angellist_deals)
    logger.info("Scheduled AngelList deals ingestion to run daily at 03:00")
    
    # Schedule YC Launch ingestion to run daily at 4 AM
    schedule.every().day.at("04:00").do(ingest_yc_launches)
    logger.info("Scheduled YC Launch ingestion to run daily at 04:00")
    
    # Also run metrics update every hour
    def update_metrics_job():
        try:
            db_session = get_session()
            calculate_and_update_metrics(db_session)
            db_session.close()
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
    
    schedule.every().hour.do(update_metrics_job)
    logger.info("Scheduled metrics update to run hourly")
    
    # Run initial metrics update
    update_metrics_job()
    
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    logger.info(f"Scheduler started in thread {scheduler_thread.name}")
    
    return scheduler_thread