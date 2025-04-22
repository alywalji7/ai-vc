"""
API module for the Graph Ingest Service.

This module contains the FastAPI routes for the Graph Ingest Service.
"""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, asc
import sqlalchemy as sa

from app.db import get_session
from app.ingestors import get_ingestor
from app.metrics import IngestTimer, calculate_and_update_metrics

# Set up logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api")

# Define enums and models
class SourceType(str, Enum):
    """Source type for data ingestion."""
    CRUNCHBASE = "crunchbase"
    GITHUB = "github"

class IngestRequest(BaseModel):
    """Request model for ingesting data."""
    source: SourceType
    identifier: str
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class IngestResponse(BaseModel):
    """Response model for ingestion operations."""
    status: str
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class EntityResponse(BaseModel):
    """Response model for entity operations."""
    id: int
    type: str
    name: str
    properties: Dict[str, Any]
    created_at: str
    updated_at: str

class RelationshipResponse(BaseModel):
    """Response model for relationship operations."""
    id: int
    source_id: int
    target_id: int
    type: str
    properties: Dict[str, Any]
    created_at: str
    updated_at: str

class EntityCreate(BaseModel):
    """Request model for creating an entity."""
    type: str
    name: str
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class RelationshipCreate(BaseModel):
    """Request model for creating a relationship."""
    source_id: int
    target_id: int
    type: str
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MetricsResponse(BaseModel):
    """Response model for metrics."""
    entities: Dict[str, int]
    relationships: Dict[str, int]
    timestamp: str

# API routes
@router.post("/ingest", response_model=IngestResponse)
async def ingest_data(request: IngestRequest, db: Session = Depends(get_session)):
    """
    Ingest data from a source into the knowledge graph.
    
    Args:
        request: Ingest request with source, identifier, and options
        db: Database session
        
    Returns:
        IngestResponse
    """
    try:
        source = request.source.value
        identifier = request.identifier
        options = request.options
        
        logger.info(f"Ingesting data from {source}: {identifier}")
        
        # Get appropriate ingestor
        ingestor = get_ingestor(source, db)
        
        # Process the ingestion with timing
        with IngestTimer(source):
            if source == SourceType.CRUNCHBASE:
                result = ingestor.ingest_company(identifier)
            elif source == SourceType.GITHUB:
                owner, repo = identifier.split("/")
                result = ingestor.ingest_repository(owner, repo)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported source: {source}")
        
        if result.get("status") == "success":
            return IngestResponse(
                status="success",
                message=f"Successfully ingested {source} data for {identifier}",
                result=result
            )
        else:
            return IngestResponse(
                status="error",
                message=result.get("message", f"Failed to ingest {source} data for {identifier}"),
                result=result
            )
            
    except Exception as e:
        logger.error(f"Error ingesting data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entities", response_model=List[EntityResponse])
