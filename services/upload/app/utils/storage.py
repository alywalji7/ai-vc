"""
S3 Storage Utilities for Upload Service.
Handles secure upload and retrieval of files from S3.
"""
import os
import logging
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# S3 configuration
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "lp-uploads")
S3_REGION = os.environ.get("AWS_REGION", "us-east-1")
KMS_KEY_ID = os.environ.get("KMS_KEY_ID")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=S3_REGION,
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)

def get_mime_type(filename):
    """Get MIME type based on file extension."""
    ext = filename.lower().split('.')[-1]
    mime_types = {
        'pdf': 'application/pdf',
        'csv': 'text/csv',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }
    return mime_types.get(ext, 'application/octet-stream')

async def upload_file_to_s3(file: UploadFile, lp_id: str):
    """
    Upload a file to S3 with server-side encryption (SSE-KMS).
    
    Args:
        file: The uploaded file
        lp_id: ID of the LP uploading the file
        
    Returns:
        dict: Information about the uploaded file including the S3 key
    """
    try:
        # Generate a unique S3 key with LP ID as prefix
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = file.filename
        unique_id = str(uuid.uuid4())[:8]
        s3_key = f"{lp_id}/{timestamp}_{unique_id}_{filename}"
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Check if file size exceeds maximum (10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if file_size > max_size:
            return {
                "success": False,
                "error": f"File size ({file_size} bytes) exceeds maximum allowed size (10MB)"
            }
        
        # Get content type
        content_type = get_mime_type(filename)
        
        # Upload to S3 with server-side encryption
        extra_args = {
            'ContentType': content_type,
            'ServerSideEncryption': 'aws:kms',
        }
        
        # Add KMS key ID if provided
        if KMS_KEY_ID:
            extra_args['SSEKMSKeyId'] = KMS_KEY_ID
        
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            **extra_args
        )
        
        # Reset file pointer for potential further use
        await file.seek(0)
        
        return {
            "success": True,
            "s3_key": s3_key,
            "filename": filename,
            "content_type": content_type,
            "size_bytes": file_size,
            "file_type": filename.split('.')[-1].lower()
        }
        
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        return {
            "success": False,
            "error": f"S3 upload error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error uploading file: {str(e)}")
        return {
            "success": False,
            "error": f"Upload error: {str(e)}"
        }

def download_file_from_s3(s3_key):
    """
    Download a file from S3.
    
    Args:
        s3_key: S3 key of the file to download
    
    Returns:
        bytes: File content if successful, None otherwise
    """
    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key
        )
        return response['Body'].read()
    except ClientError as e:
        logger.error(f"Error downloading file from S3: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error downloading file: {str(e)}")
        return None