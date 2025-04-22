"""
Observability integration for the Radar service.

This module provides the setup for OpenTelemetry tracing and
Prometheus metrics for the Radar service.
"""
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from sqlalchemy.engine import Engine
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

logger = logging.getLogger(__name__)

# Prometheus metrics
HTTP_REQUEST_COUNTER = Counter(
    "http_requests_total", "Total number of HTTP requests", ["method", "endpoint", "status"]
)
HTTP_REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)
HTTP_REQUEST_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
)

# OpenAI token metrics
OPENAI_TOKEN_COUNTER = Counter(
    "openai_token_usage_total",
    "Total number of OpenAI API tokens used",
    ["model", "purpose"],
)

OPENAI_COST_COUNTER = Counter(
    "openai_cost_total",
    "Total cost of OpenAI API usage in USD",
    ["model", "purpose"],
)

# GPU metrics
GPU_MEMORY_GAUGE = Gauge(
    "nvidia_gpu_memory_used_bytes",
    "NVIDIA GPU memory used in bytes",
    ["gpu"],
)

GPU_MEMORY_TOTAL = Gauge(
    "nvidia_gpu_memory_total_bytes",
    "NVIDIA GPU total memory in bytes",
    ["gpu"],
)

GPU_UTILIZATION_GAUGE = Gauge(
    "nvidia_gpu_utilization",
    "NVIDIA GPU utilization percentage",
    ["gpu"],
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

    @staticmethod
    def get_route_path(request: Request) -> str:
        """
        Get the route path from the request.
        
        Args:
            request: The incoming request
            
        Returns:
            The route path
        """
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return route.path
        return request.url.path

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request through the middleware and record metrics.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or route handler
            
        Returns:
            Response from the application
        """
        path = self.get_route_path(request)
        
        # Skip metrics collection for excluded paths
        if path in self.exclude_paths:
            return await call_next(request)
        
        method = request.method
        
        # Track in-progress requests
        HTTP_REQUEST_IN_PROGRESS.labels(method=method, endpoint=path).inc()
        
        # Track request latency
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Record request count
            HTTP_REQUEST_COUNTER.labels(
                method=method, endpoint=path, status=status_code
            ).inc()
            
            # Record request latency
            HTTP_REQUEST_LATENCY.labels(method=method, endpoint=path).observe(
                time.perf_counter() - start_time
            )
            
            return response
        except Exception as e:
            status_code = 500
            # Record request count for exceptions
            HTTP_REQUEST_COUNTER.labels(
                method=method, endpoint=path, status=status_code
            ).inc()
            # Record request latency for exceptions
            HTTP_REQUEST_LATENCY.labels(method=method, endpoint=path).observe(
                time.perf_counter() - start_time
            )
            raise e
        finally:
            # Decrease in-progress counter
            HTTP_REQUEST_IN_PROGRESS.labels(method=method, endpoint=path).dec()


async def metrics_endpoint(request: Request):
    """
    Endpoint to expose Prometheus metrics.
    
    Args:
        request: The incoming request
        
    Returns:
        Response with Prometheus metrics in text format
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
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
    app.add_middleware(PrometheusMiddleware, exclude_paths=exclude_paths)
    app.add_route("/metrics", metrics_endpoint)
    logger.info("Prometheus metrics middleware registered")


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
    jaeger_host = jaeger_host or "jaeger"
    jaeger_port = jaeger_port or 14268
    
    try:
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        
        if debug:
            # Console exporter for local development
            provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        
        # Jaeger exporter for production
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        
        trace.set_tracer_provider(provider)
        logger.info(f"OpenTelemetry tracing set up for service {service_name}")
    except Exception as e:
        logger.error(f"Failed to set up OpenTelemetry tracing: {e}")


def instrument_fastapi(app: FastAPI, service_name: str):
    """
    Instrument a FastAPI application with OpenTelemetry.
    
    Args:
        app: FastAPI application
        service_name: Name of the service
    """
    try:
        FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())
        logger.info(f"FastAPI instrumentation set up for service {service_name}")
    except Exception as e:
        logger.error(f"Failed to instrument FastAPI: {e}")


def instrument_sqlalchemy(engine: Engine, service_name: str):
    """
    Instrument SQLAlchemy with OpenTelemetry.
    
    Args:
        engine: SQLAlchemy engine
        service_name: Name of the service
    """
    try:
        SQLAlchemyInstrumentor().instrument(
            engine=engine, tracer_provider=trace.get_tracer_provider()
        )
        logger.info(f"SQLAlchemy instrumentation set up for service {service_name}")
    except Exception as e:
        logger.error(f"Failed to instrument SQLAlchemy: {e}")


def setup_observability(
    app: FastAPI, 
    db_engine: Optional[Engine] = None,
    service_name: str = "radar",
    enable_tracing: bool = True,
    enable_metrics: bool = True,
) -> None:
    """
    Set up observability for the Radar service.
    
    Args:
        app: FastAPI application
        db_engine: SQLAlchemy engine (optional)
        service_name: Name of the service
        enable_tracing: Whether to enable OpenTelemetry tracing
        enable_metrics: Whether to enable Prometheus metrics
    """
    if enable_metrics:
        setup_prometheus_middleware(app, exclude_paths=["/metrics"])
    
    if enable_tracing:
        setup_tracing(service_name=service_name, debug=False)
        instrument_fastapi(app, service_name)
        
        if db_engine:
            instrument_sqlalchemy(db_engine, service_name)
    
    logger.info(f"{service_name} service initialized with observability")


def get_tracer(name: str):
    """
    Get a tracer for the given name.
    
    Args:
        name: Name for the tracer
        
    Returns:
        OpenTelemetry tracer
    """
    try:
        return trace.get_tracer(name)
    except Exception as e:
        logger.error(f"Failed to get tracer: {e}")
        return trace.get_tracer(__name__)