"""
Observability integration for the backend service.

This module provides the setup for OpenTelemetry tracing and
Prometheus metrics for the backend service.
"""

import os
import time
from typing import Callable, List, Optional

from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from prometheus_client import Counter, Gauge, Histogram, CONTENT_TYPE_LATEST, REGISTRY
from prometheus_client.exposition import generate_latest
from sqlalchemy.engine import Engine
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


async def metrics_endpoint(request: Request):
    """
    Endpoint to expose Prometheus metrics.
    
    Args:
        request: The incoming request
        
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


def setup_tracing(
    service_name: str,
    jaeger_host: Optional[str] = None,
    jaeger_port: Optional[int] = None,
    debug: bool = False,
) -> None:
    """
    Set up OpenTelemetry tracing for a service.
    
    Args:
        service_name: Name of the service to be used in traces
        jaeger_host: Hostname of the Jaeger collector (defaults to 'jaeger')
        jaeger_port: Port of the Jaeger collector (defaults to 14268)
        debug: Whether to enable debug logging to console
    """
    # Get Jaeger host/port from environment or use defaults
    jaeger_host = jaeger_host or os.getenv("JAEGER_HOST", "jaeger")
    jaeger_port = jaeger_port or int(os.getenv("JAEGER_PORT", "14268"))
    
    # Create a resource with service name
    resource = Resource.create({SERVICE_NAME: service_name})
    
    # Create and set tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Create Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=jaeger_port,
    )
    
    # Add processors to the tracer provider
    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    
    # Add console processor if debug mode
    if debug:
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    
    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)


def instrument_fastapi(app: FastAPI, service_name: str):
    """
    Instrument a FastAPI application with OpenTelemetry.
    
    Args:
        app: FastAPI application
        service_name: Name of the service
    """
    FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())


def instrument_sqlalchemy(engine: Engine, service_name: str):
    """
    Instrument SQLAlchemy with OpenTelemetry.
    
    Args:
        engine: SQLAlchemy engine
        service_name: Name of the service
    """
    SQLAlchemyInstrumentor().instrument(
        engine=engine,
        service=service_name,
    )


def setup_observability(
    app: FastAPI, 
    db_engine: Optional[Engine] = None,
    service_name: str = "backend",
    enable_tracing: bool = True,
    enable_metrics: bool = True,
) -> None:
    """
    Set up observability for the backend service.
    
    Args:
        app: FastAPI application
        db_engine: SQLAlchemy engine (optional)
        service_name: Name of the service
        enable_tracing: Whether to enable OpenTelemetry tracing
        enable_metrics: Whether to enable Prometheus metrics
    """
    # Get environment variables
    jaeger_host = os.getenv("JAEGER_HOST", "jaeger")
    jaeger_port = int(os.getenv("JAEGER_PORT", "14268"))
    debug_tracing = os.getenv("DEBUG_TRACING", "false").lower() == "true"
    
    # Setup tracing if enabled
    if enable_tracing:
        # Setup OpenTelemetry tracing
        setup_tracing(
            service_name=service_name,
            jaeger_host=jaeger_host,
            jaeger_port=jaeger_port,
            debug=debug_tracing,
        )
        
        # Instrument FastAPI
        instrument_fastapi(app, service_name)
        
        # Instrument SQLAlchemy if engine is provided
        if db_engine is not None:
            instrument_sqlalchemy(db_engine, service_name)
    
    # Setup Prometheus metrics if enabled
    if enable_metrics:
        setup_prometheus_middleware(app, exclude_paths=["/metrics", "/health"])