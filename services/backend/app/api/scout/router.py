"""
Router for the scout API endpoints.
"""

import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.scout.models import ScoutedCompanyRequest, ScoutedCompanyResponse
from app.db import get_db

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/scout",
    tags=["scout"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Not authenticated"},
    },
)


@router.post("", response_model=ScoutedCompanyResponse)
async def scout_company(
    request: ScoutedCompanyRequest,
    db: Session = Depends(get_db)
):
    """
    Save a company scouted through the Chrome extension.
    
    This endpoint creates a new scouted company entity in the knowledge graph.
    """
    try:
        # In a real implementation with authentication, we would get the user from the request
        # For now, we'll use a mock user ID for demonstration
        user_id = "demo-user"
        
        # Prepare the entity data
        company_data = {
            "url": request.url,
            "name": request.title,
            "scout_notes": request.notes or "",
            "scouted_at": datetime.utcnow().isoformat(),
            "scouted_by": user_id,
            "status": "new"
        }

        # Call the graph ingest service to create the entity
        # This is a simplified version; in a real implementation, you would
        # call the graph ingest service API to create the entity
        company_id = str(uuid.uuid4())
        
        # Generate a sample referral code
        referral_code = f"SC-{uuid.uuid4().hex[:6]}"
            
        # TODO: Send email notification to the scout with their referral code
        
        return ScoutedCompanyResponse(
            success=True,
            message="Company saved successfully",
            company_id=company_id,
            referral_code=referral_code
        )
        
    except Exception as e:
        logger.error(f"Error saving scouted company: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving company: {str(e)}"
        )