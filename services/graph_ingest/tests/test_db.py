import pytest
import sys
from pathlib import Path
from unittest import mock
import os

# Add the parent directory to sys.path to allow importing app
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.graph_ingest.app.db import (
    init_db, get_session, insert_entity, insert_relationship,
    get_entity_by_id, get_entities_by_type, get_relationships_by_type,
    get_relationships_for_entity
)
from services.graph_ingest.app.models.base import (
    SourceType, EntityType, RelationshipType,
    BaseEntity, BaseRelationship
)


@pytest.fixture
def db_session():
    """Create a test database session"""
    # Use an in-memory SQLite database for testing
    with mock.patch("services.graph_ingest.app.db.schema.DATABASE_URL", "sqlite:///:memory:"):
        # Initialize the database
        init_db()
        # Get a session
        session = get_session()
        yield session
        # Clean up
        session.close()


def test_insert_entity(db_session):
    """Test inserting an entity into the database"""
    # Create a test entity
    entity = BaseEntity(
        id="test:entity:123",
        type=EntityType.PERSON,
        source=SourceType.GITHUB,
        source_id="123",
        name="Test Entity"
    )
    
    # Insert the entity
    db_entity = insert_entity(db_session, entity)
    
    # Check that the entity was inserted correctly
    assert db_entity.id == "test:entity:123"
    assert db_entity.type == EntityType.PERSON.value
    assert db_entity.source == SourceType.GITHUB.value
    assert db_entity.source_id == "123"
    assert db_entity.name == "Test Entity"


def test_insert_relationship(db_session):
    """Test inserting a relationship into the database"""
    # Create test entities
    entity1 = BaseEntity(
        id="test:entity:1",
        type=EntityType.PERSON,
        source=SourceType.GITHUB,
        source_id="1",
        name="Test Entity 1"
    )
    
    entity2 = BaseEntity(
        id="test:entity:2",
        type=EntityType.ORGANIZATION,
        source=SourceType.GITHUB,
        source_id="2",
        name="Test Entity 2"
    )
    
    # Insert the entities
    insert_entity(db_session, entity1)
    insert_entity(db_session, entity2)
    
    # Create a test relationship
    relationship = BaseRelationship(
        id="test:rel:123",
        type=RelationshipType.WORKS_FOR,
        source=SourceType.GITHUB,
        from_entity_id="test:entity:1",
        to_entity_id="test:entity:2"
    )
    
    # Insert the relationship
    db_relationship = insert_relationship(db_session, relationship)
    
    # Check that the relationship was inserted correctly
    assert db_relationship.id == "test:rel:123"
    assert db_relationship.type == RelationshipType.WORKS_FOR.value
    assert db_relationship.source == SourceType.GITHUB.value
    assert db_relationship.from_entity_id == "test:entity:1"
    assert db_relationship.to_entity_id == "test:entity:2"


def test_get_entity_by_id(db_session):
    """Test getting an entity by ID"""
    # Create and insert a test entity
    entity = BaseEntity(
        id="test:entity:123",
        type=EntityType.PERSON,
        source=SourceType.GITHUB,
        source_id="123",
        name="Test Entity"
    )
    insert_entity(db_session, entity)
    
    # Get the entity by ID
    db_entity = get_entity_by_id(db_session, "test:entity:123")
    
    # Check that the entity was retrieved correctly
    assert db_entity is not None
    assert db_entity.id == "test:entity:123"
    assert db_entity.type == EntityType.PERSON.value
    assert db_entity.source == SourceType.GITHUB.value
    assert db_entity.source_id == "123"
    assert db_entity.name == "Test Entity"


def test_get_entities_by_type(db_session):
    """Test getting entities by type"""
    # Create and insert test entities
    entities = [
        BaseEntity(
            id=f"test:entity:{i}",
            type=EntityType.PERSON if i % 2 == 0 else EntityType.ORGANIZATION,
            source=SourceType.GITHUB,
            source_id=str(i),
            name=f"Test Entity {i}"
        )
        for i in range(10)
    ]
    
    for entity in entities:
        insert_entity(db_session, entity)
    
    # Get entities by type
    person_entities = get_entities_by_type(db_session, EntityType.PERSON.value)
    org_entities = get_entities_by_type(db_session, EntityType.ORGANIZATION.value)
    
    # Check that the entities were retrieved correctly
    assert len(person_entities) == 5  # IDs 0, 2, 4, 6, 8
    assert len(org_entities) == 5  # IDs 1, 3, 5, 7, 9
    
    for entity in person_entities:
        assert entity.type == EntityType.PERSON.value
    
    for entity in org_entities:
        assert entity.type == EntityType.ORGANIZATION.value