async def get_entities(
    type: Optional[str] = Query(None, description="Filter by entity type"),
    name: Optional[str] = Query(None, description="Filter by entity name (partial match)"),
    limit: int = Query(100, description="Limit the number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_dir: str = Query("asc", description="Sort direction (asc or desc)"),
    db: Session = Depends(get_session)
):
    """
    Get entities from the knowledge graph.
    
    Args:
        type: Filter by entity type
        name: Filter by entity name (partial match)
        limit: Limit the number of results
        offset: Offset for pagination
        sort_by: Field to sort by
        sort_dir: Sort direction (asc or desc)
        db: Database session
        
    Returns:
        List of entities
    """
    try:
        query = sa.text("""
        SELECT id, type, name, properties, created_at, updated_at
        FROM entities
        WHERE 1=1
        """)
        
        params = {}
        
        if type:
            query = sa.text(f"{query.text} AND type = :type")
            params["type"] = type
        
        if name:
            query = sa.text(f"{query.text} AND name ILIKE :name")
            params["name"] = f"%{name}%"
        
        # Add sorting
        if sort_by in ["id", "type", "name", "created_at", "updated_at"]:
            direction = "ASC" if sort_dir.lower() == "asc" else "DESC"
            query = sa.text(f"{query.text} ORDER BY {sort_by} {direction}")
        
        # Add pagination
        query = sa.text(f"{query.text} LIMIT :limit OFFSET :offset")
        params["limit"] = limit
        params["offset"] = offset
        
        result = db.execute(query, params)
        
        entities = []
        for row in result:
            entities.append({
                "id": row[0],
                "type": row[1],
                "name": row[2],
                "properties": row[3],
                "created_at": row[4].isoformat(),
                "updated_at": row[5].isoformat()
            })
        
        return entities
        
    except Exception as e:
        logger.error(f"Error getting entities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: int = Path(..., description="ID of the entity"),
    db: Session = Depends(get_session)
):
    """
    Get a specific entity by ID.
    
    Args:
        entity_id: ID of the entity
        db: Database session
        
    Returns:
        Entity
    """
    try:
        result = db.execute(
            sa.text("""
            SELECT id, type, name, properties, created_at, updated_at
            FROM entities
            WHERE id = :id
            """),
            {"id": entity_id}
        )
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Entity with ID {entity_id} not found")
        
        return {
            "id": row[0],
            "type": row[1],
            "name": row[2],
            "properties": row[3],
            "created_at": row[4].isoformat(),
            "updated_at": row[5].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity {entity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/entities", response_model=EntityResponse)
async def create_entity_api(
    entity: EntityCreate,
    db: Session = Depends(get_session)
):
    """
    Create a new entity.
    
    Args:
        entity: Entity to create
        db: Database session
        
    Returns:
        Created entity
    """
    try:
        from app.db import create_entity
        
        result = create_entity(db, entity.type, entity.name, entity.properties)
        
        return {
            "id": result.id,
            "type": result.type,
            "name": result.name,
            "properties": result.properties,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating entity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships", response_model=List[RelationshipResponse])
async def get_relationships(
    source_id: Optional[int] = Query(None, description="Filter by source entity ID"),
    target_id: Optional[int] = Query(None, description="Filter by target entity ID"),
    type: Optional[str] = Query(None, description="Filter by relationship type"),
    limit: int = Query(100, description="Limit the number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_session)
):
    """
    Get relationships from the knowledge graph.
    
    Args:
        source_id: Filter by source entity ID
        target_id: Filter by target entity ID
        type: Filter by relationship type
        limit: Limit the number of results
        offset: Offset for pagination
        db: Database session
        
    Returns:
        List of relationships
    """
    try:
        query = sa.text("""
        SELECT id, source_id, target_id, type, properties, created_at, updated_at
        FROM relationships
        WHERE 1=1
        """)
        
        params = {}
        
        if source_id:
            query = sa.text(f"{query.text} AND source_id = :source_id")
            params["source_id"] = source_id
        
        if target_id:
            query = sa.text(f"{query.text} AND target_id = :target_id")
            params["target_id"] = target_id
        
        if type:
            query = sa.text(f"{query.text} AND type = :type")
            params["type"] = type
        
        # Add pagination
        query = sa.text(f"{query.text} LIMIT :limit OFFSET :offset")
        params["limit"] = limit
        params["offset"] = offset
        
        result = db.execute(query, params)
        
        relationships = []
        for row in result:
            relationships.append({
                "id": row[0],
                "source_id": row[1],
                "target_id": row[2],
                "type": row[3],
                "properties": row[4],
                "created_at": row[5].isoformat(),
                "updated_at": row[6].isoformat()
            })
        
        return relationships
        
    except Exception as e:
        logger.error(f"Error getting relationships: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/relationships", response_model=RelationshipResponse)
async def create_relationship_api(
    relationship: RelationshipCreate,
    db: Session = Depends(get_session)
):
    """
    Create a new relationship.
    
    Args:
        relationship: Relationship to create
        db: Database session
        
    Returns:
        Created relationship
    """
    try:
        from app.db import create_relationship
        
        result = create_relationship(
            db, 
            relationship.source_id, 
            relationship.target_id, 
            relationship.type, 
            relationship.properties
        )
        
        return {
            "id": result.id,
            "source_id": result.source_id,
            "target_id": result.target_id,
            "type": result.type,
            "properties": result.properties,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating relationship: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: Session = Depends(get_session)):
    """
    Get metrics about the knowledge graph.
    
    Args:
        db: Database session
        
    Returns:
        Metrics response
    """
    try:
        metrics = calculate_and_update_metrics(db)
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Create FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
api = FastAPI(
    title="Data Ingestion & Knowledge Graph Service",
    description="Service for ingesting data from various sources and building a knowledge graph",
    version="0.1.0",
)

# Add CORS middleware
origins = [
    "http://localhost:5000",  # Frontend service
    "http://localhost:3000",  # Development frontend
    "http://frontend:5000",   # Docker frontend service
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
api.include_router(router)

@api.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Data Ingestion & Knowledge Graph Service",
        "version": "0.1.0",
        "status": "running"
    }

@api.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}