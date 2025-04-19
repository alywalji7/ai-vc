"""
API endpoints for the Investment Committee Simulator.

This module provides the FastAPI endpoints for interacting with the
IC simulator, including the main endpoint for running the two-stage
analysis process.
"""

import logging
from typing import Dict, Any, Optional
import json

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

from app.models.schemas import CompanyData, ICResult
from app.core.rule_filter import apply_rule_filter
from app.core.llm_analysis import perform_tot_analysis
from app.utils.storage import MinioLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Initialize Minio logger
minio_logger = MinioLogger()


class SimulationRequest(BaseModel):
    """Request model for investment committee simulation."""
    company_data: Optional[CompanyData] = None
    company_id: Optional[str] = None


@router.post("/ic_sim")
async def run_ic_simulation(
    company_id: str = Query(None, description="ID of the company to analyze (if not providing full data)"),
    request_data: Optional[SimulationRequest] = None
) -> Dict[str, Any]:
    """
    Run the two-stage investment committee simulation.
    
    This endpoint applies the rule filter and, if passed, runs the LLM-based
    Tree-of-Thought analysis to generate an investment decision.
    
    Args:
        company_id: ID of the company to analyze (if not providing full data)
        request_data: Detailed company data if not fetching by ID
        
    Returns:
        Result of the investment committee analysis
    """
    logger.info(f"Starting IC simulation for company_id: {company_id}")
    
    # Resolve company data - in a real system, we'd fetch from DB if only ID provided
    company_data = None
    
    if request_data and request_data.company_data:
        company_data = request_data.company_data
        logger.info(f"Using provided company data for {company_data.name}")
    elif company_id:
        # For this example, we'll use a test company when only ID is provided
        # In a real system, this would be a database lookup
        logger.info(f"Creating test company data for ID: {company_id}")
        company_data = _get_test_company_data(company_id)
    else:
        raise HTTPException(status_code=400, detail="Either company_id or company_data must be provided")
    
    # Stage 1: Apply rule filter
    logger.info(f"Applying rule filter for company: {company_data.name}")
    rule_result = apply_rule_filter(company_data)
    
    # If rule filter failed, return early with the reasons
    if not rule_result.passed:
        logger.info(f"Company {company_data.name} failed rule filter: {rule_result.reasons}")
        return {
            "company_id": company_data.id,
            "company_name": company_data.name,
            "passed_rule_filter": False,
            "reasons": rule_result.reasons,
            "result": None
        }
    
    # Stage 2: Run LLM Tree-of-Thought analysis
    logger.info(f"Company {company_data.name} passed rule filter, running LLM analysis")
    analysis_result = await perform_tot_analysis(company_data)
    
    # Log the complete analysis to Minio for audit
    analysis_data = {
        "company_data": company_data.model_dump(),
        "rule_filter_result": rule_result.model_dump(),
        "llm_analysis_result": analysis_result.model_dump()
    }
    
    # Log to Minio (or console if Minio unavailable)
    log_path = minio_logger.log_analysis(company_data.id, analysis_data)
    
    # Prepare response
    response = {
        "company_id": company_data.id,
        "company_name": company_data.name,
        "passed_rule_filter": True,
        "rule_filter_info": rule_result.reasons,
        "result": analysis_result,
        "analysis_log_path": log_path
    }
    
    logger.info(f"Completed IC simulation for {company_data.name} with decision: {analysis_result.decision}")
    return response


def _get_test_company_data(company_id: str) -> CompanyData:
    """
    Create test company data for the given ID.
    
    This is a simple function to create sample company data for testing.
    In a real system, this would fetch from a database.
    
    Args:
        company_id: ID of the company
        
    Returns:
        Test company data
    """
    # Create a plausible test company that should pass rule filters
    return CompanyData(
        id=company_id,
        name=f"TechCorp {company_id}",
        sector="ai",
        round="series_a",
        region="north_america",
        raise_amount=10_000_000,
        valuation=50_000_000,
        revenue=2_000_000,
        growth_rate=0.8,
        burn_rate=300_000,
        runway=12,
        team_size=25,
        founding_year=2022,
        founder_background="PhD in AI from Stanford, previously founded a successful fintech startup",
        market_size=5_000_000_000,
        competitors=["OpenAI", "Anthropic", "Google"],
        description="TechCorp is developing advanced AI models for enterprise data analysis, focusing on financial analytics and risk assessment.",
        business_model="SaaS subscription with tiered pricing based on data volume and features.",
        key_metrics={
            "arr": 2_000_000,
            "cac": 15000,
            "ltv": 120000,
            "monthly_active_users": 150,
            "nps": 65
        }
    )