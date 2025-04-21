"""
Stripe Connector module for the Portfolio Telemetry service.

This module provides functionality to pull revenue and customer metrics
from the Stripe API for portfolio companies.
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import stripe
from sqlalchemy.orm import Session

from models.database import PortfolioCompany, FinancialMetric

# Configure logging
logger = logging.getLogger(__name__)

class StripeConnector:
    """
    Connector for retrieving revenue and customer metrics from Stripe.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the Stripe connector.
        
        Args:
            db: Database session
        """
        self.db = db
        logger.info("Stripe connector initialized")
    
    def get_api_key_for_company(self, company_id: str) -> Optional[str]:
        """
        Get the Stripe API key for a specific company.
        
        The API keys are stored in environment variables with the format:
        STRIPE_API_KEY_{COMPANY_ID}=sk_test_...
        
        Args:
            company_id: ID of the company
            
        Returns:
            Stripe API key if found, None otherwise
        """
        env_var_name = f"STRIPE_API_KEY_{company_id}"
        api_key = os.environ.get(env_var_name)
        
        if not api_key:
            logger.warning(f"No Stripe API key found for company {company_id}")
            return None
        
        return api_key
    
    def get_revenue_metrics(self, company_id: str) -> Dict[str, float]:
        """
        Get revenue metrics from Stripe for a specific company.
        
        Args:
            company_id: ID of the company
            
        Returns:
            Dictionary of revenue metrics
        """
        api_key = self.get_api_key_for_company(company_id)
        
        if not api_key:
            logger.error(f"Cannot get revenue metrics for company {company_id}: No API key")
            return {}
        
        # Set the API key for this request
        stripe.api_key = api_key
        
        metrics = {}
        
        try:
            # Get current month's revenue
            end_date = datetime.now()
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Convert to Unix timestamps for Stripe API
            end_timestamp = int(end_date.timestamp())
            start_timestamp = int(start_date.timestamp())
            
            # Get invoices for the current month
            current_invoices = stripe.Invoice.list(
                created={
                    'gte': start_timestamp,
                    'lte': end_timestamp
                },
                status='paid',
                limit=100
            )
            
            # Calculate current MRR (Monthly Recurring Revenue)
            current_month_revenue = sum(invoice.amount_paid / 100 for invoice in current_invoices)
            metrics["mrr"] = current_month_revenue
            
            # Calculate ARR (Annual Recurring Revenue)
            metrics["arr"] = current_month_revenue * 12
            
            # Get previous month's revenue
            prev_month_end = start_date - timedelta(days=1)
            prev_month_start = prev_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            prev_end_timestamp = int(prev_month_end.timestamp())
            prev_start_timestamp = int(prev_month_start.timestamp())
            
            prev_invoices = stripe.Invoice.list(
                created={
                    'gte': prev_start_timestamp,
                    'lte': prev_end_timestamp
                },
                status='paid',
                limit=100
            )
            
            prev_month_revenue = sum(invoice.amount_paid / 100 for invoice in prev_invoices)
            
            # Calculate month-over-month growth percentage
            if prev_month_revenue > 0:
                metrics["revenue_growth"] = ((current_month_revenue - prev_month_revenue) / prev_month_revenue) * 100
            else:
                metrics["revenue_growth"] = 0.0 if current_month_revenue == 0 else 100.0
            
            logger.info(f"Successfully retrieved revenue metrics for company {company_id}")
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error for company {company_id}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving revenue metrics for company {company_id}: {str(e)}")
        
        return metrics
    
    def get_customer_metrics(self, company_id: str) -> Dict[str, float]:
        """
        Get customer metrics from Stripe for a specific company.
        
        Args:
            company_id: ID of the company
            
        Returns:
            Dictionary of customer metrics
        """
        api_key = self.get_api_key_for_company(company_id)
        
        if not api_key:
            logger.error(f"Cannot get customer metrics for company {company_id}: No API key")
            return {}
        
        # Set the API key for this request
        stripe.api_key = api_key
        
        metrics = {}
        
        try:
            # Get current customers
            current_customers = stripe.Customer.list(limit=100)
            metrics["customer_count"] = len(current_customers)
            
            # Get new customers in the last 30 days
            thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp())
            
            new_customers = stripe.Customer.list(
                created={
                    'gte': thirty_days_ago
                },
                limit=100
            )
            
            metrics["new_customers"] = len(new_customers)
            
            # Get subscriptions that were canceled in the last 30 days
            canceled_subscriptions = stripe.Subscription.list(
                status='canceled',
                created={
                    'gte': thirty_days_ago
                },
                limit=100
            )
            
            metrics["churned_customers"] = len(canceled_subscriptions)
            
            # Calculate churn rate
            if metrics["customer_count"] > 0:
                metrics["churn_rate"] = (metrics["churned_customers"] / metrics["customer_count"]) * 100
            else:
                metrics["churn_rate"] = 0.0
            
            logger.info(f"Successfully retrieved customer metrics for company {company_id}")
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error for company {company_id}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving customer metrics for company {company_id}: {str(e)}")
        
        return metrics
    
    def update_company_metrics(self, company_id: str, revenue_metrics: Dict[str, float], customer_metrics: Dict[str, float]) -> None:
        """
        Update database with the latest metrics for a company.
        
        Args:
            company_id: ID of the company to update
            revenue_metrics: Dictionary of revenue metrics
            customer_metrics: Dictionary of customer metrics
        """
        # Check if company exists
        company = self.db.query(PortfolioCompany).filter_by(id=company_id).first()
        
        if not company:
            logger.warning(f"Company with ID {company_id} not found in database. Skipping metrics update.")
            return
        
        # Get the most recent financial metrics record or create a new one
        latest_metrics = self.db.query(FinancialMetric).filter_by(company_id=company_id).order_by(
            FinancialMetric.date.desc()
        ).first()
        
        if latest_metrics and latest_metrics.date.date() == datetime.utcnow().date():
            # Update existing record from today
            metrics = latest_metrics
        else:
            # Create new record
            metrics = FinancialMetric(
                company_id=company_id,
                date=datetime.utcnow()
            )
            self.db.add(metrics)
        
        # Update revenue metrics
        if "mrr" in revenue_metrics:
            metrics.mrr = revenue_metrics["mrr"]
        
        if "arr" in revenue_metrics:
            metrics.arr = revenue_metrics["arr"]
        
        if "revenue_growth" in revenue_metrics:
            metrics.revenue_growth = revenue_metrics["revenue_growth"]
        
        # Update customer metrics
        if "customer_count" in customer_metrics:
            metrics.customer_count = customer_metrics["customer_count"]
        
        if "new_customers" in customer_metrics:
            metrics.new_customers = customer_metrics["new_customers"]
        
        if "churned_customers" in customer_metrics:
            metrics.churned_customers = customer_metrics["churned_customers"]
        
        if "churn_rate" in customer_metrics:
            metrics.churn_rate = customer_metrics["churn_rate"]
        
        self.db.commit()
        
        logger.info(f"Updated revenue and customer metrics for company {company_id}")
    
    def process_all_companies(self) -> List[Dict]:
        """
        Process all portfolio companies to retrieve Stripe metrics.
        
        Returns:
            List of dictionaries with processing results
        """
        results = []
        
        # Get all portfolio companies
        companies = self.db.query(PortfolioCompany).all()
        
        for company in companies:
            try:
                # Get revenue metrics
                revenue_metrics = self.get_revenue_metrics(company.id)
                
                # Get customer metrics
                customer_metrics = self.get_customer_metrics(company.id)
                
                # Update the database
                self.update_company_metrics(company.id, revenue_metrics, customer_metrics)
                
                results.append({
                    "company_id": company.id,
                    "revenue_metrics": revenue_metrics,
                    "customer_metrics": customer_metrics,
                    "success": True
                })
                
            except Exception as e:
                logger.error(f"Error processing company {company.id}: {str(e)}")
                results.append({
                    "company_id": company.id,
                    "error": str(e),
                    "success": False
                })
        
        return results