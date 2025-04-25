"""
Portfolio Parser Worker.

Consumes file_uploaded events from Kafka and processes files to extract portfolio data.
"""
import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from confluent_kafka import Consumer, KafkaError

from app.models.db import UploadedFile, LpHolding, LpFundPosition, Base
from app.utils.storage import download_file_from_s3
from app.utils.portfolio_parser import PortfolioParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_FILE_UPLOADED = "file_uploaded"
KAFKA_GROUP_ID = "portfolio-parser-worker"

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = sqlalchemy.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def parse_portfolio():
    """
    Parse portfolio data from uploaded files.
    Main worker function that consumes Kafka messages and processes files.
    """
    # Create Kafka consumer
    consumer_config = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
    }
    
    consumer = Consumer(consumer_config)
    consumer.subscribe([KAFKA_TOPIC_FILE_UPLOADED])
    
    try:
        logger.info(f"Starting portfolio parser worker, listening on topic {KAFKA_TOPIC_FILE_UPLOADED}")
        
        while True:
            # Poll for messages
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                # No message received
                continue
                
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event - not an error
                    continue
                else:
                    # Error
                    logger.error(f"Kafka error: {msg.error()}")
                    continue
            
            # Process message
            try:
                # Parse message JSON
                message = json.loads(msg.value())
                lp_id = message.get('lp_id')
                file_s3_key = message.get('file_s3_key')
                
                if not lp_id or not file_s3_key:
                    logger.warning(f"Invalid message format: {msg.value()}")
                    consumer.commit(msg)
                    continue
                
                logger.info(f"Processing file upload event for LP {lp_id}, file {file_s3_key}")
                
                # Process the file
                process_file(lp_id, file_s3_key)
                
                # Commit offset
                consumer.commit(msg)
                
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                # Continue processing next message
                continue
                
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down worker")
    finally:
        # Close consumer
        consumer.close()

def process_file(lp_id: str, file_s3_key: str):
    """
    Process an uploaded file.
    
    Args:
        lp_id: ID of the LP that uploaded the file
        file_s3_key: S3 key of the uploaded file
    """
    db = get_db()
    
    try:
        # Get file record from database
        file_record = db.query(UploadedFile).filter(
            UploadedFile.lp_id == lp_id,
            UploadedFile.s3_key == file_s3_key
        ).first()
        
        if not file_record:
            logger.warning(f"File record not found for LP {lp_id}, file {file_s3_key}")
            return
        
        # Download file from S3
        file_content = download_file_from_s3(file_s3_key)
        
        if not file_content:
            logger.error(f"Failed to download file from S3: {file_s3_key}")
            # Update file status to failed
            file_record.status = "failed"
            file_record.error_message = "Failed to download file from S3"
            db.commit()
            return
        
        # Detect file type if not already known
        file_type = file_record.file_type
        if not file_type:
            file_type = PortfolioParser.detect_file_type(file_content)
            file_record.file_type = file_type
        
        # Parse file based on type
        holdings = []
        funds = []
        
        if file_type == 'csv':
            holdings, funds = PortfolioParser.parse_csv(file_content)
        elif file_type == 'xlsx':
            holdings, funds = PortfolioParser.parse_xlsx(file_content)
        elif file_type == 'pdf':
            holdings, funds = PortfolioParser.parse_pdf(file_content)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            file_record.status = "failed"
            file_record.error_message = f"Unsupported file type: {file_type}"
            db.commit()
            return
        
        # If no data was parsed, mark as failed
        if not holdings and not funds:
            logger.warning(f"No portfolio data found in file {file_s3_key}")
            file_record.status = "failed"
            file_record.error_message = "No portfolio data found in file"
            db.commit()
            return
        
        # Store holdings in database
        for holding in holdings:
            # Convert ISO format date strings to datetime objects
            acquisition_date = None
            if holding.get('acquisition_date'):
                try:
                    acquisition_date = datetime.fromisoformat(holding['acquisition_date'])
                except:
                    pass
            
            valuation_date = datetime.utcnow()
            if holding.get('valuation_date'):
                try:
                    valuation_date = datetime.fromisoformat(holding['valuation_date'])
                except:
                    pass
            
            # Create or update holding record
            db_holding = LpHolding(
                lp_id=lp_id,
                company_name=holding['company_name'],
                cost_basis=holding['cost_basis'],
                current_value=holding['current_value'],
                currency=holding.get('currency', 'USD'),
                acquisition_date=acquisition_date,
                valuation_date=valuation_date,
                file_id=file_record.id
            )
            
            db.add(db_holding)
        
        # Store fund positions in database
        for fund in funds:
            # Convert ISO format date string to datetime object
            valuation_date = datetime.utcnow()
            if fund.get('valuation_date'):
                try:
                    valuation_date = datetime.fromisoformat(fund['valuation_date'])
                except:
                    pass
            
            # Create or update fund position record
            db_fund = LpFundPosition(
                lp_id=lp_id,
                fund_name=fund['fund_name'],
                committed_capital=fund['committed_capital'],
                contributed_capital=fund['contributed_capital'],
                remaining_capital=fund.get('remaining_capital'),
                distributed_capital=fund.get('distributed_capital'),
                nav=fund['nav'],
                vintage_year=fund.get('vintage_year'),
                currency=fund.get('currency', 'USD'),
                valuation_date=valuation_date,
                irr=fund.get('irr'),
                tvpi=fund.get('tvpi'),
                dpi=fund.get('dpi'),
                file_id=file_record.id
            )
            
            db.add(db_fund)
        
        # Update file status to processed
        file_record.status = "processed"
        file_record.processed_at = datetime.utcnow()
        
        # Commit all changes
        db.commit()
        
        logger.info(f"Successfully processed file {file_s3_key} for LP {lp_id}")
        logger.info(f"Imported {len(holdings)} direct holdings and {len(funds)} fund positions")
        
    except Exception as e:
        logger.error(f"Error processing file {file_s3_key}: {str(e)}")
        
        # Update file status to failed
        try:
            file_record.status = "failed"
            file_record.error_message = str(e)
            db.commit()
        except:
            pass
        
    finally:
        db.close()

if __name__ == "__main__":
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Start processing
    parse_portfolio()