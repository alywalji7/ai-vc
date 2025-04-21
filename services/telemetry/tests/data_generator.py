"""
Test data generator for acceptance testing.

This module creates synthetic data for acceptance testing the
Portfolio Telemetry & Follow-On Engine's ability to correctly
trigger follow-on investment decisions.
"""
import logging
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any
from sqlalchemy.orm import Session

from models.database import PortfolioCompany, FinancialMetric, FollowOnDecision

logger = logging.getLogger(__name__)

def generate_test_data(db: Session) -> Dict[str, Any]:
    """
    Generate synthetic test data for acceptance testing.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with information about the generated data
    """
    logger.info("Generating test data for acceptance testing")
    
    # First, clear any existing test data to avoid duplication
    clear_test_data(db)
    
    # Create portfolio companies
    companies = create_test_companies(db)
    
    # Create financial metrics for these companies
    metrics = create_test_metrics(db, companies)
    
    # Return summary information
    return {
        "status": "success",
        "message": "Test data generated successfully",
        "data": {
            "companies": len(companies),
            "metrics_per_company": len(metrics) // len(companies),
            "total_metrics": len(metrics),
            "test_cases": [
                "High-growth SaaS company (should trigger growth-based follow-on)",
                "Low-runway hardware company (should trigger runway-based follow-on)",
                "Stable company (should not trigger any follow-on)",
                "Average performers in various sectors (for peer comparison)"
            ]
        }
    }

def clear_test_data(db: Session) -> None:
    """
    Clear existing test data from the database.
    
    Args:
        db: Database session
    """
    # Delete all decisions
    db.query(FollowOnDecision).delete()
    
    # Delete all metrics
    db.query(FinancialMetric).delete()
    
    # Delete all companies
    db.query(PortfolioCompany).delete()
    
    db.commit()
    logger.info("Cleared existing test data from database")

def create_test_companies(db: Session) -> List[PortfolioCompany]:
    """
    Create test portfolio companies.
    
    Args:
        db: Database session
        
    Returns:
        List of created company objects
    """
    # Define company test data
    company_data = [
        {
            "company_id": "highgrowth-saas-1",
            "name": "RocketMetrics",
            "sector": "SaaS",
            "funding_stage": "Series A",
            "investment_date": datetime.now() - timedelta(days=365),
            "investment_amount": 2000000,
            "ownership_percentage": 15.0,
            "valuation_at_investment": 13000000
        },
        {
            "company_id": "lowrunway-hardware-1",
            "name": "QuantumChips",
            "sector": "Hardware",
            "funding_stage": "Seed",
            "investment_date": datetime.now() - timedelta(days=548),
            "investment_amount": 1000000,
            "ownership_percentage": 12.0,
            "valuation_at_investment": 8000000
        },
        {
            "company_id": "stable-fintech-1",
            "name": "SteadyPay",
            "sector": "Fintech",
            "funding_stage": "Series A",
            "investment_date": datetime.now() - timedelta(days=274),
            "investment_amount": 3000000,
            "ownership_percentage": 10.0,
            "valuation_at_investment": 30000000
        },
        {
            "company_id": "average-saas-1",
            "name": "StandardCRM",
            "sector": "SaaS",
            "funding_stage": "Series A",
            "investment_date": datetime.now() - timedelta(days=426),
            "investment_amount": 2500000,
            "ownership_percentage": 8.0,
            "valuation_at_investment": 31000000
        },
        {
            "company_id": "average-saas-2",
            "name": "NormalSoft",
            "sector": "SaaS",
            "funding_stage": "Seed",
            "investment_date": datetime.now() - timedelta(days=183),
            "investment_amount": 1200000,
            "ownership_percentage": 10.0,
            "valuation_at_investment": 12000000
        },
        {
            "company_id": "average-hardware-1",
            "name": "MedianDevices",
            "sector": "Hardware",
            "funding_stage": "Series A",
            "investment_date": datetime.now() - timedelta(days=365),
            "investment_amount": 3500000,
            "ownership_percentage": 9.0,
            "valuation_at_investment": 39000000
        }
    ]
    
    companies = []
    for data in company_data:
        company = PortfolioCompany(**data)
        db.add(company)
        companies.append(company)
    
    db.commit()
    logger.info(f"Created {len(companies)} test portfolio companies")
    
    return companies

