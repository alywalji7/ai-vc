"""
Tests for the compliance middleware package.

This module contains tests to verify the functionality of the
compliance middleware, including investor accreditation verification,
OFAC sanctions checking, and the kill-switch admin override endpoint.
"""

import pytest
import json
import hashlib
from fastapi import FastAPI
from fastapi.testclient import TestClient

from libs.compliance import (
    verify_investor_accreditation,
    check_ofac_sanctions,
    hash_decision_payload,
)
from libs.compliance.admin import admin_router
from libs.compliance.middleware import ComplianceMiddleware


@pytest.fixture
def app():
    """Create a test FastAPI application with the compliance middleware."""
    app = FastAPI()
    app.include_router(admin_router)
    
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    @app.post("/api/investments")
    async def create_investment(investment: dict):
        return {"id": "inv-123", **investment}
    
    # Add the compliance middleware
    app.add_middleware(ComplianceMiddleware)
    
    return app


@pytest.fixture
def client(app):
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def test_investor_accreditation():
    """Test the investor accreditation verification function."""
    # Test a valid investor
    is_accredited, message = verify_investor_accreditation("valid-investor")
    assert is_accredited is True
    assert "verified as accredited investor" in message
    
    # In a real test, we would also test invalid investors


def test_ofac_sanctions_check():
    """Test the OFAC sanctions checking function."""
    # Test a person not on the sanctions list
    is_sanctioned, result = check_ofac_sanctions("John Doe", "United States")
    assert is_sanctioned is False
    assert result["is_sanctioned"] is False
    
    # In a real test, we would also test sanctioned individuals


def test_hash_decision_payload():
    """Test the SHA-256 hashing of decision payloads."""
    # Create a test payload
    payload = {
        "investment_amount": 1000000,
        "company_id": "company-123",
        "investor_id": "investor-456",
        "decision": "approve"
    }
    
    # Calculate the hash manually for comparison
    serialized = json.dumps(payload, sort_keys=True)
    expected_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    
    # Test the hash_decision_payload function
    payload_hash = hash_decision_payload(payload)
    assert payload_hash == expected_hash
    
    # Change the payload and verify the hash changes
    modified_payload = payload.copy()
    modified_payload["decision"] = "reject"
    modified_hash = hash_decision_payload(modified_payload)
    assert modified_hash != payload_hash


def test_admin_override_unauthorized(client):
    """Test that unauthorized users cannot access the admin override endpoint."""
    # Test without authentication
    response = client.post("/admin/override", json={"type": "test"})
    assert response.status_code == 401
    
    # Test with non-GP role
    headers = {"Authorization": "Bearer token.with.role=LP"}
    response = client.post("/admin/override", json={"type": "test"}, headers=headers)
    assert response.status_code == 403


def test_admin_override_authorized(client):
    """Test that GP users can access the admin override endpoint."""
    # Test with GP role
    headers = {"Authorization": "Bearer token.with.role=GP"}
    response = client.post(
        "/admin/override", 
        json={
            "type": "compliance",
            "description": "Test override",
            "user_id": "gp-user",
            "target": "investment-123"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # In a real test, we would also verify the database record


def test_middleware_integration(client):
    """Test the integration of the compliance middleware."""
    # Test an exempt path
    response = client.get("/health")
    assert response.status_code == 404  # Not found, but middleware should let it through
    
    # Test an investment request with valid data
    investment_data = {
        "amount": 2000000,
        "company_id": "company-789",
        "investor_id": "investor-123",
        "founders": [
            {"name": "Jane Smith", "country": "Canada"},
            {"name": "Bob Johnson", "country": "United States"}
        ]
    }
    
    response = client.post("/api/investments", json=investment_data)
    assert response.status_code == 200
    assert response.json()["id"] == "inv-123"
    
    # In a real test, we would also test with non-accredited investors
    # and sanctioned founders