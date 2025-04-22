"""
Metrics module for the Graph Ingest Service.

This module contains metrics collection functions for the Graph Ingest Service.
"""

import logging
import time
from datetime import datetime
from prometheus_client import Counter, Gauge, Summary
from typing import Dict, List, Any

import sqlalchemy as sa

# Set up logging
logger = logging.getLogger(__name__)

# Define Prometheus metrics
GITHUB_INGEST_SUCCESS = Counter(
    'github_ingest_success_total',
    'Total number of successful GitHub ingestions'
)

CRUNCHBASE_INGEST_SUCCESS = Counter(
    'crunchbase_ingest_success_total',
    'Total number of successful Crunchbase ingestions'
)

INGEST_FAILURE = Counter(
    'ingest_failure_total',
    'Total number of failed ingestions',
    ['source']
)

ENTITY_COUNT = Gauge(
    'entity_count',
    'Number of entities in the knowledge graph',
    ['type']
)

RELATIONSHIP_COUNT = Gauge(
    'relationship_count',
    'Number of relationships in the knowledge graph',
    ['type']
)

INGEST_DURATION = Summary(
    'ingest_duration_seconds',
    'Time spent processing an ingestion request',
    ['source']
)

# Utility functions for incrementing counters
def increment_github_success():
    """Increment the GitHub ingestion success counter."""
    GITHUB_INGEST_SUCCESS.inc()

def increment_crunchbase_success():
    """Increment the Crunchbase ingestion success counter."""
    CRUNCHBASE_INGEST_SUCCESS.inc()

def increment_ingest_failure(source='unknown'):
    """
    Increment the ingestion failure counter.
    
    Args:
        source: Source of the ingestion failure
    """
    INGEST_FAILURE.labels(source=source).inc()

def record_ingest_duration(source, duration):
    """
    Record the duration of an ingestion operation.
    
    Args:
        source: Source of the ingestion
        duration: Duration in seconds
    """
    INGEST_DURATION.labels(source=source).observe(duration)

class IngestTimer:
    """
    Context manager for timing ingest operations.
    
    Usage:
        with IngestTimer('github'):
            # Perform ingestion operation
    """
    
    def __init__(self, source):
        """
        Initialize the timer.
        
        Args:
            source: Source of the ingestion
        """
        self.source = source
        self.start_time = None
    
    def __enter__(self):
        """Start the timer."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        End the timer and record the duration.
        
        If an exception occurred, increment the failure counter.
        """
        duration = time.time() - self.start_time
        record_ingest_duration(self.source, duration)
        
        if exc_type is not None:
            # An exception occurred
            increment_ingest_failure(self.source)
            logger.error(f"Error during {self.source} ingestion: {exc_val}")

def calculate_entity_counts(db_session) -> Dict[str, int]:
    """
    Calculate the number of entities by type.
    
    Args:
        db_session: Database session
        
    Returns:
        Dictionary mapping entity types to counts
    """
    try:
        # Check if the table exists first
        result = db_session.execute(
            sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'entities')")
        )
        table_exists = result.scalar()
        
        if not table_exists:
            logger.warning("Table 'entities' does not exist yet")
            return {}
            
        result = db_session.execute(
            sa.text("SELECT type, COUNT(*) FROM entities GROUP BY type")
        )
        
        counts = {}
        for row in result:
            entity_type, count = row
            counts[entity_type] = count
            
            # Update Prometheus metric
            ENTITY_COUNT.labels(type=entity_type).set(count)
            
        return counts
    
    except Exception as e:
        logger.error(f"Error calculating entity counts: {str(e)}")
        return {}

def calculate_relationship_counts(db_session) -> Dict[str, int]:
    """
    Calculate the number of relationships by type.
    
    Args:
        db_session: Database session
        
    Returns:
        Dictionary mapping relationship types to counts
    """
    try:
        # Check if the table exists first
        result = db_session.execute(
            sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'relationships')")
        )
        table_exists = result.scalar()
        
        if not table_exists:
            logger.warning("Table 'relationships' does not exist yet")
            return {}
            
        result = db_session.execute(
            sa.text("SELECT type, COUNT(*) FROM relationships GROUP BY type")
        )
        
        counts = {}
        for row in result:
            relationship_type, count = row
            counts[relationship_type] = count
            
            # Update Prometheus metric
            RELATIONSHIP_COUNT.labels(type=relationship_type).set(count)
            
        return counts
    
    except Exception as e:
        logger.error(f"Error calculating relationship counts: {str(e)}")
        return {}

def calculate_and_update_metrics(db_session):
    """
    Calculate all metrics and update Prometheus.
    
    Args:
        db_session: Database session
    """
    logger.info("Updating knowledge graph metrics")
    
    # Calculate and update entity counts
    entity_counts = calculate_entity_counts(db_session)
    logger.info(f"Entity counts: {entity_counts}")
    
    # Calculate and update relationship counts
    relationship_counts = calculate_relationship_counts(db_session)
    logger.info(f"Relationship counts: {relationship_counts}")
    
    return {
        "entities": entity_counts,
        "relationships": relationship_counts,
        "timestamp": datetime.now().isoformat()
    }