"""
Schema definitions for the Term Sheet Generator & Negotiator Bot.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Available NVCA document types"""
    SERIES_SEED_SAFE = "series_seed_safe"
    SERIES_A_TERM_SHEET = "series_a_term_sheet"
    SERIES_A_SPA = "series_a_spa"  # Stock Purchase Agreement
    SERIES_A_IRA = "series_a_ira"  # Investors' Rights Agreement
    CONVERTIBLE_NOTE = "convertible_note"


class SAFEDetails(BaseModel):
    """Model for SAFE document details"""
    investment_amount: float = Field(..., description="Investment amount in USD")
    valuation_cap: float = Field(..., description="Valuation cap in USD")
    discount_rate: float = Field(..., description="Discount rate as a percentage (e.g., 20 for 20%)")
    company_name: str = Field(..., description="Company name")
    investor_name: str = Field(..., description="Investor name")
    effective_date: str = Field(..., description="Effective date (YYYY-MM-DD)")
    company_signatory_name: str = Field(..., description="Name of company signatory")
    company_signatory_title: str = Field(..., description="Title of company signatory")
    investor_signatory_name: str = Field(..., description="Name of investor signatory")
    investor_signatory_title: str = Field(..., description="Title of investor signatory")


class TermSheetRequest(BaseModel):
    """Request model for term sheet generation"""
    document_type: DocumentType
    safe_details: Optional[SAFEDetails] = None
    # Add other document type details as needed


class NegotiationMessage(BaseModel):
    """Model for negotiation chat messages"""
    role: str = Field(..., description="Role of the message sender (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = None


class NegotiationSession(BaseModel):
    """Model for a negotiation session"""
    session_id: str
    document_type: DocumentType
    company_id: str
    investor_id: str
    messages: List[NegotiationMessage] = []
    original_terms: Dict[str, Any]
    current_terms: Dict[str, Any]
    status: str = "active"  # active, escalated, completed
    
    
class CounterOffer(BaseModel):
    """Model for a counter offer in negotiation"""
    term: str = Field(..., description="The term being negotiated")
    original_value: Any = Field(..., description="Original value of the term")
    proposed_value: Any = Field(..., description="Proposed new value")
    deviation_percentage: float = Field(..., description="Percentage deviation from original value")
    is_extreme: bool = Field(..., description="Whether this counter offer exceeds deviation threshold")


class NegotiationAnalysis(BaseModel):
    """Model for negotiation analysis results"""
    counter_offers: List[CounterOffer]
    requires_escalation: bool
    escalation_reason: Optional[str] = None