# AI.VC System Architecture

## System Overview

AI.VC is a sophisticated investment decision support system designed to assist venture capital decision-making through a combination of rule-based filtering and AI-powered analysis. The system follows a polylith architecture pattern with multiple services that work together to provide a comprehensive investment platform.

## Directory Structure

The repository follows a polylith folder pattern:

- `/services`: Contains all microservices, each in its own folder
- `/libs`: Shared libraries and utilities used across services
- `/infra`: Infrastructure configuration files (Docker, K8s, etc.)
- `/docs`: Documentation files
- `/data`: Static data files and seed data
- `/scripts`: Utility scripts for development and operations
- `/playwright`: End-to-end tests using Playwright

## Services

1. **Data Ingestion & Knowledge Graph Service** (`/services/graph_ingest`)
   - Ingests data from various sources (GitHub, Crunchbase, etc.)
   - Builds a knowledge graph of company relationships
   - Provides APIs for querying the graph

2. **Event-Driven ETL Scheduler** (`/services/scheduler`)
   - Manages scheduled tasks with cron expressions
   - Handles task execution and tracking
   - Provides metrics for monitoring

3. **Vectorizer & Similarity API** (`/services/similarity_api`)
   - Embeds textual data for semantic search
   - Provides APIs for similarity queries
   - Supports code, text, and tabular data

4. **Deal-Flow Radar** (`/services/radar`)
   - Scores companies based on various metrics
   - Identifies high-potential investment opportunities
   - Provides trend analysis and visualizations

5. **Backend Service** (`/services/backend`)
   - Main API gateway for the frontend
   - Handles user authentication and authorization
   - Coordinates between other services

6. **Investment Committee Simulator** (`/services/ic_sim`)
   - Two-stage analysis process:
     1. Rule-based filtering (sector fit, round size, geography)
     2. LLM-based assessment using Tree-of-Thought reasoning
   - Provides detailed investment recommendations with rationale

7. **Term-Sheet Generator & Negotiator Bot** (`/services/term_sheet`)
   - Generates NVCA model documents using templates
   - Provides real-time negotiation via WebSocket API
   - Implements lane guards for extreme counter-offers

8. **Frontend Service** (`/services/frontend`)
   - Next.js 14 frontend with TypeScript
   - Provides user interface for all system features
   - Responsive design for desktop and mobile

## Technology Stack

- **Languages**: Python 3.11, TypeScript
- **Frameworks**: FastAPI, Next.js 14
- **Databases**: PostgreSQL 16
- **Caching & Messaging**: Redis
- **Vector Storage**: Qdrant
- **Object Storage**: Minio
- **AI Models**: OpenAI GPT-4o, Sentence Transformers
- **Testing**: pytest, Vitest, Playwright

## Architecture Diagrams

(Detailed architecture diagrams to be added)

## Development Setup

1. Clone the repository
2. Install Docker and Docker Compose
3. Run `make dev` to start all services
4. Access the frontend at `http://localhost:5000`

## QA Checklist

### Running Tests Locally

#### Backend Tests

Run pytest for all services:

```bash
# Run all tests
python -m pytest

# Run tests for a specific service
python -m pytest services/term_sheet/tests/

# Run tests with verbose output
python -m pytest -v
```

#### Frontend Tests

Run Vitest for component tests:

```bash
cd services/frontend
npm test
```

#### End-to-End Tests

Run Playwright tests:

```bash
# Install Playwright
npx playwright install --with-deps

# Start all services
make dev

# In another terminal, seed test data
python scripts/seed_fixtures.py

# Run all Playwright tests
npx playwright test

# Run a specific test file
npx playwright test playwright/08-negotiator.spec.ts

# Run tests with UI mode
npx playwright test --ui
```

### Continuous Integration

The CI pipeline runs three main jobs:

1. `backend-tests`: Runs pytest for all Python services
2. `frontend-tests`: Runs Vitest for the Next.js components
3. `e2e-tests`: Spins up the full stack and runs Playwright tests

All jobs must pass for a PR to be considered ready for merge.

### Manual Testing

For a comprehensive manual test:

1. Start all services with `make dev`
2. Seed fixture data with `python scripts/seed_fixtures.py`
3. Navigate to `http://localhost:5000`
4. Perform a click-through test of all main features:
   - View companies in the deal flow radar
   - Check the dataroom for `acme-inc`
   - Review IC simulation results
   - Test term sheet negotiation

### Performance Testing

(To be added)

## Deployment

(To be added)