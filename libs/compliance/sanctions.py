"""
OFAC sanctions checking module.

This module provides functionality to check individuals and entities
against the latest Office of Foreign Assets Control (OFAC) sanctions lists.
It automatically downloads the newest SDN list from treasury.gov and stores it
in S3 for future reference and compliance audit purposes.
"""

import os
import csv
import io
import json
import logging
import hashlib
import datetime
import threading
import time
import requests
import tempfile
from typing import Dict, Any, List, Tuple, Optional, Set
import boto3
from Levenshtein import ratio

logger = logging.getLogger(__name__)

# Constants
OFAC_SDN_CSV_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"
OFAC_CONSOLIDATED_CSV_URL = "https://www.treasury.gov/ofac/downloads/consolidated/consolidated.csv"
S3_BUCKET_NAME = "compliance"
S3_OFAC_KEY = "ofac.csv"
S3_OFAC_METADATA_KEY = "ofac_metadata.json"
LOCAL_CACHE_DIR = os.path.join(tempfile.gettempdir(), "ofac_cache")
LOCAL_CACHE_FILE = os.path.join(LOCAL_CACHE_DIR, "ofac.csv")
LOCAL_CACHE_METADATA_FILE = os.path.join(LOCAL_CACHE_DIR, "ofac_metadata.json")
UPDATE_INTERVAL_HOURS = 24
SIMILARITY_THRESHOLD = 0.85  # Threshold for name matching

# In-memory cache for faster lookups
_sanctions_cache = {
    "data": [],
    "last_updated": None,
    "entity_count": 0
}

# Lock for thread safety
_cache_lock = threading.Lock()

def _ensure_cache_dir_exists():
    """Ensure the local cache directory exists."""
    if not os.path.exists(LOCAL_CACHE_DIR):
        os.makedirs(LOCAL_CACHE_DIR)

def _get_s3_client():
    """Get an initialized S3 client."""
    try:
        # For local development or when using AWS credentials 
        return boto3.client('s3')
    except Exception as e:
        logger.warning(f"Could not initialize S3 client: {str(e)}")
        return None

def _download_ofac_list(url: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Download the latest OFAC SDN list from Treasury.gov.
    
    Args:
        url: URL to download from
        
    Returns:
        Tuple containing:
        - List of dictionaries with sanctions data
        - Hash of the downloaded content
    """
    logger.info(f"Downloading OFAC sanctions list from {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content = response.content
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Parse CSV data
        sanctions_data = []
        csv_data = io.StringIO(content.decode('utf-8'))
        csv_reader = csv.DictReader(csv_data)
        
        for row in csv_reader:
            sanctions_data.append(dict(row))
        
        logger.info(f"Successfully downloaded OFAC list with {len(sanctions_data)} entries")
        return sanctions_data, content_hash
    
    except Exception as e:
        logger.error(f"Error downloading OFAC list: {str(e)}")
        return [], ""

def _save_to_s3(data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
    """
    Save the OFAC sanctions list to S3.
    
    Args:
        data: The sanctions data to save
        metadata: Metadata about the sanctions list
        
    Returns:
        Boolean indicating success
    """
    s3_client = _get_s3_client()
    if not s3_client:
        logger.warning("S3 client not available, skipping S3 upload")
        return False
    
    try:
        # Convert data to CSV
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        # Upload CSV to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_OFAC_KEY,
            Body=output.getvalue(),
            ContentType="text/csv"
        )
        
        # Upload metadata to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_OFAC_METADATA_KEY,
            Body=json.dumps(metadata),
            ContentType="application/json"
        )
        
        logger.info(f"Successfully saved OFAC data to S3://{S3_BUCKET_NAME}/{S3_OFAC_KEY}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving OFAC data to S3: {str(e)}")
        return False

def _save_to_local_cache(data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
    """
    Save the OFAC sanctions list to local cache.
    
    Args:
        data: The sanctions data to save
        metadata: Metadata about the sanctions list
        
    Returns:
        Boolean indicating success
    """
    _ensure_cache_dir_exists()
    
    try:
        # Save data to CSV
        with open(LOCAL_CACHE_FILE, 'w', newline='') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        # Save metadata to JSON
        with open(LOCAL_CACHE_METADATA_FILE, 'w') as f:
            json.dump(metadata, f)
        
        logger.info(f"Successfully saved OFAC data to local cache: {LOCAL_CACHE_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving OFAC data to local cache: {str(e)}")
        return False

def _load_from_s3() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Load the OFAC sanctions list from S3.
    
    Returns:
        Tuple containing:
        - List of dictionaries with sanctions data
        - Dictionary with metadata
    """
    s3_client = _get_s3_client()
    if not s3_client:
        logger.warning("S3 client not available, skipping S3 download")
        return [], {}
    
    try:
        # Check if the bucket exists, if not create it
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        except Exception:
            # If not exists, create it
            logger.info(f"Creating S3 bucket: {S3_BUCKET_NAME}")
            s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
    
        # Download CSV from S3
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_OFAC_KEY)
        csv_data = io.StringIO(response['Body'].read().decode('utf-8'))
        
        # Parse CSV
        reader = csv.DictReader(csv_data)
        data = list(reader)
        
        # Download metadata
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_OFAC_METADATA_KEY)
        metadata = json.loads(response['Body'].read().decode('utf-8'))
        
        logger.info(f"Successfully loaded OFAC data from S3 with {len(data)} entries")
        return data, metadata
        
    except Exception as e:
        logger.warning(f"Could not load OFAC data from S3: {str(e)}")
        return [], {}

