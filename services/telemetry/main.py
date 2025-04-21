"""
Portfolio Telemetry & Follow-On Engine Service.

This service collects financial data from portfolio companies via
banking CSVs and Stripe API, analyzes the data, and automatically
triggers follow-on investment decisions based on predefined criteria.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from models import PortfolioCompany, FinancialMetric, FollowOnDecision, init_db, get_db
from data import BankingConnector, StripeConnector, FollowOnEngine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Portfolio Telemetry & Follow-On Engine API",
    description="API for monitoring portfolio companies and triggering follow-on investments",
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

# Initialize database
@app.on_event("startup")
async def startup_db_client():
    init_db()
    logger.info("Database initialized")
    
    # Start the scheduler for background tasks
    scheduler = BackgroundScheduler()
    
    # Schedule data collection every 24 hours (at 1:00 AM)
    scheduler.add_job(
        collect_all_data_background,
        trigger=CronTrigger(hour=1, minute=0),
        id="collect_data_job",
        name="Collect financial data every 24 hours",
        replace_existing=True,
    )
    
    # Schedule analysis every 24 hours (at 2:00 AM, after data collection)
    scheduler.add_job(
        analyze_all_companies_background,
        trigger=CronTrigger(hour=2, minute=0),
        id="analyze_companies_job",
        name="Analyze portfolio companies every 24 hours",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info("Background scheduler started")

# Background task functions
def collect_all_data_background():
    """Collect data from all sources for all companies."""
    logger.info("Starting scheduled data collection")
    
    # Get a new database session
    db = next(get_db())
    
    try:
        # Process banking CSVs
        banking_connector = BankingConnector(db)
        banking_results = banking_connector.process_csv_files()
        logger.info(f"Processed {len(banking_results)} banking CSV files")
        
        # Process Stripe data
        stripe_connector = StripeConnector(db)
        stripe_results = stripe_connector.process_all_companies()
        logger.info(f"Processed Stripe data for {len(stripe_results)} companies")
    
    except Exception as e:
        logger.error(f"Error in scheduled data collection: {str(e)}")
    
    finally:
        db.close()
        
def analyze_all_companies_background():
    """Analyze all companies and trigger follow-on decisions."""
    logger.info("Starting scheduled company analysis")
    
    # Get a new database session
    db = next(get_db())
    
    try:
        # Analyze all companies
        follow_on_engine = FollowOnEngine(db)
        decisions = follow_on_engine.analyze_all_companies()
        logger.info(f"Created {len(decisions)} follow-on decisions")
    
    except Exception as e:
        logger.error(f"Error in scheduled company analysis: {str(e)}")
    
    finally:
        db.close()

# API Routes

@app.get("/")
async def root():
    """Root endpoint returning service information."""
    return {
        "service": "Portfolio Telemetry & Follow-On Engine",
        "status": "operational",
        "endpoints": [
            "/companies",
            "/metrics",
            "/decisions",
            "/collect-data",
            "/analyze-companies",
            "/follow-on-decision/{company_id}"
        ]
    }

@app.get("/companies", response_model=List[Dict[str, Any]])
async def get_companies(db: Session = Depends(get_db)):
    """Get all portfolio companies."""
    companies = db.query(PortfolioCompany).all()
    return [{
        "id": company.id,
        "company_id": company.company_id,
        "name": company.name,
        "sector": company.sector,
        "funding_stage": company.funding_stage,
        "investment_date": company.investment_date,
        "investment_amount": company.investment_amount,
        "ownership_percentage": company.ownership_percentage,
        "valuation_at_investment": company.valuation_at_investment
    } for company in companies]

@app.get("/metrics", response_model=List[Dict[str, Any]])
async def get_metrics(
    company_id: Optional[str] = None, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """Get financial metrics for companies."""
    query = db.query(FinancialMetric)
    
    if company_id:
        query = query.filter(FinancialMetric.company_id == company_id)
        
    metrics = query.order_by(FinancialMetric.date.desc()).limit(limit).all()
    
    return [{
        "id": metric.id,
        "company_id": metric.company_id,
        "date": metric.date,
        "cash_balance": metric.cash_balance,
        "cash_burn_rate": metric.cash_burn_rate,
        "runway_months": metric.runway_months,
        "revenue": metric.revenue,
        "revenue_growth_rate": metric.revenue_growth_rate,
        "customer_count": metric.customer_count,
        "customer_growth_rate": metric.customer_growth_rate,
        "churn_rate": metric.churn_rate,
        "growth_vs_peers": metric.growth_vs_peers,
        "data_source": metric.data_source
    } for metric in metrics]

@app.get("/decisions", response_model=List[Dict[str, Any]])
async def get_decisions(
    company_id: Optional[str] = None, 
    status: Optional[str] = None,
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """Get follow-on investment decisions."""
    query = db.query(FollowOnDecision)
    
    if company_id:
        query = query.filter(FollowOnDecision.company_id == company_id)
        
    if status:
        query = query.filter(FollowOnDecision.decision == status)
        
    decisions = query.order_by(FollowOnDecision.decision_date.desc()).limit(limit).all()
    
    return [{
        "id": decision.id,
        "company_id": decision.company_id,
        "decision_date": decision.decision_date,
        "trigger_type": decision.trigger_type,
        "trigger_value": decision.trigger_value,
        "decision": decision.decision,
        "recommended_amount": decision.recommended_amount,
        "recommended_valuation": decision.recommended_valuation,
        "pro_rata_amount": decision.pro_rata_amount,
        "super_pro_rata": decision.super_pro_rata,
        "rationale": decision.rationale
    } for decision in decisions]

@app.post("/collect-data", response_model=Dict[str, Any])
async def collect_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger data collection."""
    background_tasks.add_task(collect_all_data_background)
    return {"status": "data collection started in the background"}

@app.post("/analyze-companies", response_model=Dict[str, Any])
async def analyze_companies(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger company analysis."""
    background_tasks.add_task(analyze_all_companies_background)
    return {"status": "company analysis started in the background"}

@app.post("/follow-on-decision/{company_id}", response_model=Dict[str, Any])
async def trigger_follow_on_decision(company_id: str, db: Session = Depends(get_db)):
    """Manually trigger a follow-on decision for a specific company."""
    # Check if company exists
    company = db.query(PortfolioCompany).filter(PortfolioCompany.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
    
    # Trigger follow-on decision
    follow_on_engine = FollowOnEngine(db)
    decision = follow_on_engine.follow_on_decision(company_id)
    
    if not decision:
        return {"status": "no trigger conditions met for follow-on decision"}
    
    return decision

# Test/Demo data setup endpoint (for acceptance testing)
@app.post("/setup-test-data", response_model=Dict[str, Any])
async def setup_test_data(db: Session = Depends(get_db)):
    """
    Set up test data for acceptance testing.
    
    WARNING: This is for testing only and will create synthetic data in the database.
    """
    from tests.data_generator import generate_test_data
    result = generate_test_data(db)
    return result

# Entry point for running with Uvicorn
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8100))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Portfolio Telemetry service at http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)