import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to sys.path to allow importing app
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.graph_ingest.app.models.base import (
    SourceType, EntityType, RelationshipType,
    BaseEntity, BaseRelationship
)
from services.graph_ingest.app.models.github import (
    GitHubUser, GitHubRepository, 
    GitHubContributor, GitHubOwnership
)
from services.graph_ingest.app.models.crunchbase import (
    CrunchbaseCompany, CrunchbasePerson,
    CrunchbaseFounder, CrunchbaseFundingRound
)


def test_base_entity():
    """Test the BaseEntity model"""
    entity = BaseEntity(
        id="test:entity:123",
        type=EntityType.PERSON,
        source=SourceType.GITHUB,
        source_id="123",
        name="Test Entity"
    )
    
    assert entity.id == "test:entity:123"
    assert entity.type == EntityType.PERSON
    assert entity.source == SourceType.GITHUB
    assert entity.source_id == "123"
    assert entity.name == "Test Entity"
    assert isinstance(entity.created_at, datetime)
    assert isinstance(entity.updated_at, datetime)
    assert isinstance(entity.properties, dict)


def test_base_relationship():
    """Test the BaseRelationship model"""
    relationship = BaseRelationship(
        id="test:rel:123",
        type=RelationshipType.WORKS_FOR,
        source=SourceType.GITHUB,
        from_entity_id="test:entity:1",
        to_entity_id="test:entity:2"
    )
    
    assert relationship.id == "test:rel:123"
    assert relationship.type == RelationshipType.WORKS_FOR
    assert relationship.source == SourceType.GITHUB
    assert relationship.from_entity_id == "test:entity:1"
    assert relationship.to_entity_id == "test:entity:2"
    assert isinstance(relationship.created_at, datetime)
    assert isinstance(relationship.updated_at, datetime)
    assert isinstance(relationship.properties, dict)


def test_github_user_from_api_response():
    """Test creating a GitHubUser from API response"""
    api_response = {
        "login": "testuser",
        "id": 12345,
        "node_id": "MDQ6VXNlcjEyMzQ1",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/testuser",
        "html_url": "https://github.com/testuser",
        "followers_url": "https://api.github.com/users/testuser/followers",
        "following_url": "https://api.github.com/users/testuser/following{/other_user}",
        "gists_url": "https://api.github.com/users/testuser/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/testuser/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/testuser/subscriptions",
        "organizations_url": "https://api.github.com/users/testuser/orgs",
        "repos_url": "https://api.github.com/users/testuser/repos",
        "events_url": "https://api.github.com/users/testuser/events{/privacy}",
        "received_events_url": "https://api.github.com/users/testuser/received_events",
        "type": "User",
        "site_admin": False,
        "name": "Test User",
        "company": "Test Company",
        "blog": "https://testuser.com",
        "location": "San Francisco, CA",
        "email": "test@example.com",
        "hireable": True,
        "bio": "Test bio",
        "twitter_username": "testuser",
        "public_repos": 50,
        "public_gists": 10,
        "followers": 100,
        "following": 200,
        "created_at": "2011-01-25T18:44:36Z",
        "updated_at": "2023-04-24T12:34:56Z"
    }
    
    user = GitHubUser.from_api_response(api_response)
    
    assert user.id == "github:user:12345"
    assert user.type == EntityType.PERSON
    assert user.source == SourceType.GITHUB
    assert user.source_id == "12345"
    assert user.name == "testuser"
    assert user.github_id == 12345
    assert user.login == "testuser"
    assert user.avatar_url == "https://avatars.githubusercontent.com/u/12345?v=4"
    assert user.html_url == "https://github.com/testuser"
    assert user.followers_url == "https://api.github.com/users/testuser/followers"
    assert user.following_url == "https://api.github.com/users/testuser/following{/other_user}"
    assert user.repos_url == "https://api.github.com/users/testuser/repos"
    assert user.type == "User"
    assert user.site_admin is False
    assert user.is_organization is False
    
    # Check that properties were stored correctly
    assert user.properties["bio"] == "Test bio"
    assert user.properties["company"] == "Test Company"
    assert user.properties["location"] == "San Francisco, CA"
    assert user.properties["email"] == "test@example.com"
    assert user.properties["twitter_username"] == "testuser"
    assert user.properties["public_repos"] == 50
    assert user.properties["public_gists"] == 10
    assert user.properties["followers"] == 100
    assert user.properties["following"] == 200