def _load_from_local_cache() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Load the OFAC sanctions list from local cache.
    
    Returns:
        Tuple containing:
        - List of dictionaries with sanctions data
        - Dictionary with metadata
    """
    try:
        if not os.path.exists(LOCAL_CACHE_FILE):
            logger.warning(f"Local cache file not found: {LOCAL_CACHE_FILE}")
            return [], {}
            
        # Load data from CSV
        with open(LOCAL_CACHE_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        # Load metadata from JSON
        if os.path.exists(LOCAL_CACHE_METADATA_FILE):
            with open(LOCAL_CACHE_METADATA_FILE, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {
                "last_updated": datetime.datetime.now().isoformat(),
                "entity_count": len(data),
                "hash": ""
            }
        
        logger.info(f"Successfully loaded OFAC data from local cache with {len(data)} entries")
        return data, metadata
        
    except Exception as e:
        logger.warning(f"Could not load OFAC data from local cache: {str(e)}")
        return [], {}

def _update_sanctions_cache():
    """Update the sanctions cache with the latest data."""
    with _cache_lock:
        # Try to load from S3 first, then local cache as fallback
        data, metadata = _load_from_s3()
        if not data:
            data, metadata = _load_from_local_cache()
        
        # If we still don't have data, download from source
        if not data or _is_cache_expired(metadata.get("last_updated")):
            data, content_hash = _download_ofac_list(OFAC_SDN_CSV_URL)
            if data:
                metadata = {
                    "last_updated": datetime.datetime.now().isoformat(),
                    "entity_count": len(data),
                    "hash": content_hash,
                    "source_url": OFAC_SDN_CSV_URL
                }
                
                # Save to S3 and local cache
                _save_to_s3(data, metadata)
                _save_to_local_cache(data, metadata)
        
        # Update in-memory cache
        if data:
            _sanctions_cache["data"] = data
            _sanctions_cache["last_updated"] = metadata.get("last_updated")
            _sanctions_cache["entity_count"] = len(data)
            logger.info(f"Sanctions cache updated with {len(data)} entries")

def _is_cache_expired(last_updated_str: Optional[str]) -> bool:
    """
    Check if the cache is expired based on last updated timestamp.
    
    Args:
        last_updated_str: ISO format timestamp string
        
    Returns:
        Boolean indicating if cache is expired
    """
    if not last_updated_str:
        return True
        
    try:
        last_updated = datetime.datetime.fromisoformat(last_updated_str)
        now = datetime.datetime.now()
        diff = now - last_updated
        
        # Check if more than UPDATE_INTERVAL_HOURS have passed
        return diff.total_seconds() > (UPDATE_INTERVAL_HOURS * 3600)
    except Exception:
        return True

def _check_name_match(name: str, sanctions_data: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if a name matches any entry in the sanctions data.
    
    Args:
        name: Name to check
        sanctions_data: List of sanctions data entries
        
    Returns:
        Tuple containing:
        - Boolean indicating if there's a match
        - Dictionary with match details
    """
    best_match = None
    best_ratio = 0
    name_lower = name.lower()
    
    for entry in sanctions_data:
        # Get the name from the entry (different formats for different lists)
        entry_name = entry.get('NAME', entry.get('SDN_Name', entry.get('_name', ''))).lower()
        
        # Calculate similarity ratio
        similarity = ratio(name_lower, entry_name)
        
        if similarity > best_ratio:
            best_ratio = similarity
            best_match = entry
    
    # Check if best match exceeds threshold
    is_match = best_ratio >= SIMILARITY_THRESHOLD
    
    match_details = {
        "is_match": is_match,
        "match_score": best_ratio,
        "match_threshold": SIMILARITY_THRESHOLD,
        "matched_entry": best_match if is_match else None
    }
    
    return is_match, match_details

