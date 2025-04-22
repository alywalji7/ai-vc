"""
Seed demo data for the Graph Ingest Service.

This script creates sample data in the knowledge graph database.
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

import boto3
from dotenv import load_dotenv

import sqlalchemy as sa
from sqlalchemy.orm import Session

# Import from the file, not from the package
import app.db as db_module

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Sample data
SAMPLE_COMPANIES = [
    {
        "name": "TechFusion",
        "type": "company",
        "properties": {
            "website": "https://techfusion.ai",
            "short_description": "AI-powered software development platform",
            "founded_on": "2021-03-15",
            "num_employees_min": 50,
            "num_employees_max": 100,
            "total_funding_usd": 12000000,
            "headquarters": [{"country": "United States", "region": "California"}],
            "categories": ["Artificial Intelligence", "Software Development", "Developer Tools"],
            "source": "seed_demo"
        }
    },
    {
        "name": "QuantumLeap",
        "type": "company",
        "properties": {
            "website": "https://quantumleap.tech",
            "short_description": "Quantum computing solutions for enterprise",
            "founded_on": "2019-07-22",
            "num_employees_min": 25,
            "num_employees_max": 50,
            "total_funding_usd": 8500000,
            "headquarters": [{"country": "United States", "region": "Massachusetts"}],
            "categories": ["Quantum Computing", "Enterprise Software", "Cloud Computing"],
            "source": "seed_demo"
        }
    },
    {
        "name": "BlockMatrix",
        "type": "company",
        "properties": {
            "website": "https://blockmatrix.finance",
            "short_description": "Secure blockchain infrastructure for financial services",
            "founded_on": "2018-11-05",
            "num_employees_min": 75,
            "num_employees_max": 150,
            "total_funding_usd": 22000000,
            "headquarters": [{"country": "United Kingdom", "region": "London"}],
            "categories": ["Blockchain", "FinTech", "Cybersecurity"],
            "source": "seed_demo"
        }
    }
]

SAMPLE_PEOPLE = [
    {
        "name": "Alex Rodriguez",
        "type": "person",
        "properties": {
            "title": "CEO",
            "linkedin": "https://linkedin.com/in/alexrodriguez",
            "twitter": "@alexrtechfusion",
            "source": "seed_demo"
        }
    },
    {
        "name": "Samantha Lee",
        "type": "person",
        "properties": {
            "title": "CTO",
            "linkedin": "https://linkedin.com/in/samanthalee",
            "github": "github.com/samlee",
            "source": "seed_demo"
        }
    },
    {
        "name": "Michael Chen",
        "type": "person",
        "properties": {
            "title": "Lead Researcher",
            "linkedin": "https://linkedin.com/in/michaelchen",
            "github": "github.com/mchen",
            "source": "seed_demo"
        }
    },
    {
        "name": "Priya Patel",
        "type": "person",
        "properties": {
            "title": "VP of Product",
            "linkedin": "https://linkedin.com/in/priyapatel",
            "twitter": "@priyaproduct",
            "source": "seed_demo"
        }
    }
]

SAMPLE_INVESTORS = [
    {
        "name": "Sequoia Capital",
        "type": "investor",
        "properties": {
            "website": "https://sequoiacap.com",
            "founded_on": "1972-01-01",
            "headquarters": [{"country": "United States", "region": "California"}],
            "investor_type": "venture_capital",
            "source": "seed_demo"
        }
    },
    {
        "name": "Andreessen Horowitz",
        "type": "investor",
        "properties": {
            "website": "https://a16z.com",
            "founded_on": "2009-01-01",
            "headquarters": [{"country": "United States", "region": "California"}],
            "investor_type": "venture_capital",
            "source": "seed_demo"
        }
    },
    {
        "name": "Y Combinator",
        "type": "investor",
        "properties": {
            "website": "https://ycombinator.com",
            "founded_on": "2005-01-01",
            "headquarters": [{"country": "United States", "region": "California"}],
            "investor_type": "accelerator",
            "source": "seed_demo"
        }
    }
]

SAMPLE_REPOSITORIES = [
    {
        "name": "techfusion/ai-engine",
        "type": "repository",
        "properties": {
            "full_name": "techfusion/ai-engine",
            "description": "Core AI engine for the TechFusion platform",
            "url": "https://github.com/techfusion/ai-engine",
            "stars": 543,
            "forks": 125,
            "watchers": 43,
            "language": "Python",
            "topics": ["artificial-intelligence", "machine-learning", "deep-learning"],
            "created_at": "2021-05-12T14:23:45Z",
            "updated_at": "2025-02-15T09:10:32Z",
            "source": "seed_demo"
        }
    },
    {
        "name": "quantum-leap/qcomp",
        "type": "repository",
        "properties": {
            "full_name": "quantum-leap/qcomp",
            "description": "Quantum computing simulator for enterprise applications",
            "url": "https://github.com/quantum-leap/qcomp",
            "stars": 1205,
            "forks": 312,
            "watchers": 89,
            "language": "Rust",
            "topics": ["quantum-computing", "simulation", "enterprise"],
            "created_at": "2020-01-18T10:15:22Z",
            "updated_at": "2025-03-05T16:42:11Z",
            "source": "seed_demo"
        }
    },
    {
        "name": "blockmatrix/secure-chain",
        "type": "repository",
        "properties": {
            "full_name": "blockmatrix/secure-chain",
            "description": "Secure blockchain implementation for financial transactions",
            "url": "https://github.com/blockmatrix/secure-chain",
            "stars": 876,
            "forks": 201,
            "watchers": 67,
            "language": "Go",
            "topics": ["blockchain", "finance", "security"],
            "created_at": "2019-08-27T08:45:32Z",
            "updated_at": "2025-01-20T11:33:45Z",
            "source": "seed_demo"
        }
    }
]

# Define relationships between entities
SAMPLE_RELATIONSHIPS = [
    # People to companies
    {"source_type": "person", "source_name": "Alex Rodriguez", "target_type": "company", "target_name": "TechFusion", "relationship_type": "works_at", "properties": {"title": "CEO", "start_date": "2021-03-15"}},
    {"source_type": "person", "source_name": "Samantha Lee", "target_type": "company", "target_name": "TechFusion", "relationship_type": "works_at", "properties": {"title": "CTO", "start_date": "2021-04-10"}},
    {"source_type": "person", "source_name": "Michael Chen", "target_type": "company", "target_name": "QuantumLeap", "relationship_type": "works_at", "properties": {"title": "Lead Researcher", "start_date": "2019-08-01"}},
    {"source_type": "person", "source_name": "Priya Patel", "target_type": "company", "target_name": "BlockMatrix", "relationship_type": "works_at", "properties": {"title": "VP of Product", "start_date": "2020-01-15"}},
    {"source_type": "person", "source_name": "Alex Rodriguez", "target_type": "company", "target_name": "TechFusion", "relationship_type": "founded", "properties": {"date": "2021-03-15"}},
    {"source_type": "person", "source_name": "Samantha Lee", "target_type": "company", "target_name": "TechFusion", "relationship_type": "founded", "properties": {"date": "2021-03-15"}},
    {"source_type": "person", "source_name": "Michael Chen", "target_type": "company", "target_name": "QuantumLeap", "relationship_type": "founded", "properties": {"date": "2019-07-22"}},
    
    # Investors to companies
    {"source_type": "investor", "source_name": "Sequoia Capital", "target_type": "company", "target_name": "TechFusion", "relationship_type": "invested_in", "properties": {"amount_usd": 5000000, "date": "2022-02-10", "round": "Series A"}},
    {"source_type": "investor", "source_name": "Andreessen Horowitz", "target_type": "company", "target_name": "TechFusion", "relationship_type": "invested_in", "properties": {"amount_usd": 7000000, "date": "2022-02-10", "round": "Series A"}},
    {"source_type": "investor", "source_name": "Y Combinator", "target_type": "company", "target_name": "QuantumLeap", "relationship_type": "invested_in", "properties": {"amount_usd": 500000, "date": "2019-12-15", "round": "Seed"}},
    {"source_type": "investor", "source_name": "Sequoia Capital", "target_type": "company", "target_name": "QuantumLeap", "relationship_type": "invested_in", "properties": {"amount_usd": 8000000, "date": "2020-08-22", "round": "Series A"}},
    {"source_type": "investor", "source_name": "Andreessen Horowitz", "target_type": "company", "target_name": "BlockMatrix", "relationship_type": "invested_in", "properties": {"amount_usd": 12000000, "date": "2019-06-30", "round": "Series A"}},
    {"source_type": "investor", "source_name": "Sequoia Capital", "target_type": "company", "target_name": "BlockMatrix", "relationship_type": "invested_in", "properties": {"amount_usd": 10000000, "date": "2019-06-30", "round": "Series A"}},
    
    # Companies to repositories
    {"source_type": "company", "source_name": "TechFusion", "target_type": "repository", "target_name": "techfusion/ai-engine", "relationship_type": "developed", "properties": {}},
    {"source_type": "company", "source_name": "QuantumLeap", "target_type": "repository", "target_name": "quantum-leap/qcomp", "relationship_type": "developed", "properties": {}},
    {"source_type": "company", "source_name": "BlockMatrix", "target_type": "repository", "target_name": "blockmatrix/secure-chain", "relationship_type": "developed", "properties": {}},
    
    # People to repositories
    {"source_type": "person", "source_name": "Samantha Lee", "target_type": "repository", "target_name": "techfusion/ai-engine", "relationship_type": "contributed_to", "properties": {"contributions": 245}},
    {"source_type": "person", "source_name": "Michael Chen", "target_type": "repository", "target_name": "quantum-leap/qcomp", "relationship_type": "contributed_to", "properties": {"contributions": 176}},
    {"source_type": "person", "source_name": "Priya Patel", "target_type": "repository", "target_name": "blockmatrix/secure-chain", "relationship_type": "contributed_to", "properties": {"contributions": 132}}
]

def create_sample_entity(db_session: Session, entity_data: Dict[str, Any]) -> int:
    """
    Create a sample entity in the database.
    
    Args:
        db_session: Database session
        entity_data: Entity data
        
    Returns:
        ID of the created entity
    """
    name = entity_data["name"]
    entity_type = entity_data["type"]
    properties = entity_data.get("properties", {})
    
    try:
        entity = db_module.insert_entity(db_session, entity_type, name, properties)
        logger.info(f"Created {entity_type} entity: {name} (ID: {entity.id})")
        return entity.id
    except Exception as e:
        logger.error(f"Error creating entity {entity_type}/{name}: {e}")
        return 0  # Return 0 instead of None for type safety

def create_sample_relationship(db_session: Session, relationship_data: Dict[str, Any], entity_map: Dict[str, Dict[str, int]]):
    """
    Create a sample relationship in the database.
    
    Args:
        db_session: Database session
        relationship_data: Relationship data
        entity_map: Map of entity names to their IDs
    """
    source_type = relationship_data["source_type"]
    source_name = relationship_data["source_name"]
    target_type = relationship_data["target_type"]
    target_name = relationship_data["target_name"]
    relationship_type = relationship_data["relationship_type"]
    properties = relationship_data.get("properties", {})
    
    # Get entity IDs from the map
    source_id = entity_map.get(source_type, {}).get(source_name)
    target_id = entity_map.get(target_type, {}).get(target_name)
    
    if not source_id or not target_id:
        logger.error(f"Entity not found for relationship {source_name} -> {target_name}")
        return
    
    try:
        relationship = db_module.insert_relationship(
            db_session, 
            source_id, 
            target_id, 
            relationship_type, 
            properties
        )
        logger.info(f"Created relationship: ({source_name}) --[{relationship_type}]--> ({target_name}) (ID: {relationship.id})")
    except Exception as e:
        logger.error(f"Error creating relationship {source_name} --[{relationship_type}]--> {target_name}: {e}")

def seed_database():
    """Seed the database with sample data."""
    logger.info("Starting database seeding")
    
    # Initialize the database
    try:
        db_module.init_db()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return 1
    
    # Get database session
    db_session = db_module.get_session()
    
    # Create entities and store their IDs
    entity_map = {
        "company": {},
        "person": {},
        "investor": {},
        "repository": {}
    }
    
    # Create companies
    for company in SAMPLE_COMPANIES:
        entity_id = create_sample_entity(db_session, company)
        if entity_id:
            entity_map["company"][company["name"]] = entity_id
    
    # Create people
    for person in SAMPLE_PEOPLE:
        entity_id = create_sample_entity(db_session, person)
        if entity_id:
            entity_map["person"][person["name"]] = entity_id
    
    # Create investors
    for investor in SAMPLE_INVESTORS:
        entity_id = create_sample_entity(db_session, investor)
        if entity_id:
            entity_map["investor"][investor["name"]] = entity_id
    
    # Create repositories
    for repo in SAMPLE_REPOSITORIES:
        entity_id = create_sample_entity(db_session, repo)
        if entity_id:
            entity_map["repository"][repo["name"]] = entity_id
    
    # Create relationships
    for relationship in SAMPLE_RELATIONSHIPS:
        create_sample_relationship(db_session, relationship, entity_map)
    
    # Close session
    db_session.close()
    
    logger.info("Database seeding complete")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the knowledge graph database with sample data.")
    parser.add_argument("--force", action="store_true", help="Force database seeding even if data exists")
    args = parser.parse_args()
    
    sys.exit(seed_database())