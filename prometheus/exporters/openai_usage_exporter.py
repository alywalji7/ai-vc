#!/usr/bin/env python3
"""
OpenAI Usage Exporter for Prometheus

This script exports OpenAI API usage metrics to Prometheus, including:
- Token usage by model
- Cost calculations
- Rate limits and quotas
- Error rates

The exporter uses the OpenAI API to retrieve usage data and caches results
to minimize API calls (which can count against rate limits).
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, Any, List, Optional, Tuple
import threading
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler

# OpenAI client
import openai

# Prometheus client
from prometheus_client import REGISTRY, Gauge, Counter, generate_latest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("openai-usage-exporter")

# Default settings
DEFAULT_PORT = int(os.environ.get("PORT", "9102"))
DEFAULT_REFRESH_INTERVAL = int(os.environ.get("REFRESH_INTERVAL", "3600"))  # 1 hour

# Environment variables for OpenAI API
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_ORG_ID = os.environ.get("OPENAI_ORG_ID", "")

# Cost per model (in USD per 1K tokens)
MODEL_COSTS = {
    "gpt-4o": {
        "input": 0.005,    # $0.005 per 1K input tokens
        "output": 0.015,   # $0.015 per 1K output tokens
    },
    "gpt-4-turbo": {
        "input": 0.01,     # $0.01 per 1K input tokens
        "output": 0.03,    # $0.03 per 1K output tokens
    },
    "gpt-4": {
        "input": 0.03,     # $0.03 per 1K input tokens
        "output": 0.06,    # $0.06 per 1K output tokens
    },
    "gpt-3.5-turbo": {
        "input": 0.0015,   # $0.0015 per 1K input tokens
        "output": 0.002,   # $0.002 per 1K output tokens
    },
    "text-embedding-3-large": {
        "input": 0.00013,  # $0.00013 per 1K tokens
        "output": 0.0,     # No output tokens for embeddings
    },
    "text-embedding-3-small": {
        "input": 0.00002,  # $0.00002 per 1K tokens
        "output": 0.0,     # No output tokens for embeddings
    },
    "dall-e-3": {
        "1024x1024": 0.04, # $0.04 per image
        "1792x1024": 0.08, # $0.08 per image
    },
    "whisper-1": {
        "input": 0.006,    # $0.006 per minute
    }
}

# Define metrics
TOKENS_TOTAL = Gauge(
    "openai_tokens_total", 
    "Total OpenAI API token usage"
)
TOKENS_INPUT = Gauge(
    "openai_tokens_input", 
    "OpenAI API input token usage",
    ["model"]
)
TOKENS_OUTPUT = Gauge(
    "openai_tokens_output", 
    "OpenAI API output token usage",
    ["model"]
)
TOKENS_TOTAL_1D = Gauge(
    "openai_tokens_total_1d", 
    "Total OpenAI API token usage in the last 24 hours"
)
DAILY_COST = Gauge(
    "openai_daily_cost", 
    "Total OpenAI API cost for the current day in USD"
)
MODEL_COST = Gauge(
    "openai_model_cost", 
    "OpenAI API cost by model in USD",
    ["model"]
)
REQUEST_COUNT = Counter(
    "openai_requests_total", 
    "Total number of OpenAI API requests",
    ["model", "status"]
)
ERROR_COUNT = Counter(
    "openai_errors_total", 
    "Total number of OpenAI API errors",
    ["model", "error_type"]
)
LAST_REFRESH = Gauge(
    "openai_usage_exporter_last_refresh_timestamp",
    "Timestamp of the last successful data refresh"
)


class OpenAIUsageCollector:
    """
    Collects OpenAI API usage data.
    Implements caching to minimize API calls.
    """
    
    def __init__(self, api_key: str = OPENAI_API_KEY, org_id: str = OPENAI_ORG_ID):
        """Initialize with OpenAI API key and organization ID."""
        self.api_key = api_key
        self.org_id = org_id
        self.client = self._create_openai_client()
    
    def _create_openai_client(self):
        """Create an OpenAI API client."""
        try:
            if not self.api_key:
                logger.error("No OpenAI API key provided")
                return None
            
            # Create client with org ID if available
            if self.org_id:
                return openai.OpenAI(api_key=self.api_key, organization=self.org_id)
            else:
                return openai.OpenAI(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Error creating OpenAI client: {e}")
            return None
    
    @lru_cache(maxsize=1)
    def get_usage_data(self) -> Dict[str, Any]:
        """
        Get usage data from OpenAI API.
        Results are cached to minimize API calls.
        """
        if not self.client:
            logger.error("No OpenAI client available")
            return {}
        
        # Calculate date range (past 90 days to today)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        try:
            logger.info("Querying OpenAI API for usage data")
            
            # Unfortunately, OpenAI doesn't provide a direct usage endpoint in their Python client
            # We need to use their dashboard or billing exports for accurate data
            # This is a simplified version for demo purposes
            
            # Placeholder for actual API call
            # In production, you'd use something like:
            # response = self.client.organization.usage(
            #     start_date=start_date.strftime("%Y-%m-%d"),
            #     end_date=end_date.strftime("%Y-%m-%d")
            # )
            
            # For demonstration, we'll create mock data
            # In production, this should be replaced with actual API calls
            usage_data = {
                "total_tokens": 0,
                "total_cost": 0.0,
                "models": {}
            }
            
            # Add usage for each model
            for model_name, cost_info in MODEL_COSTS.items():
                if model_name.startswith("gpt"):
                    input_tokens = 0
                    output_tokens = 0
                    cost = 0.0
                    
                    # Log a warning that we're using estimated data
                    logger.warning(f"Using estimated usage data for {model_name}. In production, use the OpenAI dashboard or export data.")
                    
                    usage_data["models"][model_name] = {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cost": cost
                    }
                    
                    usage_data["total_tokens"] += input_tokens + output_tokens
                    usage_data["total_cost"] += cost
            
            return usage_data
        except Exception as e:
            logger.error(f"Error getting OpenAI usage data: {e}")
            return {}
    
    @lru_cache(maxsize=1)
    def get_daily_usage(self) -> Dict[str, Any]:
        """
        Get daily usage estimate.
        This is a rough estimate as OpenAI doesn't provide hourly or daily breakdowns easily.
        """
        # This would require custom tracking in your application
        # For now, we'll just provide a placeholder
        logger.warning("Daily usage is estimated. For accurate tracking, implement request logging in your application.")
        
        return {
            "total_tokens": 0,
            "total_cost": 0.0,
            "models": {}
        }
    
    def clear_cache(self):
        """Clear all cached data to force fresh queries."""
        self.get_usage_data.cache_clear()
        self.get_daily_usage.cache_clear()
        logger.info("Cleared all cached OpenAI usage data")


def update_metrics(collector: OpenAIUsageCollector):
    """Update all Prometheus metrics with fresh data from OpenAI."""
    try:
        # Get overall usage data
        usage_data = collector.get_usage_data()
        
        if usage_data:
            # Update total tokens
            total_tokens = usage_data.get("total_tokens", 0)
            TOKENS_TOTAL.set(total_tokens)
            logger.info(f"Updated total token usage: {total_tokens}")
            
            # Update per-model metrics
            for model_name, model_data in usage_data.get("models", {}).items():
                input_tokens = model_data.get("input_tokens", 0)
                output_tokens = model_data.get("output_tokens", 0)
                cost = model_data.get("cost", 0.0)
                
                TOKENS_INPUT.labels(model=model_name).set(input_tokens)
                TOKENS_OUTPUT.labels(model=model_name).set(output_tokens)
                MODEL_COST.labels(model=model_name).set(cost)
            
            logger.info(f"Updated metrics for {len(usage_data.get('models', {}))} models")
        
        # Get daily usage estimate
        daily_data = collector.get_daily_usage()
        
        if daily_data:
            # Update daily metrics
            TOKENS_TOTAL_1D.set(daily_data.get("total_tokens", 0))
            DAILY_COST.set(daily_data.get("total_cost", 0.0))
            logger.info(f"Updated daily usage metrics")
        
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


def refresh_metrics_periodically(collector: OpenAIUsageCollector, interval: int):
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
    """Main entry point for the OpenAI Usage Exporter."""
    parser = argparse.ArgumentParser(description="OpenAI Usage Exporter for Prometheus")
    parser.add_argument(
        "-p", "--port", type=int, default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "-i", "--interval", type=int, default=DEFAULT_REFRESH_INTERVAL,
        help=f"Refresh interval in seconds (default: {DEFAULT_REFRESH_INTERVAL})"
    )
    parser.add_argument(
        "-k", "--api-key", type=str, default=OPENAI_API_KEY,
        help="OpenAI API key (default: from environment)"
    )
    parser.add_argument(
        "-o", "--org-id", type=str, default=OPENAI_ORG_ID,
        help="OpenAI organization ID (default: from environment)"
    )
    args = parser.parse_args()
    
    # Update API key if provided
    api_key = args.api_key
    
    # Check if we have an API key
    if not api_key:
        logger.error("No OpenAI API key provided. Use --api-key or set OPENAI_API_KEY environment variable.")
        return 1
    
    # Create collector
    collector = OpenAIUsageCollector(api_key=api_key, org_id=args.org_id)
    
    # Populate initial metrics
    logger.info("Initializing metrics with first data pull")
    update_metrics(collector)
    
    # Start background refresh thread
    refresh_thread = refresh_metrics_periodically(collector, args.interval)
    
    # Start HTTP server
    server_address = ("", args.port)
    httpd = HTTPServer(server_address, MetricsHandler)
    logger.info(f"Starting OpenAI Usage Exporter on port {args.port}")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down OpenAI Usage Exporter")
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