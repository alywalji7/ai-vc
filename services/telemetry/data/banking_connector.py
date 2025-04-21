"""
Banking Connector module for the Portfolio Telemetry service.

This module provides functionality to parse banking CSV files and
extract financial metrics for portfolio companies.
"""
import os
import glob
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from models.database import PortfolioCompany, FinancialMetric

# Configure logging
logger = logging.getLogger(__name__)

class BankingConnector:
    """
    Connector for processing banking CSV files and extracting financial metrics.
    """
    
    def __init__(self, db: Session, csv_dir: str):
        """
        Initialize the banking connector.
        
        Args:
            db: Database session
            csv_dir: Directory containing banking CSV files
        """
        self.db = db
        self.csv_dir = csv_dir
        logger.info(f"Banking connector initialized with CSV directory: {csv_dir}")
    
    def get_latest_csv_files(self) -> Dict[str, str]:
        """
        Get the latest CSV file for each company.
        
        Returns:
            Dictionary mapping company IDs to file paths
        """
        company_files = {}
        
        # Pattern: {company_id}_banking_{date}.csv
        pattern = os.path.join(self.csv_dir, "*_banking_*.csv")
        
        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath)
            try:
                # Extract company ID from filename
                company_id = filename.split("_banking_")[0]
                
                # Check if this is the latest file for this company
                if company_id not in company_files:
                    company_files[company_id] = filepath
                else:
                    # Compare dates and keep the latest
                    current_date_str = os.path.splitext(company_files[company_id].split("_banking_")[1])[0]
                    new_date_str = os.path.splitext(filename.split("_banking_")[1])[0]
                    
                    current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
                    new_date = datetime.strptime(new_date_str, "%Y-%m-%d")
                    
                    if new_date > current_date:
                        company_files[company_id] = filepath
            
            except (IndexError, ValueError) as e:
                logger.warning(f"Skipping malformed filename: {filename}. Error: {str(e)}")
        
        return company_files
    
    def parse_csv_file(self, file_path: str) -> pd.DataFrame:
        """
        Parse a banking CSV file into a pandas DataFrame.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            DataFrame containing transaction data
        """
        try:
            df = pd.read_csv(file_path, parse_dates=["date"])
            logger.info(f"Successfully parsed {file_path} with {len(df)} transactions")
            return df
        except Exception as e:
            logger.error(f"Error parsing CSV file {file_path}: {str(e)}")
            raise
    
    def calculate_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate financial metrics from transaction data.
        
        Args:
            df: DataFrame containing transaction data
            
        Returns:
            Dictionary of financial metrics
        """
        metrics = {}
        
        # Calculate cash balance (most recent balance in the DataFrame)
        metrics["cash_balance"] = df["balance"].iloc[0]
        
        # Calculate burn rate (average of outgoing transactions in the last 30 days)
        thirty_days_ago = df["date"].iloc[0] - timedelta(days=30)
        last_30_days_df = df[df["date"] >= thirty_days_ago]
        
        # Only consider expense transactions (negative amounts)
        expenses_df = last_30_days_df[last_30_days_df["amount"] < 0]
        
        if not expenses_df.empty:
            # Monthly burn rate is the sum of all expenses
            metrics["burn_rate"] = abs(expenses_df["amount"].sum())
            
            # Calculate runway in months
            if metrics["burn_rate"] > 0:
                metrics["runway_months"] = metrics["cash_balance"] / metrics["burn_rate"]
            else:
                metrics["runway_months"] = 999.0  # Arbitrary large number for infinite runway
        else:
            # No expenses in the last 30 days
            metrics["burn_rate"] = 0.0
            metrics["runway_months"] = 999.0
        
        return metrics
    
    def update_company_metrics(self, company_id: str, metrics: Dict[str, float]) -> None:
        """
        Update database with the latest financial metrics for a company.
        
        Args:
            company_id: ID of the company to update
            metrics: Dictionary of financial metrics
        """
        # Check if company exists
        company = self.db.query(PortfolioCompany).filter_by(id=company_id).first()
        
        if not company:
            logger.warning(f"Company with ID {company_id} not found in database. Skipping metrics update.")
            return
        
        # Create new financial metrics record
        new_metrics = FinancialMetric(
            company_id=company_id,
            date=datetime.utcnow(),
            cash_balance=metrics.get("cash_balance"),
            burn_rate=metrics.get("burn_rate"),
            runway_months=metrics.get("runway_months")
        )
        
        self.db.add(new_metrics)
        self.db.commit()
        
        logger.info(f"Updated financial metrics for company {company_id}")
    
    def process_all_companies(self) -> List[Dict]:
        """
        Process all available banking data for portfolio companies.
        
        Returns:
            List of dictionaries with processing results
        """
        results = []
        
        # Get latest CSV files for all companies
        company_files = self.get_latest_csv_files()
        
        for company_id, file_path in company_files.items():
            try:
                # Parse the CSV file
                df = self.parse_csv_file(file_path)
                
                # Calculate financial metrics
                metrics = self.calculate_metrics(df)
                
                # Update the database
                self.update_company_metrics(company_id, metrics)
                
                results.append({
                    "company_id": company_id,
                    "file_processed": file_path,
                    "metrics": metrics,
                    "success": True
                })
                
            except Exception as e:
                logger.error(f"Error processing company {company_id}: {str(e)}")
                results.append({
                    "company_id": company_id,
                    "file_processed": file_path,
                    "error": str(e),
                    "success": False
                })
        
        return results