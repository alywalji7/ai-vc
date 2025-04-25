"""
API Routes for Upload Service.
"""
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.models.db import get_db, UploadedFile
from app.utils.storage import upload_file_to_s3
from app.utils.kafka_producer import kafka_producer

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    lp_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file (PDF, CSV, XLSX) for portfolio parsing.
    
    Args:
        file: The file to upload (max 10MB)
        lp_id: ID of the LP uploading the file
        db: Database session

    Returns:
        dict: Information about the uploaded file
    """
    # Validate file type
    allowed_types = ["pdf", "csv", "xlsx"]
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Must be one of: {', '.join(allowed_types)}"
        )
    
    # Upload file to S3
    upload_result = await upload_file_to_s3(file, lp_id)
    
    if not upload_result["success"]:
        logger.error(f"Failed to upload file: {upload_result['error']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=upload_result["error"]
        )
    
    try:
        # Create record in database
        db_file = UploadedFile(
            lp_id=lp_id,
            filename=upload_result["filename"],
            file_type=upload_result["file_type"],
            s3_key=upload_result["s3_key"],
            size_bytes=upload_result["size_bytes"],
            uploaded_at=datetime.utcnow()
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Publish Kafka event
        kafka_producer.publish_file_uploaded_event(lp_id, upload_result["s3_key"])
        
        return {
            "id": db_file.id,
            "lp_id": db_file.lp_id,
            "filename": db_file.filename,
            "file_type": db_file.file_type,
            "s3_key": db_file.s3_key,
            "size_bytes": db_file.size_bytes,
            "status": db_file.status,
            "uploaded_at": db_file.uploaded_at
        }
        
    except Exception as e:
        logger.error(f"Database error recording file upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record file upload: {str(e)}"
        )

@router.get("/files/{lp_id}")
async def get_files_by_lp(
    lp_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all files uploaded by a specific LP.
    
    Args:
        lp_id: ID of the LP
        db: Database session
        
    Returns:
        list: List of uploaded files
    """
    files = db.query(UploadedFile).filter(UploadedFile.lp_id == lp_id).all()
    
    return [
        {
            "id": file.id,
            "lp_id": file.lp_id,
            "filename": file.filename,
            "file_type": file.file_type,
            "s3_key": file.s3_key,
            "size_bytes": file.size_bytes,
            "status": file.status,
            "uploaded_at": file.uploaded_at,
            "processed_at": file.processed_at
        }
        for file in files
    ]

@router.get("/file/{file_id}")
async def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific uploaded file.
    
    Args:
        file_id: ID of the file
        db: Database session
        
    Returns:
        dict: File details
    """
    file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found"
        )
    
    return {
        "id": file.id,
        "lp_id": file.lp_id,
        "filename": file.filename,
        "file_type": file.file_type,
        "s3_key": file.s3_key,
        "size_bytes": file.size_bytes,
        "status": file.status,
        "error_message": file.error_message,
        "uploaded_at": file.uploaded_at,
        "processed_at": file.processed_at
    }