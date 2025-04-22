#!/usr/bin/env python3
"""
AWS Cost Exporter for Prometheus

This script exports AWS cost metrics to Prometheus, including:
- Monthly cost estimates
- Daily costs
- Service-specific costs
- Cost by resource tags

The exporter uses AWS Cost Explorer API to retrieve cost data and
caches results to minimize API calls (which are rate limited and incur costs).
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Dict, Any, List, Optional, Tuple
import threading
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler

# AWS SDK
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Prometheus client
from prometheus_client import REGISTRY, Gauge, Counter, generate_latest
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("aws-cost-exporter")

# Default settings
DEFAULT_PORT = int(os.environ.get("PORT", "9101"))
DEFAULT_REFRESH_INTERVAL = int(os.environ.get("REFRESH_INTERVAL", "3600"))  # 1 hour
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Environment variables for AWS credentials (optional, will use boto3 credential chain)
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

# Define metrics
MONTHLY_COST = Gauge(
    "aws_monthly_cost_estimate", 
    "Estimated AWS costs for the current month in USD"
)
DAILY_COST = Gauge(
    "aws_daily_cost", 
    "AWS costs for the previous day in USD"
)
SERVICE_COST = Gauge(
    "aws_service_cost", 
    "AWS costs by service in USD",
    ["service"]
)
COST_BY_TAG = Gauge(
    "aws_cost_by_tag", 
    "AWS costs by resource tag in USD",
    ["key", "value"]
)
QUERY_COUNT = Counter(
    "aws_cost_exporter_api_queries_total", 
    "Total number of AWS Cost Explorer API queries"
)
QUERY_ERRORS = Counter(
    "aws_cost_exporter_api_errors_total", 
    "Total number of AWS Cost Explorer API errors"
)
LAST_REFRESH = Gauge(
    "aws_cost_exporter_last_refresh_timestamp",
    "Timestamp of the last successful data refresh"
)


class AWSCostCollector:
    """
    Collects AWS cost data from Cost Explorer API.
    Implements caching to minimize API calls.
    """
    
    def __init__(self, region: str = AWS_REGION):
        """Initialize with AWS region and credentials."""
        self.region = region
        self.client = self._create_cost_explorer_client()
    
    def _create_cost_explorer_client(self):
        """Create an AWS Cost Explorer client."""
        try:
            if AWS_ACCESS_KEY and AWS_SECRET_KEY:
                return boto3.client(
                    "ce", 
                    region_name=self.region,
                    aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY
                )
            else:
                return boto3.client("ce", region_name=self.region)
        except Exception as e:
            logger.error(f"Error creating AWS Cost Explorer client: {e}")
            return None
    
    @lru_cache(maxsize=1)
    def get_month_to_date_cost(self) -> Optional[float]:
        """
        Get the month-to-date cost from AWS Cost Explorer.
        Results are cached to minimize API calls.
        """
        if not self.client:
            logger.error("No Cost Explorer client available")
            return None
        
        # Calculate date range (start of month to today)
        today = datetime.now(timezone.utc)
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            QUERY_COUNT.inc()
            logger.info(f"Querying AWS Cost Explorer for month-to-date ({start_date} to {end_date})")
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date,
                    "End": end_date
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"]
            )
            
            # Parse the response
            results = response.get("ResultsByTime", [])
            if results:
                amount = float(results[0].get("Total", {}).get("UnblendedCost", {}).get("Amount", 0))
                return amount
            
            return 0.0
        except ClientError as e:
            QUERY_ERRORS.inc()
            logger.error(f"AWS Cost Explorer API error: {e}")
            return None
        except Exception as e:
            QUERY_ERRORS.inc()
            logger.error(f"Error getting month-to-date cost: {e}")
            return None
    
    @lru_cache(maxsize=1)
    def get_daily_cost(self, days_ago: int = 1) -> Optional[float]:
        """
        Get the cost for a specific day.
        Default is previous day.
        """
        if not self.client:
            logger.error("No Cost Explorer client available")
            return None
        
        # Calculate date range
        today = datetime.now(timezone.utc)
        target_date = today - timedelta(days=days_ago)
        start_date = target_date.strftime("%Y-%m-%d")
        end_date = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            QUERY_COUNT.inc()
            logger.info(f"Querying AWS Cost Explorer for daily cost ({start_date})")
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date,
                    "End": end_date
                },
                Granularity="DAILY",
                Metrics=["UnblendedCost"]
            )
            
            # Parse the response
            results = response.get("ResultsByTime", [])
            if results:
                amount = float(results[0].get("Total", {}).get("UnblendedCost", {}).get("Amount", 0))
                return amount
            
            return 0.0
        except ClientError as e:
            QUERY_ERRORS.inc()
            logger.error(f"AWS Cost Explorer API error: {e}")
            return None
        except Exception as e:
            QUERY_ERRORS.inc()
            logger.error(f"Error getting daily cost: {e}")
            return None
    
    @lru_cache(maxsize=1)
    def get_cost_by_service(self, days: int = 30) -> Dict[str, float]:
        """
        Get costs broken down by AWS service.
        Results are cached to minimize API calls.
        """
        if not self.client:
            logger.error("No Cost Explorer client available")
            return {}
        
        # Calculate date range
        today = datetime.now(timezone.utc)
        start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        try:
            QUERY_COUNT.inc()
            logger.info(f"Querying AWS Cost Explorer for cost by service")
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date,
                    "End": end_date
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{
                    "Type": "DIMENSION",
                    "Key": "SERVICE"
                }]
            )
            
            # Parse the response
            results = {}
            for time_period in response.get("ResultsByTime", []):
                for group in time_period.get("Groups", []):
                    service = group.get("Keys", [""])[0]
                    amount = float(group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", 0))
                    if service in results:
                        results[service] += amount
                    else:
                        results[service] = amount
            
            return results
        except ClientError as e:
            QUERY_ERRORS.inc()
            logger.error(f"AWS Cost Explorer API error: {e}")
            return {}
        except Exception as e:
            QUERY_ERRORS.inc()
            logger.error(f"Error getting cost by service: {e}")
            return {}
    
    @lru_cache(maxsize=1)
    def get_cost_by_tag(self, tag_key: str, days: int = 30) -> Dict[str, float]:
        """
        Get costs broken down by a specific resource tag.
        Results are cached to minimize API calls.
        """
        if not self.client:
            logger.error("No Cost Explorer client available")
            return {}
        
        # Calculate date range
        today = datetime.now(timezone.utc)
        start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        try:
            QUERY_COUNT.inc()
            logger.info(f"Querying AWS Cost Explorer for cost by tag: {tag_key}")
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date,
                    "End": end_date
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{
                    "Type": "TAG",
                    "Key": tag_key
                }]
            )
            
            # Parse the response
            results = {}
            for time_period in response.get("ResultsByTime", []):
                for group in time_period.get("Groups", []):
                    tag_value = group.get("Keys", [""])[0].replace(f"{tag_key}$", "")
                    amount = float(group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", 0))
                    if tag_value in results:
                        results[tag_value] += amount
                    else:
                        results[tag_value] = amount
            
            return results
        except ClientError as e:
            QUERY_ERRORS.inc()
            logger.error(f"AWS Cost Explorer API error: {e}")
            return {}
        except Exception as e:
            QUERY_ERRORS.inc()
            logger.error(f"Error getting cost by tag: {e}")
            return {}
    
    def clear_cache(self):
        """Clear all cached data to force fresh queries."""
        self.get_month_to_date_cost.cache_clear()
        self.get_daily_cost.cache_clear()
        self.get_cost_by_service.cache_clear()
        self.get_cost_by_tag.cache_clear()
        logger.info("Cleared all cached cost data")


def update_metrics(collector: AWSCostCollector):
    """Update all Prometheus metrics with fresh data from AWS."""
    try:
        # Get monthly cost
        monthly_cost = collector.get_month_to_date_cost()
        if monthly_cost is not None:
            MONTHLY_COST.set(monthly_cost)
            logger.info(f"Updated monthly cost: ${monthly_cost:.2f}")
        
        # Get daily cost
        daily_cost = collector.get_daily_cost()
        if daily_cost is not None:
            DAILY_COST.set(daily_cost)
            logger.info(f"Updated daily cost: ${daily_cost:.2f}")
        
        # Get cost by service
        service_costs = collector.get_cost_by_service()
        # Clear existing metrics
        for label in list(SERVICE_COST._metrics.keys()):
            SERVICE_COST.remove(*label)
        # Set new values
        for service, cost in service_costs.items():
            SERVICE_COST.labels(service=service).set(cost)
        logger.info(f"Updated service costs for {len(service_costs)} services")
        
        # Get cost by environment tag
        tag_costs = collector.get_cost_by_tag("Environment")
        # Clear existing metrics
        for label in list(COST_BY_TAG._metrics.keys()):
            COST_BY_TAG.remove(*label)
        # Set new values
        for tag_value, cost in tag_costs.items():
            COST_BY_TAG.labels(key="Environment", value=tag_value).set(cost)
        logger.info(f"Updated tag costs for {len(tag_costs)} tag values")
        
        # Update last refresh timestamp
        LAST_REFRESH.set(time.time())
        logger.info("Successfully updated all metrics")
        
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics requests."""
    
    def do_GET(self):
        """Handle GET requests for metrics."""
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(generate_latest(REGISTRY))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.info(f"{self.address_string()} - {format % args}")


