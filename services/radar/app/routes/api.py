"""
API routes for the Deal-Flow Radar service.
"""
import logging
import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Shortlist, ShortlistItem, ModelMetadata
from ..service import get_daily_shortlist, handle_mock_data, load_model, enqueue_dataroom_task

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(tags=["radar"])

# Load model on startup
model = load_model()
model_metadata = None

try:
    model_metadata_path = "services/radar/models/model_metadata.json"
    with open(model_metadata_path, "r") as f:
        model_metadata = json.load(f)
except Exception as e:
    logger.warning(f"Could not load model metadata: {str(e)}")
    model_metadata = {
        "features": [],
        "train_date": datetime.now().strftime("%Y-%m-%d"),
        "model_version": "0.1.0",
    }


@router.get("/radar/daily_shortlist", response_model=List[ShortlistItem])
async def get_shortlist(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of companies to return"),
    db: Session = Depends(get_db),
):
    """
    Get the daily shortlist of investment opportunities.
    
    Args:
        limit: Maximum number of companies to return
        db: Database session
        
    Returns:
        List of shortlist items with company_id and clos (classifier score 0-1)
    """
    try:
        logger.info(f"Generating shortlist with limit {limit}")
        
        try:
            # Try to get shortlist from the database
            shortlist_items = get_daily_shortlist(db, limit=limit)
            logger.info(f"Generated shortlist with {len(shortlist_items)} items")
            
            # Trigger data room builds for high-scoring companies
            for item in shortlist_items:
                if item.clos >= 0.7:  # Green-light threshold
                    logger.info(f"Green-lighting company {item.company_id} with score {item.clos:.2f}")
                    success = enqueue_dataroom_task(item.company_id, item.clos)
                    if success:
                        logger.info(f"Data room task enqueued for company {item.company_id}")
                    else:
                        logger.warning(f"Failed to enqueue data room task for company {item.company_id}")
                
            return shortlist_items
        except Exception as db_error:
            # If database access fails, use mock data
            logger.warning(f"Database access failed: {str(db_error)}. Using mock data.")
            return handle_mock_data(limit=limit)
    
    except Exception as e:
        logger.error(f"Error generating shortlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating shortlist: {str(e)}")


@router.get("/radar/shortlist_with_metadata", response_model=Shortlist)
async def get_shortlist_with_metadata(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of companies to return"),
    db: Session = Depends(get_db),
):
    """
    Get the daily shortlist of investment opportunities with metadata.
    
    Args:
        limit: Maximum number of companies to return
        db: Database session
        
    Returns:
        Shortlist object with items and metadata
    """
    try:
        shortlist_items = await get_shortlist(limit=limit, db=db)
        
        return Shortlist(
            items=shortlist_items,
            analysis_date=datetime.now(),
            model_version=model_metadata.get("model_version", "0.1.0"),
        )
    
    except Exception as e:
        logger.error(f"Error generating shortlist with metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating shortlist: {str(e)}")


@router.get("/radar/model_metadata", response_model=ModelMetadata)
async def get_model_metadata():
    """
    Get metadata about the model used for predictions.
    
    Returns:
        Model metadata
    """
    global model_metadata
    
    if not model_metadata:
        raise HTTPException(status_code=404, detail="Model metadata not found")
    
    return ModelMetadata(**model_metadata)