def test_get_relationships_by_type(db_session):
    """Test getting relationships by type"""
    # Create and insert test entities
    entity1 = BaseEntity(
        id="test:entity:1",
        type=EntityType.PERSON,
        source=SourceType.GITHUB,
        source_id="1",
        name="Test Entity 1"
    )
    
    entity2 = BaseEntity(
        id="test:entity:2",
        type=EntityType.ORGANIZATION,
        source=SourceType.GITHUB,
        source_id="2",
        name="Test Entity 2"
    )
    
    entity3 = BaseEntity(
        id="test:entity:3",
        type=EntityType.REPOSITORY,
        source=SourceType.GITHUB,
        source_id="3",
        name="Test Entity 3"
    )
    
    insert_entity(db_session, entity1)
    insert_entity(db_session, entity2)
    insert_entity(db_session, entity3)
    
    # Create and insert test relationships
    relationships = [
        BaseRelationship(
            id="test:rel:1",
            type=RelationshipType.WORKS_FOR,
            source=SourceType.GITHUB,
            from_entity_id="test:entity:1",
            to_entity_id="test:entity:2"
        ),
        BaseRelationship(
            id="test:rel:2",
            type=RelationshipType.CONTRIBUTES_TO,
            source=SourceType.GITHUB,
            from_entity_id="test:entity:1",
            to_entity_id="test:entity:3"
        ),
        BaseRelationship(
            id="test:rel:3",
            type=RelationshipType.OWNS,
            source=SourceType.GITHUB,
            from_entity_id="test:entity:2",
            to_entity_id="test:entity:3"
        )
    ]
    
    for relationship in relationships:
        insert_relationship(db_session, relationship)
    
    # Get relationships by type
    works_for_relationships = get_relationships_by_type(db_session, RelationshipType.WORKS_FOR.value)
    contributes_to_relationships = get_relationships_by_type(db_session, RelationshipType.CONTRIBUTES_TO.value)
    owns_relationships = get_relationships_by_type(db_session, RelationshipType.OWNS.value)
    
    # Check that the relationships were retrieved correctly
    assert len(works_for_relationships) == 1
    assert len(contributes_to_relationships) == 1
    assert len(owns_relationships) == 1
    
    assert works_for_relationships[0].type == RelationshipType.WORKS_FOR.value
    assert contributes_to_relationships[0].type == RelationshipType.CONTRIBUTES_TO.value
    assert owns_relationships[0].type == RelationshipType.OWNS.value


def test_get_relationships_for_entity(db_session):
    """Test getting relationships for an entity"""
    # Create and insert test entities
    entity1 = BaseEntity(
        id="test:entity:1",
        type=EntityType.PERSON,
        source=SourceType.GITHUB,
        source_id="1",
        name="Test Entity 1"
    )
    
    entity2 = BaseEntity(
        id="test:entity:2",
        type=EntityType.ORGANIZATION,
        source=SourceType.GITHUB,
        source_id="2",
        name="Test Entity 2"
    )
    
    entity3 = BaseEntity(
        id="test:entity:3",
        type=EntityType.REPOSITORY,
        source=SourceType.GITHUB,
        source_id="3",
        name="Test Entity 3"
    )
    
    insert_entity(db_session, entity1)
    insert_entity(db_session, entity2)
    insert_entity(db_session, entity3)
    
    # Create and insert test relationships
    relationships = [
        BaseRelationship(
            id="test:rel:1",
            type=RelationshipType.WORKS_FOR,
            source=SourceType.GITHUB,
            from_entity_id="test:entity:1",
            to_entity_id="test:entity:2"
        ),
        BaseRelationship(
            id="test:rel:2",
            type=RelationshipType.CONTRIBUTES_TO,
            source=SourceType.GITHUB,
            from_entity_id="test:entity:1",
            to_entity_id="test:entity:3"
        ),
        BaseRelationship(
            id="test:rel:3",
            type=RelationshipType.OWNS,
            source=SourceType.GITHUB,
            from_entity_id="test:entity:2",
            to_entity_id="test:entity:3"
        )
    ]
    
    for relationship in relationships:
        insert_relationship(db_session, relationship)
    
    # Get outgoing relationships for entity1
    outgoing_relationships = get_relationships_for_entity(db_session, "test:entity:1", "outgoing")
    
    # Get incoming relationships for entity3
    incoming_relationships = get_relationships_for_entity(db_session, "test:entity:3", "incoming")
    
    # Check that the relationships were retrieved correctly
    assert len(outgoing_relationships) == 2  # WORKS_FOR and CONTRIBUTES_TO
    assert len(incoming_relationships) == 2  # CONTRIBUTES_TO and OWNS
    
    # Check outgoing relationships from entity1
    outgoing_types = set(rel.type for rel in outgoing_relationships)
    assert RelationshipType.WORKS_FOR.value in outgoing_types
    assert RelationshipType.CONTRIBUTES_TO.value in outgoing_types
    
    # Check incoming relationships to entity3
    incoming_types = set(rel.type for rel in incoming_relationships)
    assert RelationshipType.CONTRIBUTES_TO.value in incoming_types
    assert RelationshipType.OWNS.value in incoming_types