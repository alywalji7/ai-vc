"""
Due Diligence API endpoints.

This module provides API endpoints for running due diligence checks on companies
and retrieving results.
"""

import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db import get_db
from app.models import DueDiligenceResult
from app.due_diligence import FinancialDD, TechDD

router = APIRouter(prefix="/dd", tags=["due_diligence"])
logger = logging.getLogger(__name__)

# Initialize due diligence modules
MODULES = {
    "financial": FinancialDD(),
    "tech": TechDD()
}


@router.post("/launch", response_model=Dict[str, Any])
async def launch_due_diligence(
    company_id: str,
    modules: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Launch due diligence checks for a company.
    
    Args:
        company_id: ID of the company to analyze
        modules: List of due diligence modules to run (default: all modules)
        db: Database session
        
    Returns:
        Dictionary with due diligence results
    """
    logger.info(f"Launching due diligence for company {company_id}")
    
    # If modules not specified, run all available modules
    if not modules:
        modules = list(MODULES.keys())
    
    # Validate requested modules
    invalid_modules = [m for m in modules if m not in MODULES]
    if invalid_modules:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid modules: {', '.join(invalid_modules)}. Available modules: {', '.join(MODULES.keys())}"
        )
    
    # Run due diligence modules and collect results
    results = {}
    
    for module_name in modules:
        module = MODULES[module_name]
        
        try:
            # Run the module
            verdict = await module.run(company_id)
            
            # Store the verdict in the database
            dd_result = DueDiligenceResult(
                company_id=company_id,
                module_name=module_name,
                verdict=verdict.to_dict()
            )
            
            db.add(dd_result)
            db.commit()
            
            # Add to results
            results[module_name] = verdict.to_dict()
            
        except Exception as e:
            logger.error(f"Error running {module_name} due diligence for {company_id}: {str(e)}")
            results[module_name] = {
                "error": str(e),
                "status": "error"
            }
    
    return {
        "company_id": company_id,
        "modules_run": modules,
        "results": results
    }


@router.get("/results/{company_id}", response_model=Dict[str, Any])
async def get_due_diligence_results(
    company_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get due diligence results for a company.
    
    Args:
        company_id: ID of the company
        db: Database session
        
    Returns:
        Dictionary with due diligence results
    """
    results = db.query(DueDiligenceResult).filter(
        DueDiligenceResult.company_id == company_id
    ).order_by(desc(DueDiligenceResult.created_at)).all()
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No due diligence results found for company {company_id}"
        )
    
    # Group results by module
    grouped_results = {}
    
    for result in results:
        module_name = result.module_name
        
        # Only keep the latest result for each module
        if module_name not in grouped_results:
            grouped_results[module_name] = result.verdict
    
    return {
        "company_id": company_id,
        "results": grouped_results
    }


@router.get("/modules", response_model=Dict[str, List[str]])
async def get_available_modules() -> Dict[str, List[str]]:
    """
    Get a list of available due diligence modules.
    
    Returns:
        Dictionary with list of module names
    """
    return {
        "modules": list(MODULES.keys())
    }