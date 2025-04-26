"""
AngelList Connector for Graph Ingest Service.

This module fetches syndicate deal data from AngelList and creates
entities and relationships in the knowledge graph.
"""
import os
import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import requests
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.base import SourceType, EntityType
from app.models.angellist import AngelDeal, AngelDealRelationship
from app.db import insert_entity, insert_relationship, get_entity_by_source_id
from .base import BaseIngestor

# Set up logging
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "https://api.angel.co/v1"
DEFAULT_DAYS_LOOKBACK = 30

class AngelListConnector(BaseIngestor):
    """
    Connector for fetching syndicate deal data from AngelList.
    """
    
    def __init__(self, db: Session, api_token: Optional[str] = None, **kwargs):
        """
        Initialize the AngelList connector.
        
        Args:
            db: Database session
            api_token: AngelList API token (defaults to ANGELLIST_ACCESS_TOKEN env var)
            **kwargs: Additional arguments
        """
        super().__init__(db, **kwargs)
        self.api_token = api_token or os.environ.get("ANGELLIST_ACCESS_TOKEN")
        if not self.api_token:
            logger.warning("No AngelList API token provided. Some functionality may be limited.")
        
        # Store when the last sync occurred
        self.last_sync_path = os.path.join(os.path.dirname(__file__), "../../data/angellist_last_sync.json")
        self.last_sync_date = self._get_last_sync_date()
    
    def _get_source_type(self) -> SourceType:
        """Get the source type for the connector."""
        return SourceType.ANGELLIST
    
    def _get_last_sync_date(self) -> Optional[datetime]:
        """
        Get the date of the last sync from the file.
        
        Returns:
            Datetime of the last sync, or None if not available
        """
        try:
            if os.path.exists(self.last_sync_path):
                with open(self.last_sync_path, 'r') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data.get('last_sync_date'))
            return None
        except Exception as e:
            logger.error(f"Error reading last sync date: {e}")
            return None
    
    def _save_last_sync_date(self, sync_date: datetime):
        """
        Save the date of the current sync to a file.
        
        Args:
            sync_date: Datetime of the current sync
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.last_sync_path), exist_ok=True)
            
            with open(self.last_sync_path, 'w') as f:
                json.dump({'last_sync_date': sync_date.isoformat()}, f)
        except Exception as e:
            logger.error(f"Error saving last sync date: {e}")
    
    def _fetch_deals(self, days_lookback: int = DEFAULT_DAYS_LOOKBACK) -> List[Dict[str, Any]]:
        """
        Fetch syndicate deals from AngelList API.
        
        Args:
            days_lookback: Number of days to look back for deals
            
        Returns:
            List of deal data dictionaries
        """
        if not self.api_token:
            logger.error("AngelList API token is required to fetch deals")
            return []
        
        # Calculate the date to look back to
        lookback_date = datetime.now() - timedelta(days=days_lookback)
        # If we have a last sync date and it's more recent than the lookback date,
        # use the last sync date instead for incremental sync
        if self.last_sync_date and self.last_sync_date > lookback_date:
            lookback_date = self.last_sync_date
            logger.info(f"Using incremental sync from last sync date: {lookback_date}")
        
        # Prepare request parameters
        params = {
            "access_token": self.api_token,
            "filter": "raising",  # Only get active deals
            "sort": "created_at",
            "created_after": lookback_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        try:
            # Make request to AngelList API
            response = requests.get(f"{API_BASE_URL}/startups", params=params)
            response.raise_for_status()
            deals_data = response.json().get("startups", [])
            
            # Get more details for each deal
            enriched_deals = []
            for deal in deals_data:
                try:
                    # Get detailed information for each deal
                    deal_id = deal.get("id")
                    detail_response = requests.get(
                        f"{API_BASE_URL}/startups/{deal_id}",
                        params={"access_token": self.api_token}
                    )
                    detail_response.raise_for_status()
                    deal_detail = detail_response.json()
                    
                    # Get the round information
                    rounds_response = requests.get(
                        f"{API_BASE_URL}/startups/{deal_id}/funding",
                        params={"access_token": self.api_token}
                    )
                    rounds_response.raise_for_status()
                    rounds_data = rounds_response.json().get("rounds", [])
                    
                    # Add round data to the deal
                    if rounds_data:
                        latest_round = rounds_data[0]  # Assuming the first round is the latest
                        deal_detail["latest_round"] = latest_round
                    
                    enriched_deals.append(deal_detail)
                except Exception as e:
                    logger.error(f"Error fetching details for deal {deal.get('id')}: {e}")
            
            logger.info(f"Fetched {len(enriched_deals)} AngelList deals")
            return enriched_deals
        except Exception as e:
            logger.error(f"Error fetching AngelList deals: {e}")
            return []
    
    def _process_deal(self, deal_data: Dict[str, Any]) -> Optional[AngelDeal]:
        """
        Process a deal from AngelList API and convert to an entity.
        
        Args:
            deal_data: Deal data from the AngelList API
            
        Returns:
            AngelDeal entity or None if processing failed
        """
        try:
            deal_id = str(deal_data.get("id"))
            company_name = deal_data.get("name", "")
            
            # Extract the round information
            latest_round = deal_data.get("latest_round", {})
            round_type = latest_round.get("type", "")
            raised_amount = latest_round.get("raised_amount", 0)
            target_amount = latest_round.get("target_amount", 0)
            valuation = latest_round.get("pre_money_valuation", 0)
            
            # Create deal entity
            deal = AngelDeal(
                id=f"angellist:deal:{deal_id}",
                source_id=deal_id,
                name=f"{company_name} - {round_type} Round",
                company_name=company_name,
                commitment_usd=raised_amount,
                deal_date=datetime.fromisoformat(latest_round.get("created_at", datetime.now().isoformat())) if latest_round.get("created_at") else None,
                lead_investor=latest_round.get("source", {}).get("name") if latest_round.get("source") else None,
                round_type=round_type,
                sector=deal_data.get("markets", [{}])[0].get("name") if deal_data.get("markets") else None,
                description=deal_data.get("high_concept", ""),
                valuation_usd=valuation,
                min_investment=latest_round.get("min_investment", 0),
                target_raise_usd=target_amount,
                location=deal_data.get("location", {}).get("name") if deal_data.get("location") else None,
                properties={
                    "deal_link": deal_data.get("angellist_url", ""),
                    "twitter": deal_data.get("twitter_url", ""),
                    "website": deal_data.get("company_url", ""),
                    "logo_url": deal_data.get("logo_url", ""),
                    "status": "active" if deal_data.get("fundraising", False) else "closed"
                }
            )
            return deal
        except Exception as e:
            logger.error(f"Error processing deal {deal_data.get('id')}: {e}")
            return None
    
    def ingest(self, days_lookback: int = DEFAULT_DAYS_LOOKBACK, **kwargs) -> Dict[str, Any]:
        """
        Run the ingestion process to fetch AngelList syndicate deals.
        
        Args:
            days_lookback: Number of days to look back for deals
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with ingestion results
        """
        logger.info(f"Starting AngelList deal ingestion, looking back {days_lookback} days")
        current_sync_date = datetime.now()
        
        # Fetch deals from AngelList
        deals_data = self._fetch_deals(days_lookback)
        
        if not deals_data:
            logger.warning("No AngelList deals found")
            return {
                "status": "completed",
                "entities_created": 0,
                "relationships_created": 0,
                "message": "No deals found"
            }
        
        # Process and store deals
        entities_created = 0
        relationships_created = 0
        
        for deal_data in deals_data:
            try:
                # Convert to entity
                deal = self._process_deal(deal_data)
                if not deal:
                    continue
                
                # Check if entity already exists
                existing_entity = get_entity_by_source_id(
                    self.db, 
                    source_type=SourceType.ANGELLIST,
                    source_id=deal.source_id
                )
                
                # If it exists, update it; otherwise, create it
                if existing_entity:
                    # Update entity with new data
                    # Update properties that may have changed
                    existing_entity.name = deal.name
                    existing_entity.properties.update(deal.properties)
                    # Update specific fields
                    existing_entity.properties["commitment_usd"] = deal.commitment_usd
                    # Save changes
                    self.db.commit()
                    logger.info(f"Updated AngelList deal: {deal.name}")
                else:
                    # Create new entity
                    insert_entity(self.db, deal)
                    entities_created += 1
                    logger.info(f"Created AngelList deal: {deal.name}")
                
                # TODO: Create relationships with investors if data is available
                
            except Exception as e:
                logger.error(f"Error processing deal {deal_data.get('id')}: {e}")
        
        # Save the current sync date for incremental sync next time
        self._save_last_sync_date(current_sync_date)
        
        return {
            "status": "completed",
            "entities_created": entities_created,
            "relationships_created": relationships_created,
            "message": f"Successfully ingested {entities_created} AngelList deals"
        }