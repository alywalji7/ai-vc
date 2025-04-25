"""
Product Hunt entity models for the knowledge graph.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import Field

from .base import BaseEntity, BaseRelationship, EntityType, SourceType, RelationshipType


class ProductLaunchEvent(BaseEntity):
    """
    Represents a product launch event on Product Hunt.
    """
    type: EntityType = EntityType.LAUNCH_EVENT
    source: SourceType = SourceType.PRODUCT_HUNT
    
    # Core properties
    product_name: str
    launch_date: datetime
    upvotes: int
    comments_count: int
    maker_count: int
    topics: List[str] = []
    tagline: str
    description: str
    hunter_name: str
    url: str
    
    # Optional properties
    ranking: Optional[int] = None
    featured: bool = False
    
    class Config:
        """Model configuration."""
        json_schema_extra = {
            "example": {
                "id": "ph_product_12345",
                "source_id": "12345",
                "name": "SaaS Product Launch",
                "product_name": "AI Writing Assistant",
                "launch_date": "2024-04-01T00:00:00",
                "upvotes": 743,
                "comments_count": 52,
                "maker_count": 3,
                "topics": ["AI", "Productivity", "Writing"],
                "tagline": "Write better content with AI",
                "description": "An AI writing assistant that helps you create better content faster.",
                "hunter_name": "John Doe",
                "url": "https://www.producthunt.com/posts/ai-writing-assistant",
                "ranking": 1,
                "featured": True
            }
        }


class ProductLaunchRelationship(BaseRelationship):
    """
    Represents a relationship between a company and a product launch event.
    """
    type: RelationshipType = RelationshipType.LAUNCHED
    source: SourceType = SourceType.PRODUCT_HUNT
    
    # Metadata
    launch_date: datetime
    upvotes: int = 0
    
    class Config:
        """Model configuration."""
        json_schema_extra = {
            "example": {
                "id": "ph_rel_12345",
                "from_entity_id": "company_123",
                "to_entity_id": "ph_product_12345",
                "launch_date": "2024-04-01T00:00:00",
                "upvotes": 743,
                "properties": {
                    "featured": True,
                    "daily_ranking": 1
                }
            }
        }