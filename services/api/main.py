from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
import time
import uuid
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI.VC API Service",
    description="Centralized API service for AI.VC platform",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary in-memory database for testing (will be replaced with Supabase)
COMPANIES_DB = {}
DEALS_DB = {}
USERS_DB = {}
PORTFOLIOS_DB = {}

# Pydantic models
class Company(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CompanyCreate(BaseModel):
    name: str
    description: str
    metadata: Optional[Dict[str, Any]] = None

class Deal(BaseModel):
    id: str
    company_id: str
    deal_size: float
    equity_percentage: float
    status: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DealCreate(BaseModel):
    company_id: str
    deal_size: float
    equity_percentage: float
    status: str = "pending"

# API Health endpoint
@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "database": "in-memory", # Will be "supabase" when connected
        "services": {
            "api": "healthy",
            "worker": "healthy" if check_worker_health() else "degraded"
        }
    }

# Simple worker health check
def check_worker_health():
    # This will be implemented with a Redis ping to the worker service
    # For now, just return True
    return True

# Company endpoints
@app.post("/api/companies", response_model=Company, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate):
    try:
        company_id = str(uuid.uuid4())
        new_company = Company(
            id=company_id,
            name=company.name,
            description=company.description,
            metadata=company.metadata or {}
        )
        COMPANIES_DB[company_id] = new_company
        logger.info(f"Created new company: {company_id}")
        return new_company
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create company: {str(e)}")

@app.get("/api/companies", response_model=List[Company])
def list_companies():
    try:
        return list(COMPANIES_DB.values())
    except Exception as e:
        logger.error(f"Error listing companies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list companies: {str(e)}")

@app.get("/api/companies/{company_id}", response_model=Company)
def get_company(company_id: str):
    try:
        if company_id not in COMPANIES_DB:
            raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
        return COMPANIES_DB[company_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get company: {str(e)}")

# Deal endpoints
@app.post("/api/deals", response_model=Deal, status_code=status.HTTP_201_CREATED)
def create_deal(deal: DealCreate):
    try:
        if deal.company_id not in COMPANIES_DB:
            raise HTTPException(status_code=404, detail=f"Company with ID {deal.company_id} not found")
        
        deal_id = str(uuid.uuid4())
        new_deal = Deal(
            id=deal_id,
            company_id=deal.company_id,
            deal_size=deal.deal_size,
            equity_percentage=deal.equity_percentage,
            status=deal.status
        )
        DEALS_DB[deal_id] = new_deal
        logger.info(f"Created new deal: {deal_id}")
        return new_deal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating deal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create deal: {str(e)}")

@app.get("/api/deals", response_model=List[Deal])
def list_deals():
    try:
        return list(DEALS_DB.values())
    except Exception as e:
        logger.error(f"Error listing deals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list deals: {str(e)}")

# Add some test data
@app.post("/api/seed-test-data")
def seed_test_data():
    try:
        # Create companies
        company1 = Company(
            id="comp-001",
            name="VectorSync AI",
            description="Autonomous data integration platform",
            metadata={"sector": "AI/ML", "stage": "Series A", "location": "San Francisco, CA"}
        )
        company2 = Company(
            id="comp-002",
            name="Quantum Mesh",
            description="Quantum computing network infrastructure",
            metadata={"sector": "Quantum Computing", "stage": "Seed", "location": "Boston, MA"}
        )
        COMPANIES_DB[company1.id] = company1
        COMPANIES_DB[company2.id] = company2
        
        # Create deals
        deal1 = Deal(
            id="deal-001",
            company_id="comp-001",
            deal_size=5000000,
            equity_percentage=12.5,
            status="closed"
        )
        deal2 = Deal(
            id="deal-002",
            company_id="comp-002",
            deal_size=2000000,
            equity_percentage=15.0,
            status="pending"
        )
        DEALS_DB[deal1.id] = deal1
        DEALS_DB[deal2.id] = deal2
        
        return {"message": "Test data seeded successfully"}
    except Exception as e:
        logger.error(f"Error seeding test data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to seed test data: {str(e)}")