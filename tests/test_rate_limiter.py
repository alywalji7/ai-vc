"""
Test script for rate limiting and cost guardrails functionality.

This script sends multiple requests to the Radar API to test the rate
limiting functionality. It will make requests in rapid succession to
trigger the rate limit.
"""
import sys
import os
import time
import asyncio
import argparse
import logging
from typing import Any, Dict, List, Optional
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default API URL
DEFAULT_API_URL = "http://localhost:8050"


async def make_request(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    """
    Make an HTTP request to the specified URL.
    
    Args:
        session: aiohttp client session
        url: URL to request
        
    Returns:
        Response data (JSON) or error information
    """
    try:
        async with session.get(url) as response:
            status = response.status
            try:
                data = await response.json()
                return {
                    "status": status,
                    "data": data
                }
            except Exception as e:
                text = await response.text()
                return {
                    "status": status,
                    "error": str(e),
                    "text": text
                }
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        return {
            "status": 0,
            "error": str(e)
        }


async def test_rate_limit(base_url: str, num_requests: int, concurrency: int) -> None:
    """
    Test rate limiting by making multiple concurrent requests.
    
    Args:
        base_url: Base URL of the API
        num_requests: Number of requests to make
        concurrency: Number of concurrent requests
    """
    endpoints = [
        "/radar/daily_shortlist?limit=5",
        "/radar/model_metadata"
    ]
    
    async with aiohttp.ClientSession() as session:
        # Test endpoint information
        logger.info(f"Testing API at {base_url}")
        root_response = await make_request(session, base_url)
        
        if root_response["status"] != 200:
            logger.error(f"Failed to connect to API: {root_response}")
            return
        
        logger.info(f"API response: {root_response}")
        
        # Make concurrent requests to test rate limiting
        for endpoint in endpoints:
            logger.info(f"\nTesting endpoint: {endpoint}")
            url = f"{base_url}{endpoint}"
            
            # Make requests in batches with the specified concurrency
            for i in range(0, num_requests, concurrency):
                batch_size = min(concurrency, num_requests - i)
                tasks = [make_request(session, url) for _ in range(batch_size)]
                responses = await asyncio.gather(*tasks)
                
                # Count responses by status code
                status_counts = {}
                for response in responses:
                    status = response["status"]
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                logger.info(f"Batch {i//concurrency + 1} results: {status_counts}")
                
                # Display any rate limit errors
                for response in responses:
                    if response["status"] == 429:
                        if "data" in response and "detail" in response["data"]:
                            logger.info(f"Rate limit error: {response['data']['detail']}")
                        elif "text" in response:
                            logger.info(f"Rate limit response: {response['text']}")
                
                # Short pause between batches
                if i + batch_size < num_requests:
                    time.sleep(0.5)


async def check_metrics(base_url: str) -> None:
    """
    Check metrics endpoints.
    
    Args:
        base_url: Base URL of the API
    """
    metrics_endpoints = [
        "/metrics/status",
        "/metrics/request-counts",
        "/metrics/token-usage"
    ]
    
    logger.info("\nChecking metrics endpoints:")
    
    async with aiohttp.ClientSession() as session:
        for endpoint in metrics_endpoints:
            url = f"{base_url}{endpoint}"
            response = await make_request(session, url)
            
            if response["status"] == 200:
                logger.info(f"Endpoint {endpoint}: {response['data']}")
            else:
                logger.info(f"Endpoint {endpoint} error: {response}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test rate limiting functionality")
    parser.add_argument("--url", default=DEFAULT_API_URL, help="Base URL of the API")
    parser.add_argument("--requests", type=int, default=30, help="Number of requests to make")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent requests")
    parser.add_argument("--check-metrics", action="store_true", help="Check metrics endpoints after the test")
    
    return parser.parse_args()


async def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    logger.info(f"Starting rate limit test with {args.requests} requests, concurrency {args.concurrency}")
    
    await test_rate_limit(args.url, args.requests, args.concurrency)
    
    if args.check_metrics:
        await check_metrics(args.url)


if __name__ == "__main__":
    asyncio.run(main())