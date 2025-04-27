.PHONY: dev test format lint build clean observability seed_demo deploy_api help

# Default target
help:
        @echo "Available commands:"
        @echo "  make dev          - Start all services in development mode"
        @echo "  make test         - Run tests for all services"
        @echo "  make format       - Format code in all services"
        @echo "  make lint         - Lint code in all services"
        @echo "  make build        - Build Docker images"
        @echo "  make clean        - Remove Docker containers and volumes"
        @echo "  make observability - Start observability stack (Prometheus, Grafana, Jaeger)"
        @echo "  make seed_demo    - Run the data seeding demo to populate the knowledge graph"
        @echo "  make deploy_api   - Deploy API and worker services to Railway"

# Start development environment
dev:
        docker compose up

# Run tests for all services
test:
        cd services/api && poetry run pytest -v
        cd apps/portal && npm test

# Format code
format:
        cd services/api && poetry run black .
        cd apps/portal && npm run lint

# Lint code
lint:
        cd services/api && poetry run ruff .
        cd apps/portal && npm run lint

# Build Docker images
build:
        docker compose build

# Clean Docker resources
clean:
        docker compose down -v
        docker system prune -f

# Start observability stack
observability:
        docker compose up -d prometheus alertmanager grafana jaeger

# Run data seeding demo
seed_demo:
        @echo "Starting data seeding demo..."
        @cd services/graph_ingest && python seed_demo.py

# Deploy API and worker services to Railway
deploy_api:
        @echo "Deploying API and worker services to Railway..."
        @cd railway && railway up
