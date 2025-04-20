"""
Tests for the GrowthBot agent.
"""

import os
import json
import asyncio
import tempfile
import shutil
import uuid
from pathlib import Path
import pytest

from ..growth_bot.agent import GrowthBot
from ..config import AGENT_CONFIG


@pytest.fixture
def temp_growth_plans_dir():
    """Create a temporary directory for growth plans."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def growth_bot():
    """Create a GrowthBot instance for testing."""
    config = AGENT_CONFIG["growth_bot"]
    return GrowthBot(
        topic=config["topic"],
        group_id=config["group_id"],
        name=config["name"],
        description=config["description"]
    )


@pytest.mark.asyncio
async def test_generate_ab_test_plan(growth_bot, temp_growth_plans_dir, monkeypatch):
    """Test that the GrowthBot generates an AB test plan JSON file."""
    # Patch the GROWTH_PLANS_DIR to use our temporary directory
    monkeypatch.setattr('services.value_add_agents.growth_bot.agent.GROWTH_PLANS_DIR', temp_growth_plans_dir)
    
    # Create a sample message
    company_id = str(uuid.uuid4())
    message = {
        "company_id": company_id,
        "company_name": "TestCompany Inc.",
        "company_email": "growth@testcompany.example.com",
        "business_type": "saas",
        "growth_goal": "increase MRR by 30%",
        "current_metrics": {
            "mrr": 100000,
            "customers": 50,
            "avg_deal_size": 2000,
            "cac": 1500,
            "churn_rate": 2
        },
        "target_metrics": {
            "mrr": 130000,
            "customers": 65,
            "churn_rate": 1.5
        },
        "timeframe": "3 months",
        "focus_area": "acquisition"
    }
    
    # Process the message
    await growth_bot.process_message(message)
    
    # Check that a file was created in the temp directory
    files = os.listdir(temp_growth_plans_dir)
    assert len(files) > 0, "No AB test plan file was created"
    
    # Get the latest file
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(temp_growth_plans_dir, f)))
    file_path = os.path.join(temp_growth_plans_dir, latest_file)
    
    # Validate that it's a JSON file
    with open(file_path, 'r') as f:
        plan = json.load(f)
    
    # Verify the plan contains all required fields
    assert "company_id" in plan
    assert "company_name" in plan
    assert "test_id" in plan
    assert "test_name" in plan
    assert "hypothesis" in plan
    assert "primary_metric" in plan
    assert "variations" in plan
    assert len(plan["variations"]) >= 2  # At least control + one variation
    
    # Verify that company data was correctly passed through
    assert plan["company_id"] == company_id
    assert plan["company_name"] == "TestCompany Inc."
    assert plan["business_type"] == "saas"
    assert plan["focus_area"] == "acquisition"


@pytest.mark.asyncio
async def test_email_notification(growth_bot, temp_growth_plans_dir, monkeypatch):
    """Test that the GrowthBot sends an email notification."""
    # Patch the GROWTH_PLANS_DIR to use our temporary directory
    monkeypatch.setattr('services.value_add_agents.growth_bot.agent.GROWTH_PLANS_DIR', temp_growth_plans_dir)
    
    # Mock the send_email method
    email_sent = False
    email_to = None
    email_subject = None
    
    async def mock_send_email(self, to, subject, body, cc=None):
        nonlocal email_sent, email_to, email_subject
        email_sent = True
        email_to = to
        email_subject = subject
        return True
    
    monkeypatch.setattr('services.value_add_agents.base_agent.BaseAgent.send_email', mock_send_email)
    
    # Create a sample message
    message = {
        "company_id": str(uuid.uuid4()),
        "company_name": "TestCompany Inc.",
        "company_email": "growth@testcompany.example.com",
        "business_type": "saas",
        "growth_goal": "increase MRR by 30%",
        "timeframe": "3 months",
        "focus_area": "acquisition"
    }
    
    # Process the message
    await growth_bot.process_message(message)
    
    # Verify that an email was sent
    assert email_sent, "No email was sent"
    assert email_to == "growth@testcompany.example.com"
    assert "Growth Strategy" in email_subject