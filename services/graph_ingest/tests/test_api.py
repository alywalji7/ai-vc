import pytest
from fastapi.testclient import TestClient
import os
import sys
from pathlib import Path
from unittest import mock

# Add the parent directory to sys.path to allow importing app
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.graph_ingest.app.api import create_app
from services.graph_ingest.app.models.base import SourceType


@pytest.fixture
def client():
    """Create a test client for the API"""
    # Use an in-memory SQLite database for testing
    with mock.patch("services.graph_ingest.app.db.schema.DATABASE_URL", "sqlite:///:memory:"):
        app = create_app()
        with TestClient(app) as client:
            yield client


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Data Ingestion & Knowledge Graph Service"
    assert data["status"] == "running"


def test_health_endpoint(client):
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_ingest_github_missing_params(client):
    """Test ingesting GitHub data with missing parameters"""
    response = client.post(
        "/api/ingest",
        json={"source": "github"}
    )
    assert response.status_code == 200  # API returns 200 with error status in body
    data = response.json()
    assert data["status"] == "error"
    assert "message" in data


def test_ingest_crunchbase_missing_params(client):
    """Test ingesting Crunchbase data with missing parameters"""
    response = client.post(
        "/api/ingest",
        json={"source": "crunchbase"}
    )
    assert response.status_code == 200  # API returns 200 with error status in body
    data = response.json()
    assert data["status"] == "error"
    assert "message" in data


@mock.patch("services.graph_ingest.app.ingestors.github.GitHubIngestor.ingest")
def test_ingest_github_org(mock_ingest, client):
    """Test ingesting GitHub organization data"""
    # Mock the ingest method to return a success response
    mock_ingest.return_value = {
        "status": "success",
        "organization": "example-org",
        "org_id": "github:user:12345",
        "repositories_count": 2,
        "repositories": [
            {
                "repository": "repo1",
                "repo_id": "github:repo:67890",
                "contributors_count": 3
            },
            {
                "repository": "repo2",
                "repo_id": "github:repo:67891",
                "contributors_count": 2
            }
        ]
    }
    
    response = client.post(
        "/api/ingest",
        json={"source": "github", "org": "example-org"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["source"] == "github"
    assert data["entities_count"] > 0
    assert data["results"]["organization"] == "example-org"
    
    # Verify the mock was called with the right parameters
    mock_ingest.assert_called_once_with(org="example-org", user=None, repo=None)


@mock.patch("services.graph_ingest.app.ingestors.crunchbase.CrunchbaseIngestor.ingest")
def test_ingest_crunchbase_company(mock_ingest, client):
    """Test ingesting Crunchbase company data"""
    # Mock the ingest method to return a success response
    mock_ingest.return_value = {
        "status": "success",
        "company": "example-company",
        "company_id": "crunchbase:company:12345",
        "founders_count": 2,
        "founders": [
            {"name": "Founder 1", "id": "crunchbase:person:67890"},
            {"name": "Founder 2", "id": "crunchbase:person:67891"}
        ],
        "funding_rounds_count": 1,
        "funding_rounds": [
            {"series": "Series A", "amount": 5000000, "id": "crunchbase:round:54321"}
        ]
    }
    
    response = client.post(
        "/api/ingest",
        json={"source": "crunchbase", "company": "example-company"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["source"] == "crunchbase"
    assert data["entities_count"] > 0
    assert data["results"]["company"] == "example-company"
    
    # Verify the mock was called with the right parameters
    mock_ingest.assert_called_once_with(company="example-company", person=None)