#!/usr/bin/env python3
"""
Main entry point for the Value Add Agents system.

This script starts all three agents:
1. RecruitBot - AI-powered recruiting assistant
2. GrowthBot - AI-powered growth strategist
3. IntroBot - AI-powered networking assistant

Each agent subscribes to its respective Kafka topic and processes messages asynchronously.
"""

import os
import sys
import logging
import asyncio
import argparse
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("value_add_agents")

# Import agents
from recruit_bot.agent import RecruitBot
from growth_bot.agent import GrowthBot
from intro_bot.agent import IntroBot
from config import AGENT_CONFIG


async def run_agents(agents: List[str]):
    """
    Run the specified agents.
    
    Args:
        agents: List of agent names to run
    """
    tasks = []
    
    if "recruit_bot" in agents:
        config = AGENT_CONFIG["recruit_bot"]
        recruit_bot = RecruitBot(
            topic=config["topic"],
            group_id=config["group_id"],
            name=config["name"],
            description=config["description"]
        )
        tasks.append(recruit_bot.start())
        logger.info(f"Started {config['name']}")
    
    if "growth_bot" in agents:
        config = AGENT_CONFIG["growth_bot"]
        growth_bot = GrowthBot(
            topic=config["topic"],
            group_id=config["group_id"],
            name=config["name"],
            description=config["description"]
        )
        tasks.append(growth_bot.start())
        logger.info(f"Started {config['name']}")
    
    if "intro_bot" in agents:
        config = AGENT_CONFIG["intro_bot"]
        intro_bot = IntroBot(
            topic=config["topic"],
            group_id=config["group_id"],
            name=config["name"],
            description=config["description"]
        )
        tasks.append(intro_bot.start())
        logger.info(f"Started {config['name']}")
    
    # Wait for all agents to complete
    if tasks:
        await asyncio.gather(*tasks)
    else:
        logger.warning("No agents were started")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Run Value Add Agents")
    parser.add_argument(
        "--agents",
        nargs="+",
        choices=["recruit_bot", "growth_bot", "intro_bot", "all"],
        default=["all"],
        help="List of agents to run"
    )
    
    args = parser.parse_args()
    agents_to_run = args.agents
    
    # If "all" is specified, run all agents
    if "all" in agents_to_run:
        agents_to_run = ["recruit_bot", "growth_bot", "intro_bot"]
    
    logger.info(f"Starting Value Add Agents: {', '.join(agents_to_run)}")
    
    try:
        asyncio.run(run_agents(agents_to_run))
    except KeyboardInterrupt:
        logger.info("Stopping agents due to keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running agents: {str(e)}")
    
    logger.info("Value Add Agents system shutdown")


if __name__ == "__main__":
    main()