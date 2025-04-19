# Development Guidelines

This document provides guidelines and instructions for developing within this polyglot monorepo.

## Tech Stack

### Backend
- **Python 3.12**: Core language for backend services
- **FastAPI**: Web framework for building APIs
- **SQLAlchemy**: ORM for database access
- **Poetry**: Dependency management
- **Pytest**: Testing framework
- **Ruff & Black**: Code formatting and linting

### Frontend
- **TypeScript**: Typed JavaScript
- **Next.js 14**: React framework for the frontend
- **ESLint & Prettier**: Code formatting and linting

### Infrastructure
- **Docker & Docker Compose**: Container management
- **PostgreSQL 16**: Relational database
- **Redis**: In-memory data store
- **Qdrant**: Vector database
- **Minio**: S3-compatible object storage

## Local Development

### Prerequisites

Ensure you have the following installed:

- Docker and Docker Compose
- Python 3.12+
- Node.js 18+
- Poetry

### Setup Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Start the development environment:
   ```bash
   make dev
   ```

   This will start all services defined in `docker-compose.yml`.

### Development Workflow

#### Backend Development

1. Backend code is located in the `/services/backend` directory.

2. Install Python dependencies:
   ```bash
   cd services/backend
   poetry install
   ```

3. Run tests:
   ```bash
   poetry run pytest
   ```

4. Format code:
   ```bash
   poetry run black .
   poetry run ruff --fix .
   ```

#### Frontend Development

1. Frontend code is located in the `/services/frontend` directory.

2. Install Node.js dependencies:
   ```bash
   cd services/frontend
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Format code:
   ```bash
   npm run lint
   ```

## Working with Databases

### PostgreSQL

- Connection details are set via environment variables (see `docker-compose.yml`).
- Database migrations are handled through SQLAlchemy.

### Connecting to Databases

- **PostgreSQL**: `postgresql://${PGUSER}:${PGPASSWORD}@postgres:5432/${PGDATABASE}`
- **Redis**: `redis://redis:6379/0`
- **Qdrant**: `http://qdrant:6333`
- **Minio**: `minio:9000` (Access Key: `minio`, Secret Key: `minio123`)

## CI/CD Pipeline

The repository uses GitHub Actions for CI/CD:

1. On pull request:
   - Run tests
   - Lint code

2. On merge to main:
   - Run tests
   - Lint code
   - Build Docker images
   - Push images to Docker Hub

## Adding a New Service

1. Create a new directory in `/services`.
2. Create a `Dockerfile` for the service.
3. Add the service to `docker-compose.yml`.
4. Update the `Makefile` to include commands for the new service.
