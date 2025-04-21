"""
Follow-On Investment Decision Engine.

This module analyzes financial metrics to determine when
to trigger follow-on investment decisions.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.database import PortfolioCompany, FinancialMetric, FollowOnDecision

logger = logging.getLogger(__name__)

class FollowOnEngine:
    """
    Engine for deciding when to trigger follow-on investments.
    
    This class analyzes financial metrics to determine when a company
    should be considered for a follow-on investment based on runway
    or growth triggers.
    """
    
    def __init__(self, db: Session):
        """Initialize the follow-on engine with a database session."""
        self.db = db
        # Configuration parameters
        self.runway_threshold_months = 9.0  # Trigger if runway < 9 months
        self.growth_threshold_stdev = 3.0  # Trigger if growth > 3σ of peer median
        
    def analyze_all_companies(self) -> List[Dict[str, Any]]:
        """
        Analyze all portfolio companies and trigger follow-on decisions when needed.
        
        Returns:
            List of triggered follow-on decisions
        """
        results = []
        
        # Get all portfolio companies
        companies = self.db.query(PortfolioCompany).all()
        
        # Calculate peer statistics by sector
        sector_stats = self._calculate_sector_stats()
        
        for company in companies:
            try:
                # Get the latest metrics for this company
                latest_metrics = self.db.query(FinancialMetric).filter(
                    FinancialMetric.company_id == company.company_id
                ).order_by(desc(FinancialMetric.date)).first()
                
                if not latest_metrics:
                    logger.warning(f"No metrics found for company {company.company_id}, skipping follow-on analysis")
                    continue
                
                # Compare metrics to thresholds and compute peer comparison
                trigger_details = self._evaluate_triggers(company, latest_metrics, sector_stats)
                
                if trigger_details:
                    # Create a follow-on decision record
                    decision = self._create_follow_on_decision(company, latest_metrics, trigger_details)
                    results.append(decision)
                    
            except Exception as e:
                logger.error(f"Error analyzing company {company.company_id} for follow-on: {str(e)}")
        
        return results
    
    def _calculate_sector_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate statistics for each sector to enable peer comparisons.
        
        Returns:
            Dictionary mapping sectors to their statistics
        """
        sector_stats = {}
        
        # Get all sectors
        sectors = [c.sector for c in self.db.query(PortfolioCompany.sector).distinct()]
        
        for sector in sectors:
            # Get companies in this sector
            sector_companies = self.db.query(PortfolioCompany).filter(
                PortfolioCompany.sector == sector
            ).all()
            
            sector_company_ids = [company.company_id for company in sector_companies]
            
            # Get the latest metrics for each company in this sector
            all_metrics = []
            for company_id in sector_company_ids:
                latest = self.db.query(FinancialMetric).filter(
                    FinancialMetric.company_id == company_id
                ).order_by(desc(FinancialMetric.date)).first()
                
                if latest:
                    all_metrics.append(latest)
            
            if not all_metrics:
                logger.warning(f"No metrics found for sector {sector}, skipping")
                continue
                
            # Calculate statistics for this sector
            revenue_growth_rates = [m.revenue_growth_rate for m in all_metrics if m.revenue_growth_rate is not None]
            customer_growth_rates = [m.customer_growth_rate for m in all_metrics if m.customer_growth_rate is not None]
            churn_rates = [m.churn_rate for m in all_metrics if m.churn_rate is not None]
            
            sector_stats[sector] = {
                "revenue_growth_median": np.median(revenue_growth_rates) if revenue_growth_rates else 0,
                "revenue_growth_stdev": np.std(revenue_growth_rates) if len(revenue_growth_rates) > 1 else 0,
                "customer_growth_median": np.median(customer_growth_rates) if customer_growth_rates else 0,
                "customer_growth_stdev": np.std(customer_growth_rates) if len(customer_growth_rates) > 1 else 0,
                "churn_rate_median": np.median(churn_rates) if churn_rates else 0,
                "churn_rate_stdev": np.std(churn_rates) if len(churn_rates) > 1 else 0,
                "sample_size": len(all_metrics)
            }
            
        return sector_stats
    
    def _evaluate_triggers(
        self, 
        company: PortfolioCompany, 
        metrics: FinancialMetric, 
        sector_stats: Dict[str, Dict[str, float]]
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate if any follow-on investment triggers are activated.
        
        Args:
            company: The portfolio company
            metrics: The latest financial metrics for the company
            sector_stats: Statistics for each sector
            
        Returns:
            Trigger details if a trigger is activated, None otherwise
        """
        triggers = []
        trigger_values = {}
        
        # Check runway trigger
        if metrics.runway_months is not None and metrics.runway_months < self.runway_threshold_months:
            triggers.append("runway")
            trigger_values["runway"] = metrics.runway_months
            
        # Check growth triggers (revenue and customer growth)
        if company.sector in sector_stats:
            stats = sector_stats[company.sector]
            
            # Check revenue growth vs peers
            if (metrics.revenue_growth_rate is not None and 
                stats["revenue_growth_stdev"] > 0 and 
                stats["sample_size"] > 2):
                
                # Calculate z-score (standard deviations from the median)
                z_score = (metrics.revenue_growth_rate - stats["revenue_growth_median"]) / stats["revenue_growth_stdev"]
                
                # Update the growth_vs_peers metric
                metrics.growth_vs_peers = z_score
                self.db.commit()
                
                # Check if growth exceeds the threshold
                if z_score > self.growth_threshold_stdev:
                    triggers.append("growth")
                    trigger_values["growth"] = z_score
                    
            # Similarly for customer growth (can be implemented as needed)
        
        if not triggers:
            return None
            
        return {
            "triggers": triggers,
            "trigger_values": trigger_values,
            "sector_stats": sector_stats.get(company.sector, {})
        }
    
    def _create_follow_on_decision(
        self, 
        company: PortfolioCompany, 
        metrics: FinancialMetric, 
        trigger_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a follow-on investment decision record.
        
        Args:
            company: The portfolio company
            metrics: The latest financial metrics for the company
            trigger_details: Details about what triggered the decision
            
        Returns:
            Dictionary with the created decision details
        """
        # Determine the primary trigger (prioritize growth over runway)
        primary_trigger = "growth" if "growth" in trigger_details["triggers"] else "runway"
        trigger_value = trigger_details["trigger_values"][primary_trigger]
        
        # Calculate recommended investment amount
        # For runway trigger: Enough to extend runway to 18 months
        # For growth trigger: Super-pro-rata (2x pro-rata)
        
        # Calculate pro-rata amount (10% of the company's last round size to maintain ownership)
        pro_rata_amount = company.investment_amount * 0.1  # simplified calculation
        
        # Calculate recommended amount based on trigger type
        if primary_trigger == "runway":
            # Calculate how much cash is needed to extend runway
            monthly_burn = metrics.cash_burn_rate
            current_runway = metrics.runway_months
            target_runway = 18  # extend to 18 months
            additional_months_needed = target_runway - current_runway
            recommended_amount = monthly_burn * additional_months_needed
            
            # Ensure minimum amount
            recommended_amount = max(recommended_amount, pro_rata_amount)
        else:  # growth trigger
            # Super pro-rata based on how exceptional the growth is
            z_score = trigger_value
            multiple = min(1.0 + (z_score / 3.0), 3.0)  # Cap at 3x pro-rata
            recommended_amount = pro_rata_amount * multiple
        
        # Calculate new valuation (simplified)
        recommended_valuation = company.valuation_at_investment * 1.5  # 50% markup from last round
        
        # Create decision record
        decision = FollowOnDecision(
            company_id=company.company_id,
            trigger_type=primary_trigger,
            trigger_value=trigger_value,
            decision="pending",
            recommended_amount=recommended_amount,
            recommended_valuation=recommended_valuation,
            pro_rata_amount=pro_rata_amount,
            super_pro_rata=(recommended_amount > pro_rata_amount),
            rationale=self._generate_decision_rationale(company, metrics, trigger_details, primary_trigger),
            financial_snapshot={
                "metrics_date": metrics.date.isoformat() if isinstance(metrics.date, datetime) else metrics.date,
                "cash_balance": metrics.cash_balance,
                "burn_rate": metrics.cash_burn_rate,
                "runway": metrics.runway_months,
                "revenue": metrics.revenue,
                "revenue_growth": metrics.revenue_growth_rate,
                "customer_count": metrics.customer_count,
                "growth_vs_peers": metrics.growth_vs_peers
            }
        )
        
        # Save to database
        self.db.add(decision)
        self.db.commit()
        
        # Log the decision
        logger.info(f"Created follow-on decision for {company.company_id} based on {primary_trigger} trigger")
        
        # Return serialized decision
        return {
            "id": decision.id,
            "company_id": decision.company_id,
            "trigger_type": decision.trigger_type,
            "trigger_value": decision.trigger_value,
            "recommended_amount": decision.recommended_amount,
            "recommended_valuation": decision.recommended_valuation,
            "pro_rata_amount": decision.pro_rata_amount,
            "super_pro_rata": decision.super_pro_rata,
            "decision": decision.decision,
            "decision_date": decision.decision_date.isoformat(),
            "rationale": decision.rationale
        }
    
    def _generate_decision_rationale(
        self,
        company: PortfolioCompany,
        metrics: FinancialMetric,
        trigger_details: Dict[str, Any],
        primary_trigger: str
    ) -> str:
        """
        Generate a human-readable rationale for the follow-on decision.
        
        Args:
            company: The portfolio company
            metrics: The latest financial metrics for the company
            trigger_details: Details about what triggered the decision
            primary_trigger: The primary trigger type
            
        Returns:
            String with the rationale
        """
        if primary_trigger == "runway":
            months = metrics.runway_months
            rationale = (
                f"RUNWAY TRIGGER: {company.name} has {months:.1f} months of runway remaining, "
                f"which is below our threshold of {self.runway_threshold_months} months. "
                f"Current burn rate is ${metrics.cash_burn_rate:,.2f}/month with a cash balance "
                f"of ${metrics.cash_balance:,.2f}."
            )
        else:  # growth trigger
            z_score = trigger_details["trigger_values"]["growth"]
            sector_stats = trigger_details["sector_stats"]
            median_growth = sector_stats.get("revenue_growth_median", 0) * 100
            company_growth = metrics.revenue_growth_rate * 100
            
            rationale = (
                f"GROWTH TRIGGER: {company.name} is growing at {company_growth:.1f}%, "
                f"which is {z_score:.1f} standard deviations above the median growth "
                f"rate of {median_growth:.1f}% for peers in the {company.sector} sector. "
                f"This exceptional growth warrants a super-pro-rata follow-on investment."
            )
            
        return rationale
    
    def follow_on_decision(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Perform a follow-on investment decision for a specific company.
        
        This function is called externally to trigger a follow-on analysis
        for a specific company, rather than analyzing all companies.
        
        Args:
            company_id: The ID of the company to analyze
            
        Returns:
            Follow-on decision details if a trigger is activated, None otherwise
        """
        # Get the company
        company = self.db.query(PortfolioCompany).filter(PortfolioCompany.company_id == company_id).first()
        
        if not company:
            logger.error(f"Company with ID {company_id} not found for follow-on decision")
            return None
            
        # Get the latest metrics
        latest_metrics = self.db.query(FinancialMetric).filter(
            FinancialMetric.company_id == company_id
        ).order_by(desc(FinancialMetric.date)).first()
        
        if not latest_metrics:
            logger.error(f"No metrics found for company {company_id}, cannot perform follow-on decision")
            return None
            
        # Calculate sector stats for peer comparison
        sector_stats = self._calculate_sector_stats()
        
        # Evaluate triggers
        trigger_details = self._evaluate_triggers(company, latest_metrics, sector_stats)
        
        if not trigger_details:
            logger.info(f"No follow-on triggers activated for company {company_id}")
            return None
            
        # Create a follow-on decision
        decision = self._create_follow_on_decision(company, latest_metrics, trigger_details)
        
        return decision