def get_latest_sanctions_list() -> List[Dict[str, Any]]:
    """
    Get information about the latest OFAC sanctions lists.
    
    Returns:
        List of dictionaries containing metadata about sanctions lists
    """
    # Ensure cache is populated
    if not _sanctions_cache["data"] or _is_cache_expired(_sanctions_cache["last_updated"]):
        _update_sanctions_cache()
    
    last_updated = _sanctions_cache["last_updated"]
    if not last_updated:
        last_updated = datetime.datetime.now().isoformat()
    
    return [
        {
            "name": "Specially Designated Nationals (SDN) List",
            "last_updated": last_updated,
            "entity_count": _sanctions_cache["entity_count"],
            "description": "List of individuals and companies owned or controlled by, or acting for or on behalf of, targeted countries.",
            "source_url": OFAC_SDN_CSV_URL
        }
    ]

def check_ofac_sanctions(
    name: str, 
    country: Optional[str] = None, 
    additional_data: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if a person or entity is on the OFAC sanctions list.
    
    This implementation downloads the official OFAC SDN list from treasury.gov
    and performs similarity matching against the provided name.
    
    Args:
        name: Name of person or entity to check
        country: Country of origin/residence (optional)
        additional_data: Additional identifying information
        
    Returns:
        Tuple containing:
        - Boolean indicating if the entity is on a sanctions list (True = sanctioned)
        - Dictionary with details about the check result
    """
    logger.info(f"Checking OFAC sanctions for {name} from {country or 'unknown country'}")
    
    # Ensure we have the latest sanctions data
    if not _sanctions_cache["data"] or _is_cache_expired(_sanctions_cache["last_updated"]):
        _update_sanctions_cache()
    
    # If we still don't have data, return a failure result
    if not _sanctions_cache["data"]:
        logger.error("No sanctions data available for checking")
        return False, {
            "is_sanctioned": False,
            "error": "No sanctions data available",
            "sanctions_lists_checked": [],
            "match_percentage": 0,
            "timestamp": datetime.datetime.now().isoformat(),
            "check_id": f"ofac-check-{int(time.time())}",
        }
    
    # Check name against sanctions data
    is_sanctioned, match_details = _check_name_match(name, _sanctions_cache["data"])
    
    # Create check ID using hash of name and timestamp
    timestamp = datetime.datetime.now().isoformat()
    check_id = f"ofac-check-{hashlib.md5(f'{name}-{timestamp}'.encode()).hexdigest()[:8]}"
    
    # Prepare result
    result = {
        "is_sanctioned": is_sanctioned,
        "sanctions_lists_checked": ["SDN"],
        "match_percentage": match_details["match_score"] * 100,
        "timestamp": timestamp,
        "check_id": check_id,
    }
    
    # If sanctioned, add match details
    if is_sanctioned:
        matched_entry = match_details["matched_entry"]
        logger.warning(f"SANCTIONS MATCH FOUND: {name} matched with {matched_entry.get('NAME', matched_entry.get('SDN_Name', ''))}")
        
        result["match_details"] = {
            "matched_name": matched_entry.get('NAME', matched_entry.get('SDN_Name', '')),
            "program": matched_entry.get('PROGRAM', matched_entry.get('Program', '')),
            "address": matched_entry.get('ADDRESS', matched_entry.get('Address', '')),
            "id": matched_entry.get('ID', ''),
        }
    else:
        logger.info(f"No sanctions match for {name}")
    
    return is_sanctioned, result

# Initialize the module by starting the cache update in the background
threading.Thread(target=_update_sanctions_cache, daemon=True).start()