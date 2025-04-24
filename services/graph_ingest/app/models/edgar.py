from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .base import BaseEntity, BaseRelationship, EntityType, RelationshipType, SourceType


class EdgarFiling(BaseEntity):
    """EDGAR Filing entity model"""
    
    def __init__(self, **data):
        data["source"] = SourceType.SEC_EDGAR
        data["type"] = EntityType.FILING
        super().__init__(**data)


class CompanyFiledFiling(BaseRelationship):
    """Relationship between a Company and a Filing it filed"""
    
    def __init__(self, **data):
        data["source"] = SourceType.SEC_EDGAR
        data["type"] = RelationshipType.FILED
        super().__init__(**data)