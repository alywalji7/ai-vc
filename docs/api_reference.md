# API Reference

This document provides a comprehensive reference for all API endpoints available in the AI.VC platform.

## Table of Contents

1. [Authentication](#authentication)
2. [Graph Ingest Service](#graph-ingest-service)
3. [Similarity API](#similarity-api)
4. [Deal-Flow Radar Service](#deal-flow-radar-service)
5. [Investment Committee Simulator](#investment-committee-simulator)
6. [Term Sheet Generator](#term-sheet-generator)
7. [Portfolio Telemetry Service](#portfolio-telemetry-service)
8. [Scheduler Service](#scheduler-service)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

## Authentication

All API endpoints require authentication using JWT tokens, with the exception of public-facing endpoints.

### Obtaining an API Token

```
POST /api/auth/token
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using Authentication

Include the token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Graph Ingest Service

Base URL: `/api/graph-ingest`

The Graph Ingest Service handles all data ingestion into the AI.VC platform, creating structured data and knowledge graphs from various sources.

```mermaid
sequenceDiagram
    participant Client
    participant API as Graph Ingest API
    participant Parser as Data Parser
    participant DB as PostgreSQL
    participant Vec as Vector DB
    participant Storage as Object Storage

    Client->>API: POST /companies
    API->>Parser: Parse company data
    Parser->>API: Normalized data
    API->>DB: Store structured data
    API->>Vec: Store document vectors
    API->>Storage: Store original files
    API->>Client: Success response
```

### Endpoints

#### Ingest Company Data

```
POST /api/graph-ingest/companies
```

Creates a new company entry with associated data.

**Request Body:**
```json
{
  "name": "Acme Inc",
  "website": "https://acme.example.com",
  "description": "Innovative startup focusing on AI-powered logistics",
  "founded_year": 2022,
  "location": "San Francisco, CA",
  "industry": "Logistics",
  "stage": "Seed",
  "team": [
    {
      "name": "Jane Doe",
      "role": "CEO",
      "linkedin": "https://linkedin.com/in/janedoe"
    },
    {
      "name": "John Smith",
      "role": "CTO",
      "linkedin": "https://linkedin.com/in/johnsmith"
    }
  ],
  "tags": ["AI", "Logistics", "Supply Chain"]
}
```

**Response:**
```json
{
  "id": "comp_123abc",
  "status": "success",
  "message": "Company data ingested successfully"
}
```

#### Upload Company Documents

```
POST /api/graph-ingest/companies/{company_id}/documents
```

Uploads documents (pitch decks, financial models, etc.) for a company.

**Request Body (multipart/form-data):**
- `document` (file): The document file
- `type` (string): Document type (e.g., "pitch_deck", "financial_model", "team_bios")
- `metadata` (string, optional): JSON string with additional metadata

**Response:**
```json
{
  "document_id": "doc_456def",
  "status": "success",
  "message": "Document uploaded and processed successfully"
}
```

#### Add Financial Data

```
POST /api/graph-ingest/companies/{company_id}/financials
```

Adds financial metrics and KPIs for a company.

**Request Body:**
```json
{
  "metrics": [
    {
      "name": "revenue",
      "value": 250000,
      "currency": "USD",
      "period": "2023-Q1"
    },
    {
      "name": "burn_rate",
      "value": 45000,
      "currency": "USD",
      "period": "2023-Q1"
    },
    {
      "name": "customer_count",
      "value": 12,
      "period": "2023-Q1"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Financial data added successfully"
}
```

## Similarity API

Base URL: `/api/similarity`

The Similarity API provides vector search capabilities over companies, documents, and other entities in the system.

### Endpoints

#### Semantic Search

```
POST /api/similarity/search
```

Searches for companies or documents using natural language queries.

**Request Body:**
```json
{
  "query": "AI startups in healthcare with strong revenue growth",
  "collection": "companies",
  "limit": 10,
  "filters": {
    "industry": ["Healthcare", "MedTech"],
    "stage": ["Seed", "Series A"]
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "company_id": "comp_789ghi",
      "name": "HealthAI Solutions",
      "similarity_score": 0.89,
      "founded_year": 2021,
      "stage": "Seed",
      "description": "AI-powered diagnostic tools for healthcare providers"
    },
    {
      "company_id": "comp_012jkl",
      "name": "MedMinds",
      "similarity_score": 0.82,
      "founded_year": 2020,
      "stage": "Series A",
      "description": "Machine learning platform for medical research acceleration"
    }
  ],
  "total_matches": 24
}
```

#### Find Similar Companies

```
GET /api/similarity/companies/{company_id}/similar
```

Finds companies similar to a reference company.

**Parameters:**
- `limit` (integer, optional): Maximum number of results (default: 10)
- `min_score` (float, optional): Minimum similarity score (0-1, default: 0.6)

**Response:**
```json
{
  "reference_company": {
    "id": "comp_123abc",
    "name": "Acme Inc"
  },
  "similar_companies": [
    {
      "id": "comp_345def",
      "name": "LogiTech Solutions",
      "similarity_score": 0.87,
      "common_factors": ["Industry", "Business Model", "Technology Stack"]
    },
    {
      "id": "comp_678ghi",
      "name": "ShipStream",
      "similarity_score": 0.75,
      "common_factors": ["Industry", "Target Market"]
    }
  ]
}
```

## Deal-Flow Radar Service

Base URL: `/api/radar`

The Deal-Flow Radar service provides algorithmic scoring and filtering of potential investments.

```mermaid
flowchart TD
    A[Client] -->|Request| B[Radar API]
    B -->|1. Apply filters| C{Rule-based\nFilters}
    C -->|Pass| D[ML Scoring]
    C -->|Fail| E[Return rejection]
    D -->|Calculate score| F[Score Analysis]
    F -->|Generate recommendation| G[Return results]
    G -->|Response| A
```

### Endpoints

#### Score Company

```
POST /api/radar/score
```

Scores a company based on available data.

**Request Body:**
```json
{
  "company_id": "comp_123abc",
  "include_details": true
}
```

**Response:**
```json
{
  "company_id": "comp_123abc",
  "company_name": "Acme Inc",
  "radar_score": 78.5,
  "confidence": 0.82,
  "recommendation": "Consider",
  "insights": [
    "Strong technical team with relevant background",
    "Addressing growing market with significant TAM",
    "Early traction shows product-market fit",
    "Burn rate is higher than average for stage"
  ],
  "factor_scores": {
    "team": 85,
    "market": 80,
    "traction": 75,
    "business_model": 70,
    "financials": 65
  },
  "comparable_companies": [
    {
      "id": "comp_456def",
      "name": "LogiTech",
      "score": 82.1
    }
  ]
}
```

#### Batch Score Companies

```
POST /api/radar/batch-score
```

Scores multiple companies in a single request.

**Request Body:**
```json
{
  "company_ids": ["comp_123abc", "comp_456def", "comp_789ghi"],
  "include_details": false
}
```

**Response:**
```json
{
  "results": [
    {
      "company_id": "comp_123abc",
      "company_name": "Acme Inc",
      "radar_score": 78.5,
      "recommendation": "Consider"
    },
    {
      "company_id": "comp_456def",
      "company_name": "LogiTech",
      "radar_score": 82.1,
      "recommendation": "Strong Consider"
    },
    {
      "company_id": "comp_789ghi",
      "company_name": "ShipStream",
      "radar_score": 63.2,
      "recommendation": "Pass"
    }
  ]
}
```

#### Get Model Information

```
GET /api/radar/model-info
```

Returns information about the current scoring model.

**Response:**
```json
{
  "model_version": "1.2.3",
  "trained_date": "2023-04-15",
  "evaluation_metrics": {
    "auc": 0.85,
    "precision": 0.78,
    "recall": 0.81
  },
  "feature_importance": [
    {"feature": "team_experience", "importance": 0.23},
    {"feature": "growth_rate", "importance": 0.19},
    {"feature": "market_size", "importance": 0.15}
  ]
}
```

## Investment Committee Simulator

Base URL: `/api/ic-sim`

The Investment Committee Simulator provides automated investment decisions with detailed reasoning.

### Endpoints

#### Simulate IC Decision

```
POST /api/ic-sim/decisions
```

Simulates an investment committee decision for a company.

**Request Body:**
```json
{
  "company_id": "comp_123abc",
  "additional_data": {
    "round_size": 2000000,
    "valuation_cap": 10000000,
    "user_notes": "Strong team with previous exits"
  }
}
```

**Response:**
```json
{
  "decision": "approve",
  "company_id": "comp_123abc",
  "company_name": "Acme Inc",
  "reasoning": "Acme Inc presents a compelling investment opportunity due to its experienced founding team, strong early traction, and innovative approach to the logistics market. The company's AI-powered platform addresses significant inefficiencies in supply chain management, with demonstrable cost savings for early customers.",
  "chain_of_thought": [
    {
      "factor": "Team",
      "analysis": "The founding team has relevant domain expertise and prior startup experience. The CEO successfully exited a previous logistics company, and the CTO has a strong technical background in AI and machine learning.",
      "score": 8.5
    },
    {
      "factor": "Market",
      "analysis": "The logistics optimization market is sizable ($15B) and growing at 14% annually. The specific segment Acme targets is underserved by current solutions.",
      "score": 8.0
    },
    {
      "factor": "Traction",
      "analysis": "The company has secured 3 enterprise pilots with positive feedback and one paying customer. Early metrics show a 22% efficiency improvement.",
      "score": 7.5
    },
    {
      "factor": "Competition",
      "analysis": "While there are established players, Acme's AI-first approach provides meaningful differentiation in accuracy and adaptability.",
      "score": 7.0
    },
    {
      "factor": "Economics",
      "analysis": "Current gross margins are 65% with potential to improve as the platform scales. The proposed valuation is reasonable for the stage and traction.",
      "score": 7.5
    }
  ],
  "decision_id": "ic_456def",
  "timestamp": "2023-04-22T14:32:45Z"
}
```

#### Get Decision History

```
GET /api/ic-sim/decisions
```

Retrieves historical investment committee decisions.

**Parameters:**
- `company_id` (string, optional): Filter by company
- `decision` (string, optional): Filter by decision ("approve", "reject", "revise")
- `limit` (integer, optional): Maximum number of results (default: 20)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response:**
```json
{
  "decisions": [
    {
      "decision_id": "ic_456def",
      "company_id": "comp_123abc",
      "company_name": "Acme Inc",
      "decision": "approve",
      "timestamp": "2023-04-22T14:32:45Z"
    },
    {
      "decision_id": "ic_789ghi",
      "company_id": "comp_456def",
      "company_name": "LogiTech",
      "decision": "revise",
      "timestamp": "2023-04-21T10:15:22Z"
    }
  ],
  "total_count": 42,
  "limit": 20,
  "offset": 0
}
```

## Term Sheet Generator

Base URL: `/api/term-sheet`

The Term Sheet Generator produces legal documents and handles term negotiation.

```mermaid
sequenceDiagram
    participant Investor as Investor
    participant API as Term Sheet API
    participant Generator as Document Generator
    participant Negotiator as Negotiation Engine
    participant Storage as Document Storage

    Investor->>API: Request term sheet
    API->>Generator: Generate document
    Generator->>Storage: Save document
    API->>Investor: Return term sheet URL

    Investor->>API: Open negotiation
    API->>Negotiator: Initialize negotiation
    
    loop Negotiation
        Investor->>API: Propose terms
        API->>Negotiator: Evaluate proposal
        Negotiator->>API: Response
        API->>Investor: Negotiation response
    end
    
    Investor->>API: Finalize terms
    API->>Generator: Generate final document
    Generator->>Storage: Save final document
    API->>Investor: Return final document URL
```

### Endpoints

#### Generate Term Sheet

```
POST /api/term-sheet/generate
```

Generates a term sheet for a company.

**Request Body:**
```json
{
  "company_id": "comp_123abc",
  "investment_amount": 500000,
  "instrument_type": "safe",
  "valuation_cap": 10000000,
  "discount_rate": 20,
  "pro_rata_rights": true,
  "board_seats": 1,
  "custom_terms": {
    "information_rights": "quarterly financial reports",
    "closing_deadline": "30 days from term sheet signing"
  }
}
```

**Response:**
```json
{
  "term_sheet_id": "ts_123abc",
  "company_name": "Acme Inc",
  "document_url": "https://aivc.example.com/documents/ts_123abc.pdf",
  "status": "generated",
  "expiration_date": "2023-05-22T00:00:00Z",
  "key_terms": {
    "investment_amount": "$500,000",
    "instrument_type": "SAFE",
    "valuation_cap": "$10,000,000",
    "discount_rate": "20%"
  }
}
```

#### Start Negotiation

```
POST /api/term-sheet/{term_sheet_id}/negotiate
```

Starts a negotiation session for a term sheet.

**Request Body:**
```json
{
  "participant_emails": [
    "investor@example.com",
    "founder@acme.example.com"
  ],
  "message": "I'm excited to discuss the investment terms. Please see the attached term sheet."
}
```

**Response:**
```json
{
  "negotiation_id": "neg_456def",
  "term_sheet_id": "ts_123abc",
  "status": "active",
  "websocket_url": "wss://aivc.example.com/ws/negotiations/neg_456def",
  "participants": [
    {
      "email": "investor@example.com",
      "role": "investor"
    },
    {
      "email": "founder@acme.example.com",
      "role": "founder"
    }
  ]
}
```

#### Get Negotiation History

```
GET /api/term-sheet/negotiations/{negotiation_id}/history
```

Retrieves the history of a negotiation session.

**Response:**
```json
{
  "negotiation_id": "neg_456def",
  "term_sheet_id": "ts_123abc",
  "company_name": "Acme Inc",
  "status": "active",
  "messages": [
    {
      "sender": "investor@example.com",
      "timestamp": "2023-04-22T15:30:00Z",
      "content": "I'm excited to discuss the investment terms. Please see the attached term sheet.",
      "attachment_id": "ts_123abc"
    },
    {
      "sender": "founder@acme.example.com",
      "timestamp": "2023-04-22T16:05:22Z",
      "content": "Thanks for the term sheet. We'd like to discuss the valuation cap. We believe $12M is more appropriate given our recent traction.",
      "proposed_changes": {
        "valuation_cap": 12000000
      }
    },
    {
      "sender": "system",
      "timestamp": "2023-04-22T16:05:30Z",
      "content": "Analysis: The proposed valuation increase of 20% is within typical negotiation ranges. Recent comparable deals have seen valuations between $8M-$15M for companies at this stage and traction level."
    }
  ]
}
```

## Portfolio Telemetry Service

Base URL: `/api/telemetry`

The Portfolio Telemetry Service monitors and analyzes portfolio company performance.

### Endpoints

#### Get Company Metrics

```
GET /api/telemetry/companies/{company_id}/metrics
```

Retrieves performance metrics for a portfolio company.

**Parameters:**
- `period` (string, optional): Time period for metrics ("1m", "3m", "6m", "1y", "all", default: "all")
- `metrics` (string, optional): Comma-separated list of specific metrics to retrieve

**Response:**
```json
{
  "company_id": "comp_123abc",
  "company_name": "Acme Inc",
  "metrics": {
    "revenue": [
      {"period": "2023-01", "value": 78000},
      {"period": "2023-02", "value": 85000},
      {"period": "2023-03", "value": 92000}
    ],
    "customer_count": [
      {"period": "2023-01", "value": 12},
      {"period": "2023-02", "value": 15},
      {"period": "2023-03", "value": 18}
    ],
    "burn_rate": [
      {"period": "2023-01", "value": 45000},
      {"period": "2023-02", "value": 48000},
      {"period": "2023-03", "value": 50000}
    ],
    "runway_months": [
      {"period": "2023-01", "value": 10},
      {"period": "2023-02", "value": 9},
      {"period": "2023-03", "value": 8}
    ]
  },
  "health_indicators": {
    "revenue_growth": {
      "value": 17.9,
      "unit": "%",
      "status": "good"
    },
    "burn_multiple": {
      "value": 2.8,
      "status": "warning"
    },
    "runway": {
      "value": 8,
      "unit": "months",
      "status": "warning"
    }
  }
}
```

#### Get Portfolio Dashboard

```
GET /api/telemetry/portfolio/dashboard
```

Retrieves aggregated metrics and health indicators for the entire portfolio.

**Parameters:**
- `fund_id` (string, optional): Filter by specific fund
- `tags` (string, optional): Filter by company tags (comma-separated)

**Response:**
```json
{
  "portfolio_summary": {
    "company_count": 15,
    "total_invested": 12500000,
    "avg_growth_rate": 24.5,
    "health_distribution": {
      "excellent": 4,
      "good": 6,
      "warning": 3,
      "critical": 2
    }
  },
  "top_performers": [
    {
      "company_id": "comp_789ghi",
      "company_name": "HealthAI",
      "growth_rate": 58.3,
      "key_metric": "MRR",
      "key_metric_value": 125000
    },
    {
      "company_id": "comp_123abc",
      "company_name": "Acme Inc",
      "growth_rate": 42.1,
      "key_metric": "Customer Count",
      "key_metric_value": 18
    }
  ],
  "companies_at_risk": [
    {
      "company_id": "comp_012jkl",
      "company_name": "DataViz",
      "risk_factors": ["Short runway (3 months)", "Declining customer retention"],
      "follow_on_status": "Evaluating"
    }
  ],
  "follow_on_opportunities": [
    {
      "company_id": "comp_789ghi",
      "company_name": "HealthAI",
      "opportunity_factors": ["Strong growth", "Upcoming Series A", "Strategic partners"],
      "recommendation": "Consider pro-rata participation"
    }
  ]
}
```

#### Track Metric Update

```
POST /api/telemetry/companies/{company_id}/metrics
```

Updates tracking metrics for a portfolio company.

**Request Body:**
```json
{
  "metrics": [
    {
      "name": "revenue",
      "value": 98000,
      "period": "2023-04"
    },
    {
      "name": "customer_count",
      "value": 22,
      "period": "2023-04"
    },
    {
      "name": "burn_rate",
      "value": 52000,
      "period": "2023-04"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "metrics_updated": 3,
  "analysis": {
    "revenue_growth": "6.5% increase from previous month",
    "burn_rate": "4.0% increase from previous month",
    "customer_acquisition": "4 new customers (22.2% growth)"
  },
  "alerts": [
    {
      "type": "positive",
      "message": "Customer growth exceeding targets"
    }
  ]
}
```

## Scheduler Service

Base URL: `/api/scheduler`

The Scheduler Service manages recurring tasks and ETL workflows.

### Endpoints

#### Get Active Jobs

```
GET /api/scheduler/jobs
```

Lists all active scheduled jobs.

**Parameters:**
- `status` (string, optional): Filter by job status ("pending", "running", "completed", "failed")
- `type` (string, optional): Filter by job type

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "job_123abc",
      "name": "Daily financial data collection",
      "type": "data_collection",
      "schedule": "0 0 * * *",
      "next_run": "2023-04-23T00:00:00Z",
      "last_run": "2023-04-22T00:00:00Z",
      "last_status": "completed",
      "enabled": true
    },
    {
      "job_id": "job_456def",
      "name": "Weekly portfolio analysis",
      "type": "analysis",
      "schedule": "0 0 * * 1",
      "next_run": "2023-04-24T00:00:00Z",
      "last_run": "2023-04-17T00:00:00Z",
      "last_status": "completed",
      "enabled": true
    }
  ],
  "total_count": 8,
  "active_count": 7
}
```

#### Create Job

```
POST /api/scheduler/jobs
```

Creates a new scheduled job.

**Request Body:**
```json
{
  "name": "Monthly investor report generation",
  "description": "Generates investor reports for all portfolio companies",
  "schedule": "0 0 1 * *",
  "job_type": "report_generation",
  "target_service": "reporting",
  "payload": {
    "report_type": "investor_update",
    "format": "pdf",
    "recipients": ["investors@aivc.com"]
  },
  "retry_config": {
    "max_retries": 3,
    "retry_delay": 300
  }
}
```

**Response:**
```json
{
  "job_id": "job_789ghi",
  "name": "Monthly investor report generation",
  "status": "created",
  "schedule": "0 0 1 * *",
  "next_run": "2023-05-01T00:00:00Z",
  "created_at": "2023-04-22T16:45:30Z"
}
```

#### Job Status

```
GET /api/scheduler/jobs/{job_id}/status
```

Gets the status and history of a specific job.

**Response:**
```json
{
  "job_id": "job_123abc",
  "name": "Daily financial data collection",
  "current_status": "completed",
  "schedule": "0 0 * * *",
  "next_run": "2023-04-23T00:00:00Z",
  "execution_history": [
    {
      "execution_id": "exec_123",
      "start_time": "2023-04-22T00:00:00Z",
      "end_time": "2023-04-22T00:05:12Z",
      "status": "completed",
      "result": "Collected data for 15 companies"
    },
    {
      "execution_id": "exec_122",
      "start_time": "2023-04-21T00:00:00Z",
      "end_time": "2023-04-21T00:04:53Z",
      "status": "completed",
      "result": "Collected data for 15 companies"
    }
  ]
}
```

## Error Handling

All API endpoints follow a consistent error handling pattern:

### Error Response Format

```json
{
  "error": {
    "code": "invalid_request",
    "message": "The request is invalid or malformed",
    "details": "The 'company_id' field is required",
    "request_id": "req_123abc"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| `authentication_failed` | 401 | Authentication failed or token expired |
| `permission_denied` | 403 | User lacks required permissions |
| `resource_not_found` | 404 | Requested resource doesn't exist |
| `invalid_request` | 400 | Malformed request or invalid parameters |
| `rate_limit_exceeded` | 429 | API rate limit exceeded |
| `service_unavailable` | 503 | Service temporarily unavailable |
| `internal_error` | 500 | Unexpected server error |

## Rate Limiting

API endpoints are subject to rate limiting to ensure system stability. Rate limits are applied per API key and are based on a combination of:

1. Request count over time
2. Token consumption (for LLM-based endpoints)

### Rate Limit Headers

All API responses include rate limiting information in the headers:

- `X-RateLimit-Limit`: Maximum requests allowed in the current period
- `X-RateLimit-Remaining`: Number of requests left in the current period
- `X-RateLimit-Reset`: Time (in seconds) until the rate limit resets

### Rate Limit Tiers

| Tier | Requests per minute | Token limit per hour | Notes |
|------|---------------------|----------------------|-------|
| Free | 60 | 10,000 | Limited access to LLM features |
| Standard | 300 | 50,000 | Full access to all features |
| Enterprise | 1,000 | 200,000 | Customizable limits |

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded",
    "details": "Request limit of 60 per minute exceeded",
    "retry_after": 45
  }
}
```