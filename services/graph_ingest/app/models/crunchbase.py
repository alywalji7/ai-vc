from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .base import BaseEntity, BaseRelationship, EntityType, RelationshipType, SourceType


class CrunchbaseCompany(BaseEntity):
    """Crunchbase company entity"""
    type: EntityType = EntityType.COMPANY
    source: SourceType = SourceType.CRUNCHBASE
    permalink: str
    website: Optional[str] = None
    founded_on: Optional[str] = None
    short_description: Optional[str] = None
    country_code: Optional[str] = None
    state_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    status: Optional[str] = None
    category_list: List[str] = Field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "CrunchbaseCompany":
        """Create a CrunchbaseCompany from Crunchbase API response"""
        properties = data.get("properties", {})
        
        return cls(
            id=f"crunchbase:company:{data['uuid']}",
            source_id=data["uuid"],
            name=properties.get("name", ""),
            permalink=properties.get("permalink", ""),
            website=properties.get("website", {}).get("value") if properties.get("website") else None,
            founded_on=properties.get("founded_on", {}).get("value") if properties.get("founded_on") else None,
            short_description=properties.get("short_description", ""),
            country_code=properties.get("country_code", ""),
            state_code=properties.get("state_code", ""),
            region=properties.get("region", ""),
            city=properties.get("city", ""),
            status=properties.get("status", ""),
            category_list=properties.get("category_list", "").split(",") if properties.get("category_list") else [],
            properties={
                "num_employees_min": properties.get("num_employees_min", ""),
                "num_employees_max": properties.get("num_employees_max", ""),
                "linkedin": properties.get("linkedin", {}).get("value") if properties.get("linkedin") else None,
                "twitter": properties.get("twitter", {}).get("value") if properties.get("twitter") else None,
                "facebook": properties.get("facebook", {}).get("value") if properties.get("facebook") else None,
                "company_type": properties.get("company_type", ""),
                "stock_exchange": properties.get("stock_exchange", ""),
                "stock_symbol": properties.get("stock_symbol", ""),
                "rank_org_company": properties.get("rank_org_company", 0),
                "revenue_range": properties.get("revenue_range", ""),
                "total_funding_usd": properties.get("total_funding_usd", 0),
                "number_of_investments": properties.get("number_of_investments", 0),
                "number_of_acquisitions": properties.get("number_of_acquisitions", 0),
            }
        )


class CrunchbasePerson(BaseEntity):
    """Crunchbase person entity (founder, investor, etc.)"""
    type: EntityType = EntityType.PERSON
    source: SourceType = SourceType.CRUNCHBASE
    permalink: str
    first_name: str
    last_name: str
    gender: Optional[str] = None
    country_code: Optional[str] = None
    state_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any], entity_type: EntityType = EntityType.PERSON) -> "CrunchbasePerson":
        """Create a CrunchbasePerson from Crunchbase API response"""
        properties = data.get("properties", {})
        
        return cls(
            id=f"crunchbase:person:{data['uuid']}",
            type=entity_type,
            source_id=data["uuid"],
            name=f"{properties.get('first_name', '')} {properties.get('last_name', '')}".strip(),
            permalink=properties.get("permalink", ""),
            first_name=properties.get("first_name", ""),
            last_name=properties.get("last_name", ""),
            gender=properties.get("gender", ""),
            country_code=properties.get("country_code", ""),
            state_code=properties.get("state_code", ""),
            region=properties.get("region", ""),
            city=properties.get("city", ""),
            properties={
                "linkedin": properties.get("linkedin", {}).get("value") if properties.get("linkedin") else None,
                "twitter": properties.get("twitter", {}).get("value") if properties.get("twitter") else None,
                "facebook": properties.get("facebook", {}).get("value") if properties.get("facebook") else None,
                "rank_person": properties.get("rank_person", 0),
                "title": properties.get("title", ""),
                "featured_job_organization": properties.get("featured_job_organization", ""),
            }
        )


