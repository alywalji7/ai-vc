"""
Database models for the compliance package.

This module defines the SQLAlchemy models used by the compliance package,
including the append-only audit log.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AuditLog(Base):
    """
    Append-only audit log for investment decisions.
    
    This table stores a record of all decisions with their SHA-256 hash
    to ensure data integrity and compliance with regulatory requirements.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_type = Column(String, index=True, nullable=False)  # Type of decision (e.g., investment, due_diligence)
    decision_payload = Column(JSONB, nullable=False)  # Complete decision data as JSON
    payload_hash = Column(String, nullable=False, index=True)  # SHA-256 hash of the decision payload
    user_id = Column(String, index=True, nullable=True)  # ID of user who made the decision
    company_id = Column(String, index=True, nullable=True)  # ID of company related to decision
    related_entity_id = Column(String, index=True, nullable=True)  # ID of any other entity related to decision
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    class Config:
        orm_mode = True


class AdminOverride(Base):
    """
    Record of administrative overrides used in the system.
    
    This table stores a record of all instances where an administrative
    override was used to bypass normal system checks.
    """
    __tablename__ = "admin_overrides"
    
    id = Column(Integer, primary_key=True, index=True)
    override_type = Column(String, nullable=False)  # Type of override (e.g., "compliance", "risk", "verification")
    description = Column(Text, nullable=True)  # Description of why the override was needed
    original_decision_id = Column(Integer, nullable=True)  # ID of original decision being overridden
    override_data = Column(JSONB, nullable=False)  # Data related to the override
    user_id = Column(String, index=True, nullable=False)  # ID of user who performed the override
    user_role = Column(String, nullable=False)  # Role of user who performed the override
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    class Config:
        orm_mode = True