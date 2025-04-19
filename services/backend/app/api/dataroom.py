"""
API routes for the Data Room service.

This module provides endpoints to access data rooms created for
green-lit companies.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Path, Response, Depends
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/dataroom", tags=["dataroom"])

# Root directory for data rooms
DATA_ROOM_ROOT = "data/datarooms"


class DataRoomMetadata(BaseModel):
    """Model for data room metadata."""
    company_id: str
    name: str
    available_files: List[str]
    summary_html: Optional[str] = None
    generation_timestamp: Optional[str] = None


@router.get("/{company_id}", response_model=DataRoomMetadata)
async def get_dataroom(
    company_id: str = Path(..., description="Company ID to retrieve data room for")
):
    """
    Get metadata about a company's data room.
    
    Args:
        company_id: ID of the company
        
    Returns:
        DataRoomMetadata: Metadata about the data room
    """
    # Check if data room exists
    dataroom_path = os.path.join(DATA_ROOM_ROOT, company_id)
    if not os.path.exists(dataroom_path):
        raise HTTPException(status_code=404, detail=f"Data room for company {company_id} not found")
    
    try:
        # Load company data
        with open(os.path.join(dataroom_path, "company_data.json"), "r") as f:
            company_data = json.load(f)
        
        # Get list of available files
        files = os.listdir(dataroom_path)
        
        # Load summary.md content
        summary_html = None
        if "summary.md" in files:
            with open(os.path.join(dataroom_path, "summary.md"), "r") as f:
                summary_html = f.read()
        
        return DataRoomMetadata(
            company_id=company_id,
            name=company_data.get("name", f"Company {company_id}"),
            available_files=files,
            summary_html=summary_html,
            generation_timestamp=company_data.get("generation_timestamp")
        )
    
    except Exception as e:
        logger.error(f"Error retrieving data room for company {company_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data room: {str(e)}")


@router.get("/{company_id}/data", response_model=Dict[str, Any])
async def get_dataroom_data(
    company_id: str = Path(..., description="Company ID to retrieve data for")
):
    """
    Get raw JSON data for a company.
    
    Args:
        company_id: ID of the company
        
    Returns:
        Dict: Raw company data
    """
    # Check if data room exists
    data_path = os.path.join(DATA_ROOM_ROOT, company_id, "company_data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail=f"Data for company {company_id} not found")
    
    try:
        # Load company data
        with open(data_path, "r") as f:
            company_data = json.load(f)
        
        return company_data
    
    except Exception as e:
        logger.error(f"Error retrieving data for company {company_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")


@router.get("/{company_id}/file/{filename}")
async def get_dataroom_file(
    company_id: str = Path(..., description="Company ID to retrieve file for"),
    filename: str = Path(..., description="Name of the file to retrieve")
):
    """
    Get a specific file from a company's data room.
    
    Args:
        company_id: ID of the company
        filename: Name of the file to retrieve
        
    Returns:
        Response: File content with appropriate content type
    """
    # Check if file exists
    file_path = os.path.join(DATA_ROOM_ROOT, company_id, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found for company {company_id}")
    
    try:
        # Determine content type based on file extension
        content_type = "application/octet-stream"  # Default
        if filename.endswith(".json"):
            content_type = "application/json"
        elif filename.endswith(".md"):
            content_type = "text/markdown"
        elif filename.endswith(".pdf"):
            content_type = "application/pdf"
        elif filename.endswith(".txt"):
            content_type = "text/plain"
        
        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()
        
        return Response(content=content, media_type=content_type)
    
    except Exception as e:
        logger.error(f"Error retrieving file {filename} for company {company_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")


@router.get("/", response_model=List[Dict[str, Any]])
async def list_datarooms():
    """
    List all available data rooms.
    
    Returns:
        List[Dict]: List of data room metadata
    """
    try:
        # Ensure data room directory exists
        os.makedirs(DATA_ROOM_ROOT, exist_ok=True)
        
        # Get list of company directories
        if not os.path.exists(DATA_ROOM_ROOT):
            return []
            
        company_dirs = [d for d in os.listdir(DATA_ROOM_ROOT) 
                      if os.path.isdir(os.path.join(DATA_ROOM_ROOT, d))]
        
        datarooms = []
        for company_id in company_dirs:
            try:
                # Check if company_data.json exists
                data_path = os.path.join(DATA_ROOM_ROOT, company_id, "company_data.json")
                if os.path.exists(data_path):
                    with open(data_path, "r") as f:
                        company_data = json.load(f)
                    
                    datarooms.append({
                        "company_id": company_id,
                        "name": company_data.get("name", f"Company {company_id}"),
                        "radar_score": company_data.get("radar_score", 0.0)
                    })
            except Exception as e:
                logger.warning(f"Error processing data room for company {company_id}: {str(e)}")
                # Skip this data room and continue with the rest
        
        return datarooms
    
    except Exception as e:
        logger.error(f"Error listing data rooms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing data rooms: {str(e)}")