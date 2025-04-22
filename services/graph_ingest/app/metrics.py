"""
Metrics module for the Graph Ingest Service.

This module contains Prometheus metrics for measuring the performance and activity
of the Graph Ingest Service.
"""

import logging
from prometheus_client import Counter, Gauge

# Set up logging
logger = logging.getLogger(__name__)

# Counters for successful ingestions
github_ingest_success = Counter(
    'github_ingest_success_total',
    'Total number of successful GitHub data ingestions'
)

crunchbase_ingest_success = Counter(
    'crunchbase_ingest_success_total',
    'Total number of successful Crunchbase data ingestions'
)

# Counter for failed ingestions
ingest_failure = Counter(
    'ingest_failure_total',
    'Total number of failed data ingestions'
)

# Gauges for entity and relationship counts
entity_count = Gauge(
    'graph_entity_count',
    'Number of entities in the knowledge graph',
    ['type']
)

relationship_count = Gauge(
    'graph_relationship_count',
    'Number of relationships in the knowledge graph',
    ['type']
)

# Scheduler timestamp
scheduler_last_run = Gauge(
    'graph_ingest_scheduler_last_run_timestamp',
    'Unix timestamp of the last scheduler run'
)

# Gauge for knowledge graph density
graph_density = Gauge(
    'graph_density',
    'Ratio of actual relationships to maximum possible relationships'
)

def increment_github_success():
    """Increment the GitHub ingestion success counter."""
    github_ingest_success.inc()
    logger.debug("Incremented GitHub ingestion success counter")

def increment_crunchbase_success():
    """Increment the Crunchbase ingestion success counter."""
    crunchbase_ingest_success.inc()
    logger.debug("Incremented Crunchbase ingestion success counter")

def increment_ingest_failure():
    """Increment the ingestion failure counter."""
    ingest_failure.inc()
    logger.debug("Incremented ingestion failure counter")

def update_scheduler_timestamp(timestamp):
    """Update the scheduler last run timestamp."""
    scheduler_last_run.set(timestamp)
    logger.debug(f"Updated scheduler timestamp to {timestamp}")

def update_entity_count(entity_type, count):
    """
    Update the entity count for a given type.
    
    Args:
        entity_type: Type of entity
        count: Number of entities
    """
    entity_count.labels(type=entity_type).set(count)
    logger.debug(f"Updated entity count for {entity_type} to {count}")

def update_relationship_count(relationship_type, count):
    """
    Update the relationship count for a given type.
    
    Args:
        relationship_type: Type of relationship
        count: Number of relationships
    """
    relationship_count.labels(type=relationship_type).set(count)
    logger.debug(f"Updated relationship count for {relationship_type} to {count}")

def update_graph_density(density):
    """
    Update the graph density metric.
    
    Args:
        density: Density value (0-1)
    """
    graph_density.set(density)
    logger.debug(f"Updated graph density to {density}")

def calculate_and_update_metrics(db_session):
    """
    Calculate and update all metrics based on the current database state.
    
    Args:
        db_session: Database session
    """
    from sqlalchemy import text
    
    try:
        # Count entities by type
        result = db_session.execute(text("SELECT type, COUNT(*) FROM entities GROUP BY type"))
        for row in result:
            entity_type, count = row
            update_entity_count(entity_type, count)
        
        # Count total entities
        result = db_session.execute(text("SELECT COUNT(*) FROM entities"))
        total_entities = result.scalar()
        update_entity_count("total", total_entities)
        
        # Count relationships by type
        result = db_session.execute(text("SELECT type, COUNT(*) FROM relationships GROUP BY type"))
        for row in result:
            rel_type, count = row
            update_relationship_count(rel_type, count)
        
        # Count total relationships
        result = db_session.execute(text("SELECT COUNT(*) FROM relationships"))
        total_relationships = result.scalar()
        update_relationship_count("total", total_relationships)
        
        # Calculate graph density
        if total_entities > 1:
            max_possible_relationships = total_entities * (total_entities - 1)
            density = total_relationships / max_possible_relationships if max_possible_relationships > 0 else 0
            update_graph_density(density)
        else:
            update_graph_density(0)
        
        logger.info("Updated all metrics successfully")
        
    except Exception as e:
        logger.error(f"Error updating metrics: {str(e)}")