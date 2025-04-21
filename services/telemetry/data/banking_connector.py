"""
Banking data connector for processing CSV files from banking platforms.
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import csv
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from models.database import PortfolioCompany, FinancialMetric

logger = logging.getLogger(__name__)

class BankingConnector:
    """
    Connector for importing and processing banking data from CSV files.
    
    This class handles processing CSV exports from banking platforms to extract
    financial metrics such as cash balance, burn rate, and runway.
    """
    
    def __init__(self, db: Session):
        """Initialize the banking connector with a database session."""
        self.db = db
        self.csv_directory = os.environ.get("BANKING_CSV_DIR", "data/banking_csvs")
    
    def process_csv_files(self) -> List[Dict[str, Any]]:
        """
        Process all CSV files in the configured directory.
        
        Returns:
            List of processed data dictionaries
        """
        results = []
        
        # Ensure directory exists
        if not os.path.exists(self.csv_directory):
            logger.warning(f"Banking CSV directory does not exist: {self.csv_directory}")
            return results
            
        # Iterate through CSV files in the directory
        for filename in os.listdir(self.csv_directory):
            if not filename.endswith('.csv'):
                continue
                
            try:
                # Extract company ID from filename (assuming format: {company_id}_banking_YYYY-MM-DD.csv)
                parts = filename.split('_')
                company_id = parts[0]
                
                # Check if company exists in database
                company = self.db.query(PortfolioCompany).filter(PortfolioCompany.company_id == company_id).first()
                if not company:
                    logger.warning(f"Company with ID {company_id} not found in database, skipping file {filename}")
                    continue
                
                # Process the CSV file
                file_path = os.path.join(self.csv_directory, filename)
                metrics = self._extract_metrics_from_csv(file_path, company_id)
                
                if metrics:
                    results.append(metrics)
                    self._save_metrics_to_database(metrics)
                    
            except Exception as e:
                logger.error(f"Error processing banking CSV file {filename}: {str(e)}")
        
        return results
    
    def _extract_metrics_from_csv(self, file_path: str, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Extract financial metrics from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            company_id: ID of the company
            
        Returns:
            Dictionary of extracted financial metrics or None if extraction failed
        """
        try:
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)
            
            # Standardize column names (lowercase, replace spaces with underscores)
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            # Calculate metrics
            # Note: This is a simplified implementation. In a real-world scenario,
            # the CSV structure would be specific to the banking platform and would 
            # require custom parsing logic.
            
            # Calculate cash metrics
            latest_date = pd.to_datetime(df['date'].max()) if 'date' in df.columns else datetime.now()
            
            # Get the cash balance from the most recent entry
            if 'balance' in df.columns:
                cash_balance = float(df.loc[df['date'] == df['date'].max(), 'balance'].iloc[0])
            else:
                # Fallback: Assume the CSV has a simple list of transactions, and the cash balance
                # is the sum of all transactions
                cash_balance = float(df['amount'].sum() if 'amount' in df.columns else 0)
                
            # Calculate burn rate (average of negative cash flow over the last 3 months)
            # This is a simplified calculation
            if 'amount' in df.columns and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                three_months_ago = latest_date - pd.Timedelta(days=90)
                recent_df = df[df['date'] >= three_months_ago]
                
                # Sum only outflows (negative amounts)
                outflows = recent_df[recent_df['amount'] < 0]['amount']
                total_outflow = abs(outflows.sum()) if not outflows.empty else 0
                
                # Calculate monthly burn rate (total outflow divided by 3 months)
                monthly_burn_rate = total_outflow / 3
            else:
                monthly_burn_rate = 0
                
            # Calculate runway in months (cash balance / monthly burn rate)
            runway_months = cash_balance / monthly_burn_rate if monthly_burn_rate > 0 else float('inf')
            
            # Create metrics dictionary
            metrics = {
                "company_id": company_id,
                "date": latest_date,
                "cash_balance": cash_balance,
                "cash_burn_rate": monthly_burn_rate,
                "runway_months": runway_months,
                "data_source": "banking_csv",
                "raw_data": {
                    "file_name": os.path.basename(file_path),
                    "processing_date": datetime.now().isoformat(),
                    "summary_stats": {
                        "num_transactions": len(df),
                        "date_range": [df['date'].min(), df['date'].max()] if 'date' in df.columns else None
                    }
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting metrics from banking CSV {file_path}: {str(e)}")
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
                # Update existing metric
                for key, value in metrics.items():
                    if key != "company_id" and key != "date" and hasattr(existing_metric, key):
                        setattr(existing_metric, key, value)
                        
                self.db.commit()
                logger.info(f"Updated existing financial metrics for {metrics['company_id']} on {metrics['date']}")
                
            else:
                # Create new metric
                new_metric = FinancialMetric(**metrics)
                self.db.add(new_metric)
                self.db.commit()
                logger.info(f"Saved new financial metrics for {metrics['company_id']} on {metrics['date']}")
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving metrics to database: {str(e)}")