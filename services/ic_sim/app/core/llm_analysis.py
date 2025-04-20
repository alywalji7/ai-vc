"""
LLM-based Tree-of-Thought analysis for the Investment Committee Simulator.

This module implements the second stage of the IC process, which uses
an LLM to perform detailed analysis and generate a reasoned judgment
about an investment opportunity.
"""

import os
import json
from typing import List, Dict, Any, Tuple
import logging

from openai import OpenAI

from app.models.schemas import (
    CompanyData, ICResult, ICDecision, TOTStep
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=api_key)

# Define the system prompt for the LLM
SYSTEM_PROMPT = """
You are a sophisticated investment analyst working for a premier venture capital firm. 
Your task is to analyze investment opportunities using a Tree-of-Thought approach, considering multiple factors.

Analyze the company data thoroughly using the following structured thought process:
1. Market Analysis: Analyze market size, growth potential, and competitive landscape.
2. Business Model Evaluation: Evaluate the sustainability and scalability of the business model.
3. Team Assessment: Assess the strength, experience, and track record of the founding team.
4. Financial Analysis: Analyze revenue, growth rate, burn rate, and runway.
5. Valuation Analysis: Determine if the valuation is reasonable given the company's metrics.
6. Risk Assessment: Identify key risks (market, execution, financial, regulatory).
7. Return Potential: Estimate potential return on investment given the stage and metrics.

After considering all factors, provide one of these decisions:
- APPROVE: Recommend investment as the opportunity meets or exceeds our criteria.
- REJECT: Recommend against investment due to significant concerns or misalignment.
- REVISE: Suggest revisions to the terms before proceeding (e.g., lower valuation, smaller check).

Format your analysis as a JSON object with the following structure:
{
  "reasoning_chain": [
    {"thought": "Market Analysis", "consideration": "Detailed analysis of the market..."},
    {"thought": "Business Model Evaluation", "consideration": "Evaluation of the business model..."},
    ...all steps...
  ],
  "decision": "APPROVE|REJECT|REVISE",
  "confidence": 0.85,  // 0-1 scale
  "roi_expectation": 3.2,  // multiple of investment
  "risk_assessment": 0.6,  // 0-1 scale, higher = riskier
  "rationale": "Concise explanation of the final decision"
}
"""


async def perform_tot_analysis(company: CompanyData) -> ICResult:
    """
    Perform a Tree-of-Thought analysis using GPT-4o to evaluate an investment opportunity.
    
    Args:
        company: Company data to analyze
        
    Returns:
        Result of investment committee analysis
    """
    logger.info(f"Performing ToT analysis for company: {company.name} (ID: {company.id})")
    
    # Format company data for the prompt
    company_json = company.model_dump_json(indent=2)
    
    # Prepare the user prompt
    user_prompt = f"""
    Please analyze the following investment opportunity using a Tree-of-Thought approach.
    
    COMPANY DATA:
    {company_json}
    
    Provide your detailed analysis and final investment decision following the Tree-of-Thought process.
    """
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        # Extract the response content
        analysis_text = response.choices[0].message.content
        logger.info(f"Received analysis from LLM for company: {company.name}")
        
        # Parse the JSON response
        analysis = json.loads(analysis_text)
        
        # Convert the reasoning chain
        reasoning_chain = [
            TOTStep(thought=step["thought"], consideration=step["consideration"])
            for step in analysis["reasoning_chain"]
        ]
        
        # Create summary of analysis
        analysis_summary = "\n".join([
            f"**{step.thought}**: {step.consideration[:100]}..." 
            for step in reasoning_chain
        ])
        
        # Make sure decision is lowercase to match our enum values
        decision = analysis["decision"].lower()
        
        # Create and return the result
        return ICResult(
            company_id=company.id,
            company_name=company.name,
            decision=decision,
            confidence=analysis["confidence"],
            roi_expectation=analysis["roi_expectation"],
            risk_assessment=analysis["risk_assessment"],
            analysis_summary=analysis_summary,
            reasoning_chain=reasoning_chain,
            rationale=analysis["rationale"]
        )
        
    except Exception as e:
        logger.error(f"Error in ToT analysis for company {company.name}: {str(e)}")
        raise