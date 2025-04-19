"""
Financial due diligence module.

This module analyzes the financial health of a company, including:
- Unit economics
- Burn rate and runway
- Revenue growth and projections
- Customer acquisition costs
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple

import httpx

from .base import DDModule, Finding


class FinancialDD(DDModule):
    """
    Financial due diligence module for evaluating a company's financial health.
    """
    
    def __init__(self):
        """Initialize the financial due diligence module."""
        super().__init__("financial")
    
    async def run(self, company_id: str) -> Dict[str, Any]:
        """
        Run financial due diligence for the specified company.
        
        Args:
            company_id: ID of the company to analyze
            
        Returns:
            Dictionary containing the financial due diligence results
        """
        try:
            # Get company financial data from data room
            financial_data = await self._get_company_financial_data(company_id)
            if not financial_data:
                return {
                    "error": f"No financial data found for company {company_id}"
                }
            
            # Analyze unit economics
            unit_economics_findings = self._analyze_unit_economics(financial_data)
            
            # Analyze burn rate and runway
            burn_rate_findings = self._analyze_burn_rate(financial_data)
            
            # Analyze revenue growth
            revenue_findings = self._analyze_revenue_growth(financial_data)
            
            # Combine all findings
            all_findings = unit_economics_findings + burn_rate_findings + revenue_findings
            
            # Calculate overall score
            score = self._calculate_score(all_findings)
            
            # Determine overall status
            status = self._determine_status(score)
            
            # Generate summary
            summary = self._generate_summary(score, all_findings)
            
            # Return formatted results
            return self.format_result(
                score=score,
                status=status,
                summary=summary,
                findings=all_findings,
                details={"company_id": company_id, "financial_data": financial_data}
            )
        except Exception as e:
            return {
                "error": f"Financial due diligence failed: {str(e)}"
            }
    
    async def _get_company_financial_data(self, company_id: str) -> Dict[str, Any]:
        """
        Get financial data for the specified company from the data room.
        
        Args:
            company_id: ID of the company
            
        Returns:
            Dictionary containing the company's financial data
        """
        datarooms_dir = os.environ.get("DATAROOMS_DIR", "data/datarooms")
        
        # Try to load from file system first
        try:
            file_path = os.path.join(datarooms_dir, company_id, "company_data.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    return data.get("financials", {})
        except Exception as e:
            print(f"Error loading financial data from file system: {str(e)}")
        
        # Fall back to API if file system access fails
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8000/api/dataroom/{company_id}"
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("financials", {})
        except Exception as e:
            print(f"Error loading financial data from API: {str(e)}")
        
        return {}
    
    def _analyze_unit_economics(self, financial_data: Dict[str, Any]) -> List[Finding]:
        """
        Analyze unit economics metrics.
        
        Args:
            financial_data: Dictionary containing the company's financial data
            
        Returns:
            List of findings related to unit economics
        """
        findings = []
        
        # Extract relevant metrics
        cac = financial_data.get("cac", 0)  # Customer acquisition cost
        ltv = financial_data.get("ltv", 0)  # Lifetime value
        cogs = financial_data.get("cogs_percentage", 0)  # Cost of goods sold
        margin = financial_data.get("gross_margin", 0)  # Gross margin
        
        # Check LTV/CAC ratio
        if ltv > 0 and cac > 0:
            ltv_cac_ratio = ltv / cac
            if ltv_cac_ratio < 3:
                findings.append(Finding(
                    title="Low LTV/CAC Ratio",
                    description=f"The LTV/CAC ratio is {ltv_cac_ratio:.2f}, which is below the recommended minimum of 3.",
                    severity="warning" if ltv_cac_ratio >= 2 else "critical",
                    evidence={"ltv": ltv, "cac": cac, "ratio": ltv_cac_ratio},
                    recommendations=[
                        "Improve customer retention to increase LTV",
                        "Optimize marketing spend to reduce CAC",
                        "Consider pricing adjustments to improve unit economics"
                    ]
                ))
            else:
                findings.append(Finding(
                    title="Healthy LTV/CAC Ratio",
                    description=f"The LTV/CAC ratio is {ltv_cac_ratio:.2f}, which is above the recommended minimum of 3.",
                    severity="info",
                    evidence={"ltv": ltv, "cac": cac, "ratio": ltv_cac_ratio}
                ))
        
        # Check gross margin
        if margin is not None:
            if margin < 0.4:
                findings.append(Finding(
                    title="Low Gross Margin",
                    description=f"The gross margin is {margin:.0%}, which may not be sustainable for a SaaS or tech company.",
                    severity="warning" if margin >= 0.3 else "critical",
                    evidence={"gross_margin": margin},
                    recommendations=[
                        "Review pricing strategy",
                        "Look for ways to reduce COGS",
                        "Consider focusing on higher-margin products or customers"
                    ]
                ))
            else:
                findings.append(Finding(
                    title="Healthy Gross Margin",
                    description=f"The gross margin is {margin:.0%}, which is typical for a successful SaaS or tech company.",
                    severity="info",
                    evidence={"gross_margin": margin}
                ))
        
        return findings
    
    def _analyze_burn_rate(self, financial_data: Dict[str, Any]) -> List[Finding]:
        """
        Analyze burn rate and runway.
        
        Args:
            financial_data: Dictionary containing the company's financial data
            
        Returns:
            List of findings related to burn rate and runway
        """
        findings = []
        
        # Extract relevant metrics
        monthly_burn = financial_data.get("monthly_burn", 0)
        cash_on_hand = financial_data.get("cash_on_hand", 0)
        
        # Calculate runway
        if monthly_burn > 0 and cash_on_hand > 0:
            runway_months = cash_on_hand / monthly_burn
            
            if runway_months < 12:
                findings.append(Finding(
                    title="Short Runway",
                    description=f"The company has approximately {runway_months:.1f} months of runway based on current burn rate.",
                    severity="critical" if runway_months < 6 else "warning",
                    evidence={"cash_on_hand": cash_on_hand, "monthly_burn": monthly_burn, "runway_months": runway_months},
                    recommendations=[
                        "Reduce burn rate to extend runway",
                        "Accelerate fundraising timeline",
                        "Focus on revenue-generating activities"
                    ]
                ))
            else:
                findings.append(Finding(
                    title="Adequate Runway",
                    description=f"The company has approximately {runway_months:.1f} months of runway based on current burn rate.",
                    severity="info",
                    evidence={"cash_on_hand": cash_on_hand, "monthly_burn": monthly_burn, "runway_months": runway_months}
                ))
        
        return findings
    
    def _analyze_revenue_growth(self, financial_data: Dict[str, Any]) -> List[Finding]:
        """
        Analyze revenue growth and projections.
        
        Args:
            financial_data: Dictionary containing the company's financial data
            
        Returns:
            List of findings related to revenue growth
        """
        findings = []
        
        # Extract relevant metrics
        current_mrr = financial_data.get("current_mrr", 0)
        previous_mrr = financial_data.get("previous_mrr", 0)
        yoy_growth = financial_data.get("yoy_growth", 0)
        
        # Check MRR growth
        if current_mrr > 0 and previous_mrr > 0:
            mrr_growth = (current_mrr - previous_mrr) / previous_mrr
            
            if mrr_growth < 0.10:  # Less than 10% MRR growth
                findings.append(Finding(
                    title="Slow MRR Growth",
                    description=f"MRR growth is {mrr_growth:.1%}, which is below the benchmark for early-stage startups.",
                    severity="warning" if mrr_growth >= 0.05 else "critical",
                    evidence={"current_mrr": current_mrr, "previous_mrr": previous_mrr, "mrr_growth": mrr_growth},
                    recommendations=[
                        "Review sales and marketing strategies",
                        "Focus on customer expansion and reducing churn",
                        "Consider pivoting or refocusing product offering"
                    ]
                ))
            else:
                findings.append(Finding(
                    title="Strong MRR Growth",
                    description=f"MRR growth is {mrr_growth:.1%}, which is healthy for an early-stage startup.",
                    severity="info",
                    evidence={"current_mrr": current_mrr, "previous_mrr": previous_mrr, "mrr_growth": mrr_growth}
                ))
        
        # Check YoY growth
        if yoy_growth is not None:
            if yoy_growth < 0.5:  # Less than 50% YoY growth
                findings.append(Finding(
                    title="Below-Target Annual Growth",
                    description=f"Year-over-year growth is {yoy_growth:.1%}, which is below the typical target for venture-backed startups.",
                    severity="warning" if yoy_growth >= 0.2 else "critical",
                    evidence={"yoy_growth": yoy_growth},
                    recommendations=[
                        "Identify and address growth bottlenecks",
                        "Review competitive positioning",
                        "Consider new go-to-market strategies"
                    ]
                ))
            else:
                findings.append(Finding(
                    title="Strong Annual Growth",
                    description=f"Year-over-year growth is {yoy_growth:.1%}, which meets or exceeds typical targets for venture-backed startups.",
                    severity="info",
                    evidence={"yoy_growth": yoy_growth}
                ))
        
        return findings
    
    def _calculate_score(self, findings: List[Finding]) -> float:
        """
        Calculate an overall score based on findings.
        
        Args:
            findings: List of findings
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Count findings by severity
        critical = sum(1 for f in findings if f.severity == "critical")
        warning = sum(1 for f in findings if f.severity == "warning")
        info = sum(1 for f in findings if f.severity == "info")
        
        # Start with a base score
        base_score = 0.7
        
        # Adjust based on findings
        score = base_score - (critical * 0.2) - (warning * 0.1) + (info * 0.05)
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))
    
    def _determine_status(self, score: float) -> str:
        """
        Determine overall status based on score.
        
        Args:
            score: Score between 0.0 and 1.0
            
        Returns:
            Status (pass, warning, fail)
        """
        if score >= 0.7:
            return "pass"
        elif score >= 0.4:
            return "warning"
        else:
            return "fail"
    
    def _generate_summary(self, score: float, findings: List[Finding]) -> str:
        """
        Generate a summary based on score and findings.
        
        Args:
            score: Score between 0.0 and 1.0
            findings: List of findings
            
        Returns:
            Summary of the financial due diligence
        """
        critical_count = sum(1 for f in findings if f.severity == "critical")
        warning_count = sum(1 for f in findings if f.severity == "warning")
        
        if score >= 0.7:
            return f"The company demonstrates strong financial health with {critical_count} critical and {warning_count} minor issues identified. Overall, the financial metrics indicate a sustainable business model."
        elif score >= 0.4:
            return f"The company shows concerning financial metrics with {critical_count} critical and {warning_count} minor issues identified. These issues should be addressed before proceeding with investment."
        else:
            return f"The company exhibits poor financial health with {critical_count} critical and {warning_count} minor issues identified. The current financial model does not appear to be sustainable without significant changes."