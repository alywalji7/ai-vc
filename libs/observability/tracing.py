"""
OpenTelemetry tracing utilities for AI.VC services.

This module provides helper functions to set up OpenTelemetry tracing
with Jaeger exporter for all services in the platform.
"""

import os
from typing import Optional

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# FastAPI instrumentation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Instrumentations for common libraries
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor


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
    
    # Initialize instrumentations for common libraries
    RequestsInstrumentor().instrument()
    HTTPXInstrumentor().instrument()
    RedisInstrumentor().instrument()
    
    # Return the global tracer
    return trace.get_tracer(service_name)


def instrument_fastapi(app, service_name: str):
    """
    Instrument a FastAPI application with OpenTelemetry.
    
    Args:
        app: FastAPI application
        service_name: Name of the service
    """
    FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())


def instrument_sqlalchemy(engine, service_name: str):
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


def get_tracer(name: str):
    """
    Get a tracer for the given name.
    
    Args:
        name: Name for the tracer
        
    Returns:
        OpenTelemetry tracer
    """
    return trace.get_tracer(name)