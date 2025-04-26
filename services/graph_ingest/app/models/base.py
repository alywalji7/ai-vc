from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    GITHUB = "github"
    CRUNCHBASE = "crunchbase"
    PATENTSVIEW = "patentsview"
    SEC_EDGAR = "sec_edgar"
    TWITTER_X = "twitter_x"
    LINKEDIN = "linkedin"
    PRODUCT_HUNT = "product_hunt"
    SEC_FORM_D = "sec_form_d"
    ANGELLIST = "angellist"
    YC_LAUNCH = "yc_launch"


class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    REPOSITORY = "repository"
    COMMIT = "commit"
    COMPANY = "company"
    INVESTOR = "investor"
    FOUNDER = "founder"
    FUNDING_ROUND = "funding_round"
    PATENT = "patent"
    FILING = "filing"
    LAUNCH_EVENT = "launch_event"
    RAISE_EVENT = "raise_event"
    ANGEL_DEAL = "angel_deal"
    YC_COMPANY = "yc_company"


class RelationshipType(str, Enum):
    WORKS_FOR = "works_for"
    CONTRIBUTES_TO = "contributes_to"
    OWNS = "owns"
    FUNDED_BY = "funded_by"
    FOUNDED = "founded"
    PARTICIPATED_IN = "participated_in"
    AUTHORED = "authored"
    FILED = "filed"
    HOLDS = "holds"
    LAUNCHED = "launched"        # Company launched a product
    RAISED = "raised"            # Company raised funding


class BaseEntity(BaseModel):
    """Base class for all entities in the knowledge graph"""
    id: str
    type: EntityType
    source: SourceType
    source_id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    properties: Dict[str, Any] = Field(default_factory=dict)


class BaseRelationship(BaseModel):
    """Base class for all relationships in the knowledge graph"""
    id: str
    type: RelationshipType
    source: SourceType
    from_entity_id: str
    to_entity_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    properties: Dict[str, Any] = Field(default_factory=dict)