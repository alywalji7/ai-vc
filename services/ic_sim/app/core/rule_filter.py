"""
Rule-based filtering for the Investment Committee Simulator.

This module implements the first stage of the IC process, which applies
hard rules to filter out investment opportunities based on sector,
round size, geography, etc.
"""

from typing import List, Dict, Any, Tuple
from app.models.schemas import CompanyData, RuleFilterResult

# Define investment criteria
ALLOWED_SECTORS = ["fintech", "healthtech", "enterprise", "ai", "deeptech"]
ALLOWED_REGIONS = ["north_america", "europe", "asia"]
MIN_RAISE_AMOUNT = {
    "seed": 1_000_000,
    "series_a": 5_000_000,
    "series_b": 10_000_000,
    "series_c": 20_000_000,
    "series_d_plus": 30_000_000,
    "pre_ipo": 50_000_000,
}
MAX_RAISE_AMOUNT = {
    "seed": 5_000_000,
    "series_a": 15_000_000,
    "series_b": 30_000_000,
    "series_c": 100_000_000,
    "series_d_plus": 200_000_000,
    "pre_ipo": 500_000_000,
}
MIN_VALUATION = {
    "seed": 5_000_000,
    "series_a": 20_000_000,
    "series_b": 50_000_000,
    "series_c": 100_000_000,
    "series_d_plus": 200_000_000,
    "pre_ipo": 500_000_000, 
}


def apply_rule_filter(company: CompanyData) -> RuleFilterResult:
    """
    Apply rule-based filters to determine if a company meets our investment criteria.
    
    Args:
        company: Company data to analyze
        
    Returns:
        Result of rule-based filtering with pass/fail and reasons
    """
    reasons = []
    passed = True
    
    # Check sector
    if company.sector not in ALLOWED_SECTORS:
        passed = False
        reasons.append(f"Sector '{company.sector}' is not in our investment focus areas: {', '.join(ALLOWED_SECTORS)}")
    
    # Check region
    if company.region not in ALLOWED_REGIONS:
        passed = False
        reasons.append(f"Region '{company.region}' is not in our target geographies: {', '.join(ALLOWED_REGIONS)}")
    
    # Check round size
    round_type = company.round
    if round_type in MIN_RAISE_AMOUNT:
        if company.raise_amount < MIN_RAISE_AMOUNT[round_type]:
            passed = False
            reasons.append(f"Raise amount (${company.raise_amount:,.0f}) is below our minimum for {round_type} rounds (${MIN_RAISE_AMOUNT[round_type]:,.0f})")
        
        if company.raise_amount > MAX_RAISE_AMOUNT[round_type]:
            passed = False
            reasons.append(f"Raise amount (${company.raise_amount:,.0f}) exceeds our maximum for {round_type} rounds (${MAX_RAISE_AMOUNT[round_type]:,.0f})")
    
    # Check valuation
    if round_type in MIN_VALUATION:
        if company.valuation < MIN_VALUATION[round_type]:
            passed = False
            reasons.append(f"Valuation (${company.valuation:,.0f}) is below our minimum for {round_type} rounds (${MIN_VALUATION[round_type]:,.0f})")
    
    # If passed and no reasons, add a success message
    if passed and not reasons:
        reasons.append("Company meets all initial rule-based criteria")
    
    return RuleFilterResult(passed=passed, reasons=reasons)