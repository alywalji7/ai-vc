#!/usr/bin/env python3
"""
AWS Cost Exporter for Prometheus

This script collects AWS cost data using the AWS Cost Explorer API and exports
metrics in Prometheus format using a simple HTTP server.

Metrics exported:
- aws_cost_current_usd: Current month's AWS costs by service
- aws_cost_forecast_usd: Forecasted AWS costs for the current month
- aws_budget_percent: Percentage of monthly budget used/forecasted
- aws_cost_daily_usd: Daily AWS costs for the current month

Environment variables:
- AWS_ACCESS_KEY_ID: AWS access key with Cost Explorer permissions
- AWS_SECRET_ACCESS_KEY: AWS secret key
- AWS_REGION: AWS region (default: us-east-1)
- PROMETHEUS_PORT: Port to expose metrics on (default: 9101)
- METRICS_INTERVAL_SECONDS: How often to refresh metrics (default: 3600)
- AWS_BUDGET_LIMIT_USD: Monthly budget limit in USD (default: 1000)
"""

import os
import time
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from prometheus_client import start_http_server, Gauge

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
PROMETHEUS_PORT = int(os.environ.get('PROMETHEUS_PORT', 9101))
METRICS_INTERVAL_SECONDS = int(os.environ.get('METRICS_INTERVAL_SECONDS', 3600))
AWS_BUDGET_LIMIT_USD = float(os.environ.get('AWS_BUDGET_LIMIT_USD', 1000))

# Prometheus metrics
aws_cost_current = Gauge('aws_cost_current_usd', 'Current AWS costs in USD', ['service'])
aws_cost_forecast = Gauge('aws_cost_forecast_usd', 'Forecasted AWS costs in USD for the current month')
aws_budget_percent = Gauge('aws_budget_percent', 'Percentage of monthly budget used/forecasted')
aws_cost_daily = Gauge('aws_cost_daily_usd', 'Daily AWS costs in USD', ['date'])

# Global variable to cache the last successful API results
last_successful_results = {
    'current_costs': {},
    'forecast': 0.0,
    'daily_costs': {},
    'last_update': None
}


def get_aws_cost_explorer_client() -> Any:
    """Create and return an AWS Cost Explorer client."""
    try:
        return boto3.client('ce', region_name=AWS_REGION)
    except Exception as e:
        logger.error(f"Failed to create AWS Cost Explorer client: {str(e)}")
        return None


def get_month_date_range() -> Tuple[str, str]:
    """Get the date range for the current month in YYYY-MM-DD format."""
    today = datetime.datetime.now()
    start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    return start_of_month, today_str


def get_current_costs() -> Dict[str, float]:
    """
    Get the current month's AWS costs by service.
    
    Returns:
        Dict mapping service names to costs in USD
    """
    client = get_aws_cost_explorer_client()
    if not client:
        logger.warning("Using cached costs due to client initialization failure.")
        return last_successful_results['current_costs']
    
    try:
        start_date, end_date = get_month_date_range()
        
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        
        result = {}
        
        # Process the response
        for group in response['ResultsByTime'][0]['Groups']:
            service = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            result[service] = cost
        
        return result
    
    except ClientError as e:
        logger.error(f"AWS API error: {str(e)}")
        return last_successful_results['current_costs']
    
    except Exception as e:
        logger.error(f"Error getting current costs: {str(e)}")
        return last_successful_results['current_costs']


def get_cost_forecast() -> float:
    """
    Get the forecasted AWS costs for the current month.
    
    Returns:
        Forecasted costs in USD
    """
    client = get_aws_cost_explorer_client()
    if not client:
        logger.warning("Using cached forecast due to client initialization failure.")
        return last_successful_results['forecast']
    
    try:
        start_date, _ = get_month_date_range()
        
        # Calculate end of month
        start_date_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        if start_date_dt.month == 12:
            next_month = datetime.datetime(start_date_dt.year + 1, 1, 1)
        else:
            next_month = datetime.datetime(start_date_dt.year, start_date_dt.month + 1, 1)
        
        end_date = (next_month - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
        response = client.get_cost_forecast(
            TimePeriod={
                'Start': datetime.datetime.now().strftime('%Y-%m-%d'),
                'End': end_date
            },
            Metric='UNBLENDED_COST',
            Granularity='MONTHLY'
        )
        
        # Get the forecasted amount
        forecast = float(response['Total']['Amount'])
        
        return forecast
    
    except ClientError as e:
        logger.error(f"AWS API error: {str(e)}")
        return last_successful_results['forecast']
    
    except Exception as e:
        logger.error(f"Error getting cost forecast: {str(e)}")
        return last_successful_results['forecast']


def get_daily_costs() -> Dict[str, float]:
    """
    Get the daily AWS costs for the current month.
    
    Returns:
        Dict mapping date strings to costs in USD
    """
    client = get_aws_cost_explorer_client()
    if not client:
        logger.warning("Using cached daily costs due to client initialization failure.")
        return last_successful_results['daily_costs']
    
    try:
        start_date, end_date = get_month_date_range()
        
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
        
        result = {}
        
        # Process the response
        for day in response['ResultsByTime']:
            date = day['TimePeriod']['Start']
            cost = float(day['Total']['UnblendedCost']['Amount'])
            result[date] = cost
        
        return result
    
    except ClientError as e:
        logger.error(f"AWS API error: {str(e)}")
        return last_successful_results['daily_costs']
    
    except Exception as e:
        logger.error(f"Error getting daily costs: {str(e)}")
        return last_successful_results['daily_costs']


def update_prometheus_metrics() -> None:
    """Update Prometheus metrics with the latest AWS cost data."""
    try:
        # Get the current costs by service
        current_costs = get_current_costs()
        
        # Clear existing metrics
        aws_cost_current._metrics.clear()
        
        # Update metrics for current costs
        total_current_cost = 0.0
        for service, cost in current_costs.items():
            aws_cost_current.labels(service=service).set(cost)
            total_current_cost += cost
        
        # Get the forecasted costs
        forecast = get_cost_forecast()
        
        # Set the forecast metric
        aws_cost_forecast.set(forecast)
        
        # Calculate and set the budget percentage
        forecasted_percentage = (forecast / AWS_BUDGET_LIMIT_USD) * 100
        aws_budget_percent.set(min(forecasted_percentage, 100.0))
        
        # Get the daily costs
        daily_costs = get_daily_costs()
        
        # Clear existing daily metrics
        aws_cost_daily._metrics.clear()
        
        # Update metrics for daily costs
        for date, cost in daily_costs.items():
            aws_cost_daily.labels(date=date).set(cost)
        
        # Cache the successful results
        global last_successful_results
        last_successful_results = {
            'current_costs': current_costs,
            'forecast': forecast,
            'daily_costs': daily_costs,
            'last_update': datetime.datetime.now()
        }
        
        logger.info(f"Updated AWS cost metrics - Current: ${total_current_cost:.2f}, "
                    f"Forecast: ${forecast:.2f}, Budget %: {forecasted_percentage:.1f}%")
        
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
        logger.info("Exiting AWS Cost Exporter")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()