"""
Pydantic models for API requests and responses.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

from .database import FeedbackType


class CompanyBase(BaseModel):
    """Base model for company data."""
    name: str
    founding_date: Optional[datetime] = None
    github_stars: int = 0
    commit_velocity: float = 0
    investor_count: int = 0
    founder_exit_count: int = 0
    social_traction: int = 0
    funding_amount: float = 0


class CompanyCreate(CompanyBase):
    """Model for creating a new company."""
    id: str


class Company(CompanyBase):
    """Model for a company with additional fields."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True  # For SQLAlchemy models


class InvestorBase(BaseModel):
    """Base model for investor data."""
    name: str
    type: Optional[str] = None
    investment_count: int = 0


class InvestorCreate(InvestorBase):
    """Model for creating a new investor."""
    id: str


class Investor(InvestorBase):
    """Model for an investor with additional fields."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class FounderBase(BaseModel):
    """Base model for founder data."""
    name: str
    exit_count: int = 0


class FounderCreate(FounderBase):
    """Model for creating a new founder."""
    id: str


class Founder(FounderBase):
    """Model for a founder with additional fields."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class InvestmentOpportunityBase(BaseModel):
    """Base model for investment opportunity data."""
    company_id: str
    score: float = Field(..., ge=0, le=1)
    features_used: Optional[str] = None


class InvestmentOpportunityCreate(InvestmentOpportunityBase):
    """Model for creating a new investment opportunity."""
    pass


class InvestmentOpportunity(InvestmentOpportunityBase):
    """Model for an investment opportunity with additional fields."""
    id: int
    analysis_date: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class ShortlistItem(BaseModel):
    """Model for an item in the daily shortlist."""
    company_id: str
    name: str
    clos: float = Field(..., ge=0, le=1, description="Classifier score (0-1)")
    

class Shortlist(BaseModel):
    """Model for the daily shortlist."""
    items: List[ShortlistItem]
    analysis_date: datetime
    model_version: str


class FeatureVector(BaseModel):
    """Model for a feature vector used for prediction."""
    company_age: float
    github_stars: int
    commit_velocity: float
    investor_count: int
    founder_exit_count: int
    social_traction: int
    funding_amount: float
    stars_to_age_ratio: float
    funding_per_investor: float
    social_engagement_ratio: float


class ModelMetadata(BaseModel):
    """Model for model metadata."""
    features: List[str]
    train_date: str
    auc_score: float
    cv_auc_mean: float
    cv_auc_std: float
    top_features: List[str]


class FeedbackRequest(BaseModel):
    """Request model for LP feedback."""
    lp_id: str
    company_id: str
    feedback_type: str = Field(..., description="Feedback type: 'up' or 'down'")

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "lp_id": "lp-123",
                "company_id": "company-456",
                "feedback_type": "up"
            }
        }


class FeedbackResponse(BaseModel):
    """Response model for LP feedback."""
    id: int
    lp_id: str
    company_id: str
    feedback_type: str
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class FeedbackStats(BaseModel):
    """Statistics about LP feedback usage in model training."""
    total_feedback_count: int
    used_in_training_count: int 
    feedback_weight_percent: float
    latest_model_version: str
    latest_model_auc: float
    improvement_from_feedback: Optional[float] = None