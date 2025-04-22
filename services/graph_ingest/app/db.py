"""
Database module for the Graph Ingest Service.

This module handles database connections and schema initialization.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.sql import func

# Set up logging
logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/aivc")

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class Entity(Base):
    """
    Entity model for the knowledge graph.
    
    Entities represent nodes in the knowledge graph, such as companies, people, or repositories.
    """
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    properties = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Relationship(Base):
    """
    Relationship model for the knowledge graph.
    
    Relationships represent edges between entities in the knowledge graph.
    """
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("entities.id"), index=True, nullable=False)
    target_id = Column(Integer, ForeignKey("entities.id"), index=True, nullable=False)
    type = Column(String(50), index=True, nullable=False)
    properties = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class RawData(Base):
    """
    Raw data model for storing original data before processing.
    
    This model stores raw data from various sources (Crunchbase, GitHub, etc.)
    before it is processed and inserted into the knowledge graph.
    """
    __tablename__ = "raw_data"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), index=True, nullable=False)
    source_id = Column(String(255), index=True, nullable=False)
    data = Column(JSON)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

def init_db():
    """
    Initialize the database by creating all tables.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def get_session() -> Session:
    """
    Get a database session.
    
    Returns:
        Database session
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        logger.error(f"Error getting database session: {str(e)}")
        raise

def create_entity(session, entity_type: str, name: str, properties: Dict[str, Any] = None) -> Entity:
    """
    Create an entity in the knowledge graph.
    
    Args:
        session: Database session
        entity_type: Type of entity
        name: Name of entity
        properties: Properties of entity
        
    Returns:
        Created entity
    """
    try:
        entity = Entity(
            type=entity_type,
            name=name,
            properties=properties if properties is not None else {}
        )
        
        session.add(entity)
        session.commit()
        session.refresh(entity)
        
        return entity
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating entity {entity_type}/{name}: {str(e)}")
        raise

def create_relationship(session, source_id: int, target_id: int, relationship_type: str, properties: Dict[str, Any] = None) -> Relationship:
    """
    Create a relationship in the knowledge graph.
    
    Args:
        session: Database session
        source_id: ID of source entity
        target_id: ID of target entity
        relationship_type: Type of relationship
        properties: Properties of relationship
        
    Returns:
        Created relationship
    """
    try:
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            properties=properties if properties is not None else {}
        )
        
        session.add(relationship)
        session.commit()
        session.refresh(relationship)
        
        return relationship
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating relationship {relationship_type} ({source_id} -> {target_id}): {str(e)}")
        raise

def store_raw_data(session, source: str, source_id: str, data: Dict[str, Any] = None, content: str = None) -> RawData:
    """
    Store raw data from a source.
    
    Args:
        session: Database session
        source: Source of data (e.g., 'crunchbase', 'github')
        source_id: ID in the source system
        data: JSON data
        content: Text content
        
    Returns:
        Created raw data entry
    """
    try:
        raw_data = RawData(
            source=source,
            source_id=source_id,
            data=data if data is not None else {},
            content=content
        )
        
        session.add(raw_data)
        session.commit()
        session.refresh(raw_data)
        
        return raw_data
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error storing raw data {source}/{source_id}: {str(e)}")
        raise