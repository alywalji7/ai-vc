#!/usr/bin/env python3
"""
Seed Demo Script for Graph Ingest Service

This script demonstrates the data ingestion capabilities of the Graph Ingest Service
by populating the knowledge graph with data from Crunchbase and GitHub.

It will:
1. Create sample company data in S3
2. Ingest the companies from Crunchbase
3. Ingest top repositories from GitHub
4. Count the entities and relationships created
5. Print a summary of the ingestion results
"""
import os
import sys
import time
import json
import logging
import tempfile
import csv
import boto3
from pathlib import Path
import sqlalchemy
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add the current directory to sys.path
sys.path.append(str(Path(__file__).parent))

from app.db import init_db, get_session
from app.ingestors import GitHubIngestor, CrunchbaseIngestor
from app.utils import normalize_company_name, extract_domain_from_url, check_company_duplicate
from app.metrics import (
    increment_github_success, increment_crunchbase_success, 
    increment_ingest_failure, update_entity_count, update_relationship_count
)

# S3 client configuration
def get_s3_client():
    """Get an S3 client, using environment variables for configuration."""
    endpoint_url = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
    access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
    
    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1",
        config=boto3.session.Config(signature_version='s3v4'),
    )

def create_sample_companies_csv():
    """
    Create a sample CSV file with company data and upload it to S3.
    
    Returns:
        str: Path to the S3 file
    """
    logger.info("Creating sample companies CSV file")
    
    # Sample company data (50 companies)
    companies = [
        {"name": f"AI Startup {i}", "domain": f"aistartup{i}.com", "permalink": f"ai-startup-{i}"} 
        for i in range(1, 51)
    ]
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
        fieldnames = ['name', 'domain', 'permalink']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        
        writer.writeheader()
        for company in companies:
            writer.writerow(company)
    
    # Upload to S3
    s3_client = get_s3_client()
    bucket_name = os.getenv("S3_BUCKET_NAME", "aivc")
    file_key = "seed/companies.csv"
    
    try:
        # Create bucket if it doesn't exist
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except:
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"Created S3 bucket: {bucket_name}")
        
        # Upload file
        s3_client.upload_file(temp_file.name, bucket_name, file_key)
        logger.info(f"Uploaded sample companies to s3://{bucket_name}/{file_key}")
        
        # Clean up temp file
        os.remove(temp_file.name)
        
        return f"s3://{bucket_name}/{file_key}"
    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        logger.info("Using local file as fallback")
        return temp_file.name

def count_entities_and_relationships(db_session):
    """
    Count the number of entities and relationships in the database.
    
    Args:
        db_session: Database session
        
    Returns:
        dict: Dictionary with counts
    """
    try:
        # First, check if the tables exist
        result = db_session.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'entities')"
        ))
        entities_exists = result.scalar()
        
        result = db_session.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'relationships')"
        ))
        relationships_exists = result.scalar()
        
        if not entities_exists or not relationships_exists:
            logger.warning("Database tables don't exist yet. Returning zero counts.")
            return {"entity_count": 0, "relationship_count": 0}
        
        # Count entities
        entity_result = db_session.execute(text("SELECT COUNT(*) FROM entities"))
        entity_count = entity_result.scalar()
        
        # Count relationships
        rel_result = db_session.execute(text("SELECT COUNT(*) FROM relationships"))
        rel_count = rel_result.scalar()
        
        return {
            "entity_count": entity_count,
            "relationship_count": rel_count
        }
    except Exception as e:
        logger.error(f"Error counting entities and relationships: {str(e)}")
        return {"entity_count": 0, "relationship_count": 0}

