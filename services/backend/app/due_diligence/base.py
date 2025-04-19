"""
Base classes for due diligence modules.

This module defines the abstract base class for all due diligence modules
and shared data structures for findings and verdicts.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class Finding:
    """
    A specific finding from a due diligence module.
    
    Findings represent individual observations or issues discovered during
    due diligence analysis.
    """
    
    def __init__(
        self,
        title: str,
        description: str,
        severity: str,
        evidence: Optional[Dict[str, Any]] = None,
        recommendations: Optional[List[str]] = None
    ):
        """
        Initialize a new finding.
        
        Args:
            title: Short title describing the finding
            description: Detailed description of the finding
            severity: Severity level (critical, warning, info)
            evidence: Supporting evidence for the finding
            recommendations: Suggested actions to address the finding
        """
        self.title = title
        self.description = description
        self.severity = severity.lower()  # normalize to lowercase
        self.evidence = evidence or {}
        self.recommendations = recommendations or []
        
        # Validate severity
        if self.severity not in ["critical", "warning", "info"]:
            raise ValueError(
                f"Invalid severity '{severity}'. Must be one of: critical, warning, info"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the finding to a dictionary representation.
        
        Returns:
            Dictionary representation of the finding
        """
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "evidence": self.evidence,
            "recommendations": self.recommendations
        }


class DDModule(ABC):
    """
    Abstract base class for all due diligence modules.
    
    Due diligence modules implement specific types of analysis, such as
    financial due diligence, technical due diligence, etc.
    """
    
    def __init__(self, name: str):
        """
        Initialize a new due diligence module.
        
        Args:
            name: Name of the module
        """
        self.name = name
    
    @abstractmethod
    async def run(self, company_id: str) -> Dict[str, Any]:
        """
        Run due diligence for the specified company.
        
        Args:
            company_id: ID of the company to analyze
            
        Returns:
            Dictionary containing the due diligence results
        """
        pass
    
    def format_result(
        self,
        score: float,
        status: str,
        summary: str,
        findings: List[Finding],
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format the due diligence results in a standardized way.
        
        Args:
            score: Overall score (0.0 to 1.0)
            status: Overall status (pass, warning, fail)
            summary: Summary of the findings
            findings: List of specific findings
            details: Additional details or raw data
            
        Returns:
            Dictionary with standardized result format
        """
        # Validate score
        if not 0.0 <= score <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        
        # Validate status
        status = status.lower()  # normalize to lowercase
        if status not in ["pass", "warning", "fail", "error"]:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: pass, warning, fail, error"
            )
        
        return {
            "score": score,
            "status": status,
            "summary": summary,
            "findings": [finding.to_dict() for finding in findings],
            "details": details or {}
        }