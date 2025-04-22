"""
Ingestors module for the Graph Ingest Service.

This module contains ingestors for various data sources.
"""

import os
import time
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.db import create_entity, create_relationship, store_raw_data
from app.utils import normalize_company_name, check_company_duplicate, normalize_url

# Set up logging
logger = logging.getLogger(__name__)

# Constants
CRUNCHBASE_API_KEY = os.environ.get("CRUNCHBASE_API_KEY", "")
GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY", "")

class BaseIngestor:
    """Base class for all ingestors."""
    
    def __init__(self, db_session: Session):
        """
        Initialize the ingestor.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
        
    def validate_api_key(self) -> bool:
        """
        Validate that the API key is available.
        
        Returns:
            True if API key is available, False otherwise
        """
        raise NotImplementedError("Subclasses must implement validate_api_key")
    
    def store_raw_data(self, source: str, source_id: str, data: Dict[str, Any] = None, content: str = None) -> Any:
        """
        Store raw data from a source.
        
        Args:
            source: Source of data
            source_id: ID in the source system
            data: JSON data
            content: Text content
            
        Returns:
            Created raw data entry
        """
        return store_raw_data(self.db_session, source, source_id, data, content)

class CrunchbaseIngestor(BaseIngestor):
    """Ingestor for Crunchbase data."""
    
    BASE_URL = "https://api.crunchbase.com/api/v4"
    
    def __init__(self, db_session: Session):
        """
        Initialize the Crunchbase ingestor.
        
        Args:
            db_session: Database session
        """
        super().__init__(db_session)
        self.api_key = CRUNCHBASE_API_KEY
    
    def validate_api_key(self) -> bool:
        """
        Validate that the Crunchbase API key is available.
        
        Returns:
            True if API key is available, False otherwise
        """
        if not self.api_key:
            logger.error("Crunchbase API key not found. Set CRUNCHBASE_API_KEY environment variable.")
            return False
        return True
    
    def get_company(self, permalink: str) -> Optional[Dict[str, Any]]:
        """
        Get company data from Crunchbase.
        
        Args:
            permalink: Crunchbase permalink of the company
            
        Returns:
            Company data if successful, None otherwise
        """
        if not self.validate_api_key():
            return None
        
        url = f"{self.BASE_URL}/entities/organizations/{permalink}"
        params = {
            "user_key": self.api_key,
            "card_ids": "fields,founders,investors,team,acquirer,ipo"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("data", {})
            
        except requests.RequestException as e:
            logger.error(f"Error fetching company {permalink} from Crunchbase: {e}")
            return None
    
    def get_updated_companies(self, since_date: datetime = None) -> List[str]:
        """
        Get list of companies updated since a specified date.
        
        Args:
            since_date: Date to check for updates since
            
        Returns:
            List of company permalinks that have been updated since the specified date
        """
        if not self.validate_api_key():
            return []
        
        if since_date is None:
            since_date = datetime.now() - timedelta(days=1)
        
        date_str = since_date.strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/searches/organizations"
        params = {
            "user_key": self.api_key,
            "updated_since": date_str,
            "limit": 100  # Maximum supported by the API
        }
        
        try:
            response = requests.post(url, json=params)
            response.raise_for_status()
            data = response.json()
            
            entities = data.get("entities", [])
            permalinks = [entity.get("properties", {}).get("permalink") for entity in entities]
            return [p for p in permalinks if p]  # Filter out None values
            
        except requests.RequestException as e:
            logger.error(f"Error fetching updated companies from Crunchbase: {e}")
            return []
    
    def ingest_company(self, permalink: str) -> Dict[str, Any]:
        """
        Ingest a company from Crunchbase into the knowledge graph.
        
        Args:
            permalink: Crunchbase permalink of the company
            
        Returns:
            Dictionary with status and entity ID if successful
        """
        try:
            company_data = self.get_company(permalink)
            
            if not company_data:
                return {
                    "status": "error",
                    "message": f"Failed to fetch company data for {permalink}"
                }
            
            # Store raw data
            self.store_raw_data("crunchbase", permalink, company_data)
            
            # Extract company properties
            properties = company_data.get("properties", {})
            name = properties.get("name", "")
            
            if not name:
                return {
                    "status": "error",
                    "message": f"Invalid company data for {permalink}: name missing"
                }
            
            # Check for duplicates
            duplicate = check_company_duplicate(self.db_session, name)
            if duplicate:
                return {
                    "status": "success",
                    "message": f"Company already exists: {name}",
                    "company_id": duplicate["id"],
                    "name": name,
                    "duplicate": True,
                    "duplicate_score": duplicate["score"]
                }
            
            # Create company entity
            company_props = {
                "permalink": permalink,
                "website": properties.get("website", {}).get("value", ""),
                "short_description": properties.get("short_description", ""),
                "founded_on": properties.get("founded_on", {}).get("value", ""),
                "num_employees_min": properties.get("num_employees_min", 0),
                "num_employees_max": properties.get("num_employees_max", 0),
                "total_funding_usd": properties.get("total_funding_usd", 0),
                "headquarters": properties.get("headquarters", []),
                "categories": [c.get("value") for c in properties.get("categories", [])],
                "source": "crunchbase"
            }
            
            company_entity = create_entity(self.db_session, "company", name, company_props)
            
            # Extract and create related entities and relationships
            # Founders
            founders = company_data.get("cards", {}).get("founders", {}).get("entities", [])
            for founder in founders:
                founder_props = founder.get("properties", {})
                founder_name = founder_props.get("name", "")
                
                if founder_name:
                    founder_entity = create_entity(
                        self.db_session, 
                        "person", 
                        founder_name, 
                        {
                            "permalink": founder_props.get("permalink", ""),
                            "source": "crunchbase"
                        }
                    )
                    
                    create_relationship(
                        self.db_session,
                        founder_entity.id,
                        company_entity.id,
                        "founded",
                        {}
                    )
            
            # Investors
            investors = company_data.get("cards", {}).get("investors", {}).get("entities", [])
            for investor in investors:
                investor_props = investor.get("properties", {})
                investor_name = investor_props.get("name", "")
                investor_type = investor_props.get("type", "")
                
                if investor_name:
                    entity_type = "investor"
                    if investor_type == "company":
                        entity_type = "company"
                    elif investor_type == "person":
                        entity_type = "person"
                    
                    investor_entity = create_entity(
                        self.db_session, 
                        entity_type, 
                        investor_name, 
                        {
                            "permalink": investor_props.get("permalink", ""),
                            "investor_type": investor_type,
                            "source": "crunchbase"
                        }
                    )
                    
                    create_relationship(
                        self.db_session,
                        investor_entity.id,
                        company_entity.id,
                        "invested_in",
                        {}
                    )
            
            return {
                "status": "success",
                "company_id": company_entity.id,
                "name": name
            }
            
        except Exception as e:
            logger.error(f"Error ingesting company {permalink}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

class GitHubIngestor(BaseIngestor):
    """Ingestor for GitHub data."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, db_session: Session):
        """
        Initialize the GitHub ingestor.
        
        Args:
            db_session: Database session
        """
        super().__init__(db_session)
        self.api_key = GITHUB_API_KEY
    
    def validate_api_key(self) -> bool:
        """
        Validate that the GitHub API key is available.
        
        Returns:
            True if API key is available, False otherwise
        """
        if not self.api_key:
            logger.warning("GitHub API key not found. Set GITHUB_API_KEY environment variable. Using anonymous access with rate limits.")
            return True  # Can still work without API key, just with lower rate limits
        return True
    
    def get_repository(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Get repository data from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository data if successful, None otherwise
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        headers = {}
        
        if self.api_key:
            headers["Authorization"] = f"token {self.api_key}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching repository {owner}/{repo} from GitHub: {e}")
            return None
    
    def get_contributors(self, owner: str, repo: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get repository contributors from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name
            limit: Maximum number of contributors to return
            
        Returns:
            List of contributors if successful, empty list otherwise
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contributors"
        headers = {}
        params = {"per_page": limit}
        
        if self.api_key:
            headers["Authorization"] = f"token {self.api_key}"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching contributors for {owner}/{repo} from GitHub: {e}")
            return []
    
    def get_trending_repositories(self, time_period: str = "daily") -> List[Dict[str, Any]]:
        """
        Get trending repositories from GitHub.
        
        Args:
            time_period: Time period for trending repos (daily, weekly, monthly)
            
        Returns:
            List of trending repositories
        """
        # GitHub API doesn't have a trending API, so we'll use the trending page
        # or a third-party API that tracks trending repos
        
        # For now, return a list of popular repositories as a placeholder
        popular_repos = [
            {"owner": "facebook", "repo": "react"},
            {"owner": "tensorflow", "repo": "tensorflow"},
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "flutter", "repo": "flutter"},
            {"owner": "kubernetes", "repo": "kubernetes"}
        ]
        
        return popular_repos
    
    def ingest_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Ingest a repository from GitHub into the knowledge graph.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary with status and entity ID if successful
        """
        try:
            repo_data = self.get_repository(owner, repo)
            
            if not repo_data:
                return {
                    "status": "error",
                    "message": f"Failed to fetch repository data for {owner}/{repo}"
                }
            
            # Store raw data
            self.store_raw_data("github", f"{owner}/{repo}", repo_data)
            
            # Extract repository properties
            name = repo_data.get("name", "")
            full_name = repo_data.get("full_name", "")
            
            if not name or not full_name:
                return {
                    "status": "error",
                    "message": f"Invalid repository data for {owner}/{repo}: name missing"
                }
            
            # Create repository entity
            repo_props = {
                "full_name": full_name,
                "description": repo_data.get("description", ""),
                "url": repo_data.get("html_url", ""),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "watchers": repo_data.get("watchers_count", 0),
                "language": repo_data.get("language", ""),
                "topics": repo_data.get("topics", []),
                "created_at": repo_data.get("created_at", ""),
                "updated_at": repo_data.get("updated_at", ""),
                "source": "github"
            }
            
            repo_entity = create_entity(self.db_session, "repository", full_name, repo_props)
            
            # Create owner entity (organization or person)
            owner_data = repo_data.get("owner", {})
            owner_name = owner_data.get("login", "")
            owner_type = owner_data.get("type", "Organization")
            
            entity_type = "organization" if owner_type == "Organization" else "person"
            
            owner_entity = create_entity(
                self.db_session, 
                entity_type, 
                owner_name, 
                {
                    "url": owner_data.get("html_url", ""),
                    "avatar_url": owner_data.get("avatar_url", ""),
                    "type": owner_type,
                    "source": "github"
                }
            )
            
            # Create relationship between owner and repository
            create_relationship(
                self.db_session,
                owner_entity.id,
                repo_entity.id,
                "owns",
                {}
            )
            
            # Get and add contributors
            contributors = self.get_contributors(owner, repo)
            for contributor in contributors:
                contributor_name = contributor.get("login", "")
                
                if contributor_name:
                    contributor_entity = create_entity(
                        self.db_session, 
                        "person", 
                        contributor_name, 
                        {
                            "url": contributor.get("html_url", ""),
                            "avatar_url": contributor.get("avatar_url", ""),
                            "contributions": contributor.get("contributions", 0),
                            "source": "github"
                        }
                    )
                    
                    create_relationship(
                        self.db_session,
                        contributor_entity.id,
                        repo_entity.id,
                        "contributed_to",
                        {
                            "contributions": contributor.get("contributions", 0)
                        }
                    )
            
            # Try to link to a company if possible
            # Use the website URL from the repository if available
            company_url = repo_data.get("homepage", "")
            if company_url:
                # Query for companies with a similar website
                norm_url = normalize_url(company_url)
                if norm_url:
                    result = self.db_session.execute(
                        sa.text("""
                        SELECT id, name FROM entities 
                        WHERE type = 'company' AND properties->>'website' LIKE :url
                        LIMIT 1
                        """),
                        {"url": f"%{norm_url}%"}
                    )
                    
                    row = result.fetchone()
                    if row:
                        company_id, company_name = row
                        
                        # Create relationship between company and repository
                        create_relationship(
                            self.db_session,
                            company_id,
                            repo_entity.id,
                            "developed",
                            {}
                        )
            
            return {
                "status": "success",
                "repo_id": repo_entity.id,
                "name": full_name
            }
            
        except Exception as e:
            logger.error(f"Error ingesting repository {owner}/{repo}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

def get_ingestor(source_type: str, db_session: Session) -> BaseIngestor:
    """
    Get the appropriate ingestor for a data source.
    
    Args:
        source_type: Type of source (crunchbase, github)
        db_session: Database session
        
    Returns:
        Ingestor instance for the specified source
    """
    if source_type.lower() == "crunchbase":
        return CrunchbaseIngestor(db_session)
    elif source_type.lower() == "github":
        return GitHubIngestor(db_session)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")