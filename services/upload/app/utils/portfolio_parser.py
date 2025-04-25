"""
Portfolio Parser Utility.

Handles parsing of different file types (CSV, XLSX, PDF) to extract portfolio data.
"""
import io
import logging
import pandas as pd
import numpy as np
import tabula
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union

logger = logging.getLogger(__name__)

# Column name mappings for different formats
COMPANY_COLUMNS = ['company', 'company name', 'investment', 'portfolio company', 'name']
FUND_COLUMNS = ['fund', 'fund name', 'investment fund', 'partnership']
COST_COLUMNS = ['cost', 'cost basis', 'invested', 'investment amount', 'amount invested']
VALUE_COLUMNS = ['value', 'current value', 'fair value', 'market value', 'nav']
DATE_COLUMNS = ['date', 'investment date', 'acquisition date', 'valuation date']
CURRENCY_COLUMNS = ['currency', 'curr']
COMMITTED_COLUMNS = ['committed', 'commitment', 'committed capital']
CONTRIBUTED_COLUMNS = ['contributed', 'paid in', 'called', 'contributed capital']
REMAINING_COLUMNS = ['remaining', 'uncalled', 'remaining commitment']
DISTRIBUTED_COLUMNS = ['distributed', 'distributions', 'returned']
VINTAGE_COLUMNS = ['vintage', 'vintage year', 'year']
IRR_COLUMNS = ['irr', 'net irr', 'internal rate of return']
TVPI_COLUMNS = ['tvpi', 'multiple', 'total value to paid in']
DPI_COLUMNS = ['dpi', 'distributions to paid in']

class PortfolioParser:
    """Parser for portfolio data from various file formats."""

    @staticmethod
    def detect_file_type(file_content: bytes) -> str:
        """
        Detect the type of file based on content.
        
        Args:
            file_content: The binary content of the file
        
        Returns:
            str: Detected file type ('csv', 'xlsx', 'pdf')
        """
        # Check for PDF signature
        if file_content.startswith(b'%PDF'):
            return 'pdf'
        
        # Check for Excel signature
        if file_content.startswith(b'PK\x03\x04'):
            return 'xlsx'
        
        # Default to CSV if no other match
        return 'csv'

    @staticmethod
    def _find_best_column_match(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        """
        Find the best matching column name from a list of candidates.
        
        Args:
            df: DataFrame to search in
            candidates: List of possible column names
        
        Returns:
            str: Best matching column name, or None if no match
        """
        # First try exact match
        for col in df.columns:
            if col.lower() in candidates:
                return col
        
        # Try contains match
        for col in df.columns:
            for candidate in candidates:
                if candidate in col.lower():
                    return col
        
        # No match found
        return None

    @staticmethod
    def parse_csv(file_content: bytes) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse portfolio data from a CSV file.
        
        Args:
            file_content: CSV file content
        
        Returns:
            Tuple containing lists of direct holdings and fund positions
        """
        try:
            # Read CSV data into DataFrame
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Normalize column names (lowercase, strip whitespace)
            df.columns = [col.lower().strip() for col in df.columns]
            
            # Determine if this is company data or fund data
            company_col = PortfolioParser._find_best_column_match(df, COMPANY_COLUMNS)
            fund_col = PortfolioParser._find_best_column_match(df, FUND_COLUMNS)
            
            if company_col:
                return PortfolioParser._parse_company_data(df, company_col), []
            elif fund_col:
                return [], PortfolioParser._parse_fund_data(df, fund_col)
            else:
                logger.warning("Could not identify data type (company or fund)")
                return [], []
                
        except Exception as e:
            logger.error(f"Error parsing CSV data: {str(e)}")
            return [], []

    @staticmethod
    def parse_xlsx(file_content: bytes) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse portfolio data from an Excel file.
        
        Args:
            file_content: Excel file content
        
        Returns:
            Tuple containing lists of direct holdings and fund positions
        """
        try:
            # Read Excel data into DataFrame
            xlsx_file = io.BytesIO(file_content)
            
            # Try to read all sheets and find ones with portfolio data
            xlsx = pd.ExcelFile(xlsx_file)
            
            holdings = []
            funds = []
            
            for sheet_name in xlsx.sheet_names:
                df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
                
                # Normalize column names
                df.columns = [str(col).lower().strip() if not pd.isna(col) else f"col_{i}" 
                            for i, col in enumerate(df.columns)]
                
                # Skip empty sheets
                if df.empty:
                    continue
                
                # Determine if this is company data or fund data
                company_col = PortfolioParser._find_best_column_match(df, COMPANY_COLUMNS)
                fund_col = PortfolioParser._find_best_column_match(df, FUND_COLUMNS)
                
                if company_col:
                    holdings.extend(PortfolioParser._parse_company_data(df, company_col))
                elif fund_col:
                    funds.extend(PortfolioParser._parse_fund_data(df, fund_col))
            
            return holdings, funds
            
        except Exception as e:
            logger.error(f"Error parsing Excel data: {str(e)}")
            return [], []

    @staticmethod
    def parse_pdf(file_content: bytes) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse portfolio data from a PDF file.
        
        Args:
            file_content: PDF file content
        
        Returns:
            Tuple containing lists of direct holdings and fund positions
        """
        try:
            # Convert bytes to BytesIO for tabula-py
            pdf_file = io.BytesIO(file_content)
            
            # Extract all tables from the PDF
            tables = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
            
            holdings = []
            funds = []
            
            for df in tables:
                # Skip empty tables
                if df.empty:
                    continue
                
                # Normalize column names
                df.columns = [str(col).lower().strip() if not pd.isna(col) else f"col_{i}" 
                             for i, col in enumerate(df.columns)]
                
                # Clean up data (handle NaN, etc.)
                df = df.replace({np.nan: None})
                
                # Determine if this is company data or fund data
                company_col = PortfolioParser._find_best_column_match(df, COMPANY_COLUMNS)
                fund_col = PortfolioParser._find_best_column_match(df, FUND_COLUMNS)
                
                if company_col:
                    holdings.extend(PortfolioParser._parse_company_data(df, company_col))
                elif fund_col:
                    funds.extend(PortfolioParser._parse_fund_data(df, fund_col))
            
            return holdings, funds
            
        except Exception as e:
            logger.error(f"Error parsing PDF data: {str(e)}")
            return [], []

    @staticmethod
    def _parse_company_data(df: pd.DataFrame, company_col: str) -> List[Dict]:
        """
        Parse direct company holdings data from a DataFrame.
        
        Args:
            df: DataFrame containing company holdings data
            company_col: Column name for company names
        
        Returns:
            List of dictionaries containing parsed company holdings
        """
        holdings = []
        
        # Find other relevant columns
        cost_col = PortfolioParser._find_best_column_match(df, COST_COLUMNS)
        value_col = PortfolioParser._find_best_column_match(df, VALUE_COLUMNS)
        date_col = PortfolioParser._find_best_column_match(df, DATE_COLUMNS)
        currency_col = PortfolioParser._find_best_column_match(df, CURRENCY_COLUMNS)
        
        # Ensure required columns are present
        if not (cost_col and value_col):
            logger.warning("Missing required columns for company holdings")
            return []
        
        # Process each row
        for _, row in df.iterrows():
            # Skip rows with missing critical data
            if pd.isna(row[company_col]) or pd.isna(row[cost_col]) or pd.isna(row[value_col]):
                continue
            
            # Parse date if available
            acquisition_date = None
            if date_col and not pd.isna(row[date_col]):
                try:
                    date_str = str(row[date_col])
                    acquisition_date = pd.to_datetime(date_str).isoformat()
                except:
                    pass
            
            # Get currency if available
            currency = "USD"  # Default
            if currency_col and not pd.isna(row[currency_col]):
                currency = str(row[currency_col]).upper()
            
            # Create holding entry
            holding = {
                "company_name": str(row[company_col]),
                "cost_basis": float(row[cost_col]),
                "current_value": float(row[value_col]),
                "currency": currency,
                "acquisition_date": acquisition_date,
                "valuation_date": datetime.utcnow().isoformat()
            }
            
            holdings.append(holding)
        
        return holdings

    @staticmethod
    def _parse_fund_data(df: pd.DataFrame, fund_col: str) -> List[Dict]:
        """
        Parse fund positions data from a DataFrame.
        
        Args:
            df: DataFrame containing fund positions data
            fund_col: Column name for fund names
        
        Returns:
            List of dictionaries containing parsed fund positions
        """
        funds = []
        
        # Find other relevant columns
        committed_col = PortfolioParser._find_best_column_match(df, COMMITTED_COLUMNS)
        contributed_col = PortfolioParser._find_best_column_match(df, CONTRIBUTED_COLUMNS)
        remaining_col = PortfolioParser._find_best_column_match(df, REMAINING_COLUMNS)
        distributed_col = PortfolioParser._find_best_column_match(df, DISTRIBUTED_COLUMNS)
        nav_col = PortfolioParser._find_best_column_match(df, VALUE_COLUMNS)
        vintage_col = PortfolioParser._find_best_column_match(df, VINTAGE_COLUMNS)
        currency_col = PortfolioParser._find_best_column_match(df, CURRENCY_COLUMNS)
        irr_col = PortfolioParser._find_best_column_match(df, IRR_COLUMNS)
        tvpi_col = PortfolioParser._find_best_column_match(df, TVPI_COLUMNS)
        dpi_col = PortfolioParser._find_best_column_match(df, DPI_COLUMNS)
        
        # Ensure required columns are present
        if not (committed_col and contributed_col and nav_col):
            logger.warning("Missing required columns for fund positions")
            return []
        
        # Process each row
        for _, row in df.iterrows():
            # Skip rows with missing critical data
            if pd.isna(row[fund_col]) or pd.isna(row[committed_col]) or pd.isna(row[nav_col]):
                continue
            
            # Get vintage year if available
            vintage_year = None
            if vintage_col and not pd.isna(row[vintage_col]):
                try:
                    year_str = str(row[vintage_col])
                    vintage_year = int(year_str)
                except:
                    pass
            
            # Get currency if available
            currency = "USD"  # Default
            if currency_col and not pd.isna(row[currency_col]):
                currency = str(row[currency_col]).upper()
            
            # Create fund position entry
            fund = {
                "fund_name": str(row[fund_col]),
                "committed_capital": float(row[committed_col]),
                "contributed_capital": float(row[contributed_col]),
                "nav": float(row[nav_col]),
                "currency": currency,
                "valuation_date": datetime.utcnow().isoformat(),
            }
            
            # Add optional fields if available
            if remaining_col and not pd.isna(row[remaining_col]):
                fund["remaining_capital"] = float(row[remaining_col])
            
            if distributed_col and not pd.isna(row[distributed_col]):
                fund["distributed_capital"] = float(row[distributed_col])
            
            if vintage_year:
                fund["vintage_year"] = vintage_year
            
            if irr_col and not pd.isna(row[irr_col]):
                try:
                    # Handle percentage format
                    irr_val = str(row[irr_col])
                    if "%" in irr_val:
                        irr_val = float(irr_val.replace("%", "")) / 100
                    else:
                        irr_val = float(irr_val)
                    fund["irr"] = irr_val
                except:
                    pass
            
            if tvpi_col and not pd.isna(row[tvpi_col]):
                try:
                    fund["tvpi"] = float(row[tvpi_col])
                except:
                    pass
            
            if dpi_col and not pd.isna(row[dpi_col]):
                try:
                    fund["dpi"] = float(row[dpi_col])
                except:
                    pass
            
            funds.append(fund)
        
        return funds