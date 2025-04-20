"""
GrowthBot implementation.
"""

import json
import os
from typing import Dict, Any, List
import logging
import asyncio
import datetime
import uuid
import random

from ..base_agent import BaseAgent
from ..config import EMAIL_SIGNATURE, GROWTH_PLANS_DIR

# Growth strategies by business type
GROWTH_STRATEGIES = {
    "saas": [
        "Freemium Model",
        "Product-Led Growth",
        "Content Marketing",
        "SEO Optimization",
        "Referral Program",
        "Email Marketing Campaigns",
        "Strategic Partnerships",
        "Feature Expansion",
        "Enterprise Sales Focus",
        "International Expansion"
    ],
    "marketplace": [
        "Supply-Side Incentives",
        "Demand Generation Campaigns",
        "Geographic Expansion",
        "Category Expansion",
        "Referral Program",
        "SEO Optimization",
        "Multi-Sided Loyalty Program",
        "Platform Integration",
        "User-Generated Content",
        "Community Building"
    ],
    "ecommerce": [
        "Conversion Rate Optimization",
        "Retargeting Campaigns",
        "Loyalty Program",
        "Product Line Expansion",
        "Influencer Partnerships",
        "Email Marketing Automation",
        "SEO & Content Strategy",
        "Social Media Advertising",
        "Subscription Model",
        "Mobile App Launch"
    ],
    "fintech": [
        "Strategic Partnerships",
        "User Reward Program",
        "Educational Content Marketing",
        "Affiliate Marketing",
        "API Integration Program",
        "Regulatory Expansion Strategy",
        "Product Feature Expansion",
        "Enterprise Solutions",
        "White-Label Solutions",
        "Vertical Integration"
    ]
}

# AB test variation types
AB_TEST_VARIATIONS = [
    "Copy variations",
    "Design changes",
    "Feature visibility",
    "Pricing display",
    "Call-to-action (CTA) buttons",
    "Form fields",
    "Page layout",
    "User flow",
    "Social proof elements",
    "Onboarding sequence"
]

# Metrics to measure
GROWTH_METRICS = {
    "acquisition": [
        "Cost Per Acquisition (CPA)",
        "Conversion Rate",
        "Traffic Sources",
        "Bounce Rate",
        "Click-Through Rate (CTR)",
        "Sign-Up Rate"
    ],
    "activation": [
        "Time to Value",
        "Onboarding Completion Rate",
        "Feature Adoption Rate",
        "First Value Moment",
        "User Setup Completeness"
    ],
    "retention": [
        "Customer Retention Rate",
        "Churn Rate",
        "Monthly/Daily Active Users (MAU/DAU)",
        "Retention Curve",
        "Net Revenue Retention",
        "User Session Frequency"
    ],
    "revenue": [
        "Average Revenue Per User (ARPU)",
        "Lifetime Value (LTV)",
        "Monthly Recurring Revenue (MRR)",
        "Revenue Growth Rate",
        "Expansion Revenue",
        "Revenue Churn"
    ],
    "referral": [
        "Net Promoter Score (NPS)",
        "Referral Rate",
        "Viral Coefficient",
        "Word-of-Mouth Coefficient",
        "Share Rate"
    ]
}

class GrowthBot(BaseAgent):
    """AI-powered growth strategist for portfolio companies."""
    
    async def process_message(self, message: Dict[str, Any]):
        """
        Process a growth goal message.
        
        Args:
            message: The growth goal message with strategy details
        """
        self.logger.info(f"Processing growth goal: {json.dumps(message, indent=2)}")
        
        try:
            # Extract growth details
            company_id = message.get("company_id", str(uuid.uuid4()))
            company_name = message.get("company_name", "")
            company_email = message.get("company_email", "")
            business_type = message.get("business_type", "saas").lower()
            growth_goal = message.get("growth_goal", "")
            current_metrics = message.get("current_metrics", {})
            target_metrics = message.get("target_metrics", {})
            timeframe = message.get("timeframe", "3 months")
            focus_area = message.get("focus_area", "acquisition")
            
            # Generate AB test plan
            ab_test_plan = await self._generate_ab_test_plan(
                company_id=company_id,
                company_name=company_name,
                business_type=business_type,
                growth_goal=growth_goal,
                focus_area=focus_area,
                current_metrics=current_metrics,
                target_metrics=target_metrics,
                timeframe=timeframe
            )
            
            # Generate growth strategy
            growth_strategy = await self._generate_growth_strategy(
                business_type=business_type,
                focus_area=focus_area,
                growth_goal=growth_goal,
                current_metrics=current_metrics,
                target_metrics=target_metrics,
                timeframe=timeframe
            )
            
            # Save AB test plan to JSON file
            file_name = f"{company_id}_ab_test_plan_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = os.path.join(GROWTH_PLANS_DIR, file_name)
            
            with open(file_path, 'w') as f:
                json.dump(ab_test_plan, f, indent=2)
            
            self.logger.info(f"AB test plan saved to {file_path}")
            
            # Send email to company
            subject = f"Growth Strategy & A/B Testing Plan for {company_name}"
            
            body = f"""Dear {company_name} Team,

Thank you for sharing your growth goals with us. Based on your target to {growth_goal} within {timeframe}, I've prepared a comprehensive growth strategy and A/B testing plan.

## Growth Strategy Overview
{growth_strategy}

## A/B Testing Plan
I've created a detailed A/B testing plan to help you achieve your growth goals. The full plan is attached to this email, but here's a summary:

Test Name: {ab_test_plan['test_name']}
Hypothesis: {ab_test_plan['hypothesis']}
Primary Metric: {ab_test_plan['primary_metric']}
Expected Improvement: {ab_test_plan['expected_improvement']}
Test Duration: {ab_test_plan['duration']}

The plan includes {len(ab_test_plan['variations'])} variations to test.

## Next Steps
1. Review the attached A/B testing plan
2. Schedule a call to discuss implementation details
3. Set up tracking for the identified metrics
4. Launch the first test within the next 7 days

I'm available to assist with implementing these strategies and tests, as well as analyzing the results.

{EMAIL_SIGNATURE}
"""
            
            await self.send_email(
                to=company_email,
                subject=subject,
                body=body
            )
            
            self.logger.info(f"Growth strategy sent to {company_email}")
            
        except Exception as e:
            self.logger.error(f"Error processing growth goal: {e}")
            raise
    
    async def _generate_ab_test_plan(self, **kwargs) -> Dict[str, Any]:
        """
        Generate an A/B test plan based on the provided parameters.
        
        Args:
            **kwargs: Growth and company parameters
            
        Returns:
            A/B test plan as a dictionary
        """
        company_id = kwargs.get("company_id", str(uuid.uuid4()))
        company_name = kwargs.get("company_name", "")
        business_type = kwargs.get("business_type", "saas")
        growth_goal = kwargs.get("growth_goal", "")
        focus_area = kwargs.get("focus_area", "acquisition")
        current_metrics = kwargs.get("current_metrics", {})
        target_metrics = kwargs.get("target_metrics", {})
        timeframe = kwargs.get("timeframe", "3 months")
        
        # Select relevant metrics based on focus area
        metrics = GROWTH_METRICS.get(focus_area, GROWTH_METRICS["acquisition"])
        primary_metric = random.choice(metrics)
        secondary_metrics = random.sample([m for m in metrics if m != primary_metric], min(2, len(metrics)-1))
        
        # Select relevant growth strategies
        strategies = GROWTH_STRATEGIES.get(business_type, GROWTH_STRATEGIES["saas"])
        strategy = random.choice(strategies)
        
        # Select AB test variation type
        variation_type = random.choice(AB_TEST_VARIATIONS)
        
        # Calculate test duration based on timeframe
        # If timeframe is in months, convert to days for the test duration
        timeframe_value = int(''.join(filter(str.isdigit, timeframe))) if any(c.isdigit() for c in timeframe) else 1
        if "month" in timeframe.lower():
            total_days = timeframe_value * 30
            test_duration = min(14, total_days // 3)  # Test should be shorter than timeframe
        elif "week" in timeframe.lower():
            total_days = timeframe_value * 7
            test_duration = min(7, total_days // 2)
        else:  # Assume days
            total_days = timeframe_value
            test_duration = min(7, total_days // 2)
        
        # Generate expected improvement percentage (realistic)
        expected_improvement = random.uniform(5, 20)
        
        # Generate A/B test variations
        variations = [
            {
                "id": "A",
                "name": "Control",
                "description": "Current implementation without changes"
            }
        ]
        
        # Add 1-3 variations
        num_variations = random.randint(1, 3)
        for i in range(num_variations):
            variation_letter = chr(66 + i)  # B, C, D, ...
            variations.append({
                "id": variation_letter,
                "name": f"Variation {variation_letter}",
                "description": f"Test {variation_type.lower()} with {random.choice(['increased', 'simplified', 'redesigned', 'optimized'])} {random.choice(['layout', 'messaging', 'prominence', 'design'])}"
            })
        
        # Create hypothesis based on focus area
        hypothesis_templates = {
            "acquisition": f"By optimizing our {variation_type.lower()}, we can increase {primary_metric} by {expected_improvement:.1f}%",
            "activation": f"Improving the {variation_type.lower()} will lead to a {expected_improvement:.1f}% increase in {primary_metric}",
            "retention": f"Enhancing our {variation_type.lower()} will reduce churn and improve {primary_metric} by {expected_improvement:.1f}%",
            "revenue": f"Optimizing our {variation_type.lower()} will increase {primary_metric} by {expected_improvement:.1f}%",
            "referral": f"Improving our {variation_type.lower()} will boost {primary_metric} by {expected_improvement:.1f}%"
        }
        
        hypothesis = hypothesis_templates.get(focus_area, hypothesis_templates["acquisition"])
        
        # Generate test plan
        test_plan = {
            "company_id": company_id,
            "company_name": company_name,
            "test_id": str(uuid.uuid4()),
            "test_name": f"{strategy} {variation_type} Optimization",
            "created_at": datetime.datetime.now().isoformat(),
            "business_type": business_type,
            "focus_area": focus_area,
            "growth_goal": growth_goal,
            "hypothesis": hypothesis,
            "primary_metric": primary_metric,
            "secondary_metrics": secondary_metrics,
            "expected_improvement": f"{expected_improvement:.1f}%",
            "duration": f"{test_duration} days",
            "traffic_allocation": {
                "control": 50,
                "variations": 50
            },
            "variations": variations,
            "implementation_details": {
                "test_pages": ["Homepage", "Product Page", "Checkout Flow"],
                "user_segments": ["All Users", "New Visitors", "Returning Visitors"],
                "technical_requirements": [
                    "Implement tracking for all variations",
                    "Ensure proper A/B test bucketing",
                    "Set up analytics dashboard for monitoring"
                ]
            },
            "success_criteria": {
                "statistical_significance": "95% confidence level",
                "minimum_sample_size": "Calculated based on expected improvement",
                "decision_framework": "Winner determined by primary metric improvement with statistical significance"
            }
        }
        
        return test_plan
    
    async def _generate_growth_strategy(self, **kwargs) -> str:
        """
        Generate a growth strategy based on the provided parameters.
        
        Args:
            **kwargs: Growth and company parameters
            
        Returns:
            Growth strategy text
        """
        business_type = kwargs.get("business_type", "saas")
        focus_area = kwargs.get("focus_area", "acquisition")
        growth_goal = kwargs.get("growth_goal", "")
        current_metrics = kwargs.get("current_metrics", {})
        target_metrics = kwargs.get("target_metrics", {})
        timeframe = kwargs.get("timeframe", "3 months")
        
        # Select relevant growth strategies
        all_strategies = GROWTH_STRATEGIES.get(business_type, GROWTH_STRATEGIES["saas"])
        strategies = random.sample(all_strategies, min(3, len(all_strategies)))
        
        # Create strategy descriptions
        strategy_descriptions = []
        for strategy in strategies:
            description = f"### {strategy}\n"
            
            if strategy == "Freemium Model":
                description += "Implement a limited free tier to attract users and convert them to paid plans."
            elif strategy == "Product-Led Growth":
                description += "Focus on product experience as the primary driver of user acquisition and expansion."
            elif strategy == "Content Marketing":
                description += "Create valuable content that addresses customer pain points and establishes thought leadership."
            elif strategy == "SEO Optimization":
                description += "Optimize website and content for search engines to drive organic traffic."
            elif strategy == "Referral Program":
                description += "Incentivize existing customers to refer new users through rewards and recognition."
            elif strategy == "Email Marketing Campaigns":
                description += "Develop targeted email sequences to nurture leads and activate existing users."
            elif strategy == "Strategic Partnerships":
                description += "Form alliances with complementary businesses to expand reach and add value."
            elif strategy == "Feature Expansion":
                description += "Add new capabilities that address user needs and create upsell opportunities."
            elif strategy == "Enterprise Sales Focus":
                description += "Target larger customers with dedicated sales resources and customized solutions."
            elif strategy == "International Expansion":
                description += "Enter new geographic markets with localized offerings and marketing."
            elif strategy == "Conversion Rate Optimization":
                description += "Systematically improve website and app flows to increase conversion rates."
            elif strategy == "Mobile App Launch":
                description += "Expand to mobile platforms to increase engagement and retention."
            else:
                description += "Implement this strategy to align with your specific growth goals and market position."
            
            strategy_descriptions.append(description)
        
        # Format the growth strategy
        growth_strategy = f"""
Based on your goal to {growth_goal} within {timeframe}, and focusing on {focus_area}, I recommend the following growth strategies:

{'\n\n'.join(strategy_descriptions)}

## Implementation Timeline
Phase 1 (Weeks 1-2): Research and Planning
Phase 2 (Weeks 3-4): Implementation of Priority Initiatives
Phase 3 (Weeks 5-8): Optimization and Scaling
Phase 4 (Weeks 9-12): Measurement and Iteration

## Key Performance Indicators
We'll track the following metrics to measure success:
"""
        
        # Add relevant metrics based on focus area
        metrics = GROWTH_METRICS.get(focus_area, GROWTH_METRICS["acquisition"])
        for metric in metrics[:4]:  # Limit to 4 metrics
            growth_strategy += f"- {metric}\n"
        
        return growth_strategy