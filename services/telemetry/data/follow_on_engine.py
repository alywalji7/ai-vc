"""
Follow-On Engine module for the Portfolio Telemetry service.

This module provides a decision engine to determine whether portfolio
companies require follow-on investments based on preset criteria.
"""
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.database import PortfolioCompany, FinancialMetric, FollowOnDecision

# Configure logging
logger = logging.getLogger(__name__)

# Get thresholds from environment variables or use defaults
RUNWAY_THRESHOLD_MONTHS = float(os.environ.get("RUNWAY_THRESHOLD_MONTHS", "9.0"))
GROWTH_THRESHOLD_STDEV = float(os.environ.get("GROWTH_THRESHOLD_STDEV", "3.0"))

class FollowOnEngine:
    """
    Engine for analyzing portfolio company metrics and making follow-on investment decisions.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the follow-on engine.
        
        Args:
            db: Database session
        """
        self.db = db
        logger.info(f"Follow-on engine initialized with runway threshold: {RUNWAY_THRESHOLD_MONTHS} months, growth threshold: {GROWTH_THRESHOLD_STDEV} standard deviations")
    
    def check_runway_trigger(self, company_id: str) -> Dict[str, Any]:
        """
        Check if a company should receive a follow-on investment due to runway concerns.
        
        Args:
            company_id: ID of the company to check
            
        Returns:
            Dictionary with the decision details or empty dict if no trigger
        """
        # Get the latest financial metrics for the company
        latest_metrics = self.db.query(FinancialMetric).filter_by(company_id=company_id).order_by(
            FinancialMetric.date.desc()
        ).first()
        
        if not latest_metrics or latest_metrics.runway_months is None:
            logger.warning(f"No runway data available for company {company_id}")
            return {}
        
        # Check if runway is below threshold
        if latest_metrics.runway_months < RUNWAY_THRESHOLD_MONTHS:
            # Calculate recommended investment amount to extend runway to 18 months
            company = self.db.query(PortfolioCompany).filter_by(id=company_id).first()
            
            if not company:
                logger.error(f"Company {company_id} not found in database")
                return {}
            
            # Calculate amount needed to extend runway
            target_runway = 18.0  # Target 18 months of runway
            additional_runway = target_runway - latest_metrics.runway_months
            
            if latest_metrics.burn_rate and latest_metrics.burn_rate > 0:
                recommended_amount = latest_metrics.burn_rate * additional_runway
            else:
                # Fallback calculation if burn rate is not available
                recommended_amount = company.investment_amount * 0.5  # 50% of original investment
            
            decision = {
                "company_id": company_id,
                "trigger_type": "RUNWAY",
                "trigger_value": latest_metrics.runway_months,
                "threshold": RUNWAY_THRESHOLD_MONTHS,
                "recommended_amount": recommended_amount,
                "super_pro_rata": False,
                "expected_runway_extension": additional_runway,
                "analysis": f"Company has only {latest_metrics.runway_months:.1f} months of runway remaining, which is below our threshold of {RUNWAY_THRESHOLD_MONTHS} months. Recommending a follow-on investment of ${recommended_amount:.2f} to extend runway to 18 months."
            }
            
            logger.info(f"Runway trigger activated for company {company_id}: {latest_metrics.runway_months:.1f} months runway")
            return decision
        
        return {}
    
    def check_growth_trigger(self, company_id: str) -> Dict[str, Any]:
        """
        Check if a company should receive a follow-on investment due to exceptional growth.
        
        Args:
            company_id: ID of the company to check
            
        Returns:
            Dictionary with the decision details or empty dict if no trigger
        """
        # Get the latest financial metrics for the company
        latest_metrics = self.db.query(FinancialMetric).filter_by(company_id=company_id).order_by(
            FinancialMetric.date.desc()
        ).first()
        
        if not latest_metrics or latest_metrics.revenue_growth is None:
            logger.warning(f"No growth data available for company {company_id}")
            return {}
        
        # Get the company's sector
        company = self.db.query(PortfolioCompany).filter_by(id=company_id).first()
        
        if not company:
            logger.error(f"Company {company_id} not found in database")
            return {}
        
        # Get all companies in the same sector
        sector_companies = self.db.query(PortfolioCompany).filter_by(sector=company.sector).all()
        sector_company_ids = [c.id for c in sector_companies]
        
        # Get the latest revenue growth for all companies in the sector
        sector_growth_metrics = []
        
        for sector_company_id in sector_company_ids:
            sector_metrics = self.db.query(FinancialMetric).filter_by(company_id=sector_company_id).order_by(
                FinancialMetric.date.desc()
            ).first()
            
            if sector_metrics and sector_metrics.revenue_growth is not None:
                sector_growth_metrics.append(sector_metrics.revenue_growth)
        
        if not sector_growth_metrics:
            logger.warning(f"No sector growth data available for comparison with company {company_id}")
            return {}
        
        # Calculate sector statistics
        sector_growth_mean = np.mean(sector_growth_metrics)
        sector_growth_std = np.std(sector_growth_metrics)
        
        # Calculate standard deviations above the mean
        if sector_growth_std > 0:
            stdevs_above_mean = (latest_metrics.revenue_growth - sector_growth_mean) / sector_growth_std
        else:
            # If standard deviation is 0 (all companies have same growth), use absolute comparison
            stdevs_above_mean = 0 if latest_metrics.revenue_growth <= sector_growth_mean else float('inf')
        
        # Check if growth is above threshold
        if stdevs_above_mean >= GROWTH_THRESHOLD_STDEV:
            # Calculate recommended investment amount (higher for exceptional growth)
            recommended_amount = company.investment_amount * 0.75  # 75% of original investment
            
            decision = {
                "company_id": company_id,
                "trigger_type": "growth",
                "trigger_value": latest_metrics.revenue_growth,
                "threshold": f"{GROWTH_THRESHOLD_STDEV} std above sector mean of {sector_growth_mean:.1f}%",
                "stdevs_above_mean": stdevs_above_mean,
                "recommended_amount": recommended_amount,
                "super_pro_rata": True,  # Super pro-rata for high growth
                "expected_ownership_increase": company.ownership_percentage * 0.2,  # Estimate 20% increase in ownership
                "analysis": f"Company has {latest_metrics.revenue_growth:.1f}% growth, which is {stdevs_above_mean:.1f} standard deviations above the sector mean of {sector_growth_mean:.1f}%. This exceeds our growth threshold of {GROWTH_THRESHOLD_STDEV} std. Recommending a super pro-rata follow-on investment of ${recommended_amount:.2f}."
            }
            
            logger.info(f"Growth trigger activated for company {company_id}: {latest_metrics.revenue_growth:.1f}% growth, {stdevs_above_mean:.1f} std above sector mean")
            return decision
        
        return {}
    
    def follow_on_decision(self, company_id: str) -> Dict[str, Any]:
        """
        Make a follow-on investment decision for a specific company.
        
        Args:
            company_id: ID of the company to analyze
            
        Returns:
            Dictionary with the decision details or empty dict if no action needed
        """
        # Check runway trigger
        runway_decision = self.check_runway_trigger(company_id)
        
        # Check growth trigger
        growth_decision = self.check_growth_trigger(company_id)
        
        # Prioritize growth trigger over runway trigger
        if growth_decision:
            decision = growth_decision
        elif runway_decision:
            decision = runway_decision
        else:
            return {}
        
        # Record the decision in the database
        self.record_decision(decision)
        
        return decision
    
    def record_decision(self, decision: Dict[str, Any]) -> None:
        """
        Record a follow-on decision in the database.
        
        Args:
            decision: Dictionary with decision details
        """
        # Create a new decision record
        new_decision = FollowOnDecision(
            company_id=decision["company_id"],
            date=datetime.utcnow(),
            trigger_type=decision["trigger_type"],
            recommended_amount=decision["recommended_amount"],
            super_pro_rata=decision.get("super_pro_rata", False),
            expected_runway_extension=decision.get("expected_runway_extension"),
            expected_ownership_increase=decision.get("expected_ownership_increase"),
            analysis=decision["analysis"]
        )
        
        self.db.add(new_decision)
        self.db.commit()
        
        logger.info(f"Recorded follow-on decision for company {decision['company_id']}")
    
    def analyze_all_companies(self) -> List[Dict[str, Any]]:
        """
        Analyze all portfolio companies for potential follow-on investments.
        
        Returns:
            List of dictionaries with decision details
        """
        results = []
        
        # Get all portfolio companies
        companies = self.db.query(PortfolioCompany).all()
        
        for company in companies:
            try:
                # Make follow-on decision
                decision = self.follow_on_decision(company.id)
                
                if decision:
                    results.append(decision)
                
            except Exception as e:
                logger.error(f"Error analyzing company {company.id}: {str(e)}")
        
        logger.info(f"Analyzed {len(companies)} companies, found {len(results)} follow-on opportunities")
        return results