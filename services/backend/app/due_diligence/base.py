"""
Due Diligence Base Module

This module defines the abstract base class for all due diligence modules.
"""

import abc
from typing import List, Dict, Any, Optional, Union, Tuple


class Finding:
    """
    Represents a single due diligence finding.
    
    Findings can be positive, negative, or neutral observations
    about a company.
    """
    
    def __init__(
        self,
        title: str,
        description: str,
        severity: str = "info",  # info, warning, critical
        evidence: Optional[Dict[str, Any]] = None,
        recommendations: Optional[List[str]] = None,
    ):
        self.title = title
        self.description = description
        self.severity = severity
        self.evidence = evidence or {}
        self.recommendations = recommendations or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the finding to a dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "evidence": self.evidence,
            "recommendations": self.recommendations,
        }


class Verdict:
    """
    Represents the overall verdict of a due diligence check.
    
    The verdict includes a score, status, and list of findings.
    """
    
    def __init__(
        self,
        score: float,  # 0.0 to 1.0
        status: str,  # "pass", "warning", "fail"
        summary: str,
        findings: List[Finding],
        details: Optional[Dict[str, Any]] = None,
    ):
        self.score = score
        self.status = status
        self.summary = summary
        self.findings = findings
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the verdict to a dictionary."""
        return {
            "score": self.score,
            "status": self.status,
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "details": self.details,
        }


class DDModule(abc.ABC):
    """
    Abstract base class for due diligence modules.
    
    Each module must implement the run method to perform
    due diligence checks and return a verdict.
    """
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Get the name of the module."""
        raise NotImplementedError
    
    @abc.abstractmethod
    async def run(self, target_id: str) -> Verdict:
        """
        Run due diligence on a target.
        
        Args:
            target_id: ID of the company or entity to analyze
            
        Returns:
            Verdict with due diligence results
        """
        raise NotImplementedError