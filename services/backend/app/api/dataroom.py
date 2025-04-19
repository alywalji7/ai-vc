"""
Data Room API endpoints

This module provides the API endpoints for the data room service,
allowing access to company data, files, and summary information.
"""
import os
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

router = APIRouter(prefix="/dataroom", tags=["dataroom"])

# Path to data rooms directory - must be from the project root, not the backend service directory
# Go up four levels from this file: app/api -> app -> services/backend -> services -> root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
DATAROOMS_DIR = os.path.join(PROJECT_ROOT, "data", "datarooms")

# Debug: Print the absolute path
print(f"DATAROOMS_DIR absolute path: {os.path.abspath(DATAROOMS_DIR)}")


class DataRoom(BaseModel):
    """Model for a data room."""
    id: str
    name: str
    radar_score: float
    generation_timestamp: str


class DataRoomList(BaseModel):
    """Model for a list of data rooms."""
    datarooms: List[DataRoom]


@router.get("", response_model=DataRoomList)
async def list_datarooms() -> Dict[str, Any]:
    """
    List all available data rooms.
    
    Returns:
        Dictionary with a list of data rooms
    """
    datarooms = []
    
    # Check if the directory exists
    if not os.path.exists(DATAROOMS_DIR):
        print(f"Directory {DATAROOMS_DIR} does not exist")
        return {"datarooms": []}
    
    print(f"Directory {DATAROOMS_DIR} exists, listing content:")
    
    # List all subdirectories (company IDs)
    try:
        all_items = os.listdir(DATAROOMS_DIR)
        print(f"Items in {DATAROOMS_DIR}: {all_items}")
        
        for company_id in all_items:
            company_dir = os.path.join(DATAROOMS_DIR, company_id)
            print(f"Checking {company_dir}")
            
            if os.path.isdir(company_dir):
                print(f"{company_dir} is a directory")
                # Look for company_data.json
                data_file = os.path.join(company_dir, "company_data.json")
                
                if os.path.exists(data_file):
                    print(f"Found data file at {data_file}")
                    try:
                        with open(data_file, "r") as f:
                            company_data = json.load(f)
                            
                        datarooms.append({
                            "id": company_data.get("id", company_id),
                            "name": company_data.get("name", f"Company {company_id}"),
                            "radar_score": company_data.get("radar_score", 0.0),
                            "generation_timestamp": company_data.get("generation_timestamp", "")
                        })
                        print(f"Added dataroom for {company_id}")
                    except Exception as e:
                        print(f"Error reading data for {company_id}: {e}")
                else:
                    print(f"No data file found at {data_file}")
            else:
                print(f"{company_dir} is not a directory")
    except Exception as e:
        print(f"Error listing directory {DATAROOMS_DIR}: {e}")
    
    print(f"Returning {len(datarooms)} datarooms")
    return {"datarooms": datarooms}


@router.get("/{company_id}", response_model=Dict[str, Any])
async def get_dataroom(company_id: str) -> Dict[str, Any]:
    """
    Get details for a specific data room.
    
    Args:
        company_id: ID of the company
        
    Returns:
        Dictionary with data room details
    """
    company_dir = os.path.join(DATAROOMS_DIR, company_id)
    
    if not os.path.exists(company_dir):
        raise HTTPException(status_code=404, detail=f"Data room for company {company_id} not found")
    
    # Get company data
    data_file = os.path.join(company_dir, "company_data.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail=f"Data for company {company_id} not found")
    
    try:
        with open(data_file, "r") as f:
            company_data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading company data: {str(e)}")
    
    # Get summary markdown
    summary_file = os.path.join(company_dir, "summary.md")
    summary_content = ""
    
    if os.path.exists(summary_file):
        try:
            with open(summary_file, "r") as f:
                summary_content = f.read()
        except Exception as e:
            print(f"Error reading summary for {company_id}: {e}")
    
    # Get list of available files
    files = []
    for filename in os.listdir(company_dir):
        if os.path.isfile(os.path.join(company_dir, filename)) and filename not in ["company_data.json", "summary.md"]:
            files.append(filename)
    
    return {
        "company_data": company_data,
        "summary": summary_content,
        "files": files
    }


@router.get("/{company_id}/data", response_model=Dict[str, Any])
async def get_company_data(company_id: str) -> Dict[str, Any]:
    """
    Get raw data for a specific company.
    
    Args:
        company_id: ID of the company
        
    Returns:
        Dictionary with company data
    """
    data_file = os.path.join(DATAROOMS_DIR, company_id, "company_data.json")
    
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail=f"Data for company {company_id} not found")
    
    try:
        with open(data_file, "r") as f:
            company_data = json.load(f)
        return company_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading company data: {str(e)}")


@router.get("/{company_id}/summary")
async def get_company_summary(company_id: str) -> Dict[str, str]:
    """
    Get summary markdown for a specific company.
    
    Args:
        company_id: ID of the company
        
    Returns:
        Dictionary with summary markdown
    """
    summary_file = os.path.join(DATAROOMS_DIR, company_id, "summary.md")
    
    if not os.path.exists(summary_file):
        raise HTTPException(status_code=404, detail=f"Summary for company {company_id} not found")
    
    try:
        with open(summary_file, "r") as f:
            summary_content = f.read()
        return {"summary": summary_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading summary: {str(e)}")


@router.get("/{company_id}/file/{filename}")
async def get_company_file(company_id: str, filename: str) -> Response:
    """
    Get a file from a company's data room.
    
    Args:
        company_id: ID of the company
        filename: Name of the file
        
    Returns:
        File content with appropriate content type
    """
    file_path = os.path.join(DATAROOMS_DIR, company_id, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found for company {company_id}")
    
    try:
        # Determine content type based on file extension
        content_type = "application/octet-stream"  # Default
        if filename.endswith(".pdf"):
            content_type = "application/pdf"
        elif filename.endswith(".json"):
            content_type = "application/json"
        elif filename.endswith(".md"):
            content_type = "text/markdown"
        elif filename.endswith(".txt"):
            content_type = "text/plain"
        
        # Read the file
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Return file with appropriate content type
        return Response(content=content, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")