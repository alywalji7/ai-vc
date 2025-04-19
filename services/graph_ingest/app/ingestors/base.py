from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.models.base import BaseEntity, BaseRelationship, SourceType
from app.db import insert_entity, insert_relationship


class BaseIngestor(ABC):
    """Base class for all ingestors"""
    
    def __init__(self, db: Session, **kwargs):
        """
        Initialize the ingestor
        
        Args:
            db: Database session
            **kwargs: Additional arguments for the ingestor
        """
        self.db = db
        self.source_type = self._get_source_type()
    
    @abstractmethod
    def _get_source_type(self) -> SourceType:
        """Get the source type for the ingestor"""
        pass
    
    @abstractmethod
    def ingest(self, **kwargs) -> Dict[str, Any]:
        """
        Run the ingestion process
        
        Args:
            **kwargs: Arguments for the ingestion process
            
        Returns:
            Dictionary with ingestion results
        """
        pass
    
    def save_entity(self, entity: BaseEntity) -> str:
        """
        Save an entity to the database
        
        Args:
            entity: Entity to save
            
        Returns:
            Entity ID
        """
        db_entity = insert_entity(self.db, entity)
        return db_entity.id
    
    def save_relationship(self, relationship: BaseRelationship) -> str:
        """
        Save a relationship to the database
        
        Args:
            relationship: Relationship to save
            
        Returns:
            Relationship ID
        """
        db_relationship = insert_relationship(self.db, relationship)
        return db_relationship.id