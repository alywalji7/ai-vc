from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .base import BaseEntity, EntityType, SourceType


class Company(BaseEntity):
    """Company entity model"""
    
    def __init__(self, **data):
        data["type"] = EntityType.COMPANY
        super().__init__(**data)