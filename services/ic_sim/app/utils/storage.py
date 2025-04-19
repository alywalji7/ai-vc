"""
Storage utilities for the Investment Committee Simulator.

This module handles logging the entire analysis chain to S3-compatible
Minio storage for audit purposes.
"""

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict

from minio import Minio
from minio.error import S3Error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Minio configuration from environment variables
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "false").lower() == "true"
IC_LOGS_BUCKET = os.environ.get("IC_LOGS_BUCKET", "ic-analysis-logs")


class MinioLogger:
    """
    Handles interaction with Minio for storing analysis logs.
    """
    
    def __init__(self):
        """Initialize the Minio client."""
        self.client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure that the logging bucket exists, creating it if necessary."""
        try:
            if not self.client.bucket_exists(IC_LOGS_BUCKET):
                logger.info(f"Creating bucket: {IC_LOGS_BUCKET}")
                self.client.make_bucket(IC_LOGS_BUCKET)
                logger.info(f"Bucket created: {IC_LOGS_BUCKET}")
            else:
                logger.info(f"Bucket already exists: {IC_LOGS_BUCKET}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {str(e)}")
            # Don't fail if bucket creation fails - we'll just log to console instead
    
    def log_analysis(self, company_id: str, analysis_data: Dict[str, Any]) -> str:
        """
        Log the complete analysis chain to Minio for audit purposes.
        
        Args:
            company_id: ID of the company being analyzed
            analysis_data: Complete analysis data
            
        Returns:
            Object path in Minio
        """
        try:
            # Prepare timestamp-based object name
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            object_name = f"{company_id}/{timestamp}_analysis.json"
            
            # Convert analysis data to JSON
            data_json = json.dumps(analysis_data, indent=2)
            
            # Log to console as backup
            logger.info(f"Logging analysis for company {company_id}")
            
            # Upload to Minio
            self.client.put_object(
                bucket_name=IC_LOGS_BUCKET,
                object_name=object_name,
                data=data_json.encode('utf-8'),
                length=len(data_json),
                content_type="application/json"
            )
            
            logger.info(f"Analysis logged to Minio: {object_name}")
            return object_name
            
        except S3Error as e:
            logger.error(f"Error logging to Minio: {str(e)}")
            logger.info("Falling back to console logging")
            # Log to console as fallback
            logger.info(f"Analysis for company {company_id}: {json.dumps(analysis_data)}")
            return None