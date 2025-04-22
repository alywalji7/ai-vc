"""
Utility functions for the Graph Ingest Service.

This module contains various utility functions used by the Graph Ingest Service,
including entity deduplication using fuzzy matching.
"""

import json
import logging
from typing import Dict, List, Any, Optional

from sqlalchemy import text
from thefuzz import fuzz

# Set up logging
logger = logging.getLogger(__name__)

def fuzzy_match_entity(db_session, entity_type: str, name: str, threshold: int = 85) -> Optional[Dict[str, Any]]:
    """
    Find an entity using fuzzy string matching.
    
    Args:
        db_session: Database session
        entity_type: Type of entity to match
        name: Name to match
        threshold: Minimum score for a match (0-100)
        
    Returns:
        Matched entity or None if no match found
    """
    try:
        # Get all entities of the given type
        result = db_session.execute(
            text("SELECT id, name, properties FROM entities WHERE type = :type"),
            {"type": entity_type}
        )
        
        candidates = []
        for row in result:
            entity_id, entity_name, properties_json = row
            properties = json.loads(properties_json)
            
            # Get match score using fuzzy token sort ratio
            score = fuzz.token_sort_ratio(name.lower(), entity_name.lower())
            
            if score >= threshold:
                candidates.append({
                    "id": entity_id,
                    "name": entity_name,
                    "properties": properties,
                    "score": score
                })
        
        # Sort by score descending and return the best match
        if candidates:
            candidates.sort(key=lambda x: x["score"], reverse=True)
            logger.info(f"Fuzzy matched '{name}' to '{candidates[0]['name']}' with score {candidates[0]['score']}")
            return candidates[0]
        
        return None
        
    except Exception as e:
        logger.error(f"Error in fuzzy matching: {str(e)}")
        return None

def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing trailing slashes, protocol, etc.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL
    """
    # Remove protocol
    if '://' in url:
        url = url.split('://', 1)[1]
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    # Remove 'www.' prefix
    if url.startswith('www.'):
        url = url[4:]
    
    return url.lower()

def extract_domain_from_url(url: str) -> str:
    """
    Extract domain from a URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name
    """
    normalized = normalize_url(url)
    
    # Extract domain (everything before the first slash)
    if '/' in normalized:
        domain = normalized.split('/', 1)[0]
    else:
        domain = normalized
    
    return domain

def parse_csv_to_dict(csv_content: str) -> List[Dict[str, str]]:
    """
    Parse CSV content into a list of dictionaries.
    
    Args:
        csv_content: CSV content as a string
        
    Returns:
        List of dictionaries representing CSV rows
    """
    import csv
    from io import StringIO
    
    result = []
    reader = csv.DictReader(StringIO(csv_content))
    
    for row in reader:
        result.append(row)
    
    return result

def merge_properties(existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two property dictionaries, with newer values taking precedence.
    
    Args:
        existing: Existing properties
        new: New properties
        
    Returns:
        Merged properties
    """
    result = {**existing}
    
    for key, value in new.items():
        # Don't overwrite with empty values
        if value is not None and value != "":
            result[key] = value
    
    return result