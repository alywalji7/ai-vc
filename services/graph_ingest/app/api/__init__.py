from .app import create_app
from .router import router
from .models import (
    SourceType, IngestRequest, IngestResponse,
    EntityResponse, RelationshipResponse
)

# Create the FastAPI application instance
api = create_app()

__all__ = [
    "create_app", "router", "api",
    "SourceType", "IngestRequest", "IngestResponse",
    "EntityResponse", "RelationshipResponse"
]