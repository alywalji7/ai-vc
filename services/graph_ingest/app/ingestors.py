"""
Ingestors for the Graph Ingest Service.

This module contains classes to ingest data from various sources and add it
to the knowledge graph.
"""

import os
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.utils import fuzzy_match_entity
from app.metrics import increment_github_success, increment_crunchbase_success, increment_ingest_failure

# Set up logging
logger = logging.getLogger(__name__)

class BaseIngestor:
    """
    Base class for all ingestors.
    """
    def __init__(self, db_session: Session, **kwargs):
        """
        Initialize the ingestor.
        
        Args:
            db_session: Database session
            **kwargs: Additional keyword arguments
        """
        self.db = db_session
        self._setup(**kwargs)
    
    def _setup(self, **kwargs):
        """
        Set up the ingestor with additional configuration.
        
        Args:
            **kwargs: Configuration parameters
        """
        pass
    
    def _find_or_create_entity(
        self, 
        entity_type: str, 
        name: str, 
        properties: Dict[str, Any]
    ) -> int:
        """
        Find an entity by name and type, or create it if it doesn't exist.
        
        Args:
            entity_type: Type of the entity
            name: Name of the entity
            properties: Additional properties of the entity
            
        Returns:
            Entity ID
        """
        # First, check if the entity exists using fuzzy matching
        try:
            # Try to find the entity by exact name match first
            result = self.db.execute(
                text("SELECT id FROM entities WHERE type = :type AND name = :name"),
                {"type": entity_type, "name": name}
            )
            entity = result.scalar()
            
            if not entity:
                # If no exact match, try fuzzy matching
                matched_entity = fuzzy_match_entity(self.db, entity_type, name)
                
                if matched_entity:
                    # Update properties for the existing entity
                    existing_props = matched_entity.get("properties", {})
                    merged_props = {**existing_props, **properties}
                    
                    self.db.execute(
                        text("""
                        UPDATE entities 
                        SET properties = :properties, updated_at = NOW() 
                        WHERE id = :id
                        """),
                        {"properties": json.dumps(merged_props), "id": matched_entity["id"]}
                    )
                    return matched_entity["id"]
            
            if entity:
                # Update properties for the existing entity
                result = self.db.execute(
                    text("SELECT properties FROM entities WHERE id = :id"),
                    {"id": entity}
                )
                existing_props = json.loads(result.scalar() or '{}')
                merged_props = {**existing_props, **properties}
                
                self.db.execute(
                    text("""
                    UPDATE entities 
                    SET properties = :properties, updated_at = NOW() 
                    WHERE id = :id
                    """),
                    {"properties": json.dumps(merged_props), "id": entity}
                )
                
                return entity
            
            # Entity doesn't exist, create it
            result = self.db.execute(
                text("""
                INSERT INTO entities (type, name, properties, created_at, updated_at) 
                VALUES (:type, :name, :properties, NOW(), NOW()) 
                RETURNING id
                """),
                {
                    "type": entity_type, 
                    "name": name, 
                    "properties": json.dumps(properties)
                }
            )
            
            entity_id = result.scalar()
            self.db.commit()
            
            return entity_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error finding or creating entity: {str(e)}")
            raise
    
    def _create_relationship(
        self, 
        source_id: int, 
        target_id: int, 
        relationship_type: str, 
        properties: Dict[str, Any]
    ) -> bool:
        """
        Create a relationship between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            relationship_type: Type of the relationship
            properties: Additional properties of the relationship
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if the relationship already exists
            result = self.db.execute(
                text("""
                SELECT id FROM relationships 
                WHERE source_id = :source_id AND target_id = :target_id AND type = :type
                """),
                {"source_id": source_id, "target_id": target_id, "type": relationship_type}
            )
            
            existing_rel = result.scalar()
            
            if existing_rel:
                # Update properties for the existing relationship
                result = self.db.execute(
                    text("SELECT properties FROM relationships WHERE id = :id"),
                    {"id": existing_rel}
                )
                existing_props = json.loads(result.scalar() or '{}')
                merged_props = {**existing_props, **properties}
                
                self.db.execute(
                    text("""
                    UPDATE relationships 
                    SET properties = :properties, updated_at = NOW() 
                    WHERE id = :id
                    """),
                    {"properties": json.dumps(merged_props), "id": existing_rel}
                )
            else:
                # Create a new relationship
                self.db.execute(
                    text("""
                    INSERT INTO relationships (source_id, target_id, type, properties, created_at, updated_at) 
                    VALUES (:source_id, :target_id, :type, :properties, NOW(), NOW())
                    """),
                    {
                        "source_id": source_id, 
                        "target_id": target_id, 
                        "type": relationship_type, 
                        "properties": json.dumps(properties)
                    }
                )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating relationship: {str(e)}")
            return False


class CrunchbaseIngestor(BaseIngestor):
    """
    Ingestor for Crunchbase data.
    """
    def _setup(self, **kwargs):
        """
        Set up the Crunchbase ingestor.
        
        Args:
            **kwargs: Configuration parameters including api_key
        """
        self.api_key = kwargs.get("api_key", os.environ.get("CRUNCHBASE_API_KEY"))
        self.api_url = "https://api.crunchbase.com/api/v4"
        self.headers = {
            "accept": "application/json",
            "x-cb-user-key": self.api_key
        }
    
    def get_updated_companies(self, last_updated: Optional[datetime] = None) -> List[str]:
        """
        Get companies that have been updated since the specified date.
        
        Args:
            last_updated: Timestamp to check updates since
            
        Returns:
            List of company permalinks
        """
        if not self.api_key:
            logger.warning("Crunchbase API key not provided")
            return []
        
        # For demo purposes, return a few hardcoded companies
        # In a real implementation, this would query the Crunchbase API
        if not last_updated or last_updated < datetime(2025, 1, 1):
            return ["openai", "anthropic", "replit", "stability-ai", "cohere"]
        else:
            return ["openai"]
    
    def ingest_company(self, permalink: str) -> Dict[str, Any]:
        """
        Ingest a company from Crunchbase into the knowledge graph.
        
        Args:
            permalink: Crunchbase permalink for the company
            
        Returns:
            Status of the ingestion
        """
        try:
            # In a real implementation, this would call the Crunchbase API
            # For demo purposes, simulate API data
            company_data = self._get_demo_company_data(permalink)
            
            if not company_data:
                logger.warning(f"No data available for company: {permalink}")
                return {"status": "error", "message": "No data available"}
            
            # Create or update company entity
            company_properties = {
                "permalink": permalink,
                "description": company_data.get("description", ""),
                "founded_on": company_data.get("founded_on", ""),
                "location": company_data.get("location", ""),
                "funding_total": company_data.get("funding_total", 0),
                "funding_rounds": company_data.get("funding_rounds", 0),
                "last_funding_type": company_data.get("last_funding_type", ""),
                "website": company_data.get("website", ""),
                "employee_count": company_data.get("employee_count", ""),
                "data_source": "crunchbase"
            }
            
            company_id = self._find_or_create_entity(
                "company", 
                company_data.get("name", permalink), 
                company_properties
            )
            
            # Process categories
            for category in company_data.get("categories", []):
                category_id = self._find_or_create_entity(
                    "category", 
                    category, 
                    {"data_source": "crunchbase"}
                )
                
                self._create_relationship(
                    company_id,
                    category_id,
                    "has_category",
                    {"data_source": "crunchbase"}
                )
            
            # Process investors
            for investor in company_data.get("investors", []):
                investor_id = self._find_or_create_entity(
                    "investor", 
                    investor, 
                    {"data_source": "crunchbase"}
                )
                
                self._create_relationship(
                    investor_id,
                    company_id,
                    "invested_in",
                    {"data_source": "crunchbase"}
                )
            
            # Process founders
            for founder in company_data.get("founders", []):
                founder_id = self._find_or_create_entity(
                    "person", 
                    founder, 
                    {"data_source": "crunchbase", "role": "founder"}
                )
                
                self._create_relationship(
                    founder_id,
                    company_id,
                    "founded",
                    {"data_source": "crunchbase"}
                )
            
            return {"status": "success", "company_id": company_id}
            
        except Exception as e:
            logger.error(f"Error ingesting company {permalink}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _get_demo_company_data(self, permalink: str) -> Dict[str, Any]:
        """
        Get demo company data for testing purposes.
        
        Args:
            permalink: Crunchbase permalink for the company
            
        Returns:
            Company data
        """
        demo_data = {
            "openai": {
                "name": "OpenAI",
                "description": "AI research and deployment company",
                "founded_on": "2015-12-10",
                "location": "San Francisco, California",
                "funding_total": 11300000000,
                "funding_rounds": 6,
                "last_funding_type": "Series A",
                "website": "https://openai.com",
                "employee_count": "1001-5000",
                "categories": ["Artificial Intelligence", "Machine Learning", "Natural Language Processing"],
                "investors": ["Microsoft", "Khosla Ventures", "Reid Hoffman"],
                "founders": ["Sam Altman", "Elon Musk", "Greg Brockman"]
            },
            "anthropic": {
                "name": "Anthropic",
                "description": "AI safety company",
                "founded_on": "2021-01-15",
                "location": "San Francisco, California",
                "funding_total": 7350000000,
                "funding_rounds": 4,
                "last_funding_type": "Series C",
                "website": "https://www.anthropic.com",
                "employee_count": "101-250",
                "categories": ["Artificial Intelligence", "Machine Learning", "Natural Language Processing"],
                "investors": ["Google", "Spark Capital", "Salesforce Ventures"],
                "founders": ["Dario Amodei", "Daniela Amodei"]
            },
            "replit": {
                "name": "Replit",
                "description": "Collaborative browser-based IDE",
                "founded_on": "2016-03-01",
                "location": "San Francisco, California",
                "funding_total": 105000000,
                "funding_rounds": 4,
                "last_funding_type": "Series B",
                "website": "https://replit.com",
                "employee_count": "51-100",
                "categories": ["Software", "Developer Tools", "Education"],
                "investors": ["a16z", "Y Combinator", "Coatue"],
                "founders": ["Amjad Masad", "Haya Odeh"]
            },
            "stability-ai": {
                "name": "Stability AI",
                "description": "Open source artificial intelligence company",
                "founded_on": "2020-01-01",
                "location": "London, United Kingdom",
                "funding_total": 101000000,
                "funding_rounds": 1,
                "last_funding_type": "Series A",
                "website": "https://stability.ai",
                "employee_count": "51-100",
                "categories": ["Artificial Intelligence", "Image Generation", "Developer Tools"],
                "investors": ["Coatue", "Lightspeed Venture Partners"],
                "founders": ["Emad Mostaque"]
            },
            "cohere": {
                "name": "Cohere",
                "description": "Natural language processing platform",
                "founded_on": "2019-05-01",
                "location": "Toronto, Canada",
                "funding_total": 445000000,
                "funding_rounds": 3,
                "last_funding_type": "Series C",
                "website": "https://cohere.ai",
                "employee_count": "51-100",
                "categories": ["Artificial Intelligence", "Natural Language Processing", "Enterprise Software"],
                "investors": ["Tiger Global Management", "Index Ventures", "Radical Ventures"],
                "founders": ["Aidan Gomez", "Nick Frosst", "Ivan Zhang"]
            }
        }
        
        # If permalink isn't in our demo data, generate a generic company
        if permalink not in demo_data:
            name = permalink.replace("-", " ").title()
            return {
                "name": name,
                "description": f"{name} is a technology company",
                "founded_on": "2020-01-01",
                "location": "San Francisco, California",
                "funding_total": 10000000,
                "funding_rounds": 2,
                "last_funding_type": "Seed",
                "website": f"https://{permalink}.com",
                "employee_count": "11-50",
                "categories": ["Software", "Technology"],
                "investors": ["Acme Ventures", "Example Capital"],
                "founders": ["John Doe", "Jane Smith"]
            }
        
        return demo_data.get(permalink)


class GitHubIngestor(BaseIngestor):
    """
    Ingestor for GitHub data.
    """
    def _setup(self, **kwargs):
        """
        Set up the GitHub ingestor.
        
        Args:
            **kwargs: Configuration parameters including api_token
        """
        self.api_token = kwargs.get("api_token", os.environ.get("GITHUB_API_TOKEN"))
        self.api_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.api_token}" if self.api_token else None
        }
    
    def get_trending_repositories(self, language: Optional[str] = None, since: str = "daily") -> List[Dict[str, str]]:
        """
        Get trending repositories from GitHub.
        
        Args:
            language: Filter by programming language
            since: Time period (daily, weekly, monthly)
            
        Returns:
            List of repository information (owner and name)
        """
        # For demo purposes, return a few hardcoded repositories
        # In a real implementation, this would query the GitHub API
        repos = [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react"},
            {"owner": "tensorflow", "repo": "tensorflow"},
            {"owner": "angular", "repo": "angular"},
            {"owner": "vuejs", "repo": "vue"}
        ]
        
        if language:
            language_repos = {
                "python": [
                    {"owner": "python", "repo": "cpython"},
                    {"owner": "pallets", "repo": "flask"},
                    {"owner": "django", "repo": "django"}
                ],
                "javascript": [
                    {"owner": "facebook", "repo": "react"},
                    {"owner": "vuejs", "repo": "vue"},
                    {"owner": "angular", "repo": "angular"}
                ],
                "rust": [
                    {"owner": "rust-lang", "repo": "rust"},
                    {"owner": "tauri-apps", "repo": "tauri"},
                    {"owner": "denoland", "repo": "deno"}
                ]
            }
            
            return language_repos.get(language.lower(), repos)
        
        return repos
    
    def ingest_repository(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Ingest a repository from GitHub into the knowledge graph.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Status of the ingestion
        """
        try:
            # In a real implementation, this would call the GitHub API
            # For demo purposes, simulate API data
            repo_data = self._get_demo_repo_data(owner, repo_name)
            
            if not repo_data:
                logger.warning(f"No data available for repository: {owner}/{repo_name}")
                return {"status": "error", "message": "No data available"}
            
            # Create or update repository entity
            repo_properties = {
                "full_name": f"{owner}/{repo_name}",
                "description": repo_data.get("description", ""),
                "language": repo_data.get("language", ""),
                "stars": repo_data.get("stars", 0),
                "forks": repo_data.get("forks", 0),
                "open_issues": repo_data.get("open_issues", 0),
                "created_at": repo_data.get("created_at", ""),
                "updated_at": repo_data.get("updated_at", ""),
                "license": repo_data.get("license", ""),
                "url": repo_data.get("url", f"https://github.com/{owner}/{repo_name}"),
                "data_source": "github"
            }
            
            repo_id = self._find_or_create_entity(
                "repository", 
                repo_name, 
                repo_properties
            )
            
            # Create or update organization entity
            org_properties = {
                "url": f"https://github.com/{owner}",
                "data_source": "github"
            }
            
            org_id = self._find_or_create_entity(
                "organization", 
                owner, 
                org_properties
            )
            
            # Create relationship between org and repo
            self._create_relationship(
                org_id,
                repo_id,
                "owns",
                {"data_source": "github"}
            )
            
            # Process languages
            if repo_data.get("language"):
                lang_id = self._find_or_create_entity(
                    "language", 
                    repo_data["language"], 
                    {"data_source": "github"}
                )
                
                self._create_relationship(
                    repo_id,
                    lang_id,
                    "written_in",
                    {"data_source": "github"}
                )
            
            # Process topics
            for topic in repo_data.get("topics", []):
                topic_id = self._find_or_create_entity(
                    "topic", 
                    topic, 
                    {"data_source": "github"}
                )
                
                self._create_relationship(
                    repo_id,
                    topic_id,
                    "has_topic",
                    {"data_source": "github"}
                )
            
            # Process contributors
            for contributor in repo_data.get("contributors", []):
                contributor_id = self._find_or_create_entity(
                    "person", 
                    contributor, 
                    {"data_source": "github"}
                )
                
                self._create_relationship(
                    contributor_id,
                    repo_id,
                    "contributed_to",
                    {"data_source": "github"}
                )
            
            return {"status": "success", "repo_id": repo_id}
            
        except Exception as e:
            logger.error(f"Error ingesting repository {owner}/{repo_name}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _get_demo_repo_data(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Get demo repository data for testing purposes.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Repository data
        """
        demo_data = {
            "microsoft/vscode": {
                "description": "Visual Studio Code",
                "language": "TypeScript",
                "stars": 152000,
                "forks": 28000,
                "open_issues": 7800,
                "created_at": "2015-09-03",
                "updated_at": "2025-04-20",
                "license": "MIT",
                "url": "https://github.com/microsoft/vscode",
                "topics": ["editor", "code", "development", "typescript"],
                "contributors": ["joaomoreno", "weinand", "aeschli", "bpasero"]
            },
            "facebook/react": {
                "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
                "language": "JavaScript",
                "stars": 211000,
                "forks": 44000,
                "open_issues": 1100,
                "created_at": "2013-05-24",
                "updated_at": "2025-04-21",
                "license": "MIT",
                "url": "https://github.com/facebook/react",
                "topics": ["javascript", "ui", "frontend", "library"],
                "contributors": ["sophiebits", "gaearon", "sebmarkbage", "acdlite"]
            },
            "tensorflow/tensorflow": {
                "description": "An open source machine learning framework for everyone",
                "language": "C++",
                "stars": 179000,
                "forks": 89000,
                "open_issues": 2700,
                "created_at": "2015-11-07",
                "updated_at": "2025-04-19",
                "license": "Apache-2.0",
                "url": "https://github.com/tensorflow/tensorflow",
                "topics": ["machine-learning", "deep-learning", "neural-networks", "python"],
                "contributors": ["tensorflower-gardener", "martinwicke", "rohan100jain", "ewilderj"]
            },
            "angular/angular": {
                "description": "The modern web developer's platform",
                "language": "TypeScript",
                "stars": 90000,
                "forks": 24000,
                "open_issues": 1500,
                "created_at": "2014-09-18",
                "updated_at": "2025-04-18",
                "license": "MIT",
                "url": "https://github.com/angular/angular",
                "topics": ["javascript", "typescript", "web", "framework"],
                "contributors": ["IgorMinar", "mhevery", "kara", "tbosch"]
            },
            "vuejs/vue": {
                "description": "Vue.js is a progressive, incrementally-adoptable JavaScript framework for building UI on the web.",
                "language": "JavaScript",
                "stars": 205000,
                "forks": 35000,
                "open_issues": 590,
                "created_at": "2013-07-29",
                "updated_at": "2025-04-20",
                "license": "MIT",
                "url": "https://github.com/vuejs/vue",
                "topics": ["javascript", "vue", "frontend", "framework"],
                "contributors": ["yyx990803", "posva", "Hanks10100", "defcc"]
            }
        }
        
        key = f"{owner}/{repo_name}"
        
        # If repo isn't in our demo data, generate generic data
        if key not in demo_data:
            return {
                "description": f"{repo_name} - a {owner} project",
                "language": "JavaScript",
                "stars": 1000,
                "forks": 200,
                "open_issues": 50,
                "created_at": "2022-01-01",
                "updated_at": "2025-04-20",
                "license": "MIT",
                "url": f"https://github.com/{owner}/{repo_name}",
                "topics": ["software", "development"],
                "contributors": ["contributor1", "contributor2"]
            }
        
        return demo_data.get(key)


# Function to get the appropriate ingestor class based on source
def get_ingestor(source: str, db_session: Session, **kwargs) -> BaseIngestor:
    """
    Get the appropriate ingestor for a given source.
    
    Args:
        source: Source type (e.g., "github", "crunchbase")
        db_session: Database session
        **kwargs: Additional keyword arguments for the ingestor
        
    Returns:
        An ingestor instance
    """
    ingestors = {
        "github": GitHubIngestor,
        "crunchbase": CrunchbaseIngestor
    }
    
    ingestor_class = ingestors.get(source.lower())
    
    if not ingestor_class:
        raise ValueError(f"Unknown source: {source}")
    
    return ingestor_class(db_session, **kwargs)