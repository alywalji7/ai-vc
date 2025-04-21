"""
Main module for the Portfolio Telemetry service.

This module provides a FastAPI application for monitoring portfolio companies
and making follow-on investment decisions.
"""
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from models import PortfolioCompany, FinancialMetric, FollowOnDecision, get_db
from data.banking_connector import BankingConnector
from data.stripe_connector import StripeConnector
from data.follow_on_engine import FollowOnEngine
from tests.data_generator import generate_test_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio Telemetry & Follow-On Engine",
    description="Service for monitoring portfolio company performance and making follow-on investment decisions",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background scheduler for periodic tasks
scheduler = BackgroundScheduler()

# Get configuration from environment
BANKING_CSV_DIR = os.environ.get("BANKING_CSV_DIR", "data/banking_csvs")

@lru_cache()
def get_banking_connector(db: Session = Depends(get_db)) -> BankingConnector:
    """
    Get a singleton BankingConnector instance.
    
    Args:
        db: Database session
        
    Returns:
        BankingConnector instance
    """
    return BankingConnector(db, BANKING_CSV_DIR)

@lru_cache()
def get_stripe_connector(db: Session = Depends(get_db)) -> StripeConnector:
    """
    Get a singleton StripeConnector instance.
    
    Args:
        db: Database session
        
    Returns:
        StripeConnector instance
    """
    return StripeConnector(db)

@lru_cache()
def get_follow_on_engine(db: Session = Depends(get_db)) -> FollowOnEngine:
    """
    Get a singleton FollowOnEngine instance.
    
    Args:
        db: Database session
        
    Returns:
        FollowOnEngine instance
    """
    return FollowOnEngine(db)

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    """
    logger.info("Database initialized")
    
    # Schedule banking data collection job (every 24 hours at 2 AM)
    scheduler.add_job(
        collect_financial_data,
        CronTrigger(hour=2, minute=0),
        id="collect_financial_data",
        name="Collect financial data every 24 hours",
        replace_existing=True,
    )
    
    # Schedule follow-on analysis job (every 24 hours at 4 AM)
    scheduler.add_job(
        analyze_portfolio,
        CronTrigger(hour=4, minute=0),
        id="analyze_portfolio",
        name="Analyze portfolio companies every 24 hours",
        replace_existing=True,
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Background scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    """
    scheduler.shutdown()
    logger.info("Background scheduler shut down")

# API endpoints

@app.get("/", tags=["Status"])
async def root():
    """
    Root endpoint.
    """
    return {
        "service": "Portfolio Telemetry & Follow-On Engine",
        "status": "operational",
        "version": "1.0.0",
    }

@app.get("/companies", tags=["Companies"], response_model=List[Dict[str, Any]])
async def get_companies(db: Session = Depends(get_db)):
    """
    Get all portfolio companies.
    """
    companies = db.query(PortfolioCompany).all()
    return [
        {
            "id": company.id,
            "name": company.name,
            "description": company.description,
            "sector": company.sector.value,
            "stage": company.stage.value,
            "investment_date": company.investment_date,
            "investment_amount": company.investment_amount,
            "ownership_percentage": company.ownership_percentage,
            "valuation_at_investment": company.valuation_at_investment,
        }
        for company in companies
    ]

@app.get("/companies/{company_id}", tags=["Companies"], response_model=Dict[str, Any])
async def get_company(company_id: str, db: Session = Depends(get_db)):
    """
    Get a specific portfolio company.
    """
    company = db.query(PortfolioCompany).filter_by(id=company_id).first()
    
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
    
    return {
        "id": company.id,
        "name": company.name,
        "description": company.description,
        "sector": company.sector.value,
        "stage": company.stage.value,
        "investment_date": company.investment_date,
        "investment_amount": company.investment_amount,
        "ownership_percentage": company.ownership_percentage,
        "valuation_at_investment": company.valuation_at_investment,
    }

