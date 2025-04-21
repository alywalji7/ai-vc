"""
OpenAI token usage monitoring and tracking.

This module provides utilities for tracking OpenAI API token usage,
implementing usage quotas, and enforcing rate limits.
"""
import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List, Any
import json
import requests
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_ORGANIZATION_ID = os.environ.get("OPENAI_ORGANIZATION_ID")

# Default quota settings
DEFAULT_USER_TOKEN_QUOTA = int(os.environ.get("DEFAULT_USER_TOKEN_QUOTA", "100000"))  # 100K tokens per user per day
DEFAULT_ENDPOINT_TOKEN_QUOTA = int(os.environ.get("DEFAULT_ENDPOINT_TOKEN_QUOTA", "1000000"))  # 1M tokens per endpoint per day
DEFAULT_ORGANIZATION_TOKEN_QUOTA = int(os.environ.get("DEFAULT_ORGANIZATION_TOKEN_QUOTA", "10000000"))  # 10M tokens per org per day

# Token usage storage
# In production, this would be replaced with a persistent store like Redis
class TokenUsageStore:
    """In-memory token usage storage with thread safety."""
    
    def __init__(self):
        self.user_usage = {}  # user_id -> {date -> usage_count}
        self.endpoint_usage = {}  # endpoint -> {date -> usage_count}
        self.org_usage = {}  # date -> usage_count
        self.lock = threading.RLock()
    
    def log_usage(self, tokens: int, user_id: str, endpoint: str):
        """Log token usage for user, endpoint, and organization."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        with self.lock:
            # Update user usage
            if user_id not in self.user_usage:
                self.user_usage[user_id] = {}
            if today not in self.user_usage[user_id]:
                self.user_usage[user_id][today] = 0
            self.user_usage[user_id][today] += tokens
            
            # Update endpoint usage
            if endpoint not in self.endpoint_usage:
                self.endpoint_usage[endpoint] = {}
            if today not in self.endpoint_usage[endpoint]:
                self.endpoint_usage[endpoint][today] = 0
            self.endpoint_usage[endpoint][today] += tokens
            
            # Update org usage
            if today not in self.org_usage:
                self.org_usage[today] = 0
            self.org_usage[today] += tokens
    
    def get_user_usage(self, user_id: str, days: int = 1) -> int:
        """Get user token usage for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.user_usage.get(user_id, {}).get(date, 0) for date in dates)
    
    def get_endpoint_usage(self, endpoint: str, days: int = 1) -> int:
        """Get endpoint token usage for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.endpoint_usage.get(endpoint, {}).get(date, 0) for date in dates)
    
    def get_org_usage(self, days: int = 1) -> int:
        """Get organization token usage for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.org_usage.get(date, 0) for date in dates)
    
    def _get_date_range(self, days: int) -> List[str]:
        """Get date strings for the last N days."""
        today = datetime.now()
        return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]


# Create a global token usage store
token_usage_store = TokenUsageStore()


class OpenAIUsageMonitor:
    """
    Monitor OpenAI API usage and enforce rate limits.
    """
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.org_id = OPENAI_ORGANIZATION_ID
        self.usage_url = "https://api.openai.com/v1/usage"
    
    def get_usage_stats(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get OpenAI API usage statistics for a date range.
        
        Args:
            start_date: Start date in format YYYY-MM-DD
            end_date: End date in format YYYY-MM-DD
            
        Returns:
            Dictionary with usage statistics
        """
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment")
            return {"error": "API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if self.org_id:
            headers["OpenAI-Organization"] = self.org_id
        
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        try:
            response = requests.get(
                self.usage_url,
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return {"error": f"API error: {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Error fetching OpenAI usage: {str(e)}")
            return {"error": str(e)}
    
    def get_today_usage(self) -> Dict[str, Any]:
        """
        Get OpenAI API usage statistics for today.
        
        Returns:
            Dictionary with usage statistics
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_usage_stats(today, today)


# Rate limiting decorator
def token_rate_limit(
    user_quota: int = DEFAULT_USER_TOKEN_QUOTA,
    endpoint_quota: int = DEFAULT_ENDPOINT_TOKEN_QUOTA,
    org_quota: int = DEFAULT_ORGANIZATION_TOKEN_QUOTA
):
    """
    Decorator to enforce token rate limits on API endpoints.
    
    Args:
        user_quota: Maximum tokens per user per day
        endpoint_quota: Maximum tokens per endpoint per day
        org_quota: Maximum tokens per organization per day
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request object based on typical FastAPI signature
            request = kwargs.get('request')
            if not request and args and hasattr(args[0], 'client'):
                request = args[0]
            
            # Extract user ID from request if available
            user_id = "anonymous"
            if request and hasattr(request, 'state') and hasattr(request.state, 'user'):
                user_id = request.state.user.id
            
            # Get endpoint path
            endpoint = request.url.path if request and hasattr(request, 'url') else "unknown"
            
            # Check if any quota is exceeded
            user_usage = token_usage_store.get_user_usage(user_id)
            endpoint_usage = token_usage_store.get_endpoint_usage(endpoint)
            org_usage = token_usage_store.get_org_usage()
            
            if user_usage >= user_quota:
                logger.warning(f"User token quota exceeded for {user_id}: {user_usage}/{user_quota}")
                from fastapi import HTTPException
                raise HTTPException(status_code=429, detail="Rate limit exceeded: User token quota")
            
            if endpoint_usage >= endpoint_quota:
                logger.warning(f"Endpoint token quota exceeded for {endpoint}: {endpoint_usage}/{endpoint_quota}")
                from fastapi import HTTPException
                raise HTTPException(status_code=429, detail="Rate limit exceeded: Endpoint token quota")
            
            if org_usage >= org_quota:
                logger.warning(f"Organization token quota exceeded: {org_usage}/{org_quota}")
                from fastapi import HTTPException
                raise HTTPException(status_code=429, detail="Rate limit exceeded: Organization token quota")
            
            # Call the original function
            response = await func(*args, **kwargs)
            
            # Estimate token usage from response (if possible)
            estimated_tokens = 0
            if hasattr(response, 'model_dump'):
                # Convert Pydantic model to dict
                response_data = response.model_dump()
            elif isinstance(response, dict):
                response_data = response
            else:
                response_data = {}
            
            # Extract token usage if available in response
            if 'token_usage' in response_data:
                estimated_tokens = response_data['token_usage']
            else:
                # Rough estimate based on response size
                response_json = json.dumps(response_data)
                # Very rough approximation: 1 token ≈ 4 characters
                estimated_tokens = len(response_json) // 4
            
            # Log the estimated token usage
            token_usage_store.log_usage(estimated_tokens, user_id, endpoint)
            
            return response
        
        return wrapper
    
    return decorator


# Utility function to monitor GPT model response tokens
def track_openai_usage(
    model: str, 
    prompt_tokens: int, 
    completion_tokens: int, 
    user_id: str = "anonymous",
    endpoint: str = "unknown"
):
    """
    Track OpenAI model usage.
    
    Args:
        model: OpenAI model name
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        user_id: User ID
        endpoint: API endpoint
    """
    total_tokens = prompt_tokens + completion_tokens
    token_usage_store.log_usage(total_tokens, user_id, endpoint)
    
    logger.info(
        f"OpenAI API usage: model={model}, prompt_tokens={prompt_tokens}, "
        f"completion_tokens={completion_tokens}, total_tokens={total_tokens}, "
        f"user={user_id}, endpoint={endpoint}"
    )
    
    return total_tokens