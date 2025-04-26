"""
Y Combinator Launch Connector for Graph Ingest Service.

This module fetches Y Combinator company launch data from the YC RSS feed and creates
entities and relationships in the knowledge graph.
"""
import os
import logging
import uuid
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import requests
import feedparser
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.base import SourceType, EntityType
from app.models.yc_launch import YCCompany, YCLaunchRelationship
from app.db import insert_entity, insert_relationship, get_entity_by_source_id
from .base import BaseIngestor

# Set up logging
logger = logging.getLogger(__name__)

# Constants
YC_RSS_URL = "https://www.ycombinator.com/launches/rss"
YC_COMPANIES_URL = "https://www.ycombinator.com/companies"
DEFAULT_DAYS_LOOKBACK = 30

class YCLaunchConnector(BaseIngestor):
    """
    Connector for fetching company launch data from Y Combinator.
    """
    
    def __init__(self, db: Session, **kwargs):
        """
        Initialize the YC Launch connector.
        
        Args:
            db: Database session
            **kwargs: Additional arguments
        """
        super().__init__(db, **kwargs)
        
        # Store when the last sync occurred
        self.last_sync_path = os.path.join(os.path.dirname(__file__), "../../data/yc_launch_last_sync.json")
        self.last_sync_date = self._get_last_sync_date()
    
    def _get_source_type(self) -> SourceType:
        """Get the source type for the connector."""
        return SourceType.YC_LAUNCH
    
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
    
    def _fetch_launches(self, days_lookback: int = DEFAULT_DAYS_LOOKBACK) -> List[Dict[str, Any]]:
        """
        Fetch YC company launches from the RSS feed.
        
        Args:
            days_lookback: Number of days to look back for launches
            
        Returns:
            List of launch data dictionaries
        """
        try:
            # Parse the RSS feed
            feed = feedparser.parse(YC_RSS_URL)
            
            if not feed.entries:
                logger.warning("No entries found in YC RSS feed")
                return []
            
            # Calculate the date to look back to
            lookback_date = datetime.now() - timedelta(days=days_lookback)
            # If we have a last sync date and it's more recent than the lookback date,
            # use the last sync date instead for incremental sync
            if self.last_sync_date and self.last_sync_date > lookback_date:
                lookback_date = self.last_sync_date
                logger.info(f"Using incremental sync from last sync date: {lookback_date}")
            
            # Filter entries by published date
            filtered_entries = []
            for entry in feed.entries:
                # Parse the published date
                published_date = datetime.fromtimestamp(
                    datetime(*entry.published_parsed[:6]).timestamp()
                )
                
                # Check if the entry is newer than our lookback date
                if published_date >= lookback_date:
                    entry_data = {
                        "id": entry.get("id", ""),
                        "link": entry.get("link", ""),
                        "title": entry.get("title", ""),
                        "published": published_date,
                        "summary": entry.get("summary", ""),
                        "content": entry.get("content", [{}])[0].get("value", "") if entry.get("content") else "",
                    }
                    filtered_entries.append(entry_data)
            
            logger.info(f"Fetched {len(filtered_entries)} YC company launches")
            return filtered_entries
        except Exception as e:
            logger.error(f"Error fetching YC launches: {e}")
            return []
    
    def _enrich_launch_data(self, launch_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich launch data with additional information from the company page.
        
        Args:
            launch_data: Basic launch data from the RSS feed
            
        Returns:
            Enriched launch data dictionary
        """
        try:
            # Extract company name from title
            company_name = launch_data["title"].strip()
            
            # Fetch the company page
            try:
                response = requests.get(launch_data["link"])
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract logo URL
                logo_element = soup.select_one('img.company-logo')
                logo_url = logo_element.get('src') if logo_element else None
                
                # Extract description
                description_element = soup.select_one('div.company-description')
                description = description_element.text.strip() if description_element else None
                
                # Extract batch
                batch_element = soup.select_one('div.batch')
                batch = batch_element.text.strip() if batch_element else None
                
                # Extract founders
                founders_element = soup.select('div.founder-name')
                founders = [f.text.strip() for f in founders_element] if founders_element else []
                
                # Calculate a launch score based on comments, views, upvotes
                # This is a simplification and would need real data in production
                comments_element = soup.select_one('span.comment-count')
                comments = int(comments_element.text.strip()) if comments_element else 0
                
                views_element = soup.select_one('span.view-count')
                views = int(views_element.text.strip()) if views_element else 0
                
                # Calculate score (simple heuristic)
                launch_score = 0.0
                if comments > 0 or views > 0:
                    launch_score = (comments * 2.0 + views * 0.1) / 10.0
                    # Cap at 10.0
                    launch_score = min(10.0, launch_score)
            except requests.RequestException as req_err:
                logger.warning(f"Failed to fetch company page for {company_name}: {req_err}")
                # Set some default values
                logo_url = None
                description = None
                batch = None
                founders = []
                launch_score = 0.0
            
            # Update launch data with enriched information
            launch_data.update({
                "logo_url": logo_url,
                "description": description,
                "batch": batch,
                "founders": founders,
                "launch_score": launch_score,
                "sector": self._extract_sector(description) if description else None,
                "website": self._extract_website(launch_data["content"]),
            })
            
            return launch_data
        except Exception as e:
            logger.error(f"Error enriching launch data for {launch_data.get('title')}: {e}")
            return launch_data
    
    def _extract_sector(self, description: str) -> Optional[str]:
        """
        Extract the sector/industry from the company description.
        
        Args:
            description: Company description
            
        Returns:
            Extracted sector or None
        """
        # Simple keyword-based extraction
        # In a production environment, this would use NLP or a more sophisticated approach
        sectors = {
            "AI": ["ai", "artificial intelligence", "machine learning", "ml", "deep learning"],
            "FinTech": ["fintech", "financial", "banking", "finance", "payment"],
            "Healthcare": ["health", "medical", "healthcare", "biotech", "life sciences"],
            "EdTech": ["education", "learning", "edtech", "teaching"],
            "Enterprise": ["enterprise", "b2b", "business software", "saas"],
            "Consumer": ["consumer", "b2c", "retail", "e-commerce"],
            "Crypto": ["crypto", "blockchain", "web3", "nft", "bitcoin"]
        }
        
        if not description:
            return None
        
        description_lower = description.lower()
        
        for sector, keywords in sectors.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return sector
        
        return None
    
    def _extract_website(self, content: str) -> Optional[str]:
        """
        Extract website URL from content.
        
        Args:
            content: HTML content
            
        Returns:
            Extracted website URL or None
        """
        if not content:
            return None
        
        # Use regex to find URLs
        url_pattern = r'https?://(?:www\.)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?(?:/[^\\s"\'>]*)?'
        urls = re.findall(url_pattern, content)
        
        if urls:
            # Filter out ycombinator URLs
            non_yc_urls = [url for url in urls if "ycombinator.com" not in url and "news.ycombinator.com" not in url]
            return non_yc_urls[0] if non_yc_urls else None
        
        return None
    
    def _process_launch(self, launch_data: Dict[str, Any]) -> Optional[YCCompany]:
        """
        Process launch data and convert to an entity.
        
        Args:
            launch_data: Launch data dictionary
            
        Returns:
            YCCompany entity or None if processing failed
        """
        try:
            # Extract a unique ID from the link
            link = launch_data.get("link", "")
            if not link:
                logger.warning("Launch data missing link")
                return None
            
            # Extract ID from the URL path
            match = re.search(r'/launches/([^/]+)', link)
            launch_id = match.group(1) if match else str(uuid.uuid4())
            
            company_name = launch_data.get("title", "").strip()
            if not company_name:
                logger.warning("Launch data missing company name")
                return None
            
            # Create YC company entity
            company = YCCompany(
                id=f"yc:company:{launch_id}",
                source_id=launch_id,
                name=company_name,
                company_name=company_name,
                batch=launch_data.get("batch"),
                launch_date=launch_data.get("published"),
                description=launch_data.get("description"),
                website=launch_data.get("website"),
                sector=launch_data.get("sector"),
                logo_url=launch_data.get("logo_url"),
                founders=launch_data.get("founders", []),
                launch_score=launch_data.get("launch_score", 0.0),
                properties={
                    "launch_link": link,
                    "rss_id": launch_data.get("id", ""),
                }
            )
            return company
        except Exception as e:
            logger.error(f"Error processing launch for {launch_data.get('title')}: {e}")
            return None
    
    def _fetch_and_process_launches(self, days_lookback: int = DEFAULT_DAYS_LOOKBACK) -> List[YCCompany]:
        """
        Fetch and process launches from the YC RSS feed.
        
        Args:
            days_lookback: Number of days to look back for launches
            
        Returns:
            List of processed YCCompany entities
        """
        # Fetch basic launch data from RSS
        launches_data = self._fetch_launches(days_lookback)
        
        if not launches_data:
            return []
        
        # Enrich the data with more details
        enriched_launches = []
        for launch_data in launches_data:
            enriched_data = self._enrich_launch_data(launch_data)
            enriched_launches.append(enriched_data)
        
        # Process the enriched data into entities
        companies = []
        for launch_data in enriched_launches:
            company = self._process_launch(launch_data)
            if company:
                companies.append(company)
        
        return companies
    
    def ingest(self, days_lookback: int = DEFAULT_DAYS_LOOKBACK, **kwargs) -> Dict[str, Any]:
        """
        Run the ingestion process to fetch YC company launches.
        
        Args:
            days_lookback: Number of days to look back for launches
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with ingestion results
        """
        logger.info(f"Starting YC launch ingestion, looking back {days_lookback} days")
        current_sync_date = datetime.now()
        
        # Fetch and process launches
        companies = self._fetch_and_process_launches(days_lookback)
        
        if not companies:
            logger.warning("No YC launches found")
            return {
                "status": "completed",
                "entities_created": 0,
                "relationships_created": 0,
                "message": "No launches found"
            }
        
        # Store processed companies
        entities_created = 0
        relationships_created = 0
        
        for company in companies:
            try:
                # Check if entity already exists
                existing_entity = get_entity_by_source_id(
                    self.db, 
                    source_type=SourceType.YC_LAUNCH,
                    source_id=company.source_id
                )
                
                # If it exists, update it; otherwise, create it
                if existing_entity:
                    # Update entity with new data
                    existing_entity.name = company.name
                    existing_entity.properties.update(company.properties)
                    # Update specific fields
                    existing_entity.properties["launch_score"] = company.launch_score
                    # Save changes
                    self.db.commit()
                    logger.info(f"Updated YC company: {company.name}")
                else:
                    # Create new entity
                    insert_entity(self.db, company)
                    entities_created += 1
                    logger.info(f"Created YC company: {company.name}")
                
                # TODO: Create relationships with founders if data is available
                
            except Exception as e:
                logger.error(f"Error processing YC company {company.name}: {e}")
        
        # Save the current sync date for incremental sync next time
        self._save_last_sync_date(current_sync_date)
        
        return {
            "status": "completed",
            "entities_created": entities_created,
            "relationships_created": relationships_created,
            "message": f"Successfully ingested {entities_created} YC company launches"
        }