@app.get("/companies/{company_id}/metrics", tags=["Metrics"], response_model=List[Dict[str, Any]])
async def get_company_metrics(
    company_id: str, 
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get financial metrics for a specific company.
    
    Args:
        company_id: ID of the company
        days: Number of days of history to retrieve
    """
    company = db.query(PortfolioCompany).filter_by(id=company_id).first()
    
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
    
    # Get metrics within the specified time range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    metrics = db.query(FinancialMetric).filter(
        FinancialMetric.company_id == company_id,
        FinancialMetric.date >= start_date
    ).order_by(FinancialMetric.date.desc()).all()
    
    return [
        {
            "id": metric.id,
            "date": metric.date,
            "cash_balance": metric.cash_balance,
            "burn_rate": metric.burn_rate,
            "runway_months": metric.runway_months,
            "mrr": metric.mrr,
            "arr": metric.arr,
            "revenue_growth": metric.revenue_growth,
            "customer_count": metric.customer_count,
            "new_customers": metric.new_customers,
            "churned_customers": metric.churned_customers,
            "churn_rate": metric.churn_rate,
        }
        for metric in metrics
    ]

@app.get("/companies/{company_id}/follow-on", tags=["Follow-On"], response_model=Dict[str, Any])
async def get_follow_on_decision(
    company_id: str,
    db: Session = Depends(get_db),
    follow_on_engine: FollowOnEngine = Depends(get_follow_on_engine)
):
    """
    Get the latest follow-on decision for a specific company.
    """
    company = db.query(PortfolioCompany).filter_by(id=company_id).first()
    
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
    
    # Check if there's a recent decision in the database
    recent_decision = db.query(FollowOnDecision).filter(
        FollowOnDecision.company_id == company_id,
        FollowOnDecision.date >= datetime.utcnow() - timedelta(days=7)
    ).order_by(FollowOnDecision.date.desc()).first()
    
    if recent_decision:
        return {
            "id": recent_decision.id,
            "company_id": recent_decision.company_id,
            "date": recent_decision.date,
            "trigger_type": recent_decision.trigger_type,
            "recommended_amount": recent_decision.recommended_amount,
            "super_pro_rata": recent_decision.super_pro_rata,
            "expected_runway_extension": recent_decision.expected_runway_extension,
            "expected_ownership_increase": recent_decision.expected_ownership_increase,
            "analysis": recent_decision.analysis,
            "approved": recent_decision.approved,
            "executed": recent_decision.executed,
            "execution_date": recent_decision.execution_date,
            "actual_amount": recent_decision.actual_amount,
            "is_recent": True
        }
    
    # Generate a new decision
    decision = follow_on_engine.follow_on_decision(company_id)
    
    if not decision:
        return {
            "company_id": company_id,
            "date": datetime.utcnow(),
            "trigger_type": None,
            "analysis": "No follow-on investment needed at this time.",
            "is_recent": False
        }
    
    return decision

@app.post("/collect-data", tags=["Data Collection"], response_model=Dict[str, Any])
async def collect_data_endpoint(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger data collection from all sources.
    """
    background_tasks.add_task(collect_financial_data, db)
    
    return {
        "status": "success",
        "message": "Data collection started in the background"
    }

@app.post("/analyze", tags=["Follow-On"], response_model=Dict[str, Any])
async def analyze_endpoint(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger follow-on analysis for all companies.
    """
    background_tasks.add_task(analyze_portfolio, db)
    
    return {
        "status": "success",
        "message": "Portfolio analysis started in the background"
    }

@app.post("/seed-test-data", tags=["Testing"], response_model=Dict[str, Any])
async def seed_test_data(db: Session = Depends(get_db)):
    """
    Seed the database with test data.
    """
    result = generate_test_data(db)
    
    return {
        "status": "success",
        "message": "Test data seeded successfully",
        "data": result
    }

# Background tasks

def collect_financial_data(db: Session = None):
    """
    Collect financial data from all sources.
    
    Args:
        db: Database session (optional, will be created if not provided)
    """
    if db is None:
        # Create a new session if one wasn't provided
        db_generator = get_db()
        db = next(db_generator)
    
    try:
        logger.info("Starting financial data collection")
        
        # Process banking CSV files
        banking_connector = BankingConnector(db, BANKING_CSV_DIR)
        banking_results = banking_connector.process_all_companies()
        
        # Process Stripe data
        stripe_connector = StripeConnector(db)
        stripe_results = stripe_connector.process_all_companies()
        
        logger.info(f"Completed financial data collection: {len(banking_results)} banking sources, {len(stripe_results)} Stripe sources")
        
    except Exception as e:
        logger.error(f"Error collecting financial data: {str(e)}")
    
    finally:
        if db is not None:
            db.close()

def analyze_portfolio(db: Session = None):
    """
    Analyze all portfolio companies for follow-on investments.
    
    Args:
        db: Database session (optional, will be created if not provided)
    """
    if db is None:
        # Create a new session if one wasn't provided
        db_generator = get_db()
        db = next(db_generator)
    
    try:
        logger.info("Starting portfolio analysis")
        
        # Run the follow-on engine
        follow_on_engine = FollowOnEngine(db)
        decisions = follow_on_engine.analyze_all_companies()
        
        logger.info(f"Completed portfolio analysis: {len(decisions)} follow-on opportunities identified")
        
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
    
    finally:
        if db is not None:
            db.close()

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)