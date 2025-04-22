.PHONY: dev test format lint build clean observability help

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

# Start development environment
dev:
        docker compose up

# Run tests for all services
test:
        cd services/backend && poetry run pytest -v
        cd services/frontend && npm test

# Format code
format:
        cd services/backend && poetry run black .
        cd services/frontend && npm run format

# Lint code
lint:
        cd services/backend && poetry run ruff .
        cd services/frontend && npm run lint

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
