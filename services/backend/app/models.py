from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

# Use the base from the db module
from app.db import Base

# For now we'll import these models directly in any file that needs them
# from libs.compliance.models import AuditLog, AdminOverride

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="items")


class DataRoom(Base):
    __tablename__ = "datarooms"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, index=True, unique=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    data_metadata = Column(JSON)  # Changed from JSONB to JSON for SQLite compatibility


class DueDiligenceResult(Base):
    __tablename__ = "due_diligence_results"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, index=True)
    module_name = Column(String, index=True)  # financial, tech, etc.
    verdict = Column(JSON)  # Changed from JSONB to JSON for SQLite compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    class Config:
        orm_mode = True