from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .base import BaseEntity, BaseRelationship, EntityType, RelationshipType, SourceType


class GitHubUser(BaseEntity):
    """GitHub user or organization"""
    type: EntityType = EntityType.PERSON
    source: SourceType = SourceType.GITHUB
    github_id: int
    login: str
    avatar_url: Optional[str] = None
    html_url: str
    followers_url: str
    following_url: str
    repos_url: str
    account_type: str = "User"
    site_admin: bool = False
    is_organization: bool = False
    
    @classmethod
    def from_api_response(cls, data: Dict) -> "GitHubUser":
        """Create a GitHubUser from GitHub API response"""
        is_org = data.get("type", "").lower() == "organization"
        entity_type = EntityType.ORGANIZATION if is_org else EntityType.PERSON
        
        return cls(
            id=f"github:user:{data['id']}",
            type=entity_type,
            source_id=str(data["id"]),
            name=data["login"],
            github_id=data["id"],
            login=data["login"],
            avatar_url=data.get("avatar_url"),
            html_url=data.get("html_url", ""),
            followers_url=data.get("followers_url", ""),
            following_url=data.get("following_url", ""),
            repos_url=data.get("repos_url", ""),
            account_type=data.get("type", "User"),
            site_admin=data.get("site_admin", False),
            is_organization=is_org,
            properties={
                "bio": data.get("bio"),
                "company": data.get("company"),
                "location": data.get("location"),
                "email": data.get("email"),
                "twitter_username": data.get("twitter_username"),
                "public_repos": data.get("public_repos"),
                "public_gists": data.get("public_gists"),
                "followers": data.get("followers"),
                "following": data.get("following"),
            }
        )


class GitHubRepository(BaseEntity):
    """GitHub repository"""
    type: EntityType = EntityType.REPOSITORY
    source: SourceType = SourceType.GITHUB
    github_id: int
    full_name: str
    html_url: str
    description: Optional[str] = None
    is_fork: bool = False
    is_archived: bool = False
    is_private: bool = False
    default_branch: str = "main"
    language: Optional[str] = None
    stars_count: int = 0
    forks_count: int = 0
    watchers_count: int = 0
    open_issues_count: int = 0
    
    @classmethod
    def from_api_response(cls, data: Dict) -> "GitHubRepository":
        """Create a GitHubRepository from GitHub API response"""
        return cls(
            id=f"github:repo:{data['id']}",
            source_id=str(data["id"]),
            name=data["name"],
            github_id=data["id"],
            full_name=data["full_name"],
            html_url=data["html_url"],
            description=data.get("description"),
            is_fork=data.get("fork", False),
            is_archived=data.get("archived", False),
            is_private=data.get("private", False),
            default_branch=data.get("default_branch", "main"),
            language=data.get("language"),
            stars_count=data.get("stargazers_count", 0),
            forks_count=data.get("forks_count", 0),
            watchers_count=data.get("watchers_count", 0),
            open_issues_count=data.get("open_issues_count", 0),
            properties={
                "topics": data.get("topics", []),
                "homepage": data.get("homepage"),
                "license": data.get("license", {}).get("key") if data.get("license") else None,
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "pushed_at": data.get("pushed_at"),
                "size": data.get("size"),
            }
        )


class GitHubContributor(BaseRelationship):
    """Relationship between a GitHub user and a repository they contribute to"""
    type: RelationshipType = RelationshipType.CONTRIBUTES_TO
    source: SourceType = SourceType.GITHUB
    contributions_count: int = 0
    
    @classmethod
    def from_api_response(cls, user_id: str, repo_id: str, data: Dict) -> "GitHubContributor":
        """Create a GitHubContributor from GitHub API response"""
        return cls(
            id=f"github:contrib:{user_id}:{repo_id}",
            from_entity_id=user_id,
            to_entity_id=repo_id,
            contributions_count=data.get("contributions", 0),
            properties={
                "contributions": data.get("contributions", 0),
            }
        )


class GitHubOwnership(BaseRelationship):
    """Relationship between a GitHub user/org and a repository they own"""
    type: RelationshipType = RelationshipType.OWNS
    source: SourceType = SourceType.GITHUB
    
    @classmethod
    def create(cls, owner_id: str, repo_id: str) -> "GitHubOwnership":
        """Create a GitHubOwnership relationship"""
        return cls(
            id=f"github:owns:{owner_id}:{repo_id}",
            from_entity_id=owner_id,
            to_entity_id=repo_id,
        )