"""
API endpoints for monitoring usage metrics.

This module provides FastAPI endpoints for monitoring:
1. Token usage (OpenAI API)
2. GPU usage (NVIDIA DCGM)
3. Request count metrics
"""
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, Union
import json

# FastAPI imports
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import APIKeyHeader

# Import metering modules
from .openai_metering import token_usage_store, OpenAIUsageMonitor
from .gpu_metering import gpu_usage_store, GPUMonitor, GPU_ENABLED
from .rate_limiter import request_limiter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_KEYS = set(os.environ.get("ADMIN_API_KEYS", "").split(","))
METRICS_ENABLED = os.environ.get("METRICS_ENABLED", "true").lower() == "true"

# API key security
api_key_header = APIKeyHeader(name="X-API-Key")

# Create router
router = APIRouter(prefix="/metrics", tags=["metrics"])


# Admin API key verification
def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Verify API key for metrics endpoints.
    
    Args:
        api_key: API key from header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not API_KEYS or api_key in API_KEYS:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "ApiKey"},
    )


@router.get("/status")
async def metrics_status():
    """
    Get status of metrics collection.
    
    Returns:
        Status information
    """
    return {
        "metrics_enabled": METRICS_ENABLED,
        "token_monitoring": True,
        "gpu_monitoring": GPU_ENABLED,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/token-usage", dependencies=[Depends(verify_api_key)])
async def token_usage_metrics(user_id: Optional[str] = None, days: int = 1):
    """
    Get token usage metrics.
    
    Args:
        user_id: Filter by user ID (optional)
        days: Number of days to include
        
    Returns:
        Token usage metrics
    """
    if not METRICS_ENABLED:
        raise HTTPException(status_code=404, detail="Metrics not enabled")
    
    metrics = {}
    
    if user_id:
        # Get metrics for specific user
        user_usage = token_usage_store.get_user_usage(user_id, days)
        metrics["user"] = {
            "id": user_id,
            "token_usage": user_usage
        }
    else:
        # Get aggregate metrics
        users = set()
        endpoints = set()
        
        # Collect all users
        for user_id in token_usage_store.user_usage.keys():
            users.add(user_id)
        
        # Collect all endpoints
        for endpoint in token_usage_store.endpoint_usage.keys():
            endpoints.add(endpoint)
        
        # Get usage for each user
        user_metrics = []
        for user_id in users:
            user_usage = token_usage_store.get_user_usage(user_id, days)
            user_metrics.append({
                "id": user_id,
                "token_usage": user_usage
            })
        
        # Get usage for each endpoint
        endpoint_metrics = []
        for endpoint in endpoints:
            endpoint_usage = token_usage_store.get_endpoint_usage(endpoint, days)
            endpoint_metrics.append({
                "endpoint": endpoint,
                "token_usage": endpoint_usage
            })
        
        # Get organization usage
        org_usage = token_usage_store.get_org_usage(days)
        
        metrics = {
            "users": user_metrics,
            "endpoints": endpoint_metrics,
            "organization": {
                "token_usage": org_usage
            }
        }
    
    metrics["time_range"] = {
        "days": days,
        "start_date": (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    return metrics


@router.get("/gpu-usage", dependencies=[Depends(verify_api_key)])
async def gpu_usage_metrics(user_id: Optional[str] = None, days: int = 1):
    """
    Get GPU usage metrics.
    
    Args:
        user_id: Filter by user ID (optional)
        days: Number of days to include
        
    Returns:
        GPU usage metrics
    """
    if not METRICS_ENABLED or not GPU_ENABLED:
        raise HTTPException(status_code=404, detail="GPU metrics not enabled")
    
    metrics = {}
    
    if user_id:
        # Get metrics for specific user
        memory_usage = gpu_usage_store.get_user_memory_usage(user_id, days)
        util_usage = gpu_usage_store.get_user_util_usage(user_id, days)
        metrics["user"] = {
            "id": user_id,
            "memory_usage_mb_seconds": memory_usage,
            "utilization_percent_seconds": util_usage
        }
    else:
        # Get aggregate metrics
        users = set()
        endpoints = set()
        
        # Collect all users
        for user_id in gpu_usage_store.user_memory_usage.keys():
            users.add(user_id)
        
        # Collect all endpoints
        for endpoint in gpu_usage_store.endpoint_memory_usage.keys():
            endpoints.add(endpoint)
        
        # Get usage for each user
        user_metrics = []
        for user_id in users:
            memory_usage = gpu_usage_store.get_user_memory_usage(user_id, days)
            util_usage = gpu_usage_store.get_user_util_usage(user_id, days)
            user_metrics.append({
                "id": user_id,
                "memory_usage_mb_seconds": memory_usage,
                "utilization_percent_seconds": util_usage
            })
        
        # Get usage for each endpoint
        endpoint_metrics = []
        for endpoint in endpoints:
            memory_usage = gpu_usage_store.get_endpoint_memory_usage(endpoint, days)
            util_usage = gpu_usage_store.get_endpoint_util_usage(endpoint, days)
            endpoint_metrics.append({
                "endpoint": endpoint,
                "memory_usage_mb_seconds": memory_usage,
                "utilization_percent_seconds": util_usage
            })
        
        metrics = {
            "users": user_metrics,
            "endpoints": endpoint_metrics,
        }
    
    metrics["time_range"] = {
        "days": days,
        "start_date": (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Add current GPU status
    gpu_monitor = GPUMonitor()
    current_metrics = gpu_monitor.get_gpu_metrics()
    metrics["current_status"] = current_metrics
    
    return metrics


@router.get("/request-counts", dependencies=[Depends(verify_api_key)])
async def request_count_metrics(user_id: Optional[str] = None):
    """
    Get request count metrics.
    
    Args:
        user_id: Filter by user ID (optional)
        
    Returns:
        Request count metrics
    """
    if not METRICS_ENABLED:
        raise HTTPException(status_code=404, detail="Metrics not enabled")
    
    metrics = {}
    
    if user_id:
        # Get metrics for specific user
        user_counts = {}
        
        if user_id in request_limiter.request_counts:
            for endpoint, minute_counts in request_limiter.request_counts[user_id].items():
                user_counts[endpoint] = sum(minute_counts.values())
        
        metrics["user"] = {
            "id": user_id,
            "request_counts": user_counts,
            "total_requests": sum(user_counts.values()) if user_counts else 0
        }
    else:
        # Get aggregate metrics
        user_metrics = []
        endpoint_totals = {}
        
        for user_id, endpoints in request_limiter.request_counts.items():
            user_counts = {}
            user_total = 0
            
            for endpoint, minute_counts in endpoints.items():
                count = sum(minute_counts.values())
                user_counts[endpoint] = count
                user_total += count
                
                # Update endpoint totals
                if endpoint not in endpoint_totals:
                    endpoint_totals[endpoint] = 0
                endpoint_totals[endpoint] += count
            
            user_metrics.append({
                "id": user_id,
                "request_counts": user_counts,
                "total_requests": user_total
            })
        
        # Convert endpoint totals to list
        endpoint_metrics = [
            {"endpoint": endpoint, "request_count": count}
            for endpoint, count in endpoint_totals.items()
        ]
        
        metrics = {
            "users": user_metrics,
            "endpoints": endpoint_metrics,
            "total_requests": sum(endpoint_totals.values()) if endpoint_totals else 0
        }
    
    metrics["timestamp"] = datetime.now().isoformat()
    metrics["note"] = "Request counts only include the current window (typically last 10 minutes)"
    
    return metrics


@router.get("/openai-usage", dependencies=[Depends(verify_api_key)])
async def openai_usage_metrics(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Get OpenAI API usage statistics.
    
    Args:
        start_date: Start date in format YYYY-MM-DD (defaults to today)
        end_date: End date in format YYYY-MM-DD (defaults to today)
        
    Returns:
        OpenAI API usage statistics
    """
    if not METRICS_ENABLED:
        raise HTTPException(status_code=404, detail="Metrics not enabled")
    
    # Set default dates if not provided
    if not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")
    
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    # Get OpenAI usage
    monitor = OpenAIUsageMonitor()
    usage_stats = monitor.get_usage_stats(start_date, end_date)
    
    return {
        "time_range": {
            "start_date": start_date,
            "end_date": end_date
        },
        "openai_usage": usage_stats
    }


@router.get("/current-gpu", dependencies=[Depends(verify_api_key)])
async def current_gpu_metrics():
    """
    Get current GPU metrics.
    
    Returns:
        Current GPU metrics
    """
    if not METRICS_ENABLED or not GPU_ENABLED:
        raise HTTPException(status_code=404, detail="GPU metrics not enabled")
    
    # Get GPU metrics
    gpu_monitor = GPUMonitor()
    metrics = gpu_monitor.get_gpu_metrics()
    
    # Try to get DCGM metrics if available
    try:
        dcgm_metrics = gpu_monitor.get_dcgm_metrics()
        if "error" not in dcgm_metrics:
            metrics["dcgm"] = dcgm_metrics
    except Exception as e:
        logger.warning(f"DCGM metrics not available: {str(e)}")
    
    return metrics