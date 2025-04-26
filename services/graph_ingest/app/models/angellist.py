"""
AngelList entity models for the knowledge graph.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import Field

from .base import BaseEntity, BaseRelationship, EntityType, SourceType, RelationshipType

class AngelDeal(BaseEntity):
    """
    AngelList syndicate deal entity.
    """
    type: EntityType = EntityType.ANGEL_DEAL
    source: SourceType = SourceType.ANGELLIST
    company_name: str
    commitment_usd: Optional[float] = None
    deal_date: Optional[datetime] = None
    lead_investor: Optional[str] = None
    round_type: Optional[str] = None
    sector: Optional[str] = None
    description: Optional[str] = None
    valuation_usd: Optional[float] = None
    min_investment: Optional[float] = None
    target_raise_usd: Optional[float] = None
    location: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "id": "angellist:deal:123",
                "source_id": "123",
                "name": "Amazing Startup Seed Round",
                "company_name": "Amazing Startup Inc",
                "commitment_usd": 250000.0,
                "deal_date": "2025-04-15T00:00:00Z",
                "lead_investor": "Top Angel VC",
                "round_type": "Seed",
                "sector": "AI & Machine Learning",
                "description": "Building the next generation of AI tools for startups",
                "valuation_usd": 10000000.0,
                "min_investment": 1000.0,
                "target_raise_usd": 1500000.0,
                "location": "San Francisco, CA",
                "properties": {
                    "deal_link": "https://angel.co/deal/123",
                    "status": "active"
                }
            }
        }


class AngelDealRelationship(BaseRelationship):
    """
    Relationship between an investor and an AngelList deal.
    """
    type: RelationshipType = RelationshipType.PARTICIPATED_IN
    source: SourceType = SourceType.ANGELLIST
    commitment_amount: Optional[float] = None
    commitment_date: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "angellist:rel:123",
                "from_entity_id": "investor:123",  # Investor entity ID
                "to_entity_id": "angellist:deal:123",  # Deal entity ID
                "commitment_amount": 50000.0,
                "commitment_date": "2025-04-15T00:00:00Z",
                "properties": {
                    "status": "confirmed"
                }
            }
        }