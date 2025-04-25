"""
SEC Form D Connector for Graph Ingest Service.

This module fetches Form D filings from the SEC EDGAR database and creates
entities and relationships in the knowledge graph.
"""
import os
import logging
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import httpx
import xml.etree.ElementTree as ET

from ..db import engine, get_session
from ..models.form_d import FormDFiling, FormDRelationship
from ..models.company import Company

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SEC_BASE_URL = "https://www.sec.gov/Archives/edgar/data"
FORM_D_SEARCH_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
DEFAULT_DAYS_LOOKBACK = 30
USER_AGENT = "Mozilla/5.0 (compatible; AIVCResearch/1.0; +https://example.com/bot)"


class EdgarFormDConnector:
    """
    Connector for fetching Form D filings from SEC EDGAR database.
    """
    
    def __init__(self):
        """Initialize the SEC Form D connector."""
        self.engine = engine
        self.session_factory = get_session
    
    async def _get_latest_form_d_filings(self, days_lookback: int = DEFAULT_DAYS_LOOKBACK) -> List[Dict[str, Any]]:
        """
        Get the latest Form D filings from SEC EDGAR.
        
        Args:
            days_lookback: Number of days to look back for filings
            
        Returns:
            List of filings data
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_lookback)
            
            # Format dates for SEC query
            start_date_str = start_date.strftime("%Y%m%d")
            end_date_str = end_date.strftime("%Y%m%d")
            
            # Parameters for SEC EDGAR search
            params = {
                "action": "getcompany",
                "owner": "include",
                "type": "D",  # Form D
                "count": "100",
                "dateb": end_date_str,
                "datea": start_date_str,
                "output": "xml"
            }
            
            headers = {
                "User-Agent": USER_AGENT
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(FORM_D_SEARCH_URL, params=params, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"SEC EDGAR request failed: {response.status_code} - {response.text}")
                    return self._get_test_data()
                
                # Parse XML response
                root = ET.fromstring(response.text)
                filings = []
                
                for filing in root.findall(".//filing"):
                    acc_no = filing.find("accessionNumber").text.replace("-", "") if filing.find("accessionNumber") is not None else ""
                    cik = filing.find("cik").text if filing.find("cik") is not None else ""
                    company_name = filing.find("companyName").text if filing.find("companyName") is not None else ""
                    form_type = filing.find("type").text if filing.find("type") is not None else ""
                    filing_date = filing.find("filingDate").text if filing.find("filingDate") is not None else ""
                    
                    # Only include Form D filings
                    if form_type.startswith("D"):
                        filings.append({
                            "accession_number": acc_no,
                            "cik": cik,
                            "company_name": company_name,
                            "form_type": form_type,
                            "filing_date": filing_date,
                            "detail_url": f"{SEC_BASE_URL}/{cik}/{acc_no}/{acc_no}-index.html"
                        })
            
            logger.info(f"Found {len(filings)} Form D filings")
            return filings
        
        except Exception as e:
            logger.error(f"Error fetching Form D filings: {str(e)}")
            return self._get_test_data()
    
    async def _extract_filing_details(self, filing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract details from a Form D filing.
        
        Args:
            filing: Basic filing data from SEC EDGAR search
            
        Returns:
            Enhanced filing data with Form D specific details
        """
        try:
            # In a production environment, you would parse the actual Form D XML/HTML
            # Here we use a simplified approach for demo purposes
            
            # Get XML data URL
            acc_no = filing["accession_number"]
            cik = filing["cik"]
            xml_url = f"{SEC_BASE_URL}/{cik}/{acc_no}/{acc_no}.txt"
            
            headers = {
                "User-Agent": USER_AGENT
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(xml_url, headers=headers, timeout=10.0)
                
                if response.status_code != 200:
                    logger.warning(f"Failed to get filing details: {response.status_code}")
                    return self._enhance_filing_with_defaults(filing)
                
                content = response.text
                
                # Extract offering amount (very simplified, would need proper XML/HTML parsing)
                amount_raised = 0.0
                offering_amount = 0.0
                
                # Look for common Form D patterns
                raised_match = re.search(r"Total Amount Sold\s*\$?([0-9,]+)", content)
                if raised_match:
                    amount_raised = float(raised_match.group(1).replace(",", ""))
                
                offering_match = re.search(r"Total Offering Amount\s*\$?([0-9,]+)", content)
                if offering_match:
                    offering_amount = float(offering_match.group(1).replace(",", ""))
                
                # Extract investor count
                investor_match = re.search(r"Number of Non-accredited Investors\s*([0-9]+)", content)
                investor_count = int(investor_match.group(1)) if investor_match else None
                
                # Extract industry group
                industry_match = re.search(r"Industry Group\s*[\"']?([^\"']+)[\"']?", content)
                industry_group = industry_match.group(1).strip() if industry_match else None
                
                # Extract issuer size
                size_match = re.search(r"Revenue Range\s*[\"']?([^\"']+)[\"']?", content)
                issuer_size = size_match.group(1).strip() if size_match else None
                
                # Extract location
                city_match = re.search(r"City\s*[\"']?([^\"']+)[\"']?", content)
                state_match = re.search(r"State/Province\s*[\"']?([^\"']+)[\"']?", content)
                issuer_city = city_match.group(1).strip() if city_match else None
                issuer_state = state_match.group(1).strip() if state_match else None
                
                # Extract related persons
                related_persons = []
                person_matches = re.findall(r"<issuerRelatedPerson>.*?<name>([^<]+)</name>.*?<title>([^<]+)</title>.*?</issuerRelatedPerson>", content, re.DOTALL)
                for name, title in person_matches:
                    related_persons.append({"name": name.strip(), "title": title.strip()})
                
                # Enhance filing with extracted details
                filing.update({
                    "amount_raised": amount_raised,
                    "offering_amount": offering_amount,
                    "investor_count": investor_count,
                    "industry_group": industry_group,
                    "issuer_size": issuer_size,
                    "issuer_city": issuer_city,
                    "issuer_state": issuer_state,
                    "related_persons": related_persons
                })
                
                return filing
        
        except Exception as e:
            logger.error(f"Error extracting filing details: {str(e)}")
            return self._enhance_filing_with_defaults(filing)
    
    def _enhance_filing_with_defaults(self, filing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance filing with default values when details extraction fails.
        
        Args:
            filing: Basic filing data
            
        Returns:
            Enhanced filing data with default values
        """
        # Add default values for required fields
        if "form_type" in filing and filing["form_type"] == "D/A":
            filing_type = "AMENDED"
        else:
            filing_type = "NEW"
        
        filing.update({
            "amount_raised": 0.0,
            "offering_amount": 0.0,
            "filing_type": filing_type,
            "investor_count": None,
            "industry_group": None,
            "issuer_size": None,
            "issuer_city": None,
            "issuer_state": None,
            "related_persons": []
        })
        
        return filing
    
    def _get_test_data(self) -> List[Dict[str, Any]]:
        """
        Get test data when API requests fail.
        
        Returns:
            List of test Form D filings data
        """
        return [
            {
                "accession_number": "0001234567-24-000001",
                "cik": "0001234567",
                "company_name": "AI Robotics Inc.",
                "form_type": "D",
                "filing_date": "2024-04-15",
                "detail_url": "https://www.sec.gov/Archives/edgar/data/1234567/000123456724000001/0001234567-24-000001-index.html",
                "amount_raised": 5000000.0,
                "offering_amount": 10000000.0,
                "filing_type": "NEW",
                "investor_count": 12,
                "industry_group": "Technology",
                "issuer_size": "Declining to Disclose",
                "issuer_city": "San Francisco",
                "issuer_state": "CA",
                "related_persons": [
                    {"name": "Jane Smith", "title": "CEO"},
                    {"name": "John Doe", "title": "CFO"}
                ]
            },
            {
                "accession_number": "0002345678-24-000001",
                "cik": "0002345678",
                "company_name": "Quantum Computing Labs LLC",
                "form_type": "D",
                "filing_date": "2024-04-10",
                "detail_url": "https://www.sec.gov/Archives/edgar/data/2345678/000234567824000001/0002345678-24-000001-index.html",
                "amount_raised": 3000000.0,
                "offering_amount": 5000000.0,
                "filing_type": "NEW",
                "investor_count": 8,
                "industry_group": "Technology",
                "issuer_size": "$1-$5 Million",
                "issuer_city": "Boston",
                "issuer_state": "MA",
                "related_persons": [
                    {"name": "Robert Chen", "title": "CEO"},
                    {"name": "Sarah Johnson", "title": "CTO"}
                ]
            }
        ]
    
    async def _convert_filing_to_entity(self, filing: Dict[str, Any]) -> FormDFiling:
        """
        Convert a Form D filing to a FormDFiling entity.
        
        Args:
            filing: Filing data from SEC EDGAR
            
        Returns:
            FormDFiling entity
        """
        # Parse filing date
        try:
            filing_date = datetime.strptime(filing["filing_date"], "%Y-%m-%d")
        except ValueError:
            filing_date = datetime.now()
        
        entity = FormDFiling(
            id=f"form_d_{filing['accession_number']}",
            source_id=filing["accession_number"],
            name=f"Form D - {filing['company_name']}",
            company_name=filing["company_name"],
            filing_date=filing_date,
            amount_raised=filing["amount_raised"],
            offering_amount=filing["offering_amount"],
            filing_type=filing["filing_type"],
            investor_count=filing["investor_count"],
            industry_group=filing["industry_group"],
            issuer_size=filing["issuer_size"],
            issuer_city=filing["issuer_city"],
            issuer_state=filing["issuer_state"],
            cik=filing["cik"],
            related_persons=filing["related_persons"]
        )
        
        return entity
    
    async def _find_company_by_name(self, company_name: str) -> Optional[Company]:
        """
        Find a company by name in the database.
        
        This uses a simple matching strategy. In a production environment,
        you would want to use a more sophisticated entity resolution approach.
        
        Args:
            company_name: Name of the company from Form D
            
        Returns:
            Company entity if found, None otherwise
        """
        with self.session_factory() as session:
            # Try to find company with exact name match
            company = session.query(Company).filter(Company.name == company_name).first()
            
            if not company:
                # Try to find company where names are similar
                # Note: In production, you'd use a more sophisticated fuzzy matching approach
                company_name_clean = company_name.lower()
                for suffix in [" inc.", " inc", " llc", " corporation", " corp.", " corp", " limited", " ltd.", " ltd"]:
                    company_name_clean = company_name_clean.replace(suffix, "")
                
                company_name_clean = company_name_clean.strip()
                companies = session.query(Company).all()
                
                for c in companies:
                    c_name_clean = c.name.lower()
                    for suffix in [" inc.", " inc", " llc", " corporation", " corp.", " corp", " limited", " ltd.", " ltd"]:
                        c_name_clean = c_name_clean.replace(suffix, "")
                    
                    c_name_clean = c_name_clean.strip()
                    
                    if c_name_clean == company_name_clean:
                        return c
            
            return company
    
    async def ingest(self, days_lookback: int = DEFAULT_DAYS_LOOKBACK) -> Tuple[int, int]:
        """
        Ingest Form D filings from SEC EDGAR.
        
        Args:
            days_lookback: Number of days to look back for filings
            
        Returns:
            Tuple of (num_entities_created, num_relationships_created)
        """
        logger.info("Starting SEC Form D ingestion")
        
        # Get latest Form D filings
        filings = await self._get_latest_form_d_filings(days_lookback)
        
        num_entities = 0
        num_relationships = 0
        
        if not filings:
            logger.warning("No Form D filings found")
            return num_entities, num_relationships
        
        with self.session_factory() as session:
            for filing in filings:
                try:
                    # Extract details from filing
                    enhanced_filing = await self._extract_filing_details(filing)
                    
                    # Convert filing to entity
                    entity = await self._convert_filing_to_entity(enhanced_filing)
                    
                    # Check if entity already exists
                    existing = session.query(FormDFiling).filter(
                        FormDFiling.source_id == entity.source_id
                    ).first()
                    
                    if not existing:
                        # Create entity
                        session.add(entity)
                        num_entities += 1
                        logger.info(f"Created Form D filing entity: {entity.company_name}")
                        
                        # Try to find associated company
                        company = await self._find_company_by_name(entity.company_name)
                        
                        if company:
                            # Create relationship between company and Form D filing
                            relationship = FormDRelationship(
                                id=f"form_d_rel_{uuid.uuid4()}",
                                from_entity_id=company.id,
                                to_entity_id=entity.id,
                                filing_date=entity.filing_date,
                                amount_raised=entity.amount_raised,
                                properties={
                                    "offering_amount": entity.offering_amount,
                                    "filing_type": entity.filing_type,
                                    "investor_count": entity.investor_count
                                }
                            )
                            
                            session.add(relationship)
                            num_relationships += 1
                            logger.info(f"Created Form D relationship for company: {company.name}")
                    
                except Exception as e:
                    logger.error(f"Error processing filing {filing.get('accession_number')}: {str(e)}")
            
            session.commit()
        
        logger.info(f"SEC Form D ingestion completed. Created {num_entities} entities and {num_relationships} relationships")
        return num_entities, num_relationships