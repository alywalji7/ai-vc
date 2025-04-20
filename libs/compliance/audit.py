"""
Audit logging module for investment decisions.

This module provides functions for hashing decision payloads with SHA-256
and storing them in an append-only audit log table.
"""

import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.sql import func
from sqlalchemy.orm import Session

# Import model later to avoid circular imports
# The model will be imported when needed in the functions

logger = logging.getLogger(__name__)

def hash_decision_payload(payload: Dict[str, Any]) -> str:
    """
    Create a SHA-256 hash of a decision payload for integrity validation.
    
    Args:
        payload: Dictionary containing the decision data
        
    Returns:
        SHA-256 hash of the payload as a hexadecimal string
    """
    # Ensure the payload is consistently serialized
    # Sort keys to ensure consistent ordering
    serialized = json.dumps(payload, sort_keys=True)
    
    # Create the SHA-256 hash
    hash_obj = hashlib.sha256(serialized.encode('utf-8'))
    return hash_obj.hexdigest()


def log_decision(
    db: Session, 
    decision_type: str,
    decision_payload: Dict[str, Any],
    user_id: Optional[str] = None,
    company_id: Optional[str] = None,
    related_entity_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log a decision to the append-only audit log.
    
    Args:
        db: Database session
        decision_type: Type of decision (e.g., "investment", "due_diligence", "term_sheet")
        decision_payload: Complete decision data
        user_id: ID of the user who made the decision
        company_id: ID of the company related to the decision
        related_entity_id: ID of any other entity related to the decision
        
    Returns:
        Dictionary with the audit log entry details
    """
    # Import here to avoid circular imports
    from models import AuditLog
    
    # Hash the decision payload
    payload_hash = hash_decision_payload(decision_payload)
    
    # Create a new audit log entry
    log_entry = AuditLog(
        decision_type=decision_type,
        decision_payload=decision_payload,
        payload_hash=payload_hash,
        user_id=user_id,
        company_id=company_id,
        related_entity_id=related_entity_id,
        created_at=func.now()
    )
    
    # Add to database and commit
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    logger.info(f"Decision logged to audit trail: {log_entry.id} (hash: {payload_hash})")
    
    return {
        "audit_id": log_entry.id,
        "payload_hash": payload_hash,
        "timestamp": log_entry.created_at,
        "decision_type": decision_type
    }


def verify_decision_integrity(
    db: Session, 
    audit_id: int
) -> Dict[str, Any]:
    """
    Verify the integrity of a logged decision by recalculating its hash.
    
    Args:
        db: Database session
        audit_id: ID of the audit log entry to verify
        
    Returns:
        Dictionary with verification result
    """
    # Import here to avoid circular imports
    from models import AuditLog
    
    # Get the audit log entry
    log_entry = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    
    if not log_entry:
        return {
            "verified": False,
            "error": "Audit log entry not found"
        }
    
    # Recalculate the hash
    recalculated_hash = hash_decision_payload(log_entry.decision_payload)
    
    # Compare with stored hash
    is_verified = recalculated_hash == log_entry.payload_hash
    
    if not is_verified:
        logger.warning(f"Integrity verification failed for audit log {audit_id}: "
                      f"stored hash {log_entry.payload_hash} != "
                      f"recalculated hash {recalculated_hash}")
    
    return {
        "verified": is_verified,
        "audit_id": audit_id,
        "stored_hash": log_entry.payload_hash,
        "recalculated_hash": recalculated_hash,
        "decision_type": log_entry.decision_type,
        "timestamp": log_entry.created_at
    }