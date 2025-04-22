# Knowledge Graph Metrics and Monitoring

This document describes the metrics and monitoring setup for the Knowledge Graph ingestion service.

## Available Metrics

The Knowledge Graph ingestion service exports the following Prometheus metrics:

### Counters

1. `github_ingest_success_total` - Total number of successful GitHub data ingestions
2. `crunchbase_ingest_success_total` - Total number of successful Crunchbase data ingestions
3. `ingest_failure_total` - Total number of failed data ingestions

### Gauges

1. `graph_entity_count` - Current number of entities in the knowledge graph, labeled by type
2. `graph_relationship_count` - Current number of relationships in the knowledge graph, labeled by type

## Accessing Metrics

Metrics are exposed via HTTP at the `/metrics` endpoint of the Graph Ingest service on port 8091:

```
http://localhost:8091/metrics
```

These metrics can be scraped by Prometheus and visualized in Grafana.

## Grafana Dashboard

A pre-configured Grafana dashboard is available at:

```
infra/grafana/dashboards/knowledge_graph_ingestion.json
```

To import this dashboard into Grafana:

1. Navigate to the Grafana UI
2. Click on "+" icon on the left sidebar
3. Select "Import" from the dropdown menu
4. Click "Upload JSON file" and select the dashboard JSON file
5. Select the appropriate Prometheus data source
6. Click "Import"

## Dashboard Panels

The Knowledge Graph Ingestion dashboard consists of the following panels:

### Summary Section

1. **Total Entities** - Shows the total number of entities in the knowledge graph
2. **Total Relationships** - Shows the total number of relationships in the knowledge graph
3. **Successful Ingestions** - Shows the total number of successful ingestions from all sources
4. **Failed Ingestions** - Shows the total number of failed ingestions

### Data Sources Section

1. **Ingestion Success Rate (per hour)** - Shows the rate of successful ingestions from different sources
2. **Distribution of Ingested Sources** - Shows the proportion of ingestions from different sources

### Entity Types Section

1. **Entity Count by Type** - Shows the number of entities in the knowledge graph, broken down by entity type
2. **Relationship Count by Type** - Shows the number of relationships in the knowledge graph, broken down by relationship type

## Data Seeding

The Knowledge Graph ingestion service includes a data seeding script that can be used to populate the knowledge graph with initial data. This script can be run using the following command:

```bash
make seed_demo
```

The script will:

1. Create sample company data in S3
2. Ingest companies from Crunchbase
3. Ingest top repositories from GitHub
4. Count the entities and relationships created
5. Print a summary of the ingestion results

## Automated Ingestion Schedule

The Knowledge Graph ingestion service automatically ingests data from various sources according to the following schedule:

- Crunchbase data is ingested daily at 2:00 AM
- GitHub data is ingested daily at 3:00 AM

These scheduled ingestions ensure that the knowledge graph stays up-to-date with the latest data from these sources.

## Monitoring Alerts

The following alert rules are recommended for monitoring the Knowledge Graph ingestion service:

1. **IngestFailureRate** - Alerts when the rate of failed ingestions exceeds a threshold
2. **NoRecentIngests** - Alerts when no successful ingestions have been recorded in the last 24 hours
3. **EntityCountDecrease** - Alerts when the total entity count decreases significantly

These alerts can be configured in Prometheus Alertmanager to notify the appropriate teams when issues arise with the Knowledge Graph ingestion service.