def test_github_repository_from_api_response():
    """Test creating a GitHubRepository from API response"""
    api_response = {
        "id": 12345,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMjM0NQ==",
        "name": "test-repo",
        "full_name": "testuser/test-repo",
        "private": False,
        "owner": {
            "login": "testuser",
            "id": 67890,
            "node_id": "MDQ6VXNlcjY3ODkw",
            "avatar_url": "https://avatars.githubusercontent.com/u/67890?v=4",
            "url": "https://api.github.com/users/testuser",
            "html_url": "https://github.com/testuser",
            "type": "User",
            "site_admin": False
        },
        "html_url": "https://github.com/testuser/test-repo",
        "description": "Test repository description",
        "fork": False,
        "url": "https://api.github.com/repos/testuser/test-repo",
        "forks_url": "https://api.github.com/repos/testuser/test-repo/forks",
        "created_at": "2022-01-01T00:00:00Z",
        "updated_at": "2022-02-01T00:00:00Z",
        "pushed_at": "2022-03-01T00:00:00Z",
        "homepage": "https://test-repo.com",
        "size": 1000,
        "stargazers_count": 500,
        "watchers_count": 500,
        "language": "Python",
        "has_issues": True,
        "has_projects": True,
        "has_downloads": True,
        "has_wiki": True,
        "has_pages": False,
        "has_discussions": False,
        "forks_count": 100,
        "archived": False,
        "disabled": False,
        "open_issues_count": 25,
        "license": {
            "key": "mit",
            "name": "MIT License",
            "spdx_id": "MIT",
            "url": "https://api.github.com/licenses/mit",
            "node_id": "MDc6TGljZW5zZTEz"
        },
        "topics": ["python", "api", "testing"],
        "visibility": "public",
        "forks": 100,
        "open_issues": 25,
        "watchers": 500,
        "default_branch": "main"
    }
    
    repo = GitHubRepository.from_api_response(api_response)
    
    assert repo.id == "github:repo:12345"
    assert repo.type == EntityType.REPOSITORY
    assert repo.source == SourceType.GITHUB
    assert repo.source_id == "12345"
    assert repo.name == "test-repo"
    assert repo.github_id == 12345
    assert repo.full_name == "testuser/test-repo"
    assert repo.html_url == "https://github.com/testuser/test-repo"
    assert repo.description == "Test repository description"
    assert repo.is_fork is False
    assert repo.is_archived is False
    assert repo.is_private is False
    assert repo.default_branch == "main"
    assert repo.language == "Python"
    assert repo.stars_count == 500
    assert repo.forks_count == 100
    assert repo.watchers_count == 500
    assert repo.open_issues_count == 25
    
    # Check that properties were stored correctly
    assert repo.properties["topics"] == ["python", "api", "testing"]
    assert repo.properties["homepage"] == "https://test-repo.com"
    assert repo.properties["license"] == "mit"
    assert repo.properties["created_at"] == "2022-01-01T00:00:00Z"
    assert repo.properties["updated_at"] == "2022-02-01T00:00:00Z"
    assert repo.properties["pushed_at"] == "2022-03-01T00:00:00Z"
    assert repo.properties["size"] == 1000


def test_crunchbase_company_from_api_response():
    """Test creating a CrunchbaseCompany from API response"""
    api_response = {
        "uuid": "abcd1234",
        "properties": {
            "name": "Test Company",
            "permalink": "test-company",
            "website": {
                "value": "https://testcompany.com"
            },
            "founded_on": {
                "value": "2020-01-01"
            },
            "short_description": "A test company for unit tests",
            "country_code": "USA",
            "state_code": "CA",
            "region": "San Francisco Bay Area",
            "city": "San Francisco",
            "status": "active",
            "category_list": "software,artificial intelligence,machine learning",
            "num_employees_min": 10,
            "num_employees_max": 50,
            "linkedin": {
                "value": "https://www.linkedin.com/company/test-company"
            },
            "twitter": {
                "value": "https://twitter.com/testcompany"
            },
            "facebook": {
                "value": "https://facebook.com/testcompany"
            },
            "company_type": "for_profit",
            "stock_exchange": "NYSE",
            "stock_symbol": "TEST",
            "rank_org_company": 12345,
            "revenue_range": "$1M-$10M",
            "total_funding_usd": 5000000,
            "number_of_investments": 3,
            "number_of_acquisitions": 1
        }
    }
    
    company = CrunchbaseCompany.from_api_response(api_response)
    
    assert company.id == "crunchbase:company:abcd1234"
    assert company.type == EntityType.COMPANY
    assert company.source == SourceType.CRUNCHBASE
    assert company.source_id == "abcd1234"
    assert company.name == "Test Company"
    assert company.permalink == "test-company"
    assert company.website == "https://testcompany.com"
    assert company.founded_on == "2020-01-01"
    assert company.short_description == "A test company for unit tests"
    assert company.country_code == "USA"
    assert company.state_code == "CA"
    assert company.region == "San Francisco Bay Area"
    assert company.city == "San Francisco"
    assert company.status == "active"
    assert company.category_list == ["software", "artificial intelligence", "machine learning"]
    
    # Check that properties were stored correctly
    assert company.properties["num_employees_min"] == 10
    assert company.properties["num_employees_max"] == 50
    assert company.properties["linkedin"] == "https://www.linkedin.com/company/test-company"
    assert company.properties["twitter"] == "https://twitter.com/testcompany"
    assert company.properties["facebook"] == "https://facebook.com/testcompany"
    assert company.properties["company_type"] == "for_profit"
    assert company.properties["stock_exchange"] == "NYSE"
    assert company.properties["stock_symbol"] == "TEST"
    assert company.properties["rank_org_company"] == 12345
    assert company.properties["revenue_range"] == "$1M-$10M"
    assert company.properties["total_funding_usd"] == 5000000
    assert company.properties["number_of_investments"] == 3
    assert company.properties["number_of_acquisitions"] == 1