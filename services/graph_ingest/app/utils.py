"""
Utilities module for the Graph Ingest Service.

This module contains utility functions for the Graph Ingest Service.
"""

import re
import logging
import urllib.parse
from typing import Dict, Any, Optional, List, Tuple

from sqlalchemy import text
from thefuzz import fuzz, process

# Set up logging
logger = logging.getLogger(__name__)

def fuzzy_match_entity(db_session, entity_type: str, name: str, min_score: int = 80) -> Optional[Dict[str, Any]]:
    """
    Find an entity by fuzzy matching its name.
    
    Args:
        db_session: Database session
        entity_type: Type of entity to search for
        name: Name to match
        min_score: Minimum score for a match (0-100)
        
    Returns:
        Dictionary with entity ID and match score if found, None otherwise
    """
    try:
        # Get all entities of the given type
        result = db_session.execute(
            text("SELECT id, name FROM entities WHERE type = :type"),
            {"type": entity_type}
        )
        
        entities = [(row[0], row[1]) for row in result.fetchall()]
        
        if not entities:
            return None
        
        # Prepare entity names for fuzzy matching
        entity_names = [entity[1] for entity in entities]
        
        # Perform fuzzy matching
        match_name, score, match_idx = process.extractOne(name, entity_names, scorer=fuzz.token_sort_ratio)
        
        if score >= min_score:
            entity_id = entities[match_idx][0]
            logger.info(f"Fuzzy matched '{name}' to '{match_name}' with score {score}")
            return {
                "id": entity_id,
                "name": match_name,
                "score": score
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error in fuzzy matching: {str(e)}")
        return None

def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing trailing slashes and protocol.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL
    """
    if not url:
        return ""
    
    # Add http:// if no protocol is present
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        parsed = urllib.parse.urlparse(url)
        
        # Normalize domain (remove www., lowercase)
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        
        # Normalize path (remove trailing slash)
        path = parsed.path
        if path.endswith('/'):
            path = path[:-1]
        
        # Return normalized URL without protocol
        return netloc + path
        
    except Exception as e:
        logger.error(f"Error normalizing URL {url}: {str(e)}")
        return url

def extract_domain_from_url(url: str) -> str:
    """
    Extract domain from a URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name
    """
    if not url:
        return ""
    
    # Add http:// if no protocol is present
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        parsed = urllib.parse.urlparse(url)
        
        # Extract domain
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        
        return netloc
        
    except Exception as e:
        logger.error(f"Error extracting domain from URL {url}: {str(e)}")
        return url

def normalize_company_name(name: str) -> str:
    """
    Normalize a company name for comparison.
    
    Args:
        name: Company name
        
    Returns:
        Normalized company name
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove common company suffixes
    suffixes = [
        r"\s+inc\.?$", r"\s+incorporated$", r"\s+corp\.?$", r"\s+corporation$",
        r"\s+llc$", r"\s+ltd\.?$", r"\s+limited$", r"\s+gmbh$", r"\s+co\.?$",
        r"\s+company$", r"\s+technologies$", r"\s+technology$", r"\s+labs$",
        r"\s+group$", r"\s+holdings$", r"\s+systems$"
    ]
    
    for suffix in suffixes:
        name = re.sub(suffix, "", name)
    
    # Remove punctuation and extra spaces
    name = re.sub(r"[^\w\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    
    return name

def check_company_duplicate(db_session, company_name: str, min_score: int = 85) -> Optional[Dict[str, Any]]:
    """
    Check if a company with a similar name already exists.
    
    Args:
        db_session: Database session
        company_name: Company name to check
        min_score: Minimum score for a match (0-100)
        
    Returns:
        Dictionary with entity ID and match score if found, None otherwise
    """
    normalized_name = normalize_company_name(company_name)
    return fuzzy_match_entity(db_session, "company", normalized_name, min_score)