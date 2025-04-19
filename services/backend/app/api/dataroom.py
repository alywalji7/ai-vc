"""
Data Room API routes.

This module provides endpoints for:
1. Retrieving a list of available data rooms
2. Getting details of a specific data room
"""

import os
import json
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Path, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/dataroom", tags=["dataroom"])


class DataRoomMetadata(BaseModel):
    """Model for data room metadata."""
    company_id: str
    company_name: str
    date_created: str
    last_updated: str
    status: str


class DataRoom(BaseModel):
    """Model for data room details."""
    company_id: str
    company_name: str
    date_created: str
    last_updated: str
    status: str
    financials: Dict[str, Any] = {}
    team: Dict[str, Any] = {}
    tech: Dict[str, Any] = {}
    market: Dict[str, Any] = {}
    legal: Dict[str, Any] = {}
    documents: List[Dict[str, Any]] = []


@router.get("/")
async def list_datarooms() -> Dict[str, List[DataRoomMetadata]]:
    """
    Get a list of available data rooms.
    
    Returns:
        Dictionary containing a list of data room metadata
    """
    datarooms_dir = os.environ.get("DATAROOMS_DIR", "data/datarooms")
    datarooms = []
    
    print(f"Directory {datarooms_dir} exists, listing content:")
    
    if os.path.exists(datarooms_dir):
        print(f"Items in {datarooms_dir}: {os.listdir(datarooms_dir)}")
        
        for item in os.listdir(datarooms_dir):
            item_path = os.path.join(datarooms_dir, item)
            print(f"Checking {item_path}")
            
            if os.path.isdir(item_path):
                print(f"{item_path} is a directory")
                data_file = os.path.join(item_path, "company_data.json")
                
                if os.path.exists(data_file):
                    print(f"Found data file at {data_file}")
                    try:
                        with open(data_file, "r") as f:
                            data = json.load(f)
                            
                            datarooms.append(DataRoomMetadata(
                                company_id=item,
                                company_name=data.get("name", f"Company {item}"),
                                date_created=data.get("date_created", "2025-01-01"),
                                last_updated=data.get("last_updated", "2025-01-01"),
                                status=data.get("status", "active")
                            ))
                            print(f"Added dataroom for {item}")
                    except Exception as e:
                        print(f"Error loading data file {data_file}: {str(e)}")
    
    print(f"Returning {len(datarooms)} datarooms")
    return {
        "datarooms": datarooms
    }


@router.get("/{company_id}")
async def get_dataroom(company_id: str = Path(..., description="ID of the company")) -> DataRoom:
    """
    Get details of a specific data room.
    
    Args:
        company_id: ID of the company
        
    Returns:
        Data room details
    """
    datarooms_dir = os.environ.get("DATAROOMS_DIR", "data/datarooms")
    data_file = os.path.join(datarooms_dir, company_id, "company_data.json")
    
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail=f"Data room for company {company_id} not found")
    
    try:
        with open(data_file, "r") as f:
            data = json.load(f)
            
            return DataRoom(
                company_id=company_id,
                company_name=data.get("name", f"Company {company_id}"),
                date_created=data.get("date_created", "2025-01-01"),
                last_updated=data.get("last_updated", "2025-01-01"),
                status=data.get("status", "active"),
                financials=data.get("financials", {}),
                team=data.get("team", {}),
                tech=data.get("tech", {}),
                market=data.get("market", {}),
                legal=data.get("legal", {}),
                documents=data.get("documents", [])
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data room: {str(e)}")