"""
Models for scout API
"""

from typing import Optional
from pydantic import BaseModel, Field


class ScoutedCompanyRequest(BaseModel):
    """
    Model for scouted company data from Chrome extension
    """
    url: str = Field(..., description="URL of the scouted company's website")
    title: str = Field(..., description="Title or name of the company")
    notes: Optional[str] = Field(None, description="Scout's notes about the company")


class ScoutedCompanyResponse(BaseModel):
    """
    Response model for scouted company submission
    """
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    company_id: Optional[str] = Field(None, description="ID of the created company entity")
    referral_code: Optional[str] = Field(None, description="Scout's referral code")