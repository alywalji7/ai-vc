"""
Financial due diligence module.

This module implements a financial due diligence check for evaluating
the financial health and unit economics of a company.
"""

import random
import logging
from typing import Dict, List, Any, Tuple, Optional

import httpx

from app.due_diligence.base import DDModule, Verdict, Finding

logger = logging.getLogger(__name__)


class FinancialDD(DDModule):
    """Financial due diligence module for unit economics analysis."""
    
    @property
    def name(self) -> str:
        """Get the name of the module."""
        return "financial"
    
    async def run(self, target_id: str) -> Verdict:
        """
        Run financial due diligence on a target.

        This module evaluates:
        - Unit economics
        - Revenue growth
        - Burn rate
        - Cash runway
        - Fundraising history

        Args:
            target_id: ID of the company to analyze

        Returns:
            Verdict with financial assessment
        """
        logger.info(f"Running financial due diligence for company {target_id}")
        
        try:
            # Get company financial data
            financial_data = await self._get_financial_data(target_id)
            
            # Analyze different aspects
            unit_economics_score, unit_economics_findings = self._analyze_unit_economics(financial_data)
            growth_score, growth_findings = self._analyze_revenue_growth(financial_data)
            burn_score, burn_findings = self._analyze_burn_rate(financial_data)
            runway_score, runway_findings = self._analyze_runway(financial_data)
            fundraising_score, fundraising_findings = self._analyze_fundraising(financial_data)
            
            # Combine findings
            findings = unit_economics_findings + growth_findings + burn_findings + runway_findings + fundraising_findings
            
            # Calculate overall score (weighted average)
            weights = {
                "unit_economics": 0.3,
                "growth": 0.2,
                "burn": 0.2,
                "runway": 0.2,
                "fundraising": 0.1
            }
            
            overall_score = (
                unit_economics_score * weights["unit_economics"] +
                growth_score * weights["growth"] +
                burn_score * weights["burn"] +
                runway_score * weights["runway"] +
                fundraising_score * weights["fundraising"]
            )
            
            # Determine status based on overall score
            status = self._get_status_from_score(overall_score)
            
            # Create summary
            summary = self._generate_summary(
                overall_score,
                unit_economics_score,
                growth_score,
                burn_score,
                runway_score,
                fundraising_score
            )
            
            # Return verdict
            return Verdict(
                score=overall_score,
                status=status,
                summary=summary,
                findings=findings,
                details={
                    "unit_economics_score": unit_economics_score,
                    "growth_score": growth_score,
                    "burn_score": burn_score,
                    "runway_score": runway_score,
                    "fundraising_score": fundraising_score,
                    "financial_data": financial_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error in financial due diligence: {str(e)}")
            return Verdict(
                score=0.0,
                status="error",
                summary=f"Failed to complete financial due diligence: {str(e)}",
                findings=[
                    Finding(
                        title="Due Diligence Error",
                        description=f"An error occurred during financial due diligence: {str(e)}",
                        severity="critical"
                    )
                ]
            )
    
    async def _get_financial_data(self, company_id: str) -> Dict[str, Any]:
        """
        Get financial data for a company.

        Args:
            company_id: ID of the company

        Returns:
            Dictionary with financial data
        """
        try:
            # Try to fetch real financial data from the graph ingest service
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8080/api/companies/{company_id}/financials",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return response.json()
            
            # If we can't get real data, use simulated data for the demo
            # In a real implementation, we'd return an error or fetch from another source
            return self._generate_financial_data(company_id)
            
        except Exception as e:
            logger.warning(f"Error fetching financial data, using generated data: {str(e)}")
            return self._generate_financial_data(company_id)
    
    def _generate_financial_data(self, company_id: str) -> Dict[str, Any]:
        """
        Generate simulated financial data.
        This is only for demonstration purposes.

        Args:
            company_id: ID of the company

        Returns:
            Dictionary with generated financial data
        """
        # Use a fixed seed based on company_id for reproducible results
        seed = sum(ord(c) for c in company_id)
        random.seed(seed)
        
        # Generate monthly revenue data for the last 12 months
        current_revenue = random.uniform(10000, 1000000)
        monthly_growth_rate = random.uniform(0.02, 0.15)  # 2% to 15% monthly growth
        
        monthly_revenue = []
        for i in range(12):
            rev = current_revenue / ((1 + monthly_growth_rate) ** (12 - i))
            monthly_revenue.append({
                "month": f"2024-{i+1:02d}",
                "revenue": round(rev, 2)
            })
        
        # Generate costs
        cogs_percentage = random.uniform(0.3, 0.7)  # 30% to 70% of revenue
        cac = random.uniform(100, 2000)  # Customer acquisition cost
        ltv = cac * random.uniform(1.5, 7)  # Lifetime value, 1.5x to 7x CAC
        
        burn_rate = current_revenue * random.uniform(0.3, 2.0)  # 30% to 200% of revenue
        cash_balance = burn_rate * random.uniform(3, 36)  # 3 to 36 months of burn
        
        # Generate fundraising rounds
        num_rounds = random.randint(1, 4)
        rounds = []
        
        total_raised = 0
        for i in range(num_rounds):
            round_type = ["Seed", "Series A", "Series B", "Series C"][min(i, 3)]
            amount = round(random.uniform(500000, 50000000), -3)  # Round to thousands
            total_raised += amount
            rounds.append({
                "date": f"202{4-i}-{random.randint(1, 12):02d}",
                "type": round_type,
                "amount": amount,
                "valuation": amount * random.uniform(3, 7)
            })
        
        return {
            "company_id": company_id,
            "monthly_revenue": monthly_revenue,
            "current_revenue": current_revenue,
            "cogs_percentage": cogs_percentage,
            "cac": cac,
            "ltv": ltv,
            "burn_rate": burn_rate,
            "cash_balance": cash_balance,
            "ltv_cac_ratio": ltv / cac,
            "gross_margin": 1 - cogs_percentage,
            "monthly_growth_rate": monthly_growth_rate,
            "funding_rounds": rounds,
            "total_raised": total_raised
        }
    
    def _analyze_unit_economics(self, data: Dict[str, Any]) -> Tuple[float, List[Finding]]:
        """
        Analyze unit economics.

        Args:
            data: Financial data

        Returns:
            Tuple of (score, findings)
        """
        findings = []
        
        # LTV/CAC ratio analysis
        ltv_cac_ratio = data.get("ltv_cac_ratio", 0)
        if ltv_cac_ratio < 1:
            findings.append(Finding(
                title="Critical LTV/CAC Ratio",
                description=f"The LTV/CAC ratio is {ltv_cac_ratio:.1f}, which is below 1. This means the company "
                           f"loses money on each customer.",
                severity="critical",
                recommendations=["Improve monetization to increase LTV", "Reduce customer acquisition costs"]
            ))
            ltv_cac_score = 0.0
        elif ltv_cac_ratio < 3:
            findings.append(Finding(
                title="Concerning LTV/CAC Ratio",
                description=f"The LTV/CAC ratio is {ltv_cac_ratio:.1f}, which is below the ideal target of 3+. "
                           f"This indicates potential challenges with the unit economics.",
                severity="warning",
                recommendations=["Work on improving retention to boost LTV", "Optimize marketing spend"]
            ))
            ltv_cac_score = 0.3 + (ltv_cac_ratio - 1) * 0.3
        else:
            findings.append(Finding(
                title="Strong LTV/CAC Ratio",
                description=f"The LTV/CAC ratio is {ltv_cac_ratio:.1f}, which is above the benchmark of 3. "
                           f"This indicates healthy unit economics.",
                severity="info"
            ))
            ltv_cac_score = min(0.9 + (ltv_cac_ratio - 3) * 0.02, 1.0)
        
        # Gross margin analysis
        gross_margin = data.get("gross_margin", 0)
        if gross_margin < 0.3:
            findings.append(Finding(
                title="Low Gross Margin",
                description=f"The gross margin is {gross_margin:.1%}, which is concerningly low. "
                           f"This may make it difficult to reach profitability.",
                severity="critical",
                recommendations=["Reduce COGS", "Increase prices", "Change product mix"]
            ))
            margin_score = gross_margin / 0.3
        elif gross_margin < 0.5:
            findings.append(Finding(
                title="Mediocre Gross Margin",
                description=f"The gross margin is {gross_margin:.1%}, which is below the ideal target of 50%+. "
                           f"There is room for improvement.",
                severity="warning",
                recommendations=["Look for ways to improve margins through pricing or cost reduction"]
            ))
            margin_score = 0.5 + (gross_margin - 0.3) * 1.5
        else:
            findings.append(Finding(
                title="Healthy Gross Margin",
                description=f"The gross margin is {gross_margin:.1%}, which is strong. "
                           f"This provides good headroom for marketing and operations.",
                severity="info"
            ))
            margin_score = min(0.8 + (gross_margin - 0.5) * 0.4, 1.0)
        
        # Calculate overall unit economics score
        score = (ltv_cac_score * 0.6) + (margin_score * 0.4)
        return score, findings
    
    def _analyze_revenue_growth(self, data: Dict[str, Any]) -> Tuple[float, List[Finding]]:
        """
        Analyze revenue growth.

        Args:
            data: Financial data

        Returns:
            Tuple of (score, findings)
        """
        findings = []
        
        # Calculate monthly growth rate
        monthly_growth_rate = data.get("monthly_growth_rate", 0)
        annual_growth_rate = (1 + monthly_growth_rate) ** 12 - 1
        
        if monthly_growth_rate < 0.03:  # Less than 3% monthly growth (42% annual)
            findings.append(Finding(
                title="Slow Growth",
                description=f"The company is growing at {monthly_growth_rate:.1%} monthly ({annual_growth_rate:.1%} annual), "
                           f"which is below venture expectations for early-stage startups.",
                severity="warning",
                recommendations=["Focus on growth initiatives", "Consider pivoting strategy"]
            ))
            growth_score = monthly_growth_rate * 20
        elif monthly_growth_rate < 0.07:  # 3% to 7% monthly (42% to 125% annual)
            findings.append(Finding(
                title="Moderate Growth",
                description=f"The company is growing at {monthly_growth_rate:.1%} monthly ({annual_growth_rate:.1%} annual), "
                           f"which is acceptable but could be improved.",
                severity="info",
                recommendations=["Continue focusing on growth", "Identify growth bottlenecks"]
            ))
            growth_score = 0.6 + (monthly_growth_rate - 0.03) * 10
        else:  # Over 7% monthly (125%+ annual)
            findings.append(Finding(
                title="Strong Growth",
                description=f"The company is growing at {monthly_growth_rate:.1%} monthly ({annual_growth_rate:.1%} annual), "
                           f"which demonstrates excellent product-market fit.",
                severity="info"
            ))
            growth_score = min(1.0, 0.9 + (monthly_growth_rate - 0.07) * 5)
        
        return growth_score, findings
    
    def _analyze_burn_rate(self, data: Dict[str, Any]) -> Tuple[float, List[Finding]]:
        """
        Analyze burn rate.

        Args:
            data: Financial data

        Returns:
            Tuple of (score, findings)
        """
        findings = []
        
        current_revenue = data.get("current_revenue", 0)
        burn_rate = data.get("burn_rate", 0)
        
        if current_revenue <= 0:
            burn_ratio = float('inf')
        else:
            burn_ratio = burn_rate / current_revenue
        
        if burn_ratio > 2.0:
            findings.append(Finding(
                title="Excessive Burn Rate",
                description=f"The burn rate is {burn_ratio:.1f}x revenue, which is unsustainably high. "
                           f"The company is spending significantly more than it earns.",
                severity="critical",
                recommendations=["Reduce operating expenses", "Focus on core business activities"]
            ))
            burn_score = max(0.0, 1.0 - (burn_ratio - 2.0) / 3.0)
        elif burn_ratio > 1.0:
            findings.append(Finding(
                title="High Burn Rate",
                description=f"The burn rate is {burn_ratio:.1f}x revenue, which means the company is burning "
                           f"more than it earns. This can be acceptable during growth phases but "
                           f"should be monitored closely.",
                severity="warning",
                recommendations=["Create a path to profitability", "Monitor burn efficiency"]
            ))
            burn_score = 0.7 - (burn_ratio - 1.0) * 0.3
        else:
            findings.append(Finding(
                title="Sustainable Burn Rate",
                description=f"The burn rate is {burn_ratio:.1f}x revenue, which is sustainable. "
                           f"The company is spending less than it earns.",
                severity="info"
            ))
            burn_score = min(1.0, 0.8 + (1.0 - burn_ratio) * 0.2)
        
        return burn_score, findings
    
    def _analyze_runway(self, data: Dict[str, Any]) -> Tuple[float, List[Finding]]:
        """
        Analyze cash runway.

        Args:
            data: Financial data

        Returns:
            Tuple of (score, findings)
        """
        findings = []
        
        burn_rate = data.get("burn_rate", 0)
        cash_balance = data.get("cash_balance", 0)
        
        if burn_rate <= 0:
            runway_months = float('inf')
        else:
            runway_months = cash_balance / burn_rate
        
        if runway_months < 6:
            findings.append(Finding(
                title="Critical Runway",
                description=f"The company has approximately {runway_months:.1f} months of runway remaining. "
                           f"Immediate fundraising or cost-cutting is necessary.",
                severity="critical",
                recommendations=["Initiate fundraising immediately", "Cut non-essential costs"]
            ))
            runway_score = max(0.0, runway_months / 6)
        elif runway_months < 12:
            findings.append(Finding(
                title="Limited Runway",
                description=f"The company has approximately {runway_months:.1f} months of runway remaining. "
                           f"Fundraising planning should be a priority.",
                severity="warning",
                recommendations=["Begin fundraising preparations", "Identify efficiency improvements"]
            ))
            runway_score = 0.5 + (runway_months - 6) / 12
        else:
            findings.append(Finding(
                title="Comfortable Runway",
                description=f"The company has approximately {runway_months:.1f} months of runway remaining, "
                           f"providing operational flexibility.",
                severity="info"
            ))
            runway_score = min(1.0, 0.8 + (runway_months - 12) / 60)
        
        return runway_score, findings
    
    def _analyze_fundraising(self, data: Dict[str, Any]) -> Tuple[float, List[Finding]]:
        """
        Analyze fundraising history.

        Args:
            data: Financial data

        Returns:
            Tuple of (score, findings)
        """
        findings = []
        
        funding_rounds = data.get("funding_rounds", [])
        total_raised = data.get("total_raised", 0)
        
        if not funding_rounds:
            findings.append(Finding(
                title="No Fundraising History",
                description="The company has no recorded fundraising rounds, which could indicate "
                           "bootstrapping or incomplete data.",
                severity="warning"
            ))
            fundraising_score = 0.5
        else:
            latest_round = funding_rounds[0]
            round_type = latest_round.get("type", "")
            round_amount = latest_round.get("amount", 0)
            
            if round_type == "Seed" and round_amount < 1000000:
                findings.append(Finding(
                    title="Small Seed Round",
                    description=f"The company raised a small seed round of ${round_amount/1000:.0f}K, "
                               f"which may be insufficient for significant growth.",
                    severity="warning"
                ))
                fundraising_score = 0.4 + (round_amount / 1000000) * 0.2
            elif round_type == "Series A" and round_amount < 5000000:
                findings.append(Finding(
                    title="Below-Average Series A",
                    description=f"The company raised ${round_amount/1000000:.1f}M in Series A, "
                               f"which is below the typical range.",
                    severity="warning"
                ))
                fundraising_score = 0.5 + (round_amount / 5000000) * 0.25
            elif round_type == "Series B" and round_amount < 10000000:
                findings.append(Finding(
                    title="Below-Average Series B",
                    description=f"The company raised ${round_amount/1000000:.1f}M in Series B, "
                               f"which is below the typical range.",
                    severity="warning"
                ))
                fundraising_score = 0.6 + (round_amount / 10000000) * 0.2
            else:
                findings.append(Finding(
                    title="Strong Fundraising",
                    description=f"The company successfully raised ${total_raised/1000000:.1f}M across "
                               f"{len(funding_rounds)} rounds, with the latest being a {round_type} round "
                               f"of ${round_amount/1000000:.1f}M.",
                    severity="info"
                ))
                fundraising_score = min(1.0, 0.8 + (0.05 * len(funding_rounds)))
        
        return fundraising_score, findings
    
    def _generate_summary(
        self,
        overall_score: float,
        unit_economics_score: float,
        growth_score: float,
        burn_score: float,
        runway_score: float,
        fundraising_score: float
    ) -> str:
        """
        Generate a summary based on financial scores.
        
        Args:
            overall_score: Overall financial score
            unit_economics_score: Unit economics score
            growth_score: Growth score
            burn_score: Burn rate score
            runway_score: Runway score
            fundraising_score: Fundraising score
            
        Returns:
            Summary text
        """
        if overall_score < 0.4:
            summary = "The financial health of the company is concerning. "
        elif overall_score < 0.7:
            summary = "The company shows mixed financial indicators. "
        else:
            summary = "The company demonstrates strong financial health. "
        
        # Add details about strongest and weakest areas
        scores = {
            "unit economics": unit_economics_score,
            "revenue growth": growth_score,
            "burn rate management": burn_score,
            "cash runway": runway_score,
            "fundraising history": fundraising_score
        }
        
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        summary += f"The strongest area is {strongest[0]} ({strongest[1]:.1%}), "
        summary += f"while the weakest is {weakest[0]} ({weakest[1]:.1%}). "
        
        if weakest[1] < 0.3:
            summary += f"Immediate attention is required to address issues with {weakest[0]}."
        elif weakest[1] < 0.6:
            summary += f"The company should focus on improving {weakest[0]}."
        else:
            summary += "All financial indicators are within acceptable ranges."
        
        return summary
    
    def _get_status_from_score(self, score: float) -> str:
        """
        Convert a score to a status string.
        
        Args:
            score: Numeric score (0.0 to 1.0)
            
        Returns:
            Status string ("pass", "warning", or "fail")
        """
        if score < 0.4:
            return "fail"
        elif score < 0.7:
            return "warning"
        else:
            return "pass"