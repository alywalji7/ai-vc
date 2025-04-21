"""
Stripe API connector for collecting revenue and customer metrics.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import stripe
from sqlalchemy.orm import Session

from models.database import PortfolioCompany, FinancialMetric

logger = logging.getLogger(__name__)

class StripeConnector:
    """
    Connector for retrieving financial data from Stripe API.
    
    This class handles connecting to the Stripe API to extract
    revenue, customer growth, and churn metrics.
    """
    
    def __init__(self, db: Session):
        """Initialize the Stripe connector with a database session."""
        self.db = db
        self.stripe_api_keys = self._load_stripe_api_keys()
    
    def _load_stripe_api_keys(self) -> Dict[str, str]:
        """
        Load Stripe API keys for portfolio companies.
        
        In a real-world scenario, these would be securely stored
        and accessed through a key management system.
        
        Returns:
            Dictionary mapping company IDs to their Stripe API keys
        """
        # In a production environment, these would be loaded from a secure source
        # For this implementation, we'll load from environment variables with a naming convention:
        # STRIPE_API_KEY_{COMPANY_ID}
        
        api_keys = {}
        
        # Get all portfolio companies
        companies = self.db.query(PortfolioCompany).all()
        
        for company in companies:
            key_env_var = f"STRIPE_API_KEY_{company.company_id}"
            api_key = os.environ.get(key_env_var)
            
            if api_key:
                api_keys[company.company_id] = api_key
            else:
                logger.warning(f"No Stripe API key found for company {company.company_id}")
        
        return api_keys
    
    def process_all_companies(self) -> List[Dict[str, Any]]:
        """
        Process Stripe data for all portfolio companies with API keys.
        
        Returns:
            List of processed data dictionaries
        """
        results = []
        
        for company_id, api_key in self.stripe_api_keys.items():
            try:
                # Check if company exists in database
                company = self.db.query(PortfolioCompany).filter(PortfolioCompany.company_id == company_id).first()
                if not company:
                    logger.warning(f"Company with ID {company_id} not found in database, skipping Stripe processing")
                    continue
                
                # Process Stripe data for this company
                metrics = self._extract_metrics_from_stripe(company_id, api_key)
                
                if metrics:
                    results.append(metrics)
                    self._save_metrics_to_database(metrics)
                    
            except Exception as e:
                logger.error(f"Error processing Stripe data for company {company_id}: {str(e)}")
        
        return results
    
    def _extract_metrics_from_stripe(self, company_id: str, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Extract financial metrics from Stripe API.
        
        Args:
            company_id: ID of the company
            api_key: Stripe API key for the company
            
        Returns:
            Dictionary of extracted financial metrics or None if extraction failed
        """
        try:
            # Set the Stripe API key for this company
            stripe.api_key = api_key
            
            # Define the time periods for the metrics
            today = datetime.today()
            end_date = int(today.timestamp())
            start_date_30d = int((today - timedelta(days=30)).timestamp())
            start_date_60d = int((today - timedelta(days=60)).timestamp())
            
            # Fetch revenue data (last 30 days)
            charges_30d = stripe.Charge.list(
                created={'gte': start_date_30d, 'lt': end_date},
                limit=100,
                status='succeeded'
            )
            
            # Fetch revenue data (30-60 days ago for comparison)
            charges_prev_30d = stripe.Charge.list(
                created={'gte': start_date_60d, 'lt': start_date_30d},
                limit=100,
                status='succeeded'
            )
            
            # Calculate current revenue (last 30 days)
            current_revenue = sum(charge.amount for charge in charges_30d.auto_paging_iter()) / 100  # Convert from cents
            
            # Calculate previous revenue (30-60 days ago)
            previous_revenue = sum(charge.amount for charge in charges_prev_30d.auto_paging_iter()) / 100
            
            # Calculate revenue growth rate
            revenue_growth_rate = ((current_revenue - previous_revenue) / previous_revenue) if previous_revenue > 0 else 0
            
            # Fetch customer data
            customers_current = stripe.Customer.list(
                created={'lt': end_date},
                limit=100
            )
            
            # Count current customers (approximation - would need pagination for a complete count)
            current_customer_count = len(customers_current.data)
            
            # Fetch customers from 30 days ago
            customers_30d_ago = stripe.Customer.list(
                created={'lt': start_date_30d},
                limit=100
            )
            
            # Count customers 30 days ago
            previous_customer_count = len(customers_30d_ago.data)
            
            # Calculate customer growth rate
            customer_growth_rate = ((current_customer_count - previous_customer_count) / previous_customer_count) if previous_customer_count > 0 else 0
            
            # Calculate churn rate (simplified)
            # In a real implementation, you would track actual subscription cancellations
            # This is just an approximation based on customer counts
            subscriptions_ended = stripe.Subscription.list(
                status='canceled',
                created={'gte': start_date_30d, 'lt': end_date},
                limit=100
            )
            
            canceled_count = len(subscriptions_ended.data)
            churn_rate = canceled_count / previous_customer_count if previous_customer_count > 0 else 0
            
            # Create metrics dictionary
            metrics = {
                "company_id": company_id,
                "date": today,
                "revenue": current_revenue,
                "revenue_growth_rate": revenue_growth_rate,
                "customer_count": current_customer_count,
                "customer_growth_rate": customer_growth_rate,
                "churn_rate": churn_rate,
                "data_source": "stripe_api",
                "raw_data": {
                    "processing_date": today.isoformat(),
                    "summary_stats": {
                        "current_revenue": current_revenue,
                        "previous_revenue": previous_revenue,
                        "current_customers": current_customer_count,
                        "previous_customers": previous_customer_count,
                        "canceled_subscriptions": canceled_count
                    }
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting metrics from Stripe for company {company_id}: {str(e)}")
            return None
    
    def _save_metrics_to_database(self, metrics: Dict[str, Any]) -> None:
        """
        Save the extracted metrics to the database.
        
        Args:
            metrics: Dictionary of financial metrics to save
        """
        try:
            # Check if we already have metrics for this company and date
            existing_metric = self.db.query(FinancialMetric).filter(
                FinancialMetric.company_id == metrics["company_id"],
                FinancialMetric.date == metrics["date"]
            ).first()
            
            if existing_metric:
                # Update existing metric with new Stripe data
                # We're selective about which fields to update since this might be
                # merging with banking data that was already collected
                stripe_fields = ["revenue", "revenue_growth_rate", "customer_count", 
                                "customer_growth_rate", "churn_rate"]
                
                for field in stripe_fields:
                    if field in metrics:
                        setattr(existing_metric, field, metrics[field])
                
                # Update raw_data by merging
                if hasattr(existing_metric, "raw_data") and existing_metric.raw_data:
                    existing_raw_data = existing_metric.raw_data
                    existing_raw_data.update({"stripe_data": metrics["raw_data"]})
                    existing_metric.raw_data = existing_raw_data
                else:
                    existing_metric.raw_data = {"stripe_data": metrics["raw_data"]}
                        
                self.db.commit()
                logger.info(f"Updated existing financial metrics with Stripe data for {metrics['company_id']} on {metrics['date']}")
                
            else:
                # Create new metric
                new_metric = FinancialMetric(**metrics)
                self.db.add(new_metric)
                self.db.commit()
                logger.info(f"Saved new financial metrics from Stripe for {metrics['company_id']} on {metrics['date']}")
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving Stripe metrics to database: {str(e)}")