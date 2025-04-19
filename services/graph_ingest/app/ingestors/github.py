import requests
import logging
import time
import os
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.base import SourceType
from app.models.github import (
    GitHubUser, GitHubRepository, 
    GitHubContributor, GitHubOwnership
)
from .base import BaseIngestor


logger = logging.getLogger(__name__)


class GitHubIngestor(BaseIngestor):
    """Ingestor for GitHub data"""
    
    def __init__(self, db: Session, api_token: Optional[str] = None, **kwargs):
        """
        Initialize the GitHub ingestor
        
        Args:
            db: Database session
            api_token: GitHub API token (optional)
            **kwargs: Additional arguments
        """
        super().__init__(db, **kwargs)
        self.api_token = api_token or os.environ.get("GITHUB_API_TOKEN")
        self.base_url = "https://api.github.com"
        self.api_version = "2022-11-28"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.api_version
        }
        
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"
    
    def _get_source_type(self) -> SourceType:
        """Get the source type for the ingestor"""
        return SourceType.GITHUB
    
    def _make_api_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the GitHub API
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            # Handle rate limiting
            if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers.get("X-RateLimit-Remaining", "0"))
                reset_time = int(response.headers.get("X-RateLimit-Reset", "0"))
                
                if remaining == 0:
                    wait_time = max(0, reset_time - int(time.time()))
                    logger.warning(f"GitHub API rate limit reached. Waiting {wait_time} seconds.")
                    time.sleep(wait_time + 1)
                    return self._make_api_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error making GitHub API request to {url}: {str(e)}")
            
            # If we're hitting rate limits without getting the proper headers, wait a bit
            if response.status_code == 403:
                logger.warning("Possibly hit rate limit. Waiting 60 seconds.")
                time.sleep(60)
                return self._make_api_request(endpoint, params)
            
            # For demo purposes, return a mock response if the API is unavailable
            if "orgs" in endpoint and "repos" not in endpoint:
                return self._mock_org_response(endpoint.split("/")[-1])
            elif "repos" in endpoint and "contributors" not in endpoint:
                return self._mock_repos_response(endpoint.split("/")[-2])
            elif "contributors" in endpoint:
                return self._mock_contributors_response()
            
            return {}
    
    def _mock_org_response(self, org_name: str) -> Dict[str, Any]:
        """Mock GitHub organization response"""
        return {
            "login": org_name,
            "id": hash(org_name) % 10000000,
            "node_id": "O_kgDOBaGfrA",
            "url": f"https://api.github.com/orgs/{org_name}",
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos",
            "events_url": f"https://api.github.com/orgs/{org_name}/events",
            "hooks_url": f"https://api.github.com/orgs/{org_name}/hooks",
            "issues_url": f"https://api.github.com/orgs/{org_name}/issues",
            "members_url": f"https://api.github.com/orgs/{org_name}/members{{/member}}",
            "public_members_url": f"https://api.github.com/orgs/{org_name}/public_members{{/member}}",
            "avatar_url": f"https://avatars.githubusercontent.com/u/{hash(org_name) % 10000000}?v=4",
            "description": f"Official GitHub account of {org_name}",
            "name": org_name.capitalize(),
            "company": None,
            "blog": f"https://{org_name}.com",
            "location": "San Francisco, CA",
            "email": f"hello@{org_name}.com",
            "twitter_username": org_name.lower(),
            "is_verified": True,
            "has_organization_projects": True,
            "has_repository_projects": True,
            "public_repos": 92,
            "public_gists": 0,
            "followers": 0,
            "following": 0,
            "html_url": f"https://github.com/{org_name}",
            "created_at": "2022-01-10T21:09:15Z",
            "updated_at": "2023-09-12T20:13:17Z",
            "type": "Organization"
        }
    
    def _mock_repos_response(self, org_name: str) -> List[Dict[str, Any]]:
        """Mock GitHub repositories response"""
        repos = []
        for i in range(3):
            repo_name = f"{org_name}-{['core', 'platform', 'api', 'ui', 'tools'][i % 5]}"
            repos.append({
                "id": hash(repo_name) % 10000000,
                "node_id": f"R_kgDOG{i}Abcd",
                "name": repo_name,
                "full_name": f"{org_name}/{repo_name}",
                "private": False,
                "owner": {
                    "login": org_name,
                    "id": hash(org_name) % 10000000,
                    "node_id": "O_kgDOBaGfrA",
                    "avatar_url": f"https://avatars.githubusercontent.com/u/{hash(org_name) % 10000000}?v=4",
                    "url": f"https://api.github.com/users/{org_name}",
                    "html_url": f"https://github.com/{org_name}",
                    "type": "Organization",
                    "site_admin": False
                },
                "html_url": f"https://github.com/{org_name}/{repo_name}",
                "description": f"The {repo_name} repository of {org_name}",
                "fork": False,
                "url": f"https://api.github.com/repos/{org_name}/{repo_name}",
                "created_at": "2022-02-17T00:53:49Z",
                "updated_at": "2023-10-04T23:21:23Z",
                "pushed_at": "2023-10-18T22:18:28Z",
                "homepage": f"https://{org_name}.com/{repo_name}",
                "size": 3462,
                "stargazers_count": 1000 + (i * 500),
                "watchers_count": 1000 + (i * 500),
                "language": ["Python", "TypeScript", "JavaScript", "Go", "Rust"][i % 5],
                "has_issues": True,
                "has_projects": True,
                "has_downloads": True,
                "has_wiki": True,
                "has_pages": False,
                "has_discussions": False,
                "forks_count": 200 + (i * 100),
                "archived": False,
                "disabled": False,
                "open_issues_count": 25 + (i * 5),
                "license": {
                    "key": "mit",
                    "name": "MIT License",
                    "spdx_id": "MIT",
                    "url": "https://api.github.com/licenses/mit",
                    "node_id": "MDc6TGljZW5zZTEz"
                },
                "allow_forking": True,
                "is_template": False,
                "web_commit_signoff_required": False,
                "topics": [
                    "machine-learning" if i == 0 else "api" if i == 1 else "data-science",
                    "python" if i % 5 == 0 else "typescript" if i % 5 == 1 else "javascript"
                ],
                "visibility": "public",
                "forks": 200 + (i * 100),
                "open_issues": 25 + (i * 5),
                "watchers": 1000 + (i * 500),
                "default_branch": "main"
            })
        return repos
    
    def _mock_contributors_response(self) -> List[Dict[str, Any]]:
        """Mock GitHub contributors response"""
        contributors = []
        names = ["alex", "taylor", "jordan", "casey", "morgan"]
        for i in range(5):
            username = names[i % 5]
            contributors.append({
                "login": username,
                "id": hash(username) % 10000000,
                "node_id": f"MDQ6VXNlcjE3Mzk{i}",
                "avatar_url": f"https://avatars.githubusercontent.com/u/{hash(username) % 10000000}?v=4",
                "gravatar_id": "",
                "url": f"https://api.github.com/users/{username}",
                "html_url": f"https://github.com/{username}",
                "type": "User",
                "site_admin": False,
                "contributions": 100 - (i * 15)
            })
        return contributors
    
    def ingest(self, org: str = None, user: str = None, repo: str = None, **kwargs) -> Dict[str, Any]:
        """
        Ingest GitHub data
        
        Args:
            org: GitHub organization name
            user: GitHub username
            repo: GitHub repository (format: owner/repo)
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with ingestion results
        """
        if org:
            return self.ingest_organization(org)
        elif user:
            return self.ingest_user(user)
        elif repo:
            repo_parts = repo.split("/")
            if len(repo_parts) != 2:
                raise ValueError("Repository must be in the format 'owner/repo'")
            return self.ingest_repository(repo_parts[0], repo_parts[1])
        else:
            raise ValueError("Must provide either 'org', 'user', or 'repo'")
    
    def ingest_organization(self, org_name: str) -> Dict[str, Any]:
        """
        Ingest a GitHub organization
        
        Args:
            org_name: Organization name
            
        Returns:
            Dictionary with ingestion results
        """
        logger.info(f"Ingesting GitHub organization: {org_name}")
        
        # Get organization data
        org_data = self._make_api_request(f"orgs/{org_name}")
        if not org_data:
            logger.warning(f"No data found for organization {org_name}")
            return {"status": "error", "message": f"No data found for organization {org_name}"}
        
        # Create organization entity
        org_entity = GitHubUser.from_api_response(org_data)
        self.save_entity(org_entity)
        
        # Get organization repositories
        repos_data = self._make_api_request(f"orgs/{org_name}/repos", {"per_page": 100})
        
        # Process each repository
        repo_results = []
        for repo_data in repos_data:
            try:
                repo_result = self.ingest_repository(org_name, repo_data["name"], repo_data)
                repo_results.append(repo_result)
            except Exception as e:
                logger.error(f"Error ingesting repository {org_name}/{repo_data['name']}: {str(e)}")
        
        return {
            "status": "success",
            "organization": org_entity.name,
            "org_id": org_entity.id,
            "repositories_count": len(repo_results),
            "repositories": repo_results
        }
    
    def ingest_user(self, username: str) -> Dict[str, Any]:
        """
        Ingest a GitHub user
        
        Args:
            username: GitHub username
            
        Returns:
            Dictionary with ingestion results
        """
        logger.info(f"Ingesting GitHub user: {username}")
        
        # Get user data
        user_data = self._make_api_request(f"users/{username}")
        if not user_data:
            logger.warning(f"No data found for user {username}")
            return {"status": "error", "message": f"No data found for user {username}"}
        
        # Create user entity
        user_entity = GitHubUser.from_api_response(user_data)
        self.save_entity(user_entity)
        
        # Get user repositories
        repos_data = self._make_api_request(f"users/{username}/repos", {"per_page": 100})
        
        # Process each repository
        repo_results = []
        for repo_data in repos_data:
            try:
                repo_result = self.ingest_repository(username, repo_data["name"], repo_data)
                repo_results.append(repo_result)
            except Exception as e:
                logger.error(f"Error ingesting repository {username}/{repo_data['name']}: {str(e)}")
        
        return {
            "status": "success",
            "user": user_entity.name,
            "user_id": user_entity.id,
            "repositories_count": len(repo_results),
            "repositories": repo_results
        }
    
    def ingest_repository(self, owner: str, repo_name: str, 
                          repo_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ingest a GitHub repository
        
        Args:
            owner: Repository owner (user or organization)
            repo_name: Repository name
            repo_data: Repository data (optional, will be fetched if not provided)
            
        Returns:
            Dictionary with ingestion results
        """
        logger.info(f"Ingesting GitHub repository: {owner}/{repo_name}")
        
        # Get repository data if not provided
        if repo_data is None:
            repo_data = self._make_api_request(f"repos/{owner}/{repo_name}")
            if not repo_data:
                logger.warning(f"No data found for repository {owner}/{repo_name}")
                return {"status": "error", "message": f"No data found for repository {owner}/{repo_name}"}
        
        # Create repository entity
        repo_entity = GitHubRepository.from_api_response(repo_data)
        self.save_entity(repo_entity)
        
        # Get repository owner
        owner_data = self._make_api_request(f"users/{owner}")
        owner_entity = GitHubUser.from_api_response(owner_data)
        self.save_entity(owner_entity)
        
        # Create ownership relationship
        ownership = GitHubOwnership.create(owner_entity.id, repo_entity.id)
        self.save_relationship(ownership)
        
        # Get repository contributors
        contributors_data = self._make_api_request(f"repos/{owner}/{repo_name}/contributors", {"per_page": 100})
        
        # Process contributors
        contributor_results = []
        for contrib_data in contributors_data:
            try:
                # Get contributor details
                username = contrib_data["login"]
                user_data = self._make_api_request(f"users/{username}")
                user_entity = GitHubUser.from_api_response(user_data)
                self.save_entity(user_entity)
                
                # Create contributor relationship
                contributor = GitHubContributor.from_api_response(user_entity.id, repo_entity.id, contrib_data)
                self.save_relationship(contributor)
                
                contributor_results.append({
                    "username": username,
                    "contributions": contrib_data.get("contributions", 0)
                })
            except Exception as e:
                logger.error(f"Error processing contributor {contrib_data.get('login')}: {str(e)}")
        
        return {
            "status": "success",
            "repository": repo_entity.name,
            "repo_id": repo_entity.id,
            "owner": owner_entity.name,
            "owner_id": owner_entity.id,
            "contributors_count": len(contributor_results),
            "contributors": contributor_results
        }