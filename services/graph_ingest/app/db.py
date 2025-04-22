"""
Database module for the graph ingestion service.

This module contains database connection and initialization logic.
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get database URL from environment or use default
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/aivc"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Create session maker
Session = sessionmaker(bind=engine)

def get_session():
    """
    Get a new database session.
    
    Returns:
        SQLAlchemy session
    """
    return Session()

def init_db():
    """
    Initialize the database with required tables.
    """
    logger.info("Initializing database for graph ingestion service")
    
    try:
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                # Check database connection
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                
                # Check if entities table exists
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'entities')"
                ))
                entities_exists = result.scalar()
                
                # Check if relationships table exists
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'relationships')"
                ))
                relationships_exists = result.scalar()
                
                # Create entities table if it doesn't exist
                if not entities_exists:
                    logger.info("Creating entities table")
                    conn.execute(text("""
                    CREATE TABLE entities (
                        id SERIAL PRIMARY KEY,
                        type VARCHAR(50) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        properties JSONB NOT NULL DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                    """))
                    conn.execute(text("""
                    CREATE INDEX idx_entities_type ON entities (type)
                    """))
                    conn.execute(text("""
                    CREATE INDEX idx_entities_name ON entities (name)
                    """))
                    conn.execute(text("""
                    CREATE INDEX idx_entities_properties ON entities USING GIN (properties)
                    """))
                    logger.info("Created entities table")
                else:
                    logger.info("Entities table already exists")
                
                # Create relationships table if it doesn't exist
                if not relationships_exists:
                    logger.info("Creating relationships table")
                    conn.execute(text("""
                    CREATE TABLE relationships (
                        id SERIAL PRIMARY KEY,
                        source_id INTEGER NOT NULL REFERENCES entities(id),
                        target_id INTEGER NOT NULL REFERENCES entities(id),
                        type VARCHAR(50) NOT NULL,
                        properties JSONB NOT NULL DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        UNIQUE(source_id, target_id, type)
                    )
                    """))
                    conn.execute(text("""
                    CREATE INDEX idx_relationships_source_id ON relationships (source_id)
                    """))
                    conn.execute(text("""
                    CREATE INDEX idx_relationships_target_id ON relationships (target_id)
                    """))
                    conn.execute(text("""
                    CREATE INDEX idx_relationships_type ON relationships (type)
                    """))
                    conn.execute(text("""
                    CREATE INDEX idx_relationships_properties ON relationships USING GIN (properties)
                    """))
                    logger.info("Created relationships table")
                else:
                    logger.info("Relationships table already exists")
                
                transaction.commit()
                logger.info("Database schema setup complete")
                
            except Exception as e:
                transaction.rollback()
                logger.error(f"Error setting up database schema: {str(e)}")
                raise
            
        # Test if tables were actually created
        with engine.connect() as conn:
            try:
                # Test entities table
                result = conn.execute(text("SELECT COUNT(*) FROM entities"))
                entities_count = result.scalar()
                logger.info(f"Entities table check: {entities_count} rows")
                
                # Test relationships table
                result = conn.execute(text("SELECT COUNT(*) FROM relationships"))
                relationships_count = result.scalar()
                logger.info(f"Relationships table check: {relationships_count} rows")
                
                logger.info("Database initialization complete and tables verified")
                
            except Exception as e:
                logger.error(f"Error verifying tables: {str(e)}")
                raise
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise