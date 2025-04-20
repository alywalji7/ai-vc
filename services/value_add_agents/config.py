"""
Configuration settings for value-add agents.
"""

import os
from typing import Dict, Any

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP_ID_PREFIX = "value_add_agents"

# Topics
TOPIC_NEW_HIRE_REQ = "new_hire_req"
TOPIC_GROWTH_GOAL = "growth_goal"
TOPIC_INTRO_REQ = "intro_req"

# Output directories
GROWTH_PLANS_DIR = os.path.abspath("./growth_plans")
os.makedirs(GROWTH_PLANS_DIR, exist_ok=True)

# Email configuration (stub)
EMAIL_FROM = "ai.vc@example.com"
EMAIL_SIGNATURE = """
--
AI.VC Operating Partners Team
Helping portfolio companies grow faster
"""

# Agent-specific configuration
AGENT_CONFIG: Dict[str, Dict[str, Any]] = {
    "recruit_bot": {
        "topic": TOPIC_NEW_HIRE_REQ,
        "group_id": f"{KAFKA_GROUP_ID_PREFIX}.recruit_bot",
        "name": "RecruitBot",
        "description": "AI-powered recruiting assistant for portfolio companies",
    },
    "growth_bot": {
        "topic": TOPIC_GROWTH_GOAL,
        "group_id": f"{KAFKA_GROUP_ID_PREFIX}.growth_bot",
        "name": "GrowthBot",
        "description": "AI-powered growth strategist for portfolio companies",
    },
    "intro_bot": {
        "topic": TOPIC_INTRO_REQ,
        "group_id": f"{KAFKA_GROUP_ID_PREFIX}.intro_bot",
        "name": "IntroBot",
        "description": "AI-powered networking assistant for portfolio companies",
    },
}