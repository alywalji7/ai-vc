"""
Data models for the Investment Committee Simulator.
"""

from enum import Enum
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field


class Sector(str, Enum):
    """Valid investment sectors."""
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    ENTERPRISE = "enterprise"
    CONSUMER = "consumer"
    DEEPTECH = "deeptech"
    AI = "ai"
    BLOCKCHAIN = "blockchain"
    CLEANTECH = "cleantech"
    EDTECH = "edtech"
    OTHER = "other"


class Region(str, Enum):
    """Valid investment regions."""
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA = "asia"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    MIDDLE_EAST = "middle_east"
    OCEANIA = "oceania"


class Round(str, Enum):
    """Valid investment rounds."""
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D_PLUS = "series_d_plus"
    PRE_IPO = "pre_ipo"


class CompanyData(BaseModel):
    """Company data model for investment committee analysis."""
    id: str
    name: str
    sector: Sector
    round: Round
    region: Region
    raise_amount: float = Field(..., description="Requested raise amount in USD")
    valuation: float = Field(..., description="Pre-money valuation in USD")
    
    # Company metrics
    revenue: Optional[float] = Field(None, description="Annual revenue in USD")
    growth_rate: Optional[float] = Field(None, description="YoY growth rate (0-1)")
    burn_rate: Optional[float] = Field(None, description="Monthly burn rate in USD")
    runway: Optional[int] = Field(None, description="Remaining runway in months")
    
    # Team information
    team_size: Optional[int] = None
    founding_year: Optional[int] = None
    founder_background: Optional[str] = None
    
    # Market information
    market_size: Optional[float] = Field(None, description="TAM in USD")
    competitors: Optional[List[str]] = None
    
    # Additional context
    description: Optional[str] = None
    business_model: Optional[str] = None
    key_metrics: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True


class ICDecision(str, Enum):
    """Investment committee decision types."""
    APPROVE = "approve"
    REJECT = "reject"
    REVISE = "revise"


class TOTStep(BaseModel):
    """A single step in the Tree of Thought reasoning process."""
    thought: str
    consideration: str


class ICResult(BaseModel):
    """Result of investment committee analysis."""
    company_id: str
    company_name: str
    decision: ICDecision
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    roi_expectation: float = Field(..., description="Expected ROI multiple")
    risk_assessment: float = Field(..., ge=0.0, le=1.0, description="Risk score (0-1)")
    analysis_summary: str
    reasoning_chain: List[TOTStep]
    rationale: str
    
    class Config:
        use_enum_values = True


class RuleFilterResult(BaseModel):
    """Result of the initial rule-based filtering."""
    passed: bool
    reasons: List[str]