def ingest_companies_from_crunchbase(s3_file_path=None):
    """
    Ingest companies from Crunchbase seed list.
    
    Args:
        s3_file_path: Path to the S3 file with company data
        
    Returns:
        dict: Dictionary with ingestion results
    """
    logger.info("Starting Crunchbase companies ingestion")
    
    # Get or create the S3 file
    if not s3_file_path:
        s3_file_path = create_sample_companies_csv()
    
    # Extract bucket and key from s3 path
    if s3_file_path.startswith('s3://'):
        bucket_name = s3_file_path.split('/')[2]
        file_key = '/'.join(s3_file_path.split('/')[3:])
    else:
        # Using local file
        with open(s3_file_path, 'r') as f:
            csv_reader = csv.DictReader(f)
            companies = list(csv_reader)
            
            # Get database session
            db = get_session()
            
            # Initialize the ingestor
            api_key = os.getenv("CRUNCHBASE_API_KEY")
            ingestor = CrunchbaseIngestor(db, api_key=api_key)
            
            # Ingest each company
            success_count = 0
            for company in companies[:50]:  # Limit to 50 companies
                try:
                    company_permalink = company.get('permalink') or company.get('name').lower().replace(" ", "-")
                    result = ingestor.ingest_company(company_permalink)
                    
                    if result.get('status') == 'success':
                        success_count += 1
                        increment_crunchbase_success()
                        logger.info(f"Successfully ingested company: {company_permalink}")
                    else:
                        increment_ingest_failure()
                        logger.warning(f"Failed to ingest company: {company_permalink}")
                except Exception as e:
                    increment_ingest_failure()
                    logger.error(f"Error ingesting company {company.get('name')}: {str(e)}")
            
            return {
                "status": "success",
                "source": "crunchbase",
                "companies_processed": len(companies[:50]),
                "companies_ingested": success_count
            }
    
    try:
        # Get the file from S3
        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(file_content.splitlines())
        companies = list(csv_reader)
        
        # Limit to 50 companies
        companies = companies[:50]
        
        # Get database session
        db = get_session()
        
        # Initialize the ingestor
        api_key = os.getenv("CRUNCHBASE_API_KEY")
        ingestor = CrunchbaseIngestor(db, api_key=api_key)
        
        # Ingest each company
        success_count = 0
        for company in companies:
            try:
                company_permalink = company.get('permalink') or company.get('name').lower().replace(" ", "-")
                result = ingestor.ingest_company(company_permalink)
                
                if result.get('status') == 'success':
                    success_count += 1
                    increment_crunchbase_success()
                    logger.info(f"Successfully ingested company: {company_permalink}")
                else:
                    increment_ingest_failure()
                    logger.warning(f"Failed to ingest company: {company_permalink}")
            except Exception as e:
                increment_ingest_failure()
                logger.error(f"Error ingesting company {company.get('name')}: {str(e)}")
        
        return {
            "status": "success",
            "source": "crunchbase",
            "companies_processed": len(companies),
            "companies_ingested": success_count
        }
    
    except Exception as e:
        logger.error(f"Error in Crunchbase ingestion: {str(e)}")
        increment_ingest_failure()
        return {
            "status": "error",
            "source": "crunchbase",
            "message": str(e)
        }

