from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.db import get_session, get_entities_by_type, get_relationships_by_type
from app.models.base import SourceType
from app.ingestors import (
    GitHubIngestor, CrunchbaseIngestor,
    ProductHuntConnector, EdgarFormDConnector
)
from .models import (
    IngestRequest, IngestResponse, 
    EntityResponse, RelationshipResponse
)


router = APIRouter()


@router.post("/ingest", response_model=IngestResponse, tags=["ingest"])
def ingest_data(request: IngestRequest, db: Session = Depends(get_session)):
    """
    Ingest data from a source
    """
    # Initialize counter for ingested entities and relationships
    entities_count = 0
    relationships_count = 0
    
    try:
        if request.source == SourceType.GITHUB:
            ingestor = GitHubIngestor(db)
            result = ingestor.ingest(
                org=request.org, 
                user=request.user, 
                repo=request.repo
            )
            
            # Count the number of entities and relationships ingested
            if result.get("status") == "success":
                # These counts are estimates based on the response structure
                if request.org:
                    # Org + repos + contributors for each repo
                    entities_count = 1 + result.get("repositories_count", 0) * 2
                    # Ownership + contributor relationships for each repo
                    relationships_count = result.get("repositories_count", 0) * 2
                elif request.user:
                    # User + repos
                    entities_count = 1 + result.get("repositories_count", 0)
                    # Ownership relationships for each repo
                    relationships_count = result.get("repositories_count", 0)
                elif request.repo:
                    # Owner + repo + contributors
                    entities_count = 2 + result.get("contributors_count", 0)
                    # Ownership + contributor relationships
                    relationships_count = 1 + result.get("contributors_count", 0)
            
        elif request.source == SourceType.CRUNCHBASE:
            ingestor = CrunchbaseIngestor(db)
            result = ingestor.ingest(
                company=request.company,
                person=request.person
            )
            
            # Count the number of entities and relationships ingested
            if result.get("status") == "success":
                # These counts are estimates based on the response structure
                if request.company:
                    # Company + founders + funding rounds + investors
                    entities_count = 1 + result.get("founders_count", 0) + result.get("funding_rounds_count", 0) * 4
                    # Founded by + funded by + participated in relationships
                    relationships_count = result.get("founders_count", 0) + result.get("funding_rounds_count", 0) * 4
                elif request.person:
                    # Person + companies founded
                    entities_count = 1 + result.get("companies_founded_count", 0)
                    # Founded relationships
                    relationships_count = result.get("companies_founded_count", 0)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported source: {request.source}")
            
        return IngestResponse(
            status="success" if result.get("status") == "success" else "error",
            message=result.get("message"),
            source=request.source,
            entities_count=entities_count,
            relationships_count=relationships_count,
            results=result
        )
    except Exception as e:
        return IngestResponse(
            status="error",
            message=str(e),
            source=request.source
        )


@router.get("/entities", response_model=List[EntityResponse], tags=["query"])
def get_entities(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    skip: int = Query(0, ge=0, description="Number of entities to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of entities to return"),
    db: Session = Depends(get_session)
):
    """
    Get entities from the knowledge graph
    """
    from app.db.schema import Entity
    entities = get_entities_by_type(db, entity_type, skip, limit) if entity_type else db.query(
        Entity
    ).offset(skip).limit(limit).all()
    
    return [
        EntityResponse(
            id=entity.id,
            type=entity.type,
            source=entity.source,
            name=entity.name,
            properties=entity.properties
        )
        for entity in entities
    ]


@router.get("/relationships", response_model=List[RelationshipResponse], tags=["query"])
def get_relationships(
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    skip: int = Query(0, ge=0, description="Number of relationships to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of relationships to return"),
    db: Session = Depends(get_session)
):
    """
    Get relationships from the knowledge graph
    """
    from app.db.schema import Relationship
    relationships = get_relationships_by_type(db, relationship_type, skip, limit) if relationship_type else db.query(
        Relationship
    ).offset(skip).limit(limit).all()
    
    return [
        RelationshipResponse(
            id=rel.id,
            type=rel.type,
            source=rel.source,
            from_entity_id=rel.from_entity_id,
            to_entity_id=rel.to_entity_id,
            properties=rel.properties
        )
        for rel in relationships
    ]


@router.post("/ingest/product_hunt", tags=["ingest"])
async def ingest_product_hunt_data(
    days_lookback: int = Query(7, description="Number of days to look back for product launches"),
    db: Session = Depends(get_session)
):
    """
    Ingest product launch data from Product Hunt
    
    This endpoint fetches recent product launches from Product Hunt and adds them
    to the knowledge graph as LAUNCH_EVENT entities with LAUNCHED relationships
    to the corresponding company entities.
    """
    try:
        connector = ProductHuntConnector()
        num_entities, num_relationships = await connector.ingest(days_lookback=days_lookback)
        
        return {
            "status": "success",
            "message": f"Ingested {num_entities} entities and {num_relationships} relationships from Product Hunt",
            "entities_count": num_entities,
            "relationships_count": num_relationships,
            "source": SourceType.PRODUCT_HUNT
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error ingesting data from Product Hunt: {str(e)}",
            "source": SourceType.PRODUCT_HUNT
        }


@router.post("/ingest/form_d", tags=["ingest"])
async def ingest_form_d_data(
    days_lookback: int = Query(7, description="Number of days to look back for SEC Form D filings"),
    db: Session = Depends(get_session)
):
    """
    Ingest SEC Form D filings
    
    This endpoint fetches recent Form D filings from the SEC EDGAR database and adds them
    to the knowledge graph as RAISE_EVENT entities with RAISED relationships
    to the corresponding company entities.
    """
    try:
        connector = EdgarFormDConnector()
        num_entities, num_relationships = await connector.ingest(days_lookback=days_lookback)
        
        return {
            "status": "success",
            "message": f"Ingested {num_entities} entities and {num_relationships} relationships from SEC Form D filings",
            "entities_count": num_entities,
            "relationships_count": num_relationships,
            "source": SourceType.SEC_FORM_D
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error ingesting data from SEC Form D filings: {str(e)}",
            "source": SourceType.SEC_FORM_D
        }


@router.get("/maintenance/cleanup", tags=["maintenance"])
def cleanup_old_data(
    days_to_keep: int = Query(90, description="Number of days of data to retain"), 
    db: Session = Depends(get_session)
):
    """
    Clean up data older than a specified number of days
    
    This endpoint removes entities and relationships that were created more than
    days_to_keep days ago. Useful for maintaining a manageable database size.
    """
    try:
        from app.db.schema import Entity, Relationship
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Delete old relationships first (to maintain referential integrity)
        old_relationships = db.query(Relationship).filter(
            Relationship.created_at < cutoff_date
        ).all()
        
        for rel in old_relationships:
            db.delete(rel)
        
        deleted_relationships = len(old_relationships)
        
        # Delete orphaned entities (no relationships)
        subquery = db.query(Relationship.from_entity_id).union(
            db.query(Relationship.to_entity_id)
        ).distinct().subquery()
        
        orphaned_entities = db.query(Entity).filter(
            Entity.created_at < cutoff_date,
            ~Entity.id.in_(subquery)
        ).all()
        
        for entity in orphaned_entities:
            db.delete(entity)
            
        deleted_entities = len(orphaned_entities)
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Cleanup complete: Removed {deleted_entities} entities and {deleted_relationships} relationships older than {days_to_keep} days",
            "deleted_entities": deleted_entities,
            "deleted_relationships": deleted_relationships
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": f"Error during cleanup: {str(e)}"
        }