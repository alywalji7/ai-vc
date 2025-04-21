"""
Alerting utilities for AI.VC services.

This module provides helpers for defining structured alerts and
sending notifications to various channels.
"""

import json
import logging
import os
from enum import Enum
from typing import Dict, List, Optional, Union

import requests
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status types."""
    
    FIRING = "firing"
    RESOLVED = "resolved"


class Alert(BaseModel):
    """Alert model for structured alerts."""
    
    name: str
    severity: AlertSeverity
    status: AlertStatus
    service: str
    instance: Optional[str] = None
    description: str
    value: Optional[float] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    

class SlackAlertSender:
    """Send alerts to Slack using incoming webhooks."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize the Slack alert sender.
        
        Args:
            webhook_url: Slack webhook URL (defaults to env var SLACK_WEBHOOK_URL)
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            logger.warning("No Slack webhook URL provided for alerts")
    
    def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert to Slack.
        
        Args:
            alert: The alert to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.warning("Cannot send alert: No Slack webhook URL configured")
            return False
        
        # Set color based on severity
        color = "#36a64f"  # green for info
        if alert.severity == AlertSeverity.WARNING:
            color = "#ff9900"  # orange for warning
        elif alert.severity == AlertSeverity.CRITICAL:
            color = "#ff0000"  # red for critical
        
        # Format the message
        message = {
            "attachments": [
                {
                    "color": color,
                    "title": f"[{alert.status.upper()}] {alert.name}",
                    "text": alert.description,
                    "fields": [
                        {
                            "title": "Service",
                            "value": alert.service,
                            "short": True
                        },
                        {
                            "title": "Severity",
                            "value": alert.severity.value,
                            "short": True
                        }
                    ],
                    "footer": "AI.VC Alerting System"
                }
            ]
        }
        
        # Add instance field if present
        if alert.instance:
            message["attachments"][0]["fields"].append({
                "title": "Instance",
                "value": alert.instance,
                "short": True
            })
        
        # Add value field if present
        if alert.value is not None:
            message["attachments"][0]["fields"].append({
                "title": "Value",
                "value": str(alert.value),
                "short": True
            })
        
        # Add any additional labels and annotations
        for key, value in alert.labels.items():
            message["attachments"][0]["fields"].append({
                "title": key,
                "value": value,
                "short": True
            })
        
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False


def create_latency_alert(
    service: str,
    instance: str,
    p95_latency: float,
    threshold: float = 1.0
) -> Alert:
    """
    Create a latency alert.
    
    Args:
        service: The service name
        instance: The instance ID or hostname
        p95_latency: The p95 latency value in seconds
        threshold: The latency threshold in seconds
        
    Returns:
        Alert object
    """
    severity = AlertSeverity.WARNING
    if p95_latency > threshold * 2:
        severity = AlertSeverity.CRITICAL
    
    return Alert(
        name="HighLatency",
        severity=severity,
        status=AlertStatus.FIRING,
        service=service,
        instance=instance,
        description=f"P95 latency is {p95_latency:.2f}s, which exceeds the threshold of {threshold:.2f}s",
        value=p95_latency,
        labels={
            "threshold": str(threshold)
        }
    )


def create_error_rate_alert(
    service: str,
    instance: str,
    error_rate: float,
    threshold: float = 0.01
) -> Alert:
    """
    Create an error rate alert.
    
    Args:
        service: The service name
        instance: The instance ID or hostname
        error_rate: The error rate as a decimal (0.0-1.0)
        threshold: The error rate threshold as a decimal
        
    Returns:
        Alert object
    """
    severity = AlertSeverity.WARNING
    if error_rate > threshold * 2:
        severity = AlertSeverity.CRITICAL
    
    return Alert(
        name="HighErrorRate",
        severity=severity,
        status=AlertStatus.FIRING,
        service=service,
        instance=instance,
        description=f"Error rate is {error_rate:.2%}, which exceeds the threshold of {threshold:.2%}",
        value=error_rate,
        labels={
            "threshold": str(threshold)
        }
    )


def send_alert_to_slack(alert: Alert) -> bool:
    """
    Send an alert to Slack.
    
    Args:
        alert: The alert to send
        
    Returns:
        True if successful, False otherwise
    """
    sender = SlackAlertSender()
    return sender.send_alert(alert)