class CrunchbaseFounder(BaseRelationship):
    """Relationship between a person and a company they founded"""
    type: RelationshipType = RelationshipType.FOUNDED
    source: SourceType = SourceType.CRUNCHBASE
    title: Optional[str] = None
    started_on: Optional[str] = None
    ended_on: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, person_id: str, company_id: str, data: Dict[str, Any]) -> "CrunchbaseFounder":
        """Create a CrunchbaseFounder from Crunchbase API response"""
        properties = data.get("properties", {})
        
        return cls(
            id=f"crunchbase:founder:{person_id}:{company_id}",
            from_entity_id=person_id,
            to_entity_id=company_id,
            title=properties.get("title", ""),
            started_on=properties.get("started_on", ""),
            ended_on=properties.get("ended_on", ""),
            properties={
                "is_current": properties.get("is_current", True),
                "sequence": properties.get("sequence", 0),
            }
        )


class CrunchbaseFundingRound(BaseEntity):
    """Crunchbase funding round entity"""
    type: EntityType = EntityType.FUNDING_ROUND
    source: SourceType = SourceType.CRUNCHBASE
    permalink: str
    investment_type: str
    announced_on: Optional[str] = None
    amount: Optional[int] = None
    amount_currency_code: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "CrunchbaseFundingRound":
        """Create a CrunchbaseFundingRound from Crunchbase API response"""
        properties = data.get("properties", {})
        
        return cls(
            id=f"crunchbase:round:{data['uuid']}",
            source_id=data["uuid"],
            name=properties.get("series", "Funding Round"),
            permalink=properties.get("permalink", ""),
            investment_type=properties.get("investment_type", ""),
            announced_on=properties.get("announced_on", ""),
            amount=properties.get("money_raised", 0),
            amount_currency_code=properties.get("money_raised_currency_code", "USD"),
            properties={
                "series": properties.get("series", ""),
                "series_qualifier": properties.get("series_qualifier", ""),
                "post_money_valuation": properties.get("post_money_valuation", 0),
                "post_money_valuation_currency_code": properties.get("post_money_valuation_currency_code", "USD"),
                "investor_count": properties.get("investor_count", 0),
                "investor_names": properties.get("investor_names", "").split(",") if properties.get("investor_names") else [],
                "lead_investor_names": properties.get("lead_investor_names", "").split(",") if properties.get("lead_investor_names") else [],
            }
        )


class CrunchbaseFundedBy(BaseRelationship):
    """Relationship between a company and a funding round"""
    type: RelationshipType = RelationshipType.FUNDED_BY
    source: SourceType = SourceType.CRUNCHBASE
    
    @classmethod
    def create(cls, company_id: str, round_id: str) -> "CrunchbaseFundedBy":
        """Create a CrunchbaseFundedBy relationship"""
        return cls(
            id=f"crunchbase:funded_by:{company_id}:{round_id}",
            from_entity_id=company_id,
            to_entity_id=round_id,
        )


class CrunchbaseParticipatedIn(BaseRelationship):
    """Relationship between an investor and a funding round"""
    type: RelationshipType = RelationshipType.PARTICIPATED_IN
    source: SourceType = SourceType.CRUNCHBASE
    is_lead_investor: bool = False
    amount: Optional[int] = None
    amount_currency_code: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, investor_id: str, round_id: str, data: Dict[str, Any]) -> "CrunchbaseParticipatedIn":
        """Create a CrunchbaseParticipatedIn from Crunchbase API response"""
        properties = data.get("properties", {})
        
        return cls(
            id=f"crunchbase:participated_in:{investor_id}:{round_id}",
            from_entity_id=investor_id,
            to_entity_id=round_id,
            is_lead_investor=properties.get("is_lead_investor", False),
            amount=properties.get("amount", 0),
            amount_currency_code=properties.get("amount_currency_code", "USD"),
            properties={
                "investor_type": properties.get("investor_type", ""),
            }
        )