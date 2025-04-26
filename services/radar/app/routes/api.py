"""
API routes for the Deal-Flow Radar service.
"""
import logging
import json
import os
import sys
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

# Add libs to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "libs"))

# Import cost guardrail components
try:
    from cost_guardrails.rate_limiter import rate_limit
    from cost_guardrails.openai_metering import track_openai_usage
    RATE_LIMITING_ENABLED = True
except ImportError:
    # Fallback if imports fail
    logging.warning("Cost guardrails module not found. Rate limiting disabled.")
    RATE_LIMITING_ENABLED = False
    
    # Create dummy decorator
    def rate_limit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def track_openai_usage(*args, **kwargs):
        return 0

from ..database import get_db, LPFeedback, FeedbackType, ModelVersion, Company
from ..models import (
    Shortlist, ShortlistItem, ModelMetadata, 
    FeedbackRequest, FeedbackResponse, FeedbackStats,
    CompanyCreate
)
from ..service import get_daily_shortlist, handle_mock_data, load_model, enqueue_dataroom_task

# Environment variables
DEFAULT_REQUESTS_PER_MINUTE = int(os.environ.get("RADAR_REQUESTS_PER_MINUTE", "10"))  # Lower limit for radar
DEFAULT_TOKEN_QUOTA = int(os.environ.get("RADAR_TOKEN_QUOTA", "50000"))  # 50K tokens per user per day

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
@rate_limit(
    requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE,
    token_quota=DEFAULT_TOKEN_QUOTA
)
async def get_shortlist(
    request: Request,
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
@rate_limit(
    requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE,
    token_quota=DEFAULT_TOKEN_QUOTA
)
async def get_shortlist_with_metadata(
    request: Request,
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
        # Need to pass the request to the get_shortlist function
        shortlist_items = await get_shortlist(request=request, limit=limit, db=db)
        
        return Shortlist(
            items=shortlist_items,
            analysis_date=datetime.now(),
            model_version=model_metadata.get("model_version", "0.1.0"),
        )
    
    except Exception as e:
        logger.error(f"Error generating shortlist with metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating shortlist: {str(e)}")


@router.get("/radar/model_metadata", response_model=ModelMetadata)
@rate_limit(
    requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE * 2  # Allow more requests for metadata
)
async def get_model_metadata(request: Request):
    """
    Get metadata about the model used for predictions.
    
    Returns:
        Model metadata
    """
    global model_metadata
    
    if not model_metadata:
        raise HTTPException(status_code=404, detail="Model metadata not found")
    
    return ModelMetadata(**model_metadata)


@router.post("/companies", status_code=status.HTTP_201_CREATED)
async def create_test_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a test company for development purposes.
    
    Args:
        company: Company data
        db: Database session
        
    Returns:
        Created company data
    """
    try:
        # Check if company already exists
        existing = db.query(Company).filter(Company.id == company.id).first()
        if existing:
            return existing
        
        # Create new company
        db_company = Company(
            id=company.id,
            name=company.name,
            founding_date=company.founding_date,
            github_stars=company.github_stars,
            commit_velocity=company.commit_velocity,
            investor_count=company.investor_count,
            founder_exit_count=company.founder_exit_count,
            social_traction=company.social_traction,
            funding_amount=company.funding_amount
        )
        
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        
        logger.info(f"Created test company {company.id}: {company.name}")
        
        return db_company
    except Exception as e:
        logger.error(f"Error creating test company: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating test company: {str(e)}"
        )


@router.post("/feedback/thumb", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
@rate_limit(
    requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE * 3  # Allow more feedback submissions
)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Submit LP feedback (thumbs up/down) for a company.
    
    Args:
        request: Feedback request with LP ID, company ID, and feedback type
        db: Database session
        
    Returns:
        Created feedback record
    """
    try:
        # Validate feedback_type (should be 'up' or 'down')
        try:
            # Ensure feedback_type is lowercase to avoid case sensitivity issues
            feedback_type_normalized = request.feedback_type.lower()
            feedback_type = FeedbackType(feedback_type_normalized)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid feedback type. Valid values are: {[t.value for t in FeedbackType]}"
            )
        
        # Create feedback record
        feedback = LPFeedback(
            lp_id=request.lp_id,
            company_id=request.company_id,
            feedback_type=feedback_type
        )
        
        # Save to database
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        logger.info(f"LP {request.lp_id} submitted {request.feedback_type} feedback for company {request.company_id}")
        
        # Format response
        return FeedbackResponse(
            id=feedback.id,
            lp_id=feedback.lp_id,
            company_id=feedback.company_id,
            feedback_type=feedback.feedback_type.value,
            created_at=feedback.created_at
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )


@router.get("/feedback/stats", response_model=FeedbackStats)
@rate_limit(
    requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE * 2
)
async def get_feedback_stats(
    db: Session = Depends(get_db)
):
    """
    Get statistics about LP feedback and its usage in model training.
    
    Args:
        db: Database session
        
    Returns:
        Feedback statistics
    """
    try:
        # Get feedback counts
        total_count = db.query(LPFeedback).count()
        used_count = db.query(LPFeedback).filter(LPFeedback.used_in_training == True).count()
        
        # Get latest model
        latest_model = db.query(ModelVersion).filter(
            ModelVersion.in_production == True
        ).first()
        
        if not latest_model:
            # No model in production yet
            return FeedbackStats(
                total_feedback_count=total_count,
                used_in_training_count=used_count,
                feedback_weight_percent=0.0,
                latest_model_version="none",
                latest_model_auc=0.0
            )
        
        # Calculate feedback weight percentage
        feedback_weight_percent = 0.0
        improvement_from_feedback = None
        
        # Parse metrics if available
        if latest_model.metrics:
            try:
                metrics = json.loads(latest_model.metrics)
                if "feedback_weight_percent" in metrics:
                    feedback_weight_percent = metrics["feedback_weight_percent"]
                if "feedback_improvement" in metrics:
                    improvement_from_feedback = metrics["feedback_improvement"]
            except json.JSONDecodeError:
                pass
        
        return FeedbackStats(
            total_feedback_count=total_count,
            used_in_training_count=used_count,
            feedback_weight_percent=feedback_weight_percent,
            latest_model_version=latest_model.model_version,
            latest_model_auc=latest_model.auc_score,
            improvement_from_feedback=improvement_from_feedback
        )
        
    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting feedback stats: {str(e)}"
        )