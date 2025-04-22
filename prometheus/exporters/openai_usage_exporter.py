#!/usr/bin/env python3
"""
OpenAI Usage Exporter for Prometheus

This script collects OpenAI API usage data and exports metrics in Prometheus
format using a simple HTTP server.

Metrics exported:
- openai_daily_tokens: Daily token usage by model
- openai_total_cost_usd: Total cost by model
- openai_quota_percent: Percentage of monthly quota used
- openai_request_latency_seconds: API latency by endpoint and model

Environment variables:
- OPENAI_API_KEY: OpenAI API key
- PROMETHEUS_PORT: Port to expose metrics on (default: 9102)
- METRICS_INTERVAL_SECONDS: How often to refresh metrics (default: 3600)
- OPENAI_QUOTA_LIMIT_USD: Monthly quota limit in USD (default: 100)
"""

import os
import time
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

import openai
from prometheus_client import start_http_server, Gauge, Histogram

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
PROMETHEUS_PORT = int(os.environ.get('PROMETHEUS_PORT', 9102))
METRICS_INTERVAL_SECONDS = int(os.environ.get('METRICS_INTERVAL_SECONDS', 3600))
OPENAI_QUOTA_LIMIT_USD = float(os.environ.get('OPENAI_QUOTA_LIMIT_USD', 100))

# OpenAI API setup
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Model cost pricing (in USD per 1K tokens)
MODEL_COSTS = {
    'gpt-4o': {'input': 0.005, 'output': 0.015},
    'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
    'gpt-4': {'input': 0.03, 'output': 0.06},
    'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
    'text-embedding-ada-002': {'input': 0.0001, 'output': 0.0},
    'text-embedding-3-small': {'input': 0.00002, 'output': 0.0},
    'text-embedding-3-large': {'input': 0.00013, 'output': 0.0},
    'dall-e-3': {'image': 0.04},  # Per image generated at 1024x1024
    'whisper-1': {'audio': 0.006}  # Per minute of audio
}

# Prometheus metrics
openai_daily_tokens = Gauge('openai_daily_tokens', 'Daily OpenAI token usage', ['model', 'date'])
openai_total_cost_usd = Gauge('openai_total_cost_usd', 'Total OpenAI cost in USD', ['model'])
openai_quota_percent = Gauge('openai_quota_percent', 'Percentage of monthly OpenAI quota used')
openai_request_latency = Histogram(
    'openai_request_latency_seconds',
    'OpenAI API request latency in seconds',
    ['endpoint', 'model'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0)
)

# Global variable to cache the last successful API results
last_successful_results = {
    'usage_data': {},
    'total_cost': 0.0,
    'last_update': None
}


def get_openai_client() -> Any:
    """Get the OpenAI client."""
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not set")
        return None
    
    try:
        return openai.OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to create OpenAI client: {str(e)}")
        return None


def get_daily_usage() -> Dict[str, Dict[str, int]]:
    """
    Get daily OpenAI API usage.
    
    Returns:
        Dict mapping dates to models to token counts
    """
    client = get_openai_client()
    if not client:
        logger.warning("Using cached usage data due to client initialization failure.")
        return last_successful_results.get('usage_data', {})
    
    try:
        # Get the current date in YYYY-MM-DD format
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # For a real implementation, you would use the OpenAI API to get usage data
        # Unfortunately, OpenAI doesn't have a simple "get usage" API endpoint
        # This would normally require parsing the usage data from billing reports
        
        # Simulate usage data for demonstration purposes
        # In a real implementation, you would retrieve this from the OpenAI API
        usage_data = {
            today: {
                'gpt-4o': 50000,
                'gpt-3.5-turbo': 200000,
                'text-embedding-3-large': 500000
            },
            (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'): {
                'gpt-4o': 45000,
                'gpt-3.5-turbo': 180000,
                'text-embedding-3-large': 450000
            },
            (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%d'): {
                'gpt-4o': 40000,
                'gpt-3.5-turbo': 160000,
                'text-embedding-3-large': 400000
            }
        }
        
        return usage_data
    
    except Exception as e:
        logger.error(f"Error getting usage data: {str(e)}")
        return last_successful_results.get('usage_data', {})


def calculate_costs(usage_data: Dict[str, Dict[str, int]]) -> Dict[str, float]:
    """
    Calculate costs by model from usage data.
    
    Args:
        usage_data: Dict mapping dates to models to token counts
        
    Returns:
        Dict mapping models to costs in USD
    """
    costs = {}
    
    # For each model, calculate cost based on token usage
    for date, models in usage_data.items():
        for model, tokens in models.items():
            # Get the base model (without fine-tuning identifiers)
            base_model = model.split(':')[0]
            
            # Default to gpt-3.5-turbo pricing if model not found
            if base_model not in MODEL_COSTS:
                logger.warning(f"Model {base_model} not found in pricing data, using gpt-3.5-turbo pricing")
                base_model = 'gpt-3.5-turbo'
            
            # Calculate cost (assuming 50% input, 50% output for simplicity)
            # In a real implementation, you would track input and output tokens separately
            input_tokens = tokens * 0.5
            output_tokens = tokens * 0.5
            
            input_cost = input_tokens * MODEL_COSTS[base_model]['input'] / 1000
            output_cost = output_tokens * MODEL_COSTS[base_model]['output'] / 1000
            total_cost = input_cost + output_cost
            
            # Add to model costs
            if model not in costs:
                costs[model] = 0
            costs[model] += total_cost
    
    return costs


def update_prometheus_metrics() -> None:
    """Update Prometheus metrics with the latest OpenAI usage data."""
    try:
        # Get the daily usage data
        usage_data = get_daily_usage()
        
        # Clear existing metrics
        openai_daily_tokens._metrics.clear()
        openai_total_cost_usd._metrics.clear()
        
        # Update daily token usage metrics
        for date, models in usage_data.items():
            for model, tokens in models.items():
                openai_daily_tokens.labels(model=model, date=date).set(tokens)
        
        # Calculate costs by model
        costs = calculate_costs(usage_data)
        
        # Update total cost metrics and calculate total spend
        total_spend = 0.0
        for model, cost in costs.items():
            openai_total_cost_usd.labels(model=model).set(cost)
            total_spend += cost
        
        # Calculate and update quota percentage
        quota_percentage = (total_spend / OPENAI_QUOTA_LIMIT_USD) * 100
        openai_quota_percent.set(min(quota_percentage, 100.0))
        
        # Cache the successful results
        global last_successful_results
        last_successful_results = {
            'usage_data': usage_data,
            'total_cost': total_spend,
            'last_update': datetime.datetime.now()
        }
        
        logger.info(f"Updated OpenAI usage metrics - Total spend: ${total_spend:.2f}, "
                    f"Quota %: {quota_percentage:.1f}%")
        
    except Exception as e:
        logger.error(f"Error updating metrics: {str(e)}")


def main() -> None:
    """Main function to start the HTTP server and update metrics periodically."""
    try:
        # Start up the server to expose the metrics
        start_http_server(PROMETHEUS_PORT)
        logger.info(f"Metrics server started on port {PROMETHEUS_PORT}")
        
        # Initial update
        logger.info("Performing initial metrics update...")
        update_prometheus_metrics()
        
        # Update metrics every interval
        while True:
            time.sleep(METRICS_INTERVAL_SECONDS)
            logger.info("Updating metrics...")
            update_prometheus_metrics()
            
    except KeyboardInterrupt:
        logger.info("Exiting OpenAI Usage Exporter")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY environment variable is not set. Using simulated data.")
    main()