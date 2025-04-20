"""
Compliance middleware package for AI.VC investment platform.

This package provides essential compliance features:
- Investor accreditation verification
- OFAC sanctions checking
- Decision payload hashing and audit logging
- Admin override functionality
"""

from .accreditation import verify_investor_accreditation
from .sanctions import check_ofac_sanctions
from .audit import hash_decision_payload, log_decision
from .middleware import ComplianceMiddleware
from .admin import admin_router

__all__ = [
    'verify_investor_accreditation',
    'check_ofac_sanctions',
    'hash_decision_payload',
    'log_decision',
    'ComplianceMiddleware',
    'admin_router',
]