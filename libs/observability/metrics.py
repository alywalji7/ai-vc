"""
Prometheus metrics utilities for AI.VC services.

This module provides helper functions to set up Prometheus metrics
for all services in the platform.
"""

import time
from typing import Callable, Dict, List, Optional

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Gauge, Histogram, Summary, REGISTRY, CONTENT_TYPE_LATEST
from prometheus_client.exposition import generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Route

# Standard metrics that will be available in all services
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"]
)

TOKEN_USAGE = Counter(
    "token_usage_total",
    "Total number of tokens used",
    ["model", "user_id", "type"]
)

INFERENCE_LATENCY = Summary(
    "model_inference_duration_seconds",
    "Model inference latency in seconds",
    ["model", "operation"]
)

ERROR_COUNT = Counter(
    "error_count_total",
    "Total number of errors",
    ["service", "type", "status_code"]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for FastAPI requests."""
    
    def __init__(self, app: FastAPI, exclude_paths: Optional[List[str]] = None):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application
            exclude_paths: List of paths to exclude from metrics collection
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request through the middleware and record metrics.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or route handler
            
        Returns:
            Response from the application
        """
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Extract route pattern, defaulting to the path if no matching route
        route_pattern = request.url.path
        for route in request.app.routes:
            if isinstance(route, Route) and route.path_regex.match(request.url.path):
                route_pattern = route.path
                break
        
        method = request.method
        
        # Increment in-progress gauge
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=route_pattern).inc()
        
        # Time the request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Record exceptions and re-raise
            status_code = 500
            ERROR_COUNT.labels(
                service="http", 
                type=type(e).__name__, 
                status_code=status_code
            ).inc()
            raise
        finally:
            # Record request duration
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(
                method=method, 
                endpoint=route_pattern
            ).observe(duration)
            
            # Decrement in-progress gauge
            REQUESTS_IN_PROGRESS.labels(
                method=method, 
                endpoint=route_pattern
            ).dec()
        
        # Count request by method, endpoint, and status
        REQUEST_COUNT.labels(
            method=method, 
            endpoint=route_pattern, 
            status=status_code
        ).inc()
        
        return response


async def metrics_endpoint():
    """
    Endpoint to expose Prometheus metrics.
    
    Returns:
        Response with Prometheus metrics in text format
    """
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )


def setup_prometheus_middleware(
    app: FastAPI, 
    exclude_paths: Optional[List[str]] = None
) -> None:
    """
    Set up Prometheus middleware and metrics endpoint.
    
    Args:
        app: FastAPI application
        exclude_paths: List of paths to exclude from metrics (e.g., "/metrics")
    """
    # Default to excluding the metrics endpoint
    exclude_paths = exclude_paths or ["/metrics"]
    
    # Add the middleware
    app.add_middleware(
        PrometheusMiddleware,
        exclude_paths=exclude_paths
    )
    
    # Add metrics endpoint
    app.add_route("/metrics", metrics_endpoint)


def record_token_usage(model: str, user_id: str, token_type: str, count: int) -> None:
    """
    Record token usage for a model.
    
    Args:
        model: Name of the model
        user_id: ID of the user
        token_type: Type of tokens (e.g., "prompt", "completion")
        count: Number of tokens used
    """
    TOKEN_USAGE.labels(
        model=model,
        user_id=user_id,
        type=token_type
    ).inc(count)


def time_model_inference(model: str, operation: str) -> Callable:
    """
    Create a decorator to time model inference.
    
    Args:
        model: Name of the model
        operation: Type of operation (e.g., "embedding", "completion")
        
    Returns:
        Decorator function that times the decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            INFERENCE_LATENCY.labels(
                model=model,
                operation=operation
            ).observe(duration)
            return result
        return wrapper
    return decorator


def record_error(service: str, error_type: str, status_code: int = 500) -> None:
    """
    Record an error.
    
    Args:
        service: Name of the service or component
        error_type: Type of error
        status_code: HTTP status code (if applicable)
    """
    ERROR_COUNT.labels(
        service=service,
        type=error_type,
        status_code=status_code
    ).inc()