def refresh_metrics_periodically(collector: AWSCostCollector, interval: int):
    """Refresh metrics periodically in the background."""
    def refresh_worker():
        while True:
            try:
                logger.info(f"Refreshing metrics (interval: {interval}s)")
                # Clear cache to force fresh data
                collector.clear_cache()
                # Update metrics
                update_metrics(collector)
                # Sleep until next refresh
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in refresh worker: {e}")
                # Sleep for a while before retrying
                time.sleep(60)
    
    # Start the refresh thread
    thread = threading.Thread(target=refresh_worker, daemon=True)
    thread.start()
    return thread


def main():
    """Main entry point for the AWS Cost Exporter."""
    parser = argparse.ArgumentParser(description="AWS Cost Exporter for Prometheus")
    parser.add_argument(
        "-p", "--port", type=int, default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "-i", "--interval", type=int, default=DEFAULT_REFRESH_INTERVAL,
        help=f"Refresh interval in seconds (default: {DEFAULT_REFRESH_INTERVAL})"
    )
    parser.add_argument(
        "-r", "--region", type=str, default=AWS_REGION,
        help=f"AWS region (default: {AWS_REGION})"
    )
    args = parser.parse_args()
    
    # Create collector
    collector = AWSCostCollector(region=args.region)
    
    # Populate initial metrics
    logger.info("Initializing metrics with first data pull")
    update_metrics(collector)
    
    # Start background refresh thread
    refresh_thread = refresh_metrics_periodically(collector, args.interval)
    
    # Start HTTP server
    server_address = ("", args.port)
    httpd = HTTPServer(server_address, MetricsHandler)
    logger.info(f"Starting AWS Cost Exporter on port {args.port}")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down AWS Cost Exporter")
        httpd.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error in server: {e}")
    finally:
        httpd.server_close()
        logger.info("Server stopped")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())