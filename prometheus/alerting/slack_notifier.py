#!/usr/bin/env python3
"""
Slack webhook notifier for Prometheus alerts

This service accepts webhook requests from Alertmanager and forwards them to Slack
with properly formatted messages.
"""

import os
import json
import logging
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#finops')
HTTP_PORT = int(os.environ.get('HTTP_PORT', 9093))

# Severity colors for Slack attachment
SEVERITY_COLORS = {
    'critical': '#FF0000',  # Red
    'warning': '#FFA500',   # Orange
    'info': '#0000FF',      # Blue
    'default': '#808080'    # Gray
}

class PrometheusAlertHandler(BaseHTTPRequestHandler):
    """Handle incoming webhook alerts from Prometheus Alertmanager"""
    
    def do_POST(self):
        """Handle POST requests from Alertmanager"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_response(400)
            self.end_headers()
            return
        
        # Read and parse the alert data
        post_data = self.rfile.read(content_length)
        try:
            alert_data = json.loads(post_data.decode('utf-8'))
            logger.info(f"Received alert: {json.dumps(alert_data)}")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON: {post_data.decode('utf-8')}")
            self.send_response(400)
            self.end_headers()
            return
            
        # Process the alert and send to Slack
        response = self._process_alert(alert_data)
        
        # Return response to Alertmanager
        self.send_response(200 if response else 500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
    
    def _process_alert(self, alert_data):
        """Process alert data and send to Slack"""
        if not SLACK_WEBHOOK_URL:
            logger.error("Slack webhook URL is not configured")
            return False
            
        # Check if there are alerts
        if 'alerts' not in alert_data or not alert_data['alerts']:
            logger.warning("No alerts in the notification")
            return True
        
        # Get status (firing or resolved)
        status = alert_data.get('status', 'firing')
        
        # Prepare message attachments for each alert
        attachments = []
        for alert in alert_data['alerts']:
            severity = alert.get('labels', {}).get('severity', 'default')
            color = SEVERITY_COLORS.get(severity, SEVERITY_COLORS['default'])
            
            # Format the alert time
            starts_at = alert.get('startsAt', '')
            try:
                time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
                parsed_time = datetime.datetime.strptime(starts_at, time_format)
                formatted_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S UTC')
            except ValueError:
                formatted_time = starts_at
            
            # Build alert fields
            fields = []
            
            # Add alert name
            alert_name = alert.get('labels', {}).get('alertname', 'Unknown Alert')
            fields.append({
                "title": "Alert",
                "value": alert_name,
                "short": True
            })
            
            # Add severity
            fields.append({
                "title": "Severity",
                "value": severity.capitalize(),
                "short": True
            })
            
            # Add start time
            fields.append({
                "title": "Start Time",
                "value": formatted_time,
                "short": True
            })
            
            # Add status
            fields.append({
                "title": "Status",
                "value": status.capitalize(),
                "short": True
            })
            
            # Add description if available
            if 'annotations' in alert and 'description' in alert['annotations']:
                fields.append({
                    "title": "Description",
                    "value": alert['annotations']['description'],
                    "short": False
                })
            
            # Add additional labels as fields
            for key, value in alert.get('labels', {}).items():
                if key not in ['alertname', 'severity']:
                    fields.append({
                        "title": key.capitalize(),
                        "value": value,
                        "short": True
                    })
            
            # Create attachment
            attachment = {
                "color": color,
                "title": f"{status.capitalize()}: {alert_name}",
                "fields": fields,
                "footer": "AI.VC Monitoring System",
                "footer_icon": "https://www.svgrepo.com/show/375433/prometheus.svg",
                "ts": int(datetime.datetime.now().timestamp())
            }
            attachments.append(attachment)
        
        # Build the Slack message
        emoji = ":rotating_light:" if status == "firing" else ":white_check_mark:"
        summary = f"{emoji} {len(alert_data['alerts'])} alert(s) {status}"
        message = {
            "channel": SLACK_CHANNEL,
            "username": "AI.VC Alert System",
            "icon_emoji": emoji,
            "text": summary,
            "attachments": attachments
        }
        
        # Send to Slack
        return self._send_to_slack(message)
    
    def _send_to_slack(self, message):
        """Send the formatted message to Slack webhook"""
        try:
            # Prepare the request
            request = Request(SLACK_WEBHOOK_URL)
            request.add_header('Content-Type', 'application/json')
            
            # Send the request
            response = urlopen(request, json.dumps(message).encode())
            
            # Check response
            if response.getcode() == 200:
                logger.info("Message sent to Slack successfully")
                return True
            else:
                logger.error(f"Error sending to Slack: {response.read().decode()}")
                return False
                
        except HTTPError as e:
            logger.error(f"HTTP Error sending to Slack: {e.code} - {e.reason}")
            return False
        except URLError as e:
            logger.error(f"URL Error sending to Slack: {e.reason}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending to Slack: {str(e)}")
            return False


def run_server(port=HTTP_PORT):
    """Start the HTTP server"""
    try:
        server = HTTPServer(('0.0.0.0', port), PrometheusAlertHandler)
        logger.info(f"Starting Slack notifier server on port {port}")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        server.socket.close()
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")


if __name__ == '__main__':
    # Check if webhook URL is configured
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL environment variable is not set. Notifications will be logged only.")
    
    run_server(HTTP_PORT)