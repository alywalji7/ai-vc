"""
Y Combinator Launch entity models for the knowledge graph.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import Field

from .base import BaseEntity, BaseRelationship, EntityType, SourceType, RelationshipType

class YCCompany(BaseEntity):
    """
    Y Combinator launched company entity.
    """
    type: EntityType = EntityType.YC_COMPANY
    source: SourceType = SourceType.YC_LAUNCH
    company_name: str
    batch: Optional[str] = None  # e.g., "S24", "W24"
    launch_date: Optional[datetime] = None
    description: Optional[str] = None
    website: Optional[str] = None
    sector: Optional[str] = None
    logo_url: Optional[str] = None
    founders: Optional[List[str]] = Field(default_factory=list)
    location: Optional[str] = None
    launch_score: Optional[float] = None  # Score based on popularity/traction
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "id": "yc:company:123",
                "source_id": "123",
                "name": "Acme AI Solutions",
                "company_name": "Acme AI Solutions",
                "batch": "W24",
                "launch_date": "2025-03-20T00:00:00Z",
                "description": "Automating document processing for legal firms",
                "website": "https://acmeai.example.com",
                "sector": "AI & Legal Tech",
                "logo_url": "https://assets.ycombinator.com/companies/acmeai.jpg",
                "founders": ["Jane Smith", "John Doe"],
                "location": "San Francisco, CA",
                "launch_score": 8.7,
                "properties": {
                    "status": "active",
                    "twitter_handle": "@acmeai"
                }
            }
        }


class YCLaunchRelationship(BaseRelationship):
    """
    Relationship between a founder and a YC company.
    """
    type: RelationshipType = RelationshipType.FOUNDED
    source: SourceType = SourceType.YC_LAUNCH
    role: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "yc:rel:123",
                "from_entity_id": "person:123",  # Person entity ID
                "to_entity_id": "yc:company:123",  # YC company entity ID
                "role": "CEO",
                "properties": {
                    "status": "active"
                }
            }
        }