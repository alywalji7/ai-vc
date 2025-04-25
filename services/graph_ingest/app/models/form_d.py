"""
SEC Form D entity models for the knowledge graph.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import Field

from .base import BaseEntity, BaseRelationship, EntityType, SourceType, RelationshipType


class FormDFiling(BaseEntity):
    """
    Represents a Form D filing with the SEC, indicating a company's exempt offering of securities.
    """
    type: EntityType = EntityType.RAISE_EVENT
    source: SourceType = SourceType.SEC_FORM_D
    
    # Core properties
    company_name: str
    filing_date: datetime
    amount_raised: float
    offering_amount: float
    filing_type: str  # "NEW" or "AMENDED"
    
    # Optional properties
    investor_count: Optional[int] = None
    min_investment: Optional[float] = None
    issuer_size: Optional[str] = None
    industry_group: Optional[str] = None
    issuer_city: Optional[str] = None
    issuer_state: Optional[str] = None
    cik: Optional[str] = None  # Central Index Key
    related_persons: List[Dict[str, str]] = []
    
    class Config:
        """Model configuration."""
        json_schema_extra = {
            "example": {
                "id": "form_d_12345",
                "source_id": "0001840624-24-000001",
                "name": "Series A Financing - Acme Inc",
                "company_name": "Acme Inc",
                "filing_date": "2024-04-01T00:00:00",
                "amount_raised": 5000000.0,
                "offering_amount": 8000000.0,
                "filing_type": "NEW",
                "investor_count": 12,
                "min_investment": 250000.0,
                "issuer_size": "Declining to Disclose",
                "industry_group": "Technology",
                "issuer_city": "San Francisco",
                "issuer_state": "CA",
                "cik": "0001234567",
                "related_persons": [
                    {
                        "name": "Jane Smith",
                        "title": "CEO"
                    },
                    {
                        "name": "John Doe",
                        "title": "CFO"
                    }
                ]
            }
        }


class FormDRelationship(BaseRelationship):
    """
    Represents a relationship between a company and a Form D filing event (fundraising).
    """
    type: RelationshipType = RelationshipType.RAISED
    source: SourceType = SourceType.SEC_FORM_D
    
    # Metadata
    filing_date: datetime
    amount_raised: float
    
    class Config:
        """Model configuration."""
        json_schema_extra = {
            "example": {
                "id": "form_d_rel_12345",
                "from_entity_id": "company_123",
                "to_entity_id": "form_d_12345",
                "filing_date": "2024-04-01T00:00:00",
                "amount_raised": 5000000.0,
                "properties": {
                    "offering_amount": 8000000.0,
                    "funding_round": "Series A"
                }
            }
        }