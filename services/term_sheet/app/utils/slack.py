"""
Slack integration utilities for the Term Sheet Generator & Negotiator Bot.

This module provides functions for sending notifications to Slack channels
when negotiation counter-offers exceed predefined thresholds.
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

# Get Slack token from environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")


def get_slack_client() -> Optional[WebClient]:
    """
    Get a Slack WebClient instance if credentials are available.
    
    Returns:
        WebClient instance or None if credentials are not available
    """
    if not SLACK_BOT_TOKEN:
        logger.warning("SLACK_BOT_TOKEN not set. Slack integration is disabled.")
        return None
        
    return WebClient(token=SLACK_BOT_TOKEN)


def send_escalation_notification(
    counter_offer: Dict[str, Any],
    negotiation_id: str,
    company_name: str,
    investor_name: str,
) -> bool:
    """
    Send an escalation notification to the human override Slack channel.
    
    Args:
        counter_offer: Counter offer details
        negotiation_id: ID of the negotiation session
        company_name: Name of the company
        investor_name: Name of the investor
        
    Returns:
        True if notification was sent successfully, False otherwise
    """
    client = get_slack_client()
    if not client or not SLACK_CHANNEL_ID:
        # Log the notification to a file as fallback
        log_to_file(counter_offer, negotiation_id, company_name, investor_name)
        return False
    
    try:
        # Create a rich message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 Term-Sheet Negotiation Escalation",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Negotiation ID:* {negotiation_id}\n*Company:* {company_name}\n*Investor:* {investor_name}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Term:* {counter_offer['term']}\n*Original Value:* {counter_offer['original_value']}\n*Proposed Value:* {counter_offer['proposed_value']}\n*Deviation:* {counter_offer['deviation_percentage']:.2f}%"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This counter-offer exceeds the normal negotiation parameters and requires human review."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Negotiation",
                            "emoji": True
                        },
                        "value": negotiation_id,
                        "action_id": "view_negotiation"
                    }
                ]
            }
        ]
        
        # Send the message
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            blocks=blocks,
            text=f"Term-Sheet Negotiation Escalation: {company_name} - {investor_name}"
        )
        
        logger.info(f"Escalation notification sent to Slack: {response['ts']}")
        return True
        
    except SlackApiError as e:
        logger.error(f"Error sending Slack notification: {str(e)}")
        # Log the notification to a file as fallback
        log_to_file(counter_offer, negotiation_id, company_name, investor_name)
        return False


def log_to_file(
    counter_offer: Dict[str, Any],
    negotiation_id: str,
    company_name: str,
    investor_name: str,
) -> None:
    """
    Log the escalation notification to a file as fallback.
    
    Args:
        counter_offer: Counter offer details
        negotiation_id: ID of the negotiation session
        company_name: Name of the company
        investor_name: Name of the investor
    """
    try:
        # Ensure the directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Format the log entry
        log_entry = {
            "timestamp": str(datetime.now().isoformat()),
            "negotiation_id": negotiation_id,
            "company_name": company_name,
            "investor_name": investor_name,
            "counter_offer": counter_offer
        }
        
        # Write to the human-override log file
        with open("logs/human-override.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        logger.info(f"Escalation notification logged to file for negotiation: {negotiation_id}")
    except Exception as e:
        logger.error(f"Error logging to file: {str(e)}")