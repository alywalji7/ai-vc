"""
API Routes for Upload Service.
"""
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from sqlalchemy import func

from app.models.db import get_db, UploadedFile, LpHolding, LpFundPosition
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

@router.get("/holdings/{lp_id}")
async def get_holdings(
    lp_id: str,
    db: Session = Depends(get_db)
):
    """
    Get portfolio company holdings for an LP.
    
    Args:
        lp_id: ID of the LP
        db: Database session
        
    Returns:
        list: List of company holdings
    """
    holdings = db.query(LpHolding).filter(LpHolding.lp_id == lp_id).all()
    
    return [
        {
            "id": holding.id,
            "lp_id": holding.lp_id,
            "company_name": holding.company_name,
            "cost_basis": holding.cost_basis,
            "current_value": holding.current_value,
            "currency": holding.currency,
            "acquisition_date": holding.acquisition_date,
            "valuation_date": holding.valuation_date,
            "notes": holding.notes,
            "file_id": holding.file_id
        }
        for holding in holdings
    ]

@router.get("/funds/{lp_id}")
async def get_funds(
    lp_id: str,
    db: Session = Depends(get_db)
):
    """
    Get fund positions for an LP.
    
    Args:
        lp_id: ID of the LP
        db: Database session
        
    Returns:
        list: List of fund positions
    """
    funds = db.query(LpFundPosition).filter(LpFundPosition.lp_id == lp_id).all()
    
    return [
        {
            "id": fund.id,
            "lp_id": fund.lp_id,
            "fund_name": fund.fund_name,
            "committed_capital": fund.committed_capital,
            "contributed_capital": fund.contributed_capital,
            "remaining_capital": fund.remaining_capital,
            "distributed_capital": fund.distributed_capital,
            "nav": fund.nav,
            "vintage_year": fund.vintage_year,
            "currency": fund.currency,
            "valuation_date": fund.valuation_date,
            "irr": fund.irr,
            "tvpi": fund.tvpi,
            "dpi": fund.dpi,
            "file_id": fund.file_id
        }
        for fund in funds
    ]

@router.get("/summary/{lp_id}")
async def get_portfolio_summary(
    lp_id: str,
    db: Session = Depends(get_db)
):
    """
    Get portfolio summary metrics for an LP.
    
    Args:
        lp_id: ID of the LP
        db: Database session
        
    Returns:
        dict: Portfolio summary metrics
    """
    try:
        # Get holdings summary
        holdings_count = db.query(func.count(LpHolding.id)).filter(LpHolding.lp_id == lp_id).scalar() or 0
        if holdings_count > 0:
            holdings_cost = db.query(func.sum(LpHolding.cost_basis)).filter(LpHolding.lp_id == lp_id).scalar() or 0
            holdings_value = db.query(func.sum(LpHolding.current_value)).filter(LpHolding.lp_id == lp_id).scalar() or 0
            holdings_multiple = holdings_value / holdings_cost if holdings_cost > 0 else 0
        else:
            holdings_cost = 0
            holdings_value = 0
            holdings_multiple = 0
        
        # Get funds summary
        funds_count = db.query(func.count(LpFundPosition.id)).filter(LpFundPosition.lp_id == lp_id).scalar() or 0
        if funds_count > 0:
            committed_capital = db.query(func.sum(LpFundPosition.committed_capital)).filter(LpFundPosition.lp_id == lp_id).scalar() or 0
            contributed_capital = db.query(func.sum(LpFundPosition.contributed_capital)).filter(LpFundPosition.lp_id == lp_id).scalar() or 0
            remaining_capital = db.query(func.sum(LpFundPosition.remaining_capital)).filter(
                LpFundPosition.lp_id == lp_id,
                LpFundPosition.remaining_capital != None
            ).scalar() or 0
            distributed_capital = db.query(func.sum(LpFundPosition.distributed_capital)).filter(
                LpFundPosition.lp_id == lp_id,
                LpFundPosition.distributed_capital != None
            ).scalar() or 0
            nav = db.query(func.sum(LpFundPosition.nav)).filter(LpFundPosition.lp_id == lp_id).scalar() or 0
            
            # Calculate aggregated metrics
            tvpi = (nav + distributed_capital) / contributed_capital if contributed_capital > 0 else 0
            dpi = distributed_capital / contributed_capital if contributed_capital > 0 else 0
            
            # Average IRR (only for funds with IRR data)
            funds_with_irr = db.query(LpFundPosition).filter(
                LpFundPosition.lp_id == lp_id,
                LpFundPosition.irr != None
            ).all()
            
            if funds_with_irr:
                avg_irr = sum(fund.irr for fund in funds_with_irr if fund.irr is not None) / len(funds_with_irr)
            else:
                avg_irr = None
        else:
            committed_capital = 0
            contributed_capital = 0
            remaining_capital = 0
            distributed_capital = 0
            nav = 0
            tvpi = 0
            dpi = 0
            avg_irr = None
        
        # Total portfolio value
        total_value = holdings_value + nav
        
        return {
            "lp_id": lp_id,
            "holdings": {
                "count": holdings_count,
                "cost_basis": holdings_cost,
                "current_value": holdings_value,
                "multiple": holdings_multiple
            },
            "funds": {
                "count": funds_count,
                "committed_capital": committed_capital,
                "contributed_capital": contributed_capital,
                "remaining_capital": remaining_capital,
                "distributed_capital": distributed_capital,
                "nav": nav,
                "tvpi": tvpi,
                "dpi": dpi,
                "avg_irr": avg_irr
            },
            "total_portfolio_value": total_value,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating portfolio summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate portfolio summary: {str(e)}"
        )