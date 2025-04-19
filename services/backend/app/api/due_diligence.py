"""
Due Diligence API routes.

This module provides endpoints for:
1. Retrieving available due diligence modules
2. Launching due diligence checks
3. Retrieving due diligence results
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
import sqlalchemy as sa

from app.db import get_db
from app.due_diligence import FinancialDD, TechDD

router = APIRouter(prefix="/dd", tags=["due_diligence"])

# Initialize the DD modules
financial_dd = FinancialDD()
tech_dd = TechDD()


@router.get("/modules")
async def get_modules() -> Dict[str, List[str]]:
    """
    Get available due diligence modules.
    
    Returns:
        Dictionary with available module names
    """
    return {
        "modules": ["financial", "tech"]
    }


@router.post("/launch")
async def launch_due_diligence(
    company_id: str = Query(..., description="ID of the company to analyze"),
    modules: List[str] = Query(["financial", "tech"], description="Due diligence modules to run")
) -> Dict[str, Any]:
    """
    Launch due diligence checks for a company.
    
    Args:
        company_id: ID of the company to analyze
        modules: List of due diligence modules to run
        
    Returns:
        Dictionary with due diligence results by module
    """
    if not company_id:
        raise HTTPException(status_code=400, detail="Company ID is required")
    
    results = {}
    
    if "financial" in modules:
        try:
            results["financial"] = await financial_dd.run(company_id)
        except Exception as e:
            results["financial"] = {
                "error": f"Financial due diligence failed: {str(e)}"
            }
    
    if "tech" in modules:
        try:
            results["tech"] = await tech_dd.run(company_id)
        except Exception as e:
            results["tech"] = {
                "error": f"Technical due diligence failed: {str(e)}"
            }
    
    return {
        "company_id": company_id,
        "results": results
    }


@router.get("/results")
async def get_due_diligence_results(
    company_id: str = Query(..., description="ID of the company"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get stored due diligence results for a company.
    
    Args:
        company_id: ID of the company
        db: Database session
        
    Returns:
        Dictionary with due diligence results
    """
    # This is a simplified version - in a real implementation, we would
    # store results in the database and retrieve them here
    
    # For demo purposes, we'll just run the due diligence again
    return await launch_due_diligence(company_id=company_id)