def ingest_top_github_repositories(count=500):
    """
    Ingest top GitHub repositories.
    
    Args:
        count: Number of repositories to ingest
        
    Returns:
        dict: Dictionary with ingestion results
    """
    logger.info(f"Starting GitHub top {count} repositories ingestion")
    
    # Get database session
    db = get_session()
    
    # Initialize the ingestor
    api_token = os.getenv("GITHUB_API_TOKEN")
    ingestor = GitHubIngestor(db, api_token=api_token)
    
    try:
        # For demo purposes, we'll use a fixed list of popular repos
        # In a real implementation, we would query the GitHub API
        popular_repos = [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react"},
            {"owner": "tensorflow", "repo": "tensorflow"},
            {"owner": "angular", "repo": "angular"},
            {"owner": "vuejs", "repo": "vue"},
        ]
        
        # Generate more repos to meet the count requirement (for demo purposes)
        base_orgs = ["github", "google", "microsoft", "facebook", "twitter", "amazon", "netflix", "uber", "airbnb"]
        base_repos = ["core", "api", "ui", "ml", "data", "infra", "tools", "docs", "platform", "app"]
        
        while len(popular_repos) < count:
            org_idx = len(popular_repos) % len(base_orgs)
            repo_idx = (len(popular_repos) // len(base_orgs)) % len(base_repos)
            
            popular_repos.append({
                "owner": base_orgs[org_idx],
                "repo": f"{base_repos[repo_idx]}-{len(popular_repos)}"
            })
        
        # Limit to the requested count
        popular_repos = popular_repos[:count]
        
        # Ingest each repository
        success_count = 0
        for repo_info in popular_repos:
            try:
                owner = repo_info["owner"]
                repo_name = repo_info["repo"]
                
                result = ingestor.ingest_repository(owner, repo_name)
                
                if result.get('status') == 'success':
                    success_count += 1
                    increment_github_success()
                    logger.info(f"Successfully ingested repository: {owner}/{repo_name}")
                else:
                    increment_ingest_failure()
                    logger.warning(f"Failed to ingest repository: {owner}/{repo_name}")
            except Exception as e:
                increment_ingest_failure()
                logger.error(f"Error ingesting repository {repo_info['owner']}/{repo_info['repo']}: {str(e)}")
        
        return {
            "status": "success",
            "source": "github",
            "repositories_processed": len(popular_repos),
            "repositories_ingested": success_count
        }
    
    except Exception as e:
        logger.error(f"Error in GitHub ingestion: {str(e)}")
        increment_ingest_failure()
        return {
            "status": "error",
            "source": "github",
            "message": str(e)
        }

def main():
    """Main entry point for the seed demo script."""
    logger.info("Starting Graph Ingest seed demo")
    
    # Initialize the database
    try:
        init_db()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return 1
    
    # Get initial counts
    db = get_session()
    initial_counts = count_entities_and_relationships(db)
    logger.info(f"Initial counts: {initial_counts}")
    
    # Ingest companies from Crunchbase
    logger.info("Step 1: Ingesting companies from Crunchbase")
    crunchbase_result = ingest_companies_from_crunchbase()
    logger.info(f"Crunchbase ingestion complete: {crunchbase_result}")
    
    # Ingest repositories from GitHub
    logger.info("Step 2: Ingesting repositories from GitHub")
    github_result = ingest_top_github_repositories(500)
    logger.info(f"GitHub ingestion complete: {github_result}")
    
    # Get final counts
    final_counts = count_entities_and_relationships(db)
    logger.info(f"Final counts: {final_counts}")
    
    # Calculate differences
    entity_diff = final_counts["entity_count"] - initial_counts["entity_count"]
    rel_diff = final_counts["relationship_count"] - initial_counts["relationship_count"]
    
    # Update metrics
    update_entity_count("total", final_counts["entity_count"])
    update_relationship_count("total", final_counts["relationship_count"])
    
    # Check if the ingestion was successful
    success = (
        crunchbase_result.get("status") == "success" and
        github_result.get("status") == "success" and
        entity_diff >= 550 and  # At least 550 nodes
        rel_diff <= 700         # No more than 700 edges
    )
    
    # Print summary
    print("\n" + "="*80)
    print("GRAPH INGEST SEED DEMO SUMMARY")
    print("="*80)
    print(f"Crunchbase Companies: {crunchbase_result.get('companies_ingested', 0)}/{crunchbase_result.get('companies_processed', 0)}")
    print(f"GitHub Repositories: {github_result.get('repositories_ingested', 0)}/{github_result.get('repositories_processed', 0)}")
    print(f"Entities created: {entity_diff}")
    print(f"Relationships created: {rel_diff}")
    print("-"*80)
    
    if success:
        print("✓ seed OK")
    else:
        print("✗ seed FAILED")
        if entity_diff < 550:
            print(f"  Not enough entities created: {entity_diff}/550")
        if rel_diff > 700:
            print(f"  Too many relationships created: {rel_diff}/700")
    
    print("="*80)
    
    # Return success status
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())