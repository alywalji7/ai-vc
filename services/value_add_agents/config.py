"""
Configuration for Value-Add Agents.
"""
import os
from pathlib import Path

# Define the path to growth plans
GROWTH_PLANS_DIR = os.environ.get('GROWTH_PLANS_DIR', str(Path(__file__).parent.parent.parent / 'growth_plans'))

# Kafka connection settings
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

# Agent configuration
AGENT_CONFIG = {
    "recruit_bot": {
        "topic": "new_hire_req",
        "group_id": "recruit_bot_group",
        "name": "RecruitBot",
        "description": "AI-powered recruiting assistant for portfolio companies"
    },
    "growth_bot": {
        "topic": "growth_goal",
        "group_id": "growth_bot_group",
        "name": "GrowthBot",
        "description": "AI-powered growth strategist for portfolio companies"
    },
    "intro_bot": {
        "topic": "intro_req",
        "group_id": "intro_bot_group",
        "name": "IntroBot",
        "description": "AI-powered networking assistant for portfolio companies"
    }
}

# Email configuration
EMAIL_CONFIG = {
    "default_from": "ai-agents@ai.vc",
    "reply_to": "support@ai.vc",
    "subject_prefix": "[AI.VC] "
}