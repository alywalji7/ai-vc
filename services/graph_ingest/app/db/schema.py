from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, 
    ForeignKey, Table, MetaData, JSON, Text,
    create_engine, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os
from datetime import datetime

# Use the DATABASE_URL from environment or a default
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

Base = declarative_base()


class Entity(Base):
    """Node in the property graph"""
    __tablename__ = "knowledge_graph_entities"
    
    id = Column(String, primary_key=True)
    type = Column(String, index=True, nullable=False)
    source = Column(String, index=True, nullable=False)
    source_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    properties = Column(JSON, nullable=False, default=dict)
    
    # Relationship with edges
    outgoing_relationships = relationship(
        "Relationship", 
        foreign_keys="Relationship.from_entity_id",
        back_populates="from_entity"
    )
    incoming_relationships = relationship(
        "Relationship", 
        foreign_keys="Relationship.to_entity_id",
        back_populates="to_entity"
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "source_id": self.source_id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "properties": self.properties or {}
        }


class Relationship(Base):
    """Edge in the property graph"""
    __tablename__ = "knowledge_graph_relationships"
    
    id = Column(String, primary_key=True)
    type = Column(String, index=True, nullable=False)
    source = Column(String, index=True, nullable=False)
    from_entity_id = Column(String, ForeignKey("knowledge_graph_entities.id"), index=True, nullable=False)
    to_entity_id = Column(String, ForeignKey("knowledge_graph_entities.id"), index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    properties = Column(JSON, nullable=False, default=dict)
    
    # Relationships to entity nodes
    from_entity = relationship(
        "Entity", 
        foreign_keys=[from_entity_id],
        back_populates="outgoing_relationships"
    )
    to_entity = relationship(
        "Entity", 
        foreign_keys=[to_entity_id],
        back_populates="incoming_relationships"
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "from_entity_id": self.from_entity_id,
            "to_entity_id": self.to_entity_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "properties": self.properties or {}
        }