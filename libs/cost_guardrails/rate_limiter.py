"""
Combined rate limiter for API requests.

This module provides a FastAPI middleware for rate limiting based on:
1. Token usage (OpenAI API)
2. GPU usage (NVIDIA DCGM)
3. Request count limits
"""
import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List, Any, Callable, Set, Union
import json
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import metering modules
from .openai_metering import token_rate_limit, token_usage_store
from .gpu_metering import gpu_rate_limit, gpu_usage_store, GPU_ENABLED

# Environment variables
DEFAULT_REQUESTS_PER_MINUTE = int(os.environ.get("DEFAULT_REQUESTS_PER_MINUTE", "60"))
RATE_LIMITING_ENABLED = os.environ.get("RATE_LIMITING_ENABLED", "true").lower() == "true"


class RequestRateLimiter:
    """Request count-based rate limiter with thread safety."""
    
    def __init__(self):
        self.request_counts = {}  # user_id -> {endpoint -> {minute -> count}}
        self.lock = threading.RLock()
    
    def increment(self, user_id: str, endpoint: str) -> int:
        """
        Increment request count for user and endpoint.
        
        Args:
            user_id: User ID
            endpoint: API endpoint
            
        Returns:
            Current request count for the current minute
        """
        minute_key = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with self.lock:
            # Initialize dictionaries if needed
            if user_id not in self.request_counts:
                self.request_counts[user_id] = {}
            
            if endpoint not in self.request_counts[user_id]:
                self.request_counts[user_id][endpoint] = {}
            
            if minute_key not in self.request_counts[user_id][endpoint]:
                self.request_counts[user_id][endpoint][minute_key] = 0
            
            # Increment count
            self.request_counts[user_id][endpoint][minute_key] += 1
            
            return self.request_counts[user_id][endpoint][minute_key]
    
    def get_count(self, user_id: str, endpoint: str) -> int:
        """
        Get request count for user and endpoint for the current minute.
        
        Args:
            user_id: User ID
            endpoint: API endpoint
            
        Returns:
            Current request count for the current minute
        """
        minute_key = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with self.lock:
            try:
                return self.request_counts[user_id][endpoint][minute_key]
            except KeyError:
                return 0
    
    def clear_old_data(self, retention_minutes: int = 10):
        """
        Clear data older than specified minutes.
        
        Args:
            retention_minutes: Minutes to retain data for
        """
        cutoff_time = datetime.now() - timedelta(minutes=retention_minutes)
        cutoff_key = cutoff_time.strftime("%Y-%m-%d %H:%M")
        
        with self.lock:
            for user_id in list(self.request_counts.keys()):
                for endpoint in list(self.request_counts[user_id].keys()):
                    for minute_key in list(self.request_counts[user_id][endpoint].keys()):
                        if minute_key < cutoff_key:
                            del self.request_counts[user_id][endpoint][minute_key]
                    
                    # Clean up empty dictionaries
                    if not self.request_counts[user_id][endpoint]:
                        del self.request_counts[user_id][endpoint]
                
                if not self.request_counts[user_id]:
                    del self.request_counts[user_id]


# Create a global request rate limiter
request_limiter = RequestRateLimiter()


# Start a cleaner thread to periodically clear old data
def start_cleaner_thread():
    """Start a background thread to clean up old rate limit data."""
    def cleaner():
        while True:
            time.sleep(60)  # Run every minute
            try:
                request_limiter.clear_old_data()
            except Exception as e:
                logger.error(f"Error in rate limiter cleaner: {str(e)}")
    
    cleaner_thread = threading.Thread(target=cleaner, daemon=True)
    cleaner_thread.start()
    logger.info("Rate limiter cleaner thread started")


# Combined rate limiting decorator
def rate_limit(
    requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
    token_quota: Optional[int] = None,
    gpu_memory_quota: Optional[int] = None,
    gpu_util_quota: Optional[int] = None
):
    """
    Combined decorator for rate limiting based on requests, tokens, and GPU usage.
    
    Args:
        requests_per_minute: Maximum requests per minute
        token_quota: Maximum tokens per user per day (None to use default)
        gpu_memory_quota: Maximum GPU memory usage in MB-seconds (None to use default)
        gpu_util_quota: Maximum GPU utilization in %-seconds (None to use default)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        # Apply individual decorators
        if token_quota is not None:
            func = token_rate_limit(user_quota=token_quota)(func)
        
        if GPU_ENABLED and (gpu_memory_quota is not None or gpu_util_quota is not None):
            func = gpu_rate_limit(
                memory_quota=gpu_memory_quota if gpu_memory_quota is not None else 0,
                util_quota=gpu_util_quota if gpu_util_quota is not None else 0
            )(func)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not RATE_LIMITING_ENABLED:
                return await func(*args, **kwargs)
            
            # Extract request object
            request = kwargs.get('request')
            if not request and args and hasattr(args[0], 'client'):
                request = args[0]
            
            # Extract user ID from request if available
            user_id = "anonymous"
            if request and hasattr(request, 'state') and hasattr(request.state, 'user'):
                user_id = request.state.user.id
            
            # Get endpoint path
            endpoint = request.url.path if request and hasattr(request, 'url') else "unknown"
            
            # Increment and check request count
            count = request_limiter.increment(user_id, endpoint)
            
            if count > requests_per_minute:
                logger.warning(f"Request rate limit exceeded for {user_id} on {endpoint}: {count}/{requests_per_minute}")
                from fastapi import HTTPException
                raise HTTPException(status_code=429, detail="Rate limit exceeded: Too many requests")
            
            # Call the original function
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# FastAPI middleware for rate limiting
def create_cost_guardrail_middleware():
    """
    Create a FastAPI middleware for cost guardrails and rate limiting.
    
    Usage:
        app = FastAPI()
        app.add_middleware(create_cost_guardrail_middleware())
    """
    from fastapi import Request, Response
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class CostGuardrailMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Extract user ID from request if available
            user_id = "anonymous"
            if hasattr(request, 'state') and hasattr(request.state, 'user'):
                user_id = request.state.user.id
            
            # Get endpoint path
            endpoint = request.url.path
            
            # Skip certain paths (like metrics or health checks)
            skip_paths = {"/health", "/metrics", "/favicon.ico"}
            if any(endpoint.startswith(path) for path in skip_paths):
                return await call_next(request)
            
            # Check request rate limit
            if RATE_LIMITING_ENABLED:
                count = request_limiter.increment(user_id, endpoint)
                
                if count > DEFAULT_REQUESTS_PER_MINUTE:
                    logger.warning(f"Request rate limit exceeded for {user_id} on {endpoint}: {count}/{DEFAULT_REQUESTS_PER_MINUTE}")
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Rate limit exceeded: Too many requests"}
                    )
            
            # Continue with the request
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log request info
            logger.info(f"Request: {request.method} {endpoint} - User: {user_id} - Duration: {duration:.2f}s")
            
            return response
    
    return CostGuardrailMiddleware


# Initialize the rate limiter
start_cleaner_thread()