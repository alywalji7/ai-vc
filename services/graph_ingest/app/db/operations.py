from sqlalchemy.orm import Session
from typing import List, Dict, Any, Type, Optional, Union
from datetime import datetime

from app.models.base import BaseEntity, BaseRelationship
from .schema import Entity, Relationship, engine, Base


def init_db():
    """Initialize database by creating tables if they don't exist"""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Get a database session"""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def insert_entity(db: Session, entity: BaseEntity) -> Entity:
    """
    Insert a new entity into the database
    
    Args:
        db: Database session
        entity: Entity model to insert
        
    Returns:
        The inserted entity
    """
    db_entity = Entity(
        id=entity.id,
        type=entity.type.value,
        source=entity.source.value,
        source_id=entity.source_id,
        name=entity.name,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        properties=entity.properties
    )
    
    # Check if entity already exists
    existing = db.query(Entity).filter(Entity.id == entity.id).first()
    if existing:
        # Update existing entity
        existing.name = entity.name
        existing.updated_at = datetime.now()
        existing.properties = entity.properties
        db.commit()
        return existing
    
    # Add new entity
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def insert_relationship(db: Session, relationship: BaseRelationship) -> Relationship:
    """
    Insert a new relationship into the database
    
    Args:
        db: Database session
        relationship: Relationship model to insert
        
    Returns:
        The inserted relationship
    """
    db_relationship = Relationship(
        id=relationship.id,
        type=relationship.type.value,
        source=relationship.source.value,
        from_entity_id=relationship.from_entity_id,
        to_entity_id=relationship.to_entity_id,
        created_at=relationship.created_at,
        updated_at=relationship.updated_at,
        properties=relationship.properties
    )
    
    # Check if relationship already exists
    existing = db.query(Relationship).filter(Relationship.id == relationship.id).first()
    if existing:
        # Update existing relationship
        existing.updated_at = datetime.now()
        existing.properties = relationship.properties
        db.commit()
        return existing
    
    # Add new relationship
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    return db_relationship


def get_entity_by_id(db: Session, entity_id: str) -> Optional[Entity]:
    """
    Get an entity by ID
    
    Args:
        db: Database session
        entity_id: Entity ID
        
    Returns:
        Entity or None if not found
    """
    return db.query(Entity).filter(Entity.id == entity_id).first()


def get_entities_by_type(db: Session, entity_type: str, 
                         skip: int = 0, limit: int = 100) -> List[Entity]:
    """
    Get entities by type
    
    Args:
        db: Database session
        entity_type: Entity type
        skip: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        List of entities
    """
    return db.query(Entity).filter(Entity.type == entity_type).offset(skip).limit(limit).all()


def get_relationships_by_type(db: Session, relationship_type: str, 
                              skip: int = 0, limit: int = 100) -> List[Relationship]:
    """
    Get relationships by type
    
    Args:
        db: Database session
        relationship_type: Relationship type
        skip: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        List of relationships
    """
    return db.query(Relationship).filter(Relationship.type == relationship_type).offset(skip).limit(limit).all()


def get_relationships_for_entity(db: Session, entity_id: str, 
                                 direction: str = "outgoing", 
                                 skip: int = 0, limit: int = 100) -> List[Relationship]:
    """
    Get relationships for an entity
    
    Args:
        db: Database session
        entity_id: Entity ID
        direction: 'outgoing' or 'incoming' relationships
        skip: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        List of relationships
    """
    if direction == "outgoing":
        return db.query(Relationship).filter(Relationship.from_entity_id == entity_id).offset(skip).limit(limit).all()
    else:
        return db.query(Relationship).filter(Relationship.to_entity_id == entity_id).offset(skip).limit(limit).all()