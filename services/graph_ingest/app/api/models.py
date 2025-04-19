from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    GITHUB = "github"
    CRUNCHBASE = "crunchbase"
    PATENTSVIEW = "patentsview"
    SEC_EDGAR = "sec_edgar"
    TWITTER_X = "twitter_x"
    LINKEDIN = "linkedin"


class IngestRequestBase(BaseModel):
    source: SourceType
    


class GitHubIngestRequest(IngestRequestBase):
    source: SourceType = SourceType.GITHUB
    org: Optional[str] = None
    user: Optional[str] = None
    repo: Optional[str] = None


class CrunchbaseIngestRequest(IngestRequestBase):
    source: SourceType = SourceType.CRUNCHBASE
    company: Optional[str] = None
    person: Optional[str] = None


class IngestRequest(BaseModel):
    source: SourceType = Field(..., description="Data source type")
    
    # GitHub-specific
    org: Optional[str] = Field(None, description="GitHub organization name")
    user: Optional[str] = Field(None, description="GitHub username")
    repo: Optional[str] = Field(None, description="GitHub repository in owner/repo format")
    
    # Crunchbase-specific
    company: Optional[str] = Field(None, description="Crunchbase company permalink")
    person: Optional[str] = Field(None, description="Crunchbase person permalink")


class IngestResponse(BaseModel):
    status: str
    message: Optional[str] = None
    source: SourceType
    entities_count: int = 0
    relationships_count: int = 0
    results: Dict[str, Any] = Field(default_factory=dict)


class EntityResponse(BaseModel):
    id: str
    type: str
    source: str
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class RelationshipResponse(BaseModel):
    id: str
    type: str
    source: str
    from_entity_id: str
    to_entity_id: str
    properties: Dict[str, Any] = Field(default_factory=dict)