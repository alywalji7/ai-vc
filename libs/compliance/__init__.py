"""
Compliance middleware package for AI.VC investment platform.

This package provides essential compliance features:
- Investor accreditation verification
- OFAC sanctions checking
- Decision payload hashing and audit logging
- Admin override functionality
"""

from .accreditation import verify_investor_accreditation, get_accreditation_requirements
from .sanctions import check_ofac_sanctions, get_latest_sanctions_list
from .audit import hash_decision_payload, log_decision, verify_decision_integrity
from .middleware import ComplianceMiddleware, log_compliance_event

__all__ = [
    "verify_investor_accreditation",
    "get_accreditation_requirements",
    "check_ofac_sanctions",
    "get_latest_sanctions_list",
    "hash_decision_payload",
    "log_decision",
    "verify_decision_integrity",
    "ComplianceMiddleware",
    "log_compliance_event"
]