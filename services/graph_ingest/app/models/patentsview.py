from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .base import BaseEntity, BaseRelationship, EntityType, RelationshipType, SourceType


class Patent(BaseEntity):
    """Patent entity model from PatentsView"""
    
    def __init__(self, **data):
        data["source"] = SourceType.PATENTSVIEW
        data["type"] = EntityType.PATENT
        super().__init__(**data)


class CompanyHoldsPatent(BaseRelationship):
    """Relationship between a Company and a Patent it holds"""
    
    def __init__(self, **data):
        data["source"] = SourceType.PATENTSVIEW
        data["type"] = RelationshipType.HOLDS
        super().__init__(**data)