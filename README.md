# Polyglot Monorepo

A polyglot monorepo containing Python backend services, TypeScript/Next.js frontend, and containerized infrastructure.

## Project Overview

This project is a sophisticated AI-driven investment decision support system that combines advanced rule-based filtering with intelligent analysis techniques. The system consists of several microservices following a polylith architecture pattern:

1. **Data Ingestion & Knowledge Graph Service** - Ingests data from various sources to build a comprehensive knowledge graph
2. **Event-Driven ETL Scheduler** - Manages data processing tasks and schedules them for execution
3. **Vectorizer & Similarity API** - Provides embeddings and similarity search capabilities for content
4. **Deal-Flow Radar** - Scores and ranks potential investment opportunities
5. **Data-Room Auto-Builder** - Automatically generates data rooms for investments
6. **Due-Diligence Agent Framework** - Performs modular due diligence checks on potential investments
7. **Investment Committee Simulator** - Applies a two-stage process with rule-based filtering and LLM analysis
8. **Term-Sheet Generator & Negotiator** - Creates and negotiates term sheets, with human escalation capabilities
9. **Post-Investment Value-Add Agents** - Helps portfolio companies with recruiting, growth, and networking needs

## Repository Structure

```
├── services/               # All microservices
│   ├── backend/            # Main backend API
│   ├── frontend/           # Next.js frontend application
│   ├── graph_ingest/       # Data ingestion service
│   ├── ic_sim/             # Investment Committee simulator
│   ├── radar/              # Deal-flow radar scoring service
│   ├── scheduler/          # Event-driven ETL scheduler
│   ├── similarity_api/     # Vector embeddings service
│   ├── term_sheet/         # Term sheet generator and negotiator
│   └── value_add_agents/   # Post-investment value-add agents
├── libs/                   # Shared libraries
├── infra/                  # Infrastructure configuration
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── playwright/             # E2E tests
```

## Value-Add Agents

The Value-Add Agents are a suite of AI-powered services designed to help portfolio companies with various post-investment needs. These agents operate asynchronously by subscribing to dedicated Kafka topics.

### Architecture

The agents follow an event-driven microservice architecture:
- Subscribe to dedicated Kafka topics
- Process requests asynchronously
- Generate specific outputs based on agent type
- Communicate results through email

### Agent Types

1. **RecruitBot**
   - Helps portfolio companies hire top talent
   - Generates job descriptions and recruiting strategies
   - Responds to `new_hire_req` Kafka topic

2. **GrowthBot**
   - Creates A/B testing plans and growth strategies
   - Generates JSON files with detailed test specifications
   - Stores plans in the `/growth_plans` directory
   - Responds to `growth_goal` Kafka topic

3. **IntroBot**
   - Facilitates introductions to relevant industry contacts
   - Manages the introduction process with personalized emails
   - Responds to `intro_req` Kafka topic

### Usage

For local testing without a Kafka environment, use the simulation script:

> **Note:** The email functionality requires a `SENDGRID_API_KEY` environment variable. Without this key, emails will be logged to the console instead of sent.

```bash
cd services/value_add_agents
python simulate.py --agents growth_bot
```

### Example Output: AB Test Plan (GrowthBot)

```json
{
  "company_id": "123e4567-e89b-12d3-a456-426614174000",
  "company_name": "DataInsights AI",
  "test_id": "789e0123-e45b-67d8-a901-234567890000",
  "test_name": "Product-Led Growth Call-to-action Optimization",
  "created_at": "2025-04-20T12:00:00.000Z",
  "business_type": "saas",
  "focus_area": "acquisition",
  "growth_goal": "increase MRR by 30%",
  "hypothesis": "By optimizing our call-to-action buttons, we can increase Conversion Rate by 15.8%",
  "primary_metric": "Conversion Rate",
  "secondary_metrics": ["Click-Through Rate", "Sign-Up Rate"],
  "expected_improvement": "15.8%",
  "duration": "14 days",
  "traffic_allocation": {
    "control": 50,
    "variations": 50
  },
  "variations": [
    {
      "id": "A",
      "name": "Control",
      "description": "Current implementation without changes"
    },
    {
      "id": "B",
      "name": "Variation B",
      "description": "Test call-to-action buttons with optimized design"
    }
  ],
  "implementation_details": {
    "test_pages": ["Homepage", "Product Page", "Checkout Flow"],
    "user_segments": ["All Users", "New Visitors"],
    "technical_requirements": [
      "Implement tracking for all variations",
      "Ensure proper A/B test bucketing"
    ]
  },
  "success_criteria": {
    "statistical_significance": "95% confidence level",
    "minimum_sample_size": "Calculated based on expected improvement"
  }
}
```