def create_test_metrics(db: Session, companies: List[PortfolioCompany]) -> List[FinancialMetric]:
    """
    Create test financial metrics for the companies.
    
    Args:
        db: Database session
        companies: List of company objects
        
    Returns:
        List of created metric objects
    """
    today = datetime.now()
    all_metrics = []
    
    # Set up 6 months of monthly metrics for each company
    for month_offset in range(6):
        date = today - timedelta(days=30 * month_offset)
        
        for company in companies:
            # Base metrics that differ by company
            if company.company_id == "highgrowth-saas-1":
                # High growth SaaS company - growing extremely fast
                metrics = {
                    "cash_balance": 1000000 - (month_offset * 150000),  # Decreasing cash balance
                    "cash_burn_rate": 150000 + (month_offset * 10000),  # Increasing burn rate
                    "runway_months": (1000000 - (month_offset * 150000)) / (150000 + (month_offset * 10000)),  # Calculated runway
                    "revenue": 100000 + (month_offset * 70000),  # Strong revenue growth
                    "revenue_growth_rate": 0.35 + (month_offset * 0.05),  # Very high growth rate
                    "customer_count": 100 + (month_offset * 30),  # Strong customer acquisition
                    "customer_growth_rate": 0.3,  # High customer growth
                    "churn_rate": 0.05  # Low churn
                }
            elif company.company_id == "lowrunway-hardware-1":
                # Hardware company with low runway
                metrics = {
                    "cash_balance": 300000 - (month_offset * 100000),  # Rapidly decreasing cash balance
                    "cash_burn_rate": 100000,  # High consistent burn rate
                    "runway_months": max(0, (300000 - (month_offset * 100000)) / 100000),  # Low runway
                    "revenue": 20000 + (month_offset * 10000),  # Moderate revenue growth
                    "revenue_growth_rate": 0.12,  # Average growth rate
                    "customer_count": 15 + (month_offset * 2),  # Slow customer acquisition
                    "customer_growth_rate": 0.1,  # Moderate customer growth
                    "churn_rate": 0.08  # Moderate churn
                }
            elif company.company_id == "stable-fintech-1":
                # Stable fintech company
                metrics = {
                    "cash_balance": 2500000 - (month_offset * 100000),  # Healthy cash balance
                    "cash_burn_rate": 100000,  # Moderate burn rate
                    "runway_months": (2500000 - (month_offset * 100000)) / 100000,  # Healthy runway
                    "revenue": 300000 + (month_offset * 15000),  # Steady revenue growth
                    "revenue_growth_rate": 0.05,  # Modest growth rate
                    "customer_count": 5000 + (month_offset * 200),  # Steady customer acquisition
                    "customer_growth_rate": 0.04,  # Modest customer growth
                    "churn_rate": 0.04  # Low churn
                }
            else:
                # Average performer - used for peer comparison
                metrics = {
                    "cash_balance": 1500000 - (month_offset * 80000),  # Decent cash balance
                    "cash_burn_rate": 80000,  # Average burn rate
                    "runway_months": (1500000 - (month_offset * 80000)) / 80000,  # Average runway
                    "revenue": 150000 + (month_offset * 10000),  # Average revenue growth
                    "revenue_growth_rate": 0.08,  # Average growth rate
                    "customer_count": 500 + (month_offset * 40),  # Average customer acquisition
                    "customer_growth_rate": 0.08,  # Average customer growth
                    "churn_rate": 0.07  # Average churn
                }
            
            # Add some randomness to avoid completely identical metrics
            for key in metrics:
                if isinstance(metrics[key], (int, float)) and key != "churn_rate":
                    # Add ±5% randomness to most metrics
                    metrics[key] *= random.uniform(0.95, 1.05)
            
            # Create the metric record
            metric = FinancialMetric(
                company_id=company.company_id,
                date=date,
                cash_balance=metrics["cash_balance"],
                cash_burn_rate=metrics["cash_burn_rate"],
                runway_months=metrics["runway_months"],
                revenue=metrics["revenue"],
                revenue_growth_rate=metrics["revenue_growth_rate"],
                customer_count=metrics["customer_count"],
                customer_growth_rate=metrics["customer_growth_rate"],
                churn_rate=metrics["churn_rate"],
                data_source="synthetic_test",
                growth_vs_peers=None,  # This will be calculated by the follow-on engine
                raw_data={"generated_for": "acceptance_testing"}
            )
            
            db.add(metric)
            all_metrics.append(metric)
    
    db.commit()
    logger.info(f"Created {len(all_metrics)} test financial metrics")
    
    return all_metrics