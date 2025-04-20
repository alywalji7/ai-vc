#!/usr/bin/env python3
"""
Main entry point for the Value Add Agents system.

This script starts all three agents:
1. RecruitBot - AI-powered recruiting assistant
2. GrowthBot - AI-powered growth strategist
3. IntroBot - AI-powered networking assistant

Each agent subscribes to its respective Kafka topic and processes messages asynchronously.
"""

import asyncio
import logging
import argparse
import sys
from typing import List, Optional

from config import AGENT_CONFIG
from recruit_bot.agent import RecruitBot
from growth_bot.agent import GrowthBot
from intro_bot.agent import IntroBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("value_add_agents")


async def run_agents(agents: List[str]):
    """
    Run the specified agents.
    
    Args:
        agents: List of agent names to run
    """
    tasks = []
    
    for agent_name in agents:
        if agent_name not in AGENT_CONFIG:
            logger.warning(f"Unknown agent: {agent_name}")
            continue
        
        config = AGENT_CONFIG[agent_name]
        logger.info(f"Starting agent: {config['name']}")
        
        if agent_name == "recruit_bot":
            task = asyncio.create_task(
                RecruitBot.run(
                    topic=config["topic"],
                    group_id=config["group_id"],
                    name=config["name"],
                    description=config["description"]
                )
            )
        elif agent_name == "growth_bot":
            task = asyncio.create_task(
                GrowthBot.run(
                    topic=config["topic"],
                    group_id=config["group_id"],
                    name=config["name"],
                    description=config["description"]
                )
            )
        elif agent_name == "intro_bot":
            task = asyncio.create_task(
                IntroBot.run(
                    topic=config["topic"],
                    group_id=config["group_id"],
                    name=config["name"],
                    description=config["description"]
                )
            )
        else:
            continue
        
        tasks.append(task)
    
    if not tasks:
        logger.error("No valid agents specified")
        return
    
    # Wait for all agents to complete (they should run indefinitely)
    await asyncio.gather(*tasks)


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
        agents_to_run = list(AGENT_CONFIG.keys())
    
    logger.info(f"Starting Value Add Agents: {', '.join(agents_to_run)}")
    
    try:
        asyncio.run(run_agents(agents_to_run))
    except KeyboardInterrupt:
        logger.info("Shutting down agents...")
        sys.exit(0)


if __name__ == "__main__":
    main()