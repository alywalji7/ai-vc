# Data Ingestion & Knowledge Graph Service

This service is responsible for ingesting data from various sources and building a knowledge graph.

## Overview

The service ingests data from external sources like GitHub, Crunchbase, and others, normalizing it into entities and relationships and storing it in a property-graph schema in PostgreSQL.

## Features

- Data ingestion from multiple sources (GitHub, Crunchbase, etc.)
- Pluggable ingestor architecture for easy addition of new data sources
- Property graph schema for entities and relationships
- REST API for data ingestion and querying
- CLI for data ingestion

## Supported Data Sources

- GitHub: Organizations, users, repositories, and contributors
- Crunchbase: Companies, people, funding rounds, and investors
- (More sources coming soon)

## Data Model

The data is stored in a property graph schema with:

- **Entities**: Nodes in the graph (e.g., people, organizations, repositories)
- **Relationships**: Edges between entities (e.g., works_for, founded, contributes_to)

Each entity and relationship has a type, source, and properties.

## Usage

### CLI

```bash
# Ingest data from GitHub
python -m services.graph_ingest.cli ingest --source github --org openai

# Ingest data from Crunchbase
python -m services.graph_ingest.cli ingest --source crunchbase --company openai

# Start the API server
python -m services.graph_ingest.cli server
```

### API

```bash
# Start the API server
python -m services.graph_ingest.main
```

Once the server is running, you can access the API at:

- API root: http://localhost:8080/
- API docs: http://localhost:8080/docs

## API Endpoints

- `GET /`: Root endpoint with service info
- `GET /health`: Health check endpoint
- `POST /api/ingest`: Ingest data from a source
- `GET /api/entities`: Get entities from the knowledge graph
- `GET /api/relationships`: Get relationships from the knowledge graph

## Configuration

The service uses the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `HOST`: Host to listen on (default: 0.0.0.0)
- `PORT`: Port to listen on (default: 8080)
- `GITHUB_API_TOKEN`: GitHub API token (optional)
- `CRUNCHBASE_API_KEY`: Crunchbase API key (optional)

## Development

### Requirements

- Python 3.11+
- PostgreSQL 16+

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest tests/
```

### Directory Structure

- `app/`: Main application code
  - `api/`: FastAPI application and routes
  - `db/`: Database models and operations
  - `ingestors/`: Data ingestion logic
  - `models/`: Data models
- `tests/`: Unit tests
- `cli.py`: Command-line interface
- `main.py`: Application entry point