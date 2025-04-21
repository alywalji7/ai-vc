"""
Test data generator for the Portfolio Telemetry service.

This module provides functions to generate test data for portfolio companies,
their financial metrics, and follow-on investment decisions.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from random import uniform, randint, choice

from sqlalchemy.orm import Session

from models.database import (
    PortfolioCompany, FinancialMetric, FollowOnDecision,
    CompanySector, CompanyStage
)

# Configure logging
logger = logging.getLogger(__name__)

def generate_test_data(db: Session) -> Dict[str, Any]:
    """
    Generate test data for portfolio companies and financial metrics.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with information about the generated data
    """
    # Clear existing data
    db.query(FollowOnDecision).delete()
    db.query(FinancialMetric).delete()
    db.query(PortfolioCompany).delete()
    db.commit()
    
    # Create test companies
    companies = [
        PortfolioCompany(
            id="highgrowth-saas-1",
            name="HighGrowth SaaS Inc.",
            description="B2B SaaS platform for workflow automation with exceptional growth.",
            sector=CompanySector.SAAS,
            stage=CompanyStage.SERIES_A,
            investment_date=datetime(2024, 8, 15),
            investment_amount=2000000.0,
            ownership_percentage=15.0,
            valuation_at_investment=13500000.0
        ),
        PortfolioCompany(
            id="lowrunway-hardware-1",
            name="LowRunway Hardware LLC",
            description="IoT hardware startup with innovative sensors but high burn rate.",
            sector=CompanySector.HARDWARE,
            stage=CompanyStage.SEED,
            investment_date=datetime(2024, 11, 5),
            investment_amount=1200000.0,
            ownership_percentage=12.0,
            valuation_at_investment=10000000.0
        ),
        PortfolioCompany(
            id="stable-fintech-1",
            name="Stable FinTech Co.",
            description="Fintech company with stable growth and good unit economics.",
            sector=CompanySector.FINTECH,
            stage=CompanyStage.SERIES_B,
            investment_date=datetime(2024, 3, 10),
            investment_amount=4500000.0,
            ownership_percentage=8.0,
            valuation_at_investment=56000000.0
        )
    ]
    
    for company in companies:
        db.add(company)
    
    db.commit()
    logger.info(f"Created {len(companies)} test companies")
    
    # Generate financial metrics
    metrics_data = []
    
    # Current date for the test data
    current_date = datetime.now()
    
    # Generate three months of data with entries every 7 days
    for days_ago in range(0, 90, 7):
        date = current_date - timedelta(days=days_ago)
        
        # High growth SaaS company metrics
        metrics_data.append(FinancialMetric(
            company_id="highgrowth-saas-1",
            date=date,
            cash_balance=2500000.0 - (50000.0 * days_ago / 30),  # Declining cash balance
            burn_rate=300000.0,
            runway_months=8.0 - (0.5 * days_ago / 30),  # Declining runway
            mrr=250000.0 + (25000.0 * days_ago / 30),  # Increasing MRR (looking backward)
            arr=3000000.0 + (300000.0 * days_ago / 30),
            revenue_growth=25.0 - (5.0 * days_ago / 90),  # Sustained high growth
            customer_count=120 - (days_ago // 15),
            new_customers=15 - (days_ago // 30),
            churned_customers=3,
            churn_rate=2.5
        ))
        
        # Low runway hardware company metrics
        metrics_data.append(FinancialMetric(
            company_id="lowrunway-hardware-1",
            date=date,
            cash_balance=550000.0 - (120000.0 * days_ago / 30),  # Rapidly declining cash
            burn_rate=130000.0,
            runway_months=4.0 - (0.8 * days_ago / 30),  # Very low runway
            mrr=50000.0 + (5000.0 * days_ago / 30),
            arr=600000.0 + (60000.0 * days_ago / 30),
            revenue_growth=10.0 - (days_ago / 45),
            customer_count=25 - (days_ago // 30),
            new_customers=3 - (days_ago // 45),
            churned_customers=1,
            churn_rate=4.0
        ))
        
        # Stable fintech company metrics
        metrics_data.append(FinancialMetric(
            company_id="stable-fintech-1",
            date=date,
            cash_balance=5000000.0 - (100000.0 * days_ago / 30),  # Slowly declining cash
            burn_rate=200000.0,
            runway_months=24.0 - (0.5 * days_ago / 30),  # Healthy runway
            mrr=500000.0 + (15000.0 * days_ago / 30),
            arr=6000000.0 + (180000.0 * days_ago / 30),
            revenue_growth=8.0 - (days_ago / 60),  # Steady growth
            customer_count=300 - (days_ago // 15),
            new_customers=12 - (days_ago // 30),
            churned_customers=5,
            churn_rate=1.6
        ))
    
    for metric in metrics_data:
        db.add(metric)
    
    db.commit()
    logger.info(f"Created {len(metrics_data)} financial metric records")
    
    return {
        "companies": [c.id for c in companies],
        "metrics_count": len(metrics_data),
        "date_range": f"{(current_date - timedelta(days=90)).strftime('%Y-%m-%d')} to {current_date.strftime('%Y-%m-%d')}"
    }