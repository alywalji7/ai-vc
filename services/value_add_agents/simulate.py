#!/usr/bin/env python3
"""
Simulator for Value Add Agents.

This script simulates Kafka messages to test the agents without a running Kafka instance.
It directly calls the agent's process_message method with sample data.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
import uuid
from datetime import datetime

from recruit_bot.agent import RecruitBot
from growth_bot.agent import GrowthBot
from intro_bot.agent import IntroBot
from config import AGENT_CONFIG, GROWTH_PLANS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simulator")

# Sample messages for testing
SAMPLE_MESSAGES = {
    "recruit_bot": {
        "company_name": "TechStartup Inc.",
        "company_email": "hr@techstartup.example.com",
        "role": "Full Stack Engineer",
        "role_type": "engineering",
        "level": "Senior",
        "requirements": {
            "experience": "5+",
            "technologies": "Python, React, TypeScript, PostgreSQL",
            "additional_skills": "Docker, Kubernetes, AWS"
        },
        "company_description": "A fast-growing startup building AI-powered analytics tools.",
        "location": "San Francisco, CA",
        "remote": True
    },
    "growth_bot": {
        "company_id": str(uuid.uuid4()),
        "company_name": "DataInsights AI",
        "company_email": "growth@datainsightsai.example.com",
        "business_type": "saas",
        "growth_goal": "increase MRR by 30%",
        "current_metrics": {
            "mrr": 100000,
            "customers": 50,
            "avg_deal_size": 2000,
            "cac": 1500,
            "churn_rate": 2
        },
        "target_metrics": {
            "mrr": 130000,
            "customers": 65,
            "churn_rate": 1.5
        },
        "timeframe": "3 months",
        "focus_area": "acquisition"
    },
    "intro_bot": {
        "company_name": "HealthTech Solutions",
        "company_email": "founders@healthtech.example.com",
        "company_description": "is developing AI-powered diagnostic tools for remote healthcare providers.",
        "industry": "healthcare",
        "introduction_type": "investor",
        "founder_name": "Dr. Sarah Chen",
        "founder_title": "CEO",
        "founder_background": "Medical Director at Regional Hospital",
        "specific_request": "Looking for investors with digital health experience for our Series A round",
        "recent_achievement": "FDA clearance for our first diagnostic algorithm",
        "challenge_area": "regulatory compliance",
        "specific_need": "navigating reimbursement models",
        "funding_round": "Series A",
        "traction_metric": "growth of 150% in pilot deployments",
        "time_period": "last quarter",
        "value_proposition": "reduce diagnostic errors by 35% while cutting costs",
        "pain_point_area": "remote diagnostics"
    }
}


async def simulate_agent(agent_name: str):
    """
    Simulate a message for the specified agent.
    
    Args:
        agent_name: Name of the agent to simulate
    """
    logger.info(f"Simulating {agent_name}")
    
    if agent_name not in SAMPLE_MESSAGES:
        logger.error(f"No sample message defined for {agent_name}")
        return
    
    message = SAMPLE_MESSAGES[agent_name]
    config = AGENT_CONFIG[agent_name]
    
    if agent_name == "recruit_bot":
        agent = RecruitBot(
            topic=config["topic"],
            group_id=config["group_id"],
            name=config["name"],
            description=config["description"]
        )
    elif agent_name == "growth_bot":
        agent = GrowthBot(
            topic=config["topic"],
            group_id=config["group_id"],
            name=config["name"],
            description=config["description"]
        )
    elif agent_name == "intro_bot":
        agent = IntroBot(
            topic=config["topic"],
            group_id=config["group_id"],
            name=config["name"],
            description=config["description"]
        )
    else:
        logger.error(f"Unknown agent: {agent_name}")
        return
    
    logger.info(f"Processing sample message for {agent_name}")
    logger.debug(f"Message: {json.dumps(message, indent=2)}")
    
    await agent.process_message(message)
    
    if agent_name == "growth_bot":
        # Check if the growth plan was generated
        logger.info(f"Checking for growth plan in {GROWTH_PLANS_DIR}")
        files = os.listdir(GROWTH_PLANS_DIR)
        
        if files:
            latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(GROWTH_PLANS_DIR, f)))
            file_path = os.path.join(GROWTH_PLANS_DIR, latest_file)
            
            logger.info(f"Found growth plan: {file_path}")
            
            with open(file_path, 'r') as f:
                plan = json.load(f)
                
            logger.info(f"Growth plan summary:")
            logger.info(f"  Test Name: {plan.get('test_name', 'N/A')}")
            logger.info(f"  Hypothesis: {plan.get('hypothesis', 'N/A')}")
            logger.info(f"  Primary Metric: {plan.get('primary_metric', 'N/A')}")
            logger.info(f"  Expected Improvement: {plan.get('expected_improvement', 'N/A')}")
            logger.info(f"  Duration: {plan.get('duration', 'N/A')}")
            logger.info(f"  Variations: {len(plan.get('variations', []))}")
        else:
            logger.warning("No growth plan files found")
    
    logger.info(f"Simulation of {agent_name} completed")


async def run_simulations(agents: list):
    """
    Run simulations for the specified agents.
    
    Args:
        agents: List of agent names to simulate
    """
    for agent_name in agents:
        await simulate_agent(agent_name)


def main():
    """Main entry point for the simulator."""
    parser = argparse.ArgumentParser(description="Simulate Value Add Agents")
    parser.add_argument(
        "--agents",
        nargs="+",
        choices=["recruit_bot", "growth_bot", "intro_bot", "all"],
        default=["all"],
        help="List of agents to simulate"
    )
    
    args = parser.parse_args()
    agents_to_simulate = args.agents
    
    # If "all" is specified, simulate all agents
    if "all" in agents_to_simulate:
        agents_to_simulate = ["recruit_bot", "growth_bot", "intro_bot"]
    
    logger.info(f"Starting Value Add Agents simulator: {', '.join(agents_to_simulate)}")
    
    asyncio.run(run_simulations(agents_to_simulate))
    
    logger.info("Simulations completed")


if __name__ == "__main__":
    main()