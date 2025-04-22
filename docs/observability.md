# Observability Infrastructure

This document outlines the observability infrastructure for the AI.VC platform.

## Overview

The observability infrastructure provides comprehensive monitoring, tracing, and alerting capabilities for all services in the platform. It consists of the following components:

- **Prometheus**: For metrics collection and storage
- **Grafana**: For metrics visualization and dashboards
- **Alertmanager**: For alert routing and notifications
- **Jaeger**: For distributed tracing

## Metrics Collection

All services expose a `/metrics` endpoint which provides Prometheus-compatible metrics. The metrics include:

- Request counts and rates
- Request durations (latency)
- Error rates
- In-progress requests
- OpenAI API usage (tokens and cost)
- GPU utilization (if enabled)

## Dashboards

The following Grafana dashboards are available:

1. **Services Overview**: Provides a high-level view of all services, including request rates, latency, error rates, and in-progress requests.
2. **Token Usage & Cost**: Shows OpenAI API usage, including token consumption rates, costs by model, and user-specific metrics.

## Alerting

Alerts are configured in Prometheus and routed through Alertmanager. The following alerts are defined:

- **HighLatency**: Triggers when P95 latency is above 500ms for more than 2 minutes
- **HighErrorRate**: Triggers when error rate is above 5% for more than 2 minutes
- **HighTokenCost**: Triggers when OpenAI API cost exceeds $5 per hour for more than 15 minutes
- **HighGPUUtilization**: Triggers when GPU utilization is above 90% for more than 5 minutes
- **HighGPUMemoryUsage**: Triggers when GPU memory usage is above 90% for more than 5 minutes
- **ServiceDown**: Triggers when a service is down for more than 1 minute

## Distributed Tracing

Distributed tracing is implemented using OpenTelemetry and Jaeger. Traces can be viewed in the Jaeger UI at `http://localhost:16686`.

## Integration

Services integrate with the observability infrastructure through the following libraries:

- `libs/observability/tracing.py`: For distributed tracing setup
- `libs/observability/metrics.py`: For metrics collection and exposition
- `libs/observability/alerting.py`: For alert configuration and management

## Setup Instructions

1. Start the observability stack:
   ```bash
   docker-compose up -d prometheus alertmanager grafana jaeger
   ```

2. Access the UIs:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)
   - Alertmanager: http://localhost:9093
   - Jaeger: http://localhost:16686

## Adding Observability to a Service

To add observability to a new service, follow these steps:

1. Import the necessary modules:
   ```python
   from libs.observability import setup_observability
   ```

2. Set up observability in your FastAPI app:
   ```python
   db_engine = get_engine()  # Get your SQLAlchemy engine
   setup_observability(
       app=app,
       db_engine=db_engine,
       service_name="your_service_name",
       enable_tracing=True,
       enable_metrics=True
   )
   ```

3. Add your service to the Prometheus scrape configuration in `infra/prometheus/prometheus.yml`.

## Custom Metrics

To add custom metrics to your service, use the Prometheus client library:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
request_counter = Counter('custom_requests_total', 'Total requests', ['endpoint'])
request_latency = Histogram('custom_request_duration_seconds', 'Request latency', ['endpoint'])
active_requests = Gauge('custom_requests_in_progress', 'Requests in progress', ['endpoint'])

# Use metrics in your code
@app.get("/example")
async def example_endpoint():
    request_counter.labels(endpoint="example").inc()
    with request_latency.labels(endpoint="example").time():
        # Your endpoint logic here
        result = await process_request()
    return result
```

## Notification Configuration

To configure notifications for alerts, modify the `infra/alertmanager/alertmanager.yml` file with your preferred notification channels (Slack, email, etc.).