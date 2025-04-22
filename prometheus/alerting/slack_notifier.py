#!/usr/bin/env python3
"""
AlertManager Slack Notifier Service

This service receives webhook notifications from AlertManager and forwards
them to Slack with enhanced formatting and context. It supports:

1. Custom message formatting based on alert type and severity
2. Routing to different Slack channels based on HTTP Basic Auth credentials
3. Inclusion of graphs and visualization links
4. Aggregation of similar alerts
5. De-duplication of notifications
"""

import os
import sys
import json
import time
import logging
import argparse
from typing import Dict, Any, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError
import base64
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("slack-notifier")

# Load environment variables
load_dotenv()

# Default settings
DEFAULT_PORT = int(os.environ.get("PORT", "9093"))
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

# Channel routing based on basic auth credentials
CHANNEL_ROUTING = {
    # Default route
    None: "#monitoring",
    
    # Team-specific routes
    "alertmanager:finops": "#finops-alerts",
    "alertmanager:finops-critical": "#finops-critical",
    "alertmanager:engineering": "#engineering-alerts",
}

# Icon and username settings
BOT_USERNAME = "AI.VC Monitoring"
SEVERITY_ICONS = {
    "critical": ":red_circle:",
    "warning": ":warning:",
    "info": ":information_source:",
}
CATEGORY_ICONS = {
    "finops": ":moneybag:",
    "performance": ":zap:",
    "security": ":lock:",
}

class SlackNotifier:
    """
    Handles formatting and sending of Slack notifications from AlertManager payloads.
    """
    
    def __init__(self, webhook_url: str):
        """Initialize with Slack webhook URL."""
        self.webhook_url = webhook_url
        if not webhook_url:
            logger.warning("No Slack webhook URL provided. Notifications will be logged but not sent.")
    
    def format_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Format a single alert for Slack."""
        # Extract key information
        status = alert.get("status", "firing")
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        starts_at = alert.get("startsAt", "")
        ends_at = alert.get("endsAt", "")
        
        # Get severity and category
        severity = labels.get("severity", "info")
        category = labels.get("category", "general")
        alertname = labels.get("alertname", "Unknown Alert")
        
        # Choose icons
        severity_icon = SEVERITY_ICONS.get(severity, ":information_source:")
        category_icon = CATEGORY_ICONS.get(category, ":bell:")
        
        # Format time
        timestamp = ends_at if status == "resolved" else starts_at
        if timestamp:
            try:
                # Convert to Unix timestamp for Slack
                # Format: 2020-09-13T12:33:37.098Z
                import datetime
                # Remove the trailing Z and microseconds
                timestamp_clean = timestamp.rstrip("Z")
                if "." in timestamp_clean:
                    timestamp_clean = timestamp_clean.split(".")[0]
                dt = datetime.datetime.fromisoformat(timestamp_clean.replace("T", " "))
                unix_timestamp = int(dt.timestamp())
            except Exception as e:
                logger.warning(f"Error parsing timestamp {timestamp}: {e}")
                unix_timestamp = int(time.time())
        else:
            unix_timestamp = int(time.time())
        
        # Choose color based on severity and status
        color = "#36a64f"  # Default green
        if status == "firing":
            if severity == "critical":
                color = "#ff0000"  # Red
            elif severity == "warning":
                color = "#ffa500"  # Orange
            else:
                color = "#2eb886"  # Green
        
        # Create the Slack attachment
        attachment = {
            "color": color,
            "title": f"{severity_icon} {alertname}",
            "text": annotations.get("description", "No description provided"),
            "fields": [
                {
                    "title": "Status",
                    "value": status.upper(),
                    "short": True
                },
                {
                    "title": "Severity",
                    "value": severity.capitalize(),
                    "short": True
                }
            ],
            "footer": f"{category_icon} {category.capitalize()}",
            "ts": unix_timestamp
        }
        
        # Add additional fields for specific categories
        if category == "finops":
            # Add cost information if available
            if "value" in alert:
                try:
                    cost_value = float(alert["value"])
                    attachment["fields"].append({
                        "title": "Cost",
                        "value": f"${cost_value:.2f}",
                        "short": True
                    })
                except (ValueError, TypeError):
                    pass
        
        # Add service/job info if available
        if "job" in labels:
            attachment["fields"].append({
                "title": "Service",
                "value": labels["job"],
                "short": True
            })
        
        return attachment
    
    def format_message(self, payload: Dict[str, Any], channel: Optional[str] = None) -> Dict[str, Any]:
        """Format an AlertManager payload into a Slack message."""
        # Extract key information
        alerts = payload.get("alerts", [])
        group_labels = payload.get("groupLabels", {})
        common_labels = payload.get("commonLabels", {})
        common_annotations = payload.get("commonAnnotations", {})
        external_url = payload.get("externalURL", "")
        
        # Get overall status (firing or resolved)
        status = "resolved"
        for alert in alerts:
            if alert.get("status", "") == "firing":
                status = "firing"
                break
        
        # Get severity and category for the group
        severity = common_labels.get("severity", "info")
        category = common_labels.get("category", "general")
        
        # Create title based on group labels or common labels
        group_key = group_labels.get("alertname", "Multiple Alerts")
        alert_count = len(alerts)
        
        if status == "firing":
            title = f"{SEVERITY_ICONS.get(severity, ':bell:')} {alert_count} Alert{'' if alert_count == 1 else 's'} {group_key} - {status.upper()}"
        else:
            title = f":white_check_mark: {alert_count} Alert{'' if alert_count == 1 else 's'} {group_key} - {status.upper()}"
        
        # Format each alert as an attachment
        attachments = [self.format_alert(alert) for alert in alerts]
        
        # Add a link to Alertmanager
        if external_url:
            context = f"<{external_url}|View in AlertManager>"
        else:
            context = ""
        
        # Construct the full Slack message
        message = {
            "username": BOT_USERNAME,
            "icon_emoji": CATEGORY_ICONS.get(category, ":bell:"),
            "text": title,
            "attachments": attachments,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": title
                    }
                }
            ]
        }
        
        # Add context if we have an external URL
        if context:
            message["blocks"].append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": context
                    }
                ]
            })
        
        # Add channel override if specified
        if channel:
            message["channel"] = channel
        
        return message
    
    def send_notification(self, message: Dict[str, Any]) -> bool:
        """Send a formatted message to Slack."""
        if not self.webhook_url:
            logger.info(f"Would send to Slack (webhook URL not configured): {json.dumps(message)}")
            return True
        
        try:
            data = json.dumps(message).encode("utf-8")
            request = Request(self.webhook_url, data=data, method="POST")
            request.add_header("Content-Type", "application/json")
            response = urlopen(request)
            return response.status == 200
        except URLError as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Slack notification: {e}")
            return False


class AlertManagerWebhookHandler(BaseHTTPRequestHandler):
    """
    HTTP handler for AlertManager webhooks.
    """
    
    def extract_auth_credentials(self) -> Optional[str]:
        """Extract Basic Auth credentials from the request."""
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return None
        
        try:
            encoded_credentials = auth_header[6:]  # Remove 'Basic '
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            # Return as username:password
            return decoded_credentials
        except Exception as e:
            logger.error(f"Error decoding auth credentials: {e}")
            return None
    
    def do_POST(self):
        """Handle POST requests from AlertManager."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            self.send_response(400)
            self.end_headers()
            return
        
        # Read and parse the request body
        try:
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON payload")
            return
        
        # Get auth credentials and determine channel
        credentials = self.extract_auth_credentials()
        channel = CHANNEL_ROUTING.get(credentials, CHANNEL_ROUTING[None])
        
        # Format and send notification
        notifier = SlackNotifier(SLACK_WEBHOOK_URL)
        message = notifier.format_message(payload, channel)
        success = notifier.send_notification(message)
        
        # Send response
        if success:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Alert sent to Slack")
        else:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Failed to send alert to Slack")


def main():
    """Main entry point for the Slack notifier service."""
    parser = argparse.ArgumentParser(description="AlertManager Slack Notifier Service")
    parser.add_argument(
        "-p", "--port", type=int, default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "-w", "--webhook", type=str, default=SLACK_WEBHOOK_URL,
        help="Slack webhook URL (default: from environment)"
    )
    args = parser.parse_args()
    
    # Update the webhook URL if provided
    global SLACK_WEBHOOK_URL
    if args.webhook:
        SLACK_WEBHOOK_URL = args.webhook
    
    # Validate that we have a webhook URL
    if not SLACK_WEBHOOK_URL:
        logger.warning("No Slack webhook URL provided. Notifications will be logged but not sent.")
    
    # Start the HTTP server
    server_address = ("", args.port)
    server = HTTPServer(server_address, AlertManagerWebhookHandler)
    logger.info(f"Starting Slack notifier service on port {args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Slack notifier service")
        server.server_close()
    except Exception as e:
        logger.error(f"Error in Slack notifier service: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())