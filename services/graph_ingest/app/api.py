"""
API module for the Graph Ingest Service.

This module contains the FastAPI routes for the Graph Ingest Service.
"""

import logging
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_session
from app.metrics import calculate_and_update_metrics
from app.ingestors import CrunchbaseIngestor, GitHubIngestor, get_ingestor
from app.scheduler import ingest_crunchbase_companies, ingest_github_repositories

# Set up logging
logger = logging.getLogger(__name__)

# Create API
api = FastAPI(title="Graph Ingest API")


# Models for API requests and responses
class EntityBase(BaseModel):
    type: str
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class EntityResponse(EntityBase):
    id: int
    created_at: str
    updated_at: str


class RelationshipBase(BaseModel):
    source_id: int
    target_id: int
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class RelationshipResponse(RelationshipBase):
    id: int
    created_at: str
    updated_at: str


class CrunchbaseIngestionRequest(BaseModel):
    permalink: str


class GitHubIngestionRequest(BaseModel):
    owner: str
    repo: str


class IngestionResponse(BaseModel):
    status: str
    message: Optional[str] = None
    entity_id: Optional[int] = None


class CountResponse(BaseModel):
    entity_count: int
    relationship_count: int
    entity_types: Dict[str, int]
    relationship_types: Dict[str, int]


# Dependency for database session
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


# API routes
@api.get("/", tags=["health"])
def root():
    """Root endpoint for health checks."""
    return {"status": "ok", "service": "graph_ingest"}


@api.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "graph_ingest"}


@api.get("/entities", tags=["entities"], response_model=List[EntityResponse])
def get_entities(
    type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get entities from the knowledge graph.
    
    Args:
        type: Filter by entity type
        limit: Maximum number of entities to return
        offset: Offset for pagination
        db: Database session
    """
    from sqlalchemy import text
    
    try:
        query = "SELECT id, type, name, properties, created_at, updated_at FROM entities"
        params = {}
        
        if type:
            query += " WHERE type = :type"
            params["type"] = type
        
        query += " ORDER BY id LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = db.execute(text(query), params)
        
        entities = []
        for row in result:
            entity = {
                "id": row[0],
                "type": row[1],
                "name": row[2],
                "properties": row[3],
                "created_at": row[4].isoformat(),
                "updated_at": row[5].isoformat()
            }
            entities.append(entity)
        
        return entities
    
    except Exception as e:
        logger.error(f"Error getting entities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting entities: {str(e)}")


@api.get("/relationships", tags=["relationships"], response_model=List[RelationshipResponse])
def get_relationships(
    type: Optional[str] = None,
    source_id: Optional[int] = None,
    target_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get relationships from the knowledge graph.
    
    Args:
        type: Filter by relationship type
        source_id: Filter by source entity ID
        target_id: Filter by target entity ID
        limit: Maximum number of relationships to return
        offset: Offset for pagination
        db: Database session
    """
    from sqlalchemy import text
    
    try:
        query = "SELECT id, source_id, target_id, type, properties, created_at, updated_at FROM relationships"
        params = {}
        
        where_clauses = []
        if type:
            where_clauses.append("type = :type")
            params["type"] = type
        
        if source_id:
            where_clauses.append("source_id = :source_id")
            params["source_id"] = source_id
        
        if target_id:
            where_clauses.append("target_id = :target_id")
            params["target_id"] = target_id
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY id LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = db.execute(text(query), params)
        
        relationships = []
        for row in result:
            relationship = {
                "id": row[0],
                "source_id": row[1],
                "target_id": row[2],
                "type": row[3],
                "properties": row[4],
                "created_at": row[5].isoformat(),
                "updated_at": row[6].isoformat()
            }
            relationships.append(relationship)
        
        return relationships
    
    except Exception as e:
        logger.error(f"Error getting relationships: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting relationships: {str(e)}")


@api.post("/entities", tags=["entities"], response_model=EntityResponse)
def create_entity(entity: EntityBase, db: Session = Depends(get_db)):
    """
    Create a new entity in the knowledge graph.
    
    Args:
        entity: Entity to create
        db: Database session
    """
    from sqlalchemy import text
    import json
    
    try:
        result = db.execute(
            text("""
            INSERT INTO entities (type, name, properties, created_at, updated_at)
            VALUES (:type, :name, :properties, NOW(), NOW())
            RETURNING id, created_at, updated_at
            """),
            {
                "type": entity.type,
                "name": entity.name,
                "properties": json.dumps(entity.properties)
            }
        )
        
        id, created_at, updated_at = result.fetchone()
        
        db.commit()
        
        return {
            "id": id,
            "type": entity.type,
            "name": entity.name,
            "properties": entity.properties,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating entity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating entity: {str(e)}")


@api.post("/relationships", tags=["relationships"], response_model=RelationshipResponse)
def create_relationship(relationship: RelationshipBase, db: Session = Depends(get_db)):
    """
    Create a new relationship in the knowledge graph.
    
    Args:
        relationship: Relationship to create
        db: Database session
    """
    from sqlalchemy import text
    import json
    
    try:
        # Check if source and target entities exist
        result = db.execute(
            text("SELECT COUNT(*) FROM entities WHERE id IN (:source_id, :target_id)"),
            {"source_id": relationship.source_id, "target_id": relationship.target_id}
        )
        count = result.scalar()
        
        if count < 2:
            raise HTTPException(status_code=404, detail="Source or target entity not found")
        
        result = db.execute(
            text("""
            INSERT INTO relationships (source_id, target_id, type, properties, created_at, updated_at)
            VALUES (:source_id, :target_id, :type, :properties, NOW(), NOW())
            RETURNING id, created_at, updated_at
            """),
            {
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "type": relationship.type,
                "properties": json.dumps(relationship.properties)
            }
        )
        
        id, created_at, updated_at = result.fetchone()
        
        db.commit()
        
        return {
            "id": id,
            "source_id": relationship.source_id,
            "target_id": relationship.target_id,
            "type": relationship.type,
            "properties": relationship.properties,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat()
        }
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating relationship: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating relationship: {str(e)}")


@api.post("/ingest/crunchbase", tags=["ingestion"], response_model=IngestionResponse)
def ingest_crunchbase_company(
    request: CrunchbaseIngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Ingest a company from Crunchbase.
    
    Args:
        request: Crunchbase ingestion request
        background_tasks: FastAPI background tasks
        db: Database session
    """
    try:
        ingestor = CrunchbaseIngestor(db)
        result = ingestor.ingest_company(request.permalink)
        
        # Update metrics in background
        background_tasks.add_task(calculate_and_update_metrics, db)
        
        if result.get("status") == "success":
            return {
                "status": "success",
                "entity_id": result.get("company_id")
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Unknown error")
            }
    
    except Exception as e:
        logger.error(f"Error ingesting Crunchbase company: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting Crunchbase company: {str(e)}")


@api.post("/ingest/github", tags=["ingestion"], response_model=IngestionResponse)
def ingest_github_repository(
    request: GitHubIngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Ingest a repository from GitHub.
    
    Args:
        request: GitHub ingestion request
        background_tasks: FastAPI background tasks
        db: Database session
    """
    try:
        ingestor = GitHubIngestor(db)
        result = ingestor.ingest_repository(request.owner, request.repo)
        
        # Update metrics in background
        background_tasks.add_task(calculate_and_update_metrics, db)
        
        if result.get("status") == "success":
            return {
                "status": "success",
                "entity_id": result.get("repo_id")
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Unknown error")
            }
    
    except Exception as e:
        logger.error(f"Error ingesting GitHub repository: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting GitHub repository: {str(e)}")


@api.post("/ingest/batch/crunchbase", tags=["ingestion"])
def batch_ingest_crunchbase(background_tasks: BackgroundTasks):
    """
    Trigger a batch ingestion of Crunchbase companies.
    
    Args:
        background_tasks: FastAPI background tasks
    """
    try:
        background_tasks.add_task(ingest_crunchbase_companies)
        return {"status": "success", "message": "Started Crunchbase batch ingestion"}
    
    except Exception as e:
        logger.error(f"Error starting Crunchbase batch ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting Crunchbase batch ingestion: {str(e)}")


@api.post("/ingest/batch/github", tags=["ingestion"])
def batch_ingest_github(background_tasks: BackgroundTasks):
    """
    Trigger a batch ingestion of GitHub repositories.
    
    Args:
        background_tasks: FastAPI background tasks
    """
    try:
        background_tasks.add_task(ingest_github_repositories)
        return {"status": "success", "message": "Started GitHub batch ingestion"}
    
    except Exception as e:
        logger.error(f"Error starting GitHub batch ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting GitHub batch ingestion: {str(e)}")


@api.get("/count", tags=["metrics"], response_model=CountResponse)
def get_counts(db: Session = Depends(get_db)):
    """
    Get entity and relationship counts.
    
    Args:
        db: Database session
    """
    from sqlalchemy import text
    
    try:
        # Count entities
        result = db.execute(text("SELECT COUNT(*) FROM entities"))
        entity_count = result.scalar()
        
        # Count relationships
        result = db.execute(text("SELECT COUNT(*) FROM relationships"))
        relationship_count = result.scalar()
        
        # Count entities by type
        result = db.execute(text("SELECT type, COUNT(*) FROM entities GROUP BY type"))
        entity_types = {row[0]: row[1] for row in result}
        
        # Count relationships by type
        result = db.execute(text("SELECT type, COUNT(*) FROM relationships GROUP BY type"))
        relationship_types = {row[0]: row[1] for row in result}
        
        return {
            "entity_count": entity_count,
            "relationship_count": relationship_count,
            "entity_types": entity_types,
            "relationship_types": relationship_types
        }
    
    except Exception as e:
        logger.error(f"Error getting counts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting counts: {str(e)}")


@api.post("/refresh-metrics", tags=["metrics"])
def refresh_metrics(db: Session = Depends(get_db)):
    """
    Recalculate and update all metrics.
    
    Args:
        db: Database session
    """
    try:
        calculate_and_update_metrics(db)
        return {"status": "success", "message": "Metrics refreshed"}
    
    except Exception as e:
        logger.error(f"Error refreshing metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error refreshing metrics: {str(e)}")