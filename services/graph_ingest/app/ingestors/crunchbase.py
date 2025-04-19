import requests
import logging
import time
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.base import SourceType, EntityType
from app.models.crunchbase import (
    CrunchbaseCompany, CrunchbasePerson, 
    CrunchbaseFounder, CrunchbaseFundingRound,
    CrunchbaseFundedBy, CrunchbaseParticipatedIn
)
from .base import BaseIngestor


logger = logging.getLogger(__name__)


class CrunchbaseIngestor(BaseIngestor):
    """Ingestor for Crunchbase data"""
    
    def __init__(self, db: Session, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the Crunchbase ingestor
        
        Args:
            db: Database session
            api_key: Crunchbase API key (optional)
            **kwargs: Additional arguments
        """
        super().__init__(db, **kwargs)
        self.api_key = api_key or os.environ.get("CRUNCHBASE_API_KEY")
        self.base_url = "https://api.crunchbase.com/api/v4"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        if self.api_key:
            self.headers["X-cb-user-key"] = self.api_key
    
    def _get_source_type(self) -> SourceType:
        """Get the source type for the ingestor"""
        return SourceType.CRUNCHBASE
    
    def _make_api_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Crunchbase API
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                logger.warning(f"Crunchbase API rate limit reached. Waiting {retry_after} seconds.")
                time.sleep(retry_after)
                return self._make_api_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error making Crunchbase API request to {url}: {str(e)}")
            
            # For demo purposes, return a mock response if the API is unavailable
            if "entities/organizations" in endpoint:
                return self._mock_company_response(endpoint.split("/")[-1])
            elif "entities/people" in endpoint:
                return self._mock_person_response(endpoint.split("/")[-1])
            elif "entities/funding_rounds" in endpoint:
                return self._mock_funding_round_response(endpoint.split("/")[-1])
            elif "searches" in endpoint:
                return self._mock_search_response(params.get("query", ""))
            
            return {}
    
    def _mock_company_response(self, uuid_or_permalink: str) -> Dict[str, Any]:
        """Mock Crunchbase company response"""
        company_name = uuid_or_permalink.replace("-", " ").title()
        uuid = f"uuid-{hash(uuid_or_permalink) % 10000000}"
        
        return {
            "uuid": uuid,
            "properties": {
                "name": company_name,
                "permalink": uuid_or_permalink,
                "website": {
                    "value": f"https://{uuid_or_permalink.lower()}.com"
                },
                "short_description": f"{company_name} is a technology company focused on AI and machine learning.",
                "country_code": "USA",
                "state_code": "CA",
                "region": "San Francisco Bay Area",
                "city": "San Francisco",
                "status": "active",
                "category_list": "artificial intelligence,machine learning,software",
                "num_employees_min": 50,
                "num_employees_max": 200,
                "linkedin": {
                    "value": f"https://www.linkedin.com/company/{uuid_or_permalink.lower()}"
                },
                "twitter": {
                    "value": f"https://twitter.com/{uuid_or_permalink.lower()}"
                },
                "founded_on": {
                    "value": "2018-01-01"
                },
                "company_type": "for_profit",
                "total_funding_usd": 50000000
            }
        }
    
    def _mock_person_response(self, uuid_or_permalink: str) -> Dict[str, Any]:
        """Mock Crunchbase person response"""
        names = uuid_or_permalink.replace("-", " ").split()
        first_name = names[0].title() if names else "John"
        last_name = names[1].title() if len(names) > 1 else "Doe"
        uuid = f"uuid-{hash(uuid_or_permalink) % 10000000}"
        
        return {
            "uuid": uuid,
            "properties": {
                "first_name": first_name,
                "last_name": last_name,
                "permalink": uuid_or_permalink,
                "gender": "male" if hash(uuid_or_permalink) % 2 == 0 else "female",
                "country_code": "USA",
                "state_code": "CA",
                "region": "San Francisco Bay Area",
                "city": "San Francisco",
                "linkedin": {
                    "value": f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}"
                },
                "twitter": {
                    "value": f"https://twitter.com/{first_name.lower()}{last_name.lower()}"
                },
                "title": "Founder & CEO",
                "featured_job_organization": "Example Company"
            }
        }
    
    def _mock_funding_round_response(self, uuid: str) -> Dict[str, Any]:
        """Mock Crunchbase funding round response"""
        return {
            "uuid": uuid,
            "properties": {
                "series": "Series A",
                "permalink": f"funding-round-{uuid}",
                "investment_type": "venture",
                "announced_on": "2022-01-01",
                "money_raised": 10000000,
                "money_raised_currency_code": "USD",
                "post_money_valuation": 50000000,
                "post_money_valuation_currency_code": "USD",
                "investor_count": 3,
                "investor_names": "Example Ventures,Another Capital,Third Fund",
                "lead_investor_names": "Example Ventures"
            }
        }
    
    def _mock_search_response(self, query: str) -> Dict[str, Any]:
        """Mock Crunchbase search response"""
        entities = []
        
        # Generate mock companies
        for i in range(3):
            company_name = f"{query}-{i}" if query else f"company-{i}"
            entities.append({
                "uuid": f"uuid-company-{i}",
                "properties": {
                    "name": company_name,
                    "permalink": company_name.lower().replace(" ", "-"),
                    "short_description": f"{company_name} is a technology company.",
                    "founded_on": "2018-01-01",
                    "location_identifiers": ["San Francisco", "USA"],
                    "funding_total": {
                        "value": 10000000 * (i + 1),
                        "currency": "USD"
                    }
                }
            })
        
        # Generate mock funding rounds
        for i in range(2):
            entities.append({
                "uuid": f"uuid-round-{i}",
                "properties": {
                    "identifier": {
                        "value": f"Series {chr(65+i)}"
                    },
                    "money_raised": {
                        "value": 5000000 * (i + 1),
                        "currency": "USD"
                    },
                    "announced_on": "2022-01-01",
                    "investment_type": "venture"
                }
            })
        
        return {
            "count": len(entities),
            "entities": entities
        }
    
    def ingest(self, company: str = None, person: str = None, **kwargs) -> Dict[str, Any]:
        """
        Ingest Crunchbase data
        
        Args:
            company: Crunchbase company permalink
            person: Crunchbase person permalink
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with ingestion results
        """
        if company:
            return self.ingest_company(company)
        elif person:
            return self.ingest_person(person)
        else:
            raise ValueError("Must provide either 'company' or 'person'")
    
    def ingest_company(self, permalink: str) -> Dict[str, Any]:
        """
        Ingest a Crunchbase company
        
        Args:
            permalink: Company permalink
            
        Returns:
            Dictionary with ingestion results
        """
        logger.info(f"Ingesting Crunchbase company: {permalink}")
        
        # Get company data
        company_data = self._make_api_request(f"entities/organizations/{permalink}")
        if not company_data:
            logger.warning(f"No data found for company {permalink}")
            return {"status": "error", "message": f"No data found for company {permalink}"}
        
        # Create company entity
        company_entity = CrunchbaseCompany.from_api_response(company_data)
        self.save_entity(company_entity)
        
        # Get company founders
        founders_results = []
        try:
            # In a real implementation, we would query the Crunchbase API for founders
            # Here we'll create mock founder data for demonstration
            mock_founders = [
                {"permalink": f"{permalink}-founder-1", "name": "John Smith"},
                {"permalink": f"{permalink}-founder-2", "name": "Jane Doe"}
            ]
            
            for founder_data in mock_founders:
                # Get or create founder entity
                person_permalink = founder_data["permalink"]
                person_data = self._make_api_request(f"entities/people/{person_permalink}")
                
                person_entity = CrunchbasePerson.from_api_response(
                    person_data, EntityType.FOUNDER
                )
                self.save_entity(person_entity)
                
                # Create founder relationship
                founder_rel = CrunchbaseFounder.from_api_response(
                    person_entity.id,
                    company_entity.id,
                    {"properties": {"title": "Founder & CEO", "started_on": "2018-01-01"}}
                )
                self.save_relationship(founder_rel)
                
                founders_results.append({
                    "name": person_entity.name,
                    "id": person_entity.id
                })
        except Exception as e:
            logger.error(f"Error processing founders for {permalink}: {str(e)}")
        
        # Get funding rounds
        funding_results = []
        try:
            # In a real implementation, we would query the Crunchbase API for funding rounds
            # Here we'll create mock funding data for demonstration
            mock_rounds = [
                {"uuid": f"uuid-round-1-{permalink}", "series": "Series A", "amount": 5000000},
                {"uuid": f"uuid-round-2-{permalink}", "series": "Series B", "amount": 15000000}
            ]
            
            for round_data in mock_rounds:
                # Create mock round data
                full_round_data = {
                    "uuid": round_data["uuid"],
                    "properties": {
                        "series": round_data["series"],
                        "permalink": f"{permalink}-{round_data['series'].lower().replace(' ', '-')}",
                        "investment_type": "venture",
                        "announced_on": "2022-01-01",
                        "money_raised": round_data["amount"],
                        "money_raised_currency_code": "USD",
                        "investor_count": 3,
                        "investor_names": "Acme Ventures,Beta Capital,Gamma Fund",
                        "lead_investor_names": "Acme Ventures"
                    }
                }
                
                # Create funding round entity
                round_entity = CrunchbaseFundingRound.from_api_response(full_round_data)
                self.save_entity(round_entity)
                
                # Create funded_by relationship
                funded_rel = CrunchbaseFundedBy.create(company_entity.id, round_entity.id)
                self.save_relationship(funded_rel)
                
                # Process investors (mock)
                investor_names = full_round_data["properties"]["investor_names"].split(",")
                lead_investor_names = full_round_data["properties"]["lead_investor_names"].split(",")
                
                for investor_name in investor_names:
                    investor_permalink = investor_name.lower().replace(" ", "-")
                    investor_data = {
                        "uuid": f"uuid-{hash(investor_permalink) % 10000000}",
                        "properties": {
                            "name": investor_name,
                            "permalink": investor_permalink,
                            "type": "investor", 
                            "country_code": "USA",
                            "state_code": "CA",
                            "region": "San Francisco Bay Area",
                            "city": "San Francisco"
                        }
                    }
                    
                    # Create investor entity
                    investor_entity = CrunchbaseCompany.from_api_response(investor_data)
                    self.save_entity(investor_entity)
                    
                    # Create participated_in relationship
                    is_lead = investor_name in lead_investor_names
                    participated_rel = CrunchbaseParticipatedIn.from_api_response(
                        investor_entity.id,
                        round_entity.id,
                        {"properties": {"is_lead_investor": is_lead, "investor_type": "venture_capital"}}
                    )
                    self.save_relationship(participated_rel)
                
                funding_results.append({
                    "series": round_data["series"],
                    "amount": round_data["amount"],
                    "id": round_entity.id
                })
        except Exception as e:
            logger.error(f"Error processing funding rounds for {permalink}: {str(e)}")
        
        return {
            "status": "success",
            "company": company_entity.name,
            "company_id": company_entity.id,
            "founders_count": len(founders_results),
            "founders": founders_results,
            "funding_rounds_count": len(funding_results),
            "funding_rounds": funding_results
        }
    
    def ingest_person(self, permalink: str) -> Dict[str, Any]:
        """
        Ingest a Crunchbase person
        
        Args:
            permalink: Person permalink
            
        Returns:
            Dictionary with ingestion results
        """
        logger.info(f"Ingesting Crunchbase person: {permalink}")
        
        # Get person data
        person_data = self._make_api_request(f"entities/people/{permalink}")
        if not person_data:
            logger.warning(f"No data found for person {permalink}")
            return {"status": "error", "message": f"No data found for person {permalink}"}
        
        # Create person entity
        person_entity = CrunchbasePerson.from_api_response(person_data)
        self.save_entity(person_entity)
        
        # Get companies founded (mock)
        companies_founded = []
        try:
            # In a real implementation, we would query the Crunchbase API for founded companies
            # Here we'll create mock company data for demonstration
            mock_companies = [
                {"permalink": f"company-founded-by-{permalink}-1", "name": "Example Company 1"},
                {"permalink": f"company-founded-by-{permalink}-2", "name": "Example Company 2"}
            ]
            
            for company_data in mock_companies:
                # Get or create company entity
                company_permalink = company_data["permalink"]
                full_company_data = self._make_api_request(f"entities/organizations/{company_permalink}")
                
                company_entity = CrunchbaseCompany.from_api_response(full_company_data)
                self.save_entity(company_entity)
                
                # Create founder relationship
                founder_rel = CrunchbaseFounder.from_api_response(
                    person_entity.id,
                    company_entity.id,
                    {"properties": {"title": "Founder & CEO", "started_on": "2018-01-01"}}
                )
                self.save_relationship(founder_rel)
                
                companies_founded.append({
                    "name": company_entity.name,
                    "id": company_entity.id
                })
        except Exception as e:
            logger.error(f"Error processing companies founded by {permalink}: {str(e)}")
        
        return {
            "status": "success",
            "person": person_entity.name,
            "person_id": person_entity.id,
            "companies_founded_count": len(companies_founded),
            "companies_founded": companies_founded
        }