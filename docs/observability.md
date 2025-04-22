# Observability Infrastructure

This document describes the observability infrastructure of the AI.VC platform, including metrics collection, distributed tracing, alerting, and dashboard configurations.

## Overview

The AI.VC platform implements a comprehensive observability stack that includes:

1. **Metrics Collection**: Using Prometheus for time-series metrics
2. **Distributed Tracing**: Using Jaeger for end-to-end request tracing
3. **Alerting**: Using Alertmanager for notification and escalation
4. **Dashboards**: Using Grafana for visualization and analysis

```mermaid
graph TB
    subgraph Services
        BE["Backend Service"]
        GI["Graph Ingest Service"]
        SA["Similarity API"]
        R["Radar Service"]
        ICS["IC Simulator"]
        TSG["Term Sheet Generator"]
        PT["Portfolio Telemetry"]
    end
    
    subgraph Observability
        Prom["Prometheus"]
        Jaeger["Jaeger"]
        AlertMgr["Alert Manager"]
        Grafana["Grafana"]
    end
    
    subgraph Notification
        Email["Email"]
        Slack["Slack"]
        PagerDuty["PagerDuty"]
    end
    
    BE --> Prom
    GI --> Prom
    SA --> Prom
    R --> Prom
    ICS --> Prom
    TSG --> Prom
    PT --> Prom
    
    BE --> Jaeger
    GI --> Jaeger
    SA --> Jaeger
    R --> Jaeger
    ICS --> Jaeger
    TSG --> Jaeger
    PT --> Jaeger
    
    Prom --> AlertMgr
    AlertMgr --> Email
    AlertMgr --> Slack
    AlertMgr --> PagerDuty
    
    Prom --> Grafana
    Jaeger --> Grafana
```

## Metrics Collection

### Prometheus Configuration

Prometheus is configured to scrape metrics from all services every 15 seconds. The configuration is defined in `infra/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  scrape_timeout: 10s

rule_files:
  - "rules/alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "backend-service"
    static_configs:
      - targets: ["backend:8000"]
    metrics_path: "/metrics"

  - job_name: "radar-service"
    static_configs:
      - targets: ["radar:8050"]
    metrics_path: "/metrics"

  - job_name: "ic-simulator-service"
    static_configs:
      - targets: ["ic-sim:8060"]
    metrics_path: "/metrics"

  - job_name: "term-sheet-service"
    static_configs:
      - targets: ["term-sheet:8070"]
    metrics_path: "/metrics"

  - job_name: "similarity-api-service"
    static_configs:
      - targets: ["similarity-api:8090"]
    metrics_path: "/metrics"

  - job_name: "graph-ingest-service"
    static_configs:
      - targets: ["graph-ingest:8080"]
    metrics_path: "/metrics"

  - job_name: "telemetry-service"
    static_configs:
      - targets: ["telemetry:8100"]
    metrics_path: "/metrics"

  - job_name: "node-exporter"
    static_configs:
      - targets: ["node-exporter:9100"]
```

### Service Metrics

Each service exposes the following standard metrics:

1. **Request Metrics**:
   - `http_requests_total{status, method, path}`: Total number of HTTP requests
   - `http_request_duration_seconds{status, method, path}`: Request duration histogram
   - `http_requests_in_progress{method, path}`: Gauge of in-progress requests

2. **Database Metrics**:
   - `database_connections{state}`: Number of database connections by state
   - `database_query_duration_seconds{operation}`: Database query duration histogram

3. **Cache Metrics**:
   - `cache_hits_total`: Cache hit counter
   - `cache_misses_total`: Cache miss counter
   - `cache_size_bytes`: Current cache size in bytes

4. **Business Metrics**:
   - Service-specific metrics relevant to business operations

### Custom AI Metrics

The AI-powered services (Radar, IC Simulator, Term Sheet Generator) expose additional metrics:

1. **Token Usage**:
   - `openai_tokens_total{model, endpoint}`: Total tokens consumed
   - `openai_tokens_prompt{model, endpoint}`: Prompt tokens consumed
   - `openai_tokens_completion{model, endpoint}`: Completion tokens consumed
   - `openai_requests_total{model, endpoint}`: Total API requests made
   - `openai_request_duration_seconds{model, endpoint}`: Request duration histogram

2. **Model Performance**:
   - `ml_model_prediction_duration_seconds{model}`: Prediction time histogram
   - `ml_model_version{model}`: Model version gauge
   - `ml_model_performance{model, metric}`: Model performance metrics

## Distributed Tracing

### Jaeger Configuration

Jaeger is used for distributed tracing, capturing spans across service boundaries to provide end-to-end visibility into request flows.

```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant Service as Backend Service
    participant DB as Database
    participant Jaeger as Jaeger

    Client->>API: Request
    activate API
    API->>Service: Process request
    activate Service
    Service->>DB: Query data
    activate DB
    DB-->>Service: Return data
    deactivate DB
    Service-->>API: Response
    deactivate Service
    API-->>Client: Response
    deactivate API
    
    Note over Client,Jaeger: All steps are traced
    API->>Jaeger: Report spans
    Service->>Jaeger: Report spans
    DB->>Jaeger: Report spans
```

### Trace Context Propagation

Trace context is propagated between services using the W3C Trace Context standard. Headers include:

- `traceparent`: Contains trace ID, span ID, and sampling flags
- `tracestate`: Optional vendor-specific information

### Trace Sampling

The tracing configuration uses an adaptive sampling strategy:

- 100% sampling for errors and slow requests
- 20% sampling for normal requests
- 5% sampling for high-volume endpoints

## Alerting

### Alert Rules

Alert rules are defined in `infra/prometheus/rules/alerts.yml`:

```yaml
groups:
  - name: service_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }} for the past 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (job, le)) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency on {{ $labels.job }}"
          description: "95th percentile latency is {{ $value }} seconds for the past 5 minutes"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "Service has been down for more than 1 minute"
          
      - alert: HighDatabaseConnectionCount
        expr: database_connections{state="active"} > 50
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connection count on {{ $labels.job }}"
          description: "Database has {{ $value }} active connections for the past 5 minutes"

  - name: token_usage_alerts
    rules:
      - alert: HighTokenRate
        expr: rate(openai_tokens_total[1h]) > 100000
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High token usage rate on {{ $labels.job }}"
          description: "Token usage rate is {{ $value | humanize }} tokens/hour for the past 15 minutes"

      - alert: TokenQuotaNearLimit
        expr: sum(increase(openai_tokens_total[24h])) by (job) > 4000000
        labels:
          severity: warning
        annotations:
          summary: "Token quota approaching limit on {{ $labels.job }}"
          description: "Token usage is {{ $value | humanize }} tokens in the past 24 hours (80% of daily quota)"

  - name: ml_model_alerts
    rules:
      - alert: ModelPerformanceDegradation
        expr: ml_model_performance{metric="auc"} < 0.7
        for: 1d
        labels:
          severity: warning
        annotations:
          summary: "Model performance degradation detected"
          description: "Model {{ $labels.model }} has AUC of {{ $value }} which is below threshold"

      - alert: ModelPredictionLatency
        expr: histogram_quantile(0.95, sum(rate(ml_model_prediction_duration_seconds_bucket[5m])) by (model, le)) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High model prediction latency"
          description: "Model {{ $labels.model }} has 95th percentile prediction time of {{ $value }} seconds"
```

### Alertmanager Configuration

Alertmanager is configured to route alerts based on severity and service. The configuration is defined in `infra/alertmanager/alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'

templates:
  - '/etc/alertmanager/template/*.tmpl'

route:
  group_by: ['alertname', 'job']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-notifications'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true
    - match:
        severity: warning
      receiver: 'slack-notifications'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'job']

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts'
        send_resolved: true
        icon_url: 'https://avatars3.githubusercontent.com/u/3380462'
        title: '{{ template "slack.default.title" . }}'
        text: '{{ template "slack.default.text" . }}'
        footer: '{{ template "slack.default.footer" . }}'
  
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '<pagerduty-service-key>'
        send_resolved: true
```

### Notification Templates

Slack notification templates are defined in `infra/alertmanager/template/slack.tmpl`:

```
{{ define "slack.default.title" }}
[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .CommonLabels.alertname }}
{{ end }}

{{ define "slack.default.text" }}
{{ range .Alerts }}
*Alert:* {{ .Annotations.summary }}
*Description:* {{ .Annotations.description }}
*Severity:* {{ .Labels.severity }}
*Service:* {{ .Labels.job }}
*Started:* {{ .StartsAt | since }}
{{ end }}
{{ end }}

{{ define "slack.default.footer" }}
AI.VC Alertmanager
{{ end }}
```

## Dashboards

### Service Dashboard

The main service dashboard visualizes the health and performance of all services. Dashboard configuration is stored in `infra/grafana/dashboards/service_dashboard.json`.

Key panels include:

1. **Service Status**:
   - Uptime and health status for all services

2. **Request Performance**:
   - Request rate by service
   - Error rate by service
   - Latency percentiles (p50, p95, p99)

3. **Resource Usage**:
   - CPU usage by service
   - Memory usage by service
   - Database connection count

4. **Business Metrics**:
   - Companies analyzed per day
   - Investment decisions made
   - Term sheets generated

### Token Usage Dashboard

The token usage dashboard monitors OpenAI API consumption. Dashboard configuration is stored in `infra/grafana/dashboards/token_usage_dashboard.json`.

Key panels include:

1. **Token Consumption**:
   - Total tokens per hour by service
   - Token consumption by model
   - Prompt vs. completion token distribution

2. **Cost Analysis**:
   - Estimated cost per day
   - Cost per service
   - Cost trend over time

3. **Usage Patterns**:
   - Request rate by endpoint
   - Average tokens per request
   - Token usage heatmap by time of day

4. **Quota Management**:
   - Daily usage vs. quota
   - Projected monthly usage
   - Quota utilization percentage

## Integration in Services

### Metrics Middleware

The observability stack is integrated into FastAPI services using a custom middleware that:

1. Captures request metrics (count, duration, status)
2. Exposes Prometheus metrics endpoint
3. Creates and propagates trace context

Example middleware integration:

```python
from fastapi import FastAPI
from libs.observability.metrics import PrometheusMiddleware, metrics_endpoint
from libs.observability.tracing import setup_tracing

app = FastAPI()

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics_endpoint)

# Setup OpenTelemetry tracing
setup_tracing(
    service_name="my-service",
    jaeger_host="jaeger",
    jaeger_port=6831
)
```

### Business Metrics

Services add custom business metrics using the Prometheus client:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
investment_decisions = Counter(
    'investment_decisions_total', 
    'Total number of investment decisions', 
    ['decision']
)

analysis_duration = Histogram(
    'investment_analysis_duration_seconds',
    'Time spent analyzing investment opportunities',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

active_analyses = Gauge(
    'investment_analyses_in_progress',
    'Number of investment analyses currently in progress'
)

# Use metrics in code
def analyze_investment(company_id):
    active_analyses.inc()
    with analysis_duration.time():
        try:
            result = perform_analysis(company_id)
            investment_decisions.labels(decision=result.decision).inc()
            return result
        finally:
            active_analyses.dec()
```

### Token Usage Tracking

AI services track token usage with an OpenAI client wrapper:

```python
from prometheus_client import Counter
from openai import OpenAI

# Define metrics
tokens_total = Counter(
    'openai_tokens_total',
    'Total number of OpenAI API tokens consumed',
    ['model', 'endpoint']
)

# OpenAI client wrapper
class InstrumentedOpenAI:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)
    
    def chat_completion(self, model, messages, endpoint):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        # Track token usage
        tokens_total.labels(
            model=model,
            endpoint=endpoint
        ).inc(response.usage.total_tokens)
        
        return response
```

## Development and Testing

### Local Setup

To run the observability stack locally:

```bash
# Start the observability stack
make start-observability

# View Grafana dashboards
open http://localhost:3000

# View Jaeger traces
open http://localhost:16686

# View Prometheus metrics
open http://localhost:9090

# View Alertmanager UI
open http://localhost:9093
```

### Testing Alerting

To test the alerting system:

```bash
# Trigger a test alert
curl -X POST http://localhost:9090/api/v1/admin/alerts \
  -d '{
    "alerts": [
      {
        "labels": {
          "alertname": "TestAlert",
          "severity": "critical",
          "job": "test"
        },
        "annotations": {
          "summary": "This is a test alert",
          "description": "This alert was manually triggered for testing purposes"
        },
        "generatorURL": "http://localhost:9090"
      }
    ]
  }'
```

## Best Practices

### Metric Naming

Metric names follow the Prometheus best practices:

- Use snake_case for metric names
- Use a prefix for application-specific metrics
- Include units in the metric name (e.g. `_seconds`, `_bytes`)
- Use total suffix for counters (e.g. `http_requests_total`)

### Alert Design

Alerts are designed to be:

- **Actionable**: Every alert should require a human response
- **Accurate**: Minimize false positives
- **Clear**: Alert messages should clearly describe the problem
- **Unique**: Avoid duplicate alerts for the same issue
- **Prioritized**: Use severity levels to indicate urgency

### Runbook References

Critical alerts include links to runbooks in the alert annotation:

```yaml
annotations:
  summary: "Service is down"
  description: "Service has been down for more than 1 minute"
  runbook: "https://ai.vc/docs/runbooks/service-down.md"
```

## Future Improvements

1. **Log Aggregation**: Add centralized logging with Elasticsearch, Fluentd, and Kibana (EFK stack)
2. **Custom Anomaly Detection**: Implement ML-based anomaly detection for metrics
3. **Service Level Objectives (SLOs)**: Define and monitor SLOs for key services
4. **Advanced Dashboards**: Create executive dashboards for business metrics
5. **Auto-remediation**: Implement automatic remediation for common issues