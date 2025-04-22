# AI.VC Platform Architecture

This document provides a comprehensive overview of the AI.VC platform architecture, detailing the system components, data flows, and integration points.

## System Overview

AI.VC is an advanced AI-driven investment decision support system that combines sophisticated rule-based filtering with intelligent analysis techniques. The platform is designed to help venture capital firms streamline their investment process, from deal sourcing to portfolio monitoring.

```mermaid
graph TB
    subgraph Frontend
        LP["LP Portal<br/>(Next.js)"]
    end
    
    subgraph Core_Services
        GI["Graph Ingest<br/>Service"]
        SA["Similarity API"]
        R["Radar<br/>Scoring Service"]
        ICS["Investment Committee<br/>Simulator"]
        TSG["Term Sheet<br/>Generator"]
        PT["Portfolio<br/>Telemetry"]
    end
    
    subgraph Infrastructure
        DB[(PostgreSQL)]
        Vector[(Qdrant<br/>Vector DB)]
        ObjStore[(MinIO<br/>Object Storage)]
        Redis[(Redis)]
        Kafka[(Kafka)]
    end
    
    subgraph ML_Ops
        MLflow["MLflow<br/>Tracking Server"]
        Models[(Model Registry)]
    end
    
    subgraph Observability
        Prometheus["Prometheus"]
        Grafana["Grafana"]
        Jaeger["Jaeger<br/>Tracing"]
        AlertMgr["Alert Manager"]
    end
    
    LP --> GI
    LP --> SA
    LP --> R
    LP --> ICS
    LP --> TSG
    LP --> PT
    
    GI --> DB
    GI --> Vector
    GI --> ObjStore
    GI --> Kafka
    
    SA --> Vector
    SA --> DB
    
    R --> DB
    R --> Models
    R --> MLflow
    
    ICS --> DB
    ICS --> ObjStore
    
    TSG --> DB
    TSG --> ObjStore
    
    PT --> DB
    PT --> Kafka
    
    R --> Prometheus
    ICS --> Prometheus
    TSG --> Prometheus
    PT --> Prometheus
    GI --> Prometheus
    SA --> Prometheus
    
    Prometheus --> Grafana
    Prometheus --> AlertMgr
    
    R --> Jaeger
    ICS --> Jaeger
    TSG --> Jaeger
    PT --> Jaeger
    GI --> Jaeger
    SA --> Jaeger
```

## Architecture Principles

The AI.VC platform follows these core architectural principles:

1. **Microservices Architecture**: The system is decomposed into specialized services that focus on specific business capabilities.
2. **Event-Driven Design**: Services communicate via events for asynchronous processing of long-running tasks.
3. **Polyglot Persistence**: Different data storage technologies are used based on the specific requirements of each service.
4. **AI-First Approach**: Machine learning and AI capabilities are integrated throughout the platform, not as bolt-on features.
5. **Observability by Design**: Comprehensive monitoring, tracing, and alerting are built into all services.
6. **Security and Compliance**: Regulatory requirements are addressed through purpose-built compliance middleware.

## Core Services

### 1. Graph Ingest Service

The Graph Ingest Service handles all data ingestion into the AI.VC platform, creating structured data and knowledge graphs from various sources.

```mermaid
flowchart TB
    subgraph "Graph Ingest Service"
        API["REST API"]
        Parsers["Data Parsers"]
        Enrichers["Data Enrichers"]
        GraphBuilder["Knowledge Graph Builder"]
        Validators["Data Validators"]
    end
    
    subgraph "External Sources"
        Web["Web Data"]
        Docs["Documents"]
        APIs["External APIs"]
        Manual["Manual Input"]
    end
    
    subgraph "Storage"
        DB[(PostgreSQL)]
        Vector[(Vector DB)]
        ObjStore[(Object Storage)]
    end
    
    Web --> API
    Docs --> API
    APIs --> API
    Manual --> API
    
    API --> Parsers
    Parsers --> Validators
    Validators --> Enrichers
    Enrichers --> GraphBuilder
    
    GraphBuilder --> DB
    GraphBuilder --> Vector
    Docs --> ObjStore
```

**Key Features**:
- Multi-format ingestion (spreadsheets, PDFs, web data)
- Automatic entity extraction and linking
- Knowledge graph construction
- Data validation and enrichment

### 2. Similarity API

The Similarity API provides vector search capabilities over companies, documents, and other entities in the system.

```mermaid
flowchart LR
    subgraph "Similarity API"
        API["REST API"]
        QueryProcessor["Query Processor"]
        VectorOperations["Vector Operations"]
        Filtering["Filtering Engine"]
        Ranking["Result Ranking"]
    end
    
    subgraph "Storage"
        Vector[(Vector DB)]
        DB[(PostgreSQL)]
    end
    
    Client --> API
    API --> QueryProcessor
    QueryProcessor --> VectorOperations
    VectorOperations --> Vector
    VectorOperations --> Filtering
    Filtering --> DB
    Filtering --> Ranking
    Ranking --> API
    API --> Client
```

**Key Features**:
- Semantic search across portfolios and companies
- Hybrid ranking (vector similarity + metadata filtering)
- Multi-modal search (text, numerical data, graphs)
- Configurable similarity thresholds

### 3. Deal-Flow Radar Service

The Radar service provides algorithmic scoring and filtering of potential investments.

```mermaid
flowchart TB
    subgraph "Radar Service"
        API["REST API"]
        RuleEngine["Rule Engine"]
        MLScoring["ML Scoring Models"]
        Explainer["Explanation Generator"]
        CostGuardrail["Cost Guardrails"]
    end
    
    subgraph "ML Ops"
        Training["Model Training Pipeline"]
        Evaluation["Model Evaluation"]
        Registry["Model Registry"]
        Scheduler["Training Scheduler"]
    end
    
    subgraph "Storage"
        DB[(PostgreSQL)]
        MLflow[(MLflow)]
    end
    
    Client --> API
    API --> CostGuardrail
    CostGuardrail --> RuleEngine
    RuleEngine --> MLScoring
    MLScoring --> Explainer
    Explainer --> API
    API --> Client
    
    Scheduler --> Training
    Training --> DB
    Training --> Evaluation
    Evaluation --> Registry
    Registry --> MLflow
    MLScoring --> Registry
```

**Key Features**:
- Two-stage filtering (rules + ML models)
- Explainable AI for investment recommendations
- Automatic model retraining with performance monitoring
- Cost guardrails for API usage

### 4. Investment Committee Simulator

The Investment Committee Simulator provides automated investment decisions with detailed reasoning.

```mermaid
flowchart TB
    subgraph "IC Simulator"
        API["REST API"]
        RuleFilter["Rule-Based Filter"]
        LLMAnalysis["LLM Analysis Engine"]
        ToT["Tree of Thought Processing"]
        Audit["Audit Logging"]
    end
    
    subgraph "External"
        OpenAI["OpenAI GPT-4o"]
    end
    
    subgraph "Storage"
        DB[(PostgreSQL)]
        ObjStore[(Audit Logs Storage)]
    end
    
    Client --> API
    API --> RuleFilter
    RuleFilter --> LLMAnalysis
    LLMAnalysis --> OpenAI
    OpenAI --> ToT
    ToT --> Audit
    Audit --> ObjStore
    ToT --> API
    API --> Client
```

**Key Features**:
- Two-stage decision process (rule filter + LLM analysis)
- Tree of Thought investment reasoning
- Detailed chain-of-thought documentation
- Audit trail for compliance

### 5. Term Sheet Generator & Negotiator

The Term Sheet Generator produces legal documents and handles term negotiation.

```mermaid
flowchart TB
    subgraph "Term Sheet Service"
        API["REST API"]
        DocGen["Document Generator"]
        WSServer["WebSocket Server"]
        Negotiator["Negotiation Engine"]
        Escalator["Escalation Handler"]
    end
    
    subgraph "External"
        Templates[("Document<br>Templates")]
        Slack["Slack<br>Integration"]
        OpenAI["OpenAI<br>GPT-4o"]
    end
    
    subgraph "Storage"
        DB[(PostgreSQL)]
        ObjStore[(Document<br>Storage)]
    end
    
    Client --> API
    API --> DocGen
    DocGen --> Templates
    DocGen --> ObjStore
    
    Client --> WSServer
    WSServer --> Negotiator
    Negotiator --> OpenAI
    Negotiator --> WSServer
    Negotiator --> Escalator
    Escalator --> Slack
    
    Negotiator --> DB
    DocGen --> DB
```

**Key Features**:
- NVCA-compliant document generation
- Real-time negotiation via WebSockets
- LLM-powered negotiation assistant
- Extreme counter-offer detection and escalation

### 6. Portfolio Telemetry Service

The Portfolio Telemetry Service tracks company performance metrics and identifies follow-on investment opportunities.

```mermaid
flowchart TB
    subgraph "Telemetry Service"
        API["REST API"]
        MetricsCollector["Metrics Collector"]
        Analyzer["Performance Analyzer"]
        Triggers["Follow-On Triggers"]
        Scheduler["Scheduled Tasks"]
    end
    
    subgraph "Decision Engines"
        RunwayEngine["Runway-Based Engine"]
        GrowthEngine["Growth-Based Engine"]
    end
    
    subgraph "Storage"
        DB[(PostgreSQL)]
        TimeSeries[(Time Series Data)]
    end
    
    Client --> API
    API --> MetricsCollector
    MetricsCollector --> DB
    MetricsCollector --> TimeSeries
    
    Scheduler --> Analyzer
    Analyzer --> DB
    Analyzer --> RunwayEngine
    Analyzer --> GrowthEngine
    
    RunwayEngine --> Triggers
    GrowthEngine --> Triggers
    Triggers --> API
```

**Key Features**:
- Automated data collection from portfolio companies
- Time-series tracking of key financial metrics
- Runway-based and growth-based follow-on triggers
- Portfolio health monitoring dashboard

### 7. Scheduler Service

The Scheduler Service manages recurring tasks and ETL workflows.

```mermaid
flowchart TB
    subgraph "Scheduler Service"
        API["REST API"]
        JobRegistry["Job Registry"]
        TaskScheduler["Task Scheduler"]
        ExecutionEngine["Execution Engine"]
        Retry["Retry Handler"]
    end
    
    subgraph "Task Types"
        DataTasks["Data Collection Tasks"]
        AnalysisTasks["Analysis Tasks"]
        ReportTasks["Reporting Tasks"]
    end
    
    subgraph "Infrastructure"
        DB[(PostgreSQL)]
        Kafka[(Kafka)]
    end
    
    Client --> API
    API --> JobRegistry
    JobRegistry --> DB
    
    TaskScheduler --> JobRegistry
    TaskScheduler --> ExecutionEngine
    ExecutionEngine --> DataTasks
    ExecutionEngine --> AnalysisTasks
    ExecutionEngine --> ReportTasks
    ExecutionEngine --> Retry
    Retry --> ExecutionEngine
    
    ExecutionEngine --> Kafka
```

**Key Features**:
- Cron-style scheduling of recurring tasks
- Event-driven task execution
- Retry logic with configurable backoff
- Task history and audit logging

## Infrastructure Components

### PostgreSQL Database

PostgreSQL serves as the primary relational database for the AI.VC platform:

- **Companies Table**: Core company information, financial data, and investment details
- **Deals Table**: Information about investment deals, terms, and statuses
- **Users Table**: User accounts, roles, and permissions
- **Audit Log Table**: Append-only audit log for compliance purposes
- **Metrics Table**: Time-series data for company performance tracking

### Qdrant Vector Database

Qdrant provides vector search capabilities for similarity matching:

- **Company Vectors**: Embeddings of company descriptions, business models, and pitches
- **Document Vectors**: Embeddings of documents, sections, and key paragraphs
- **Market Vectors**: Embeddings of market descriptions and trends
- **Founder Vectors**: Embeddings of founder profiles and backgrounds

### MinIO Object Storage

MinIO serves as the object storage solution for:

- **Documents**: Company pitch decks, financial models, and legal documents
- **AI Analysis Logs**: Complete logs of LLM-based analyses with chain-of-thought details
- **Generated Documents**: Term sheets, investment memos, and reports
- **Backups**: Database backups and configuration snapshots

### Redis

Redis provides in-memory storage for:

- **Caching**: API response caching and query result caching
- **Rate Limiting**: Tracking request counts for API rate limiting
- **Session Management**: User session data
- **Job Queues**: Lightweight task queues for background processing

### Kafka

Kafka enables event-driven communication between services:

- **Data Ingestion Events**: Notifications about new data being ingested
- **Analysis Events**: Triggers for analysis tasks based on new data
- **Follow-On Triggers**: Events related to potential follow-on investment opportunities
- **Compliance Events**: Events related to compliance checks and verifications

## ML & AI Components

### MLflow

MLflow provides tracking and management for machine learning:

- **Experiment Tracking**: Tracking of model training experiments
- **Model Registry**: Central repository for trained models
- **Model Versioning**: Versioning and promotion of models to production
- **Parameter Tracking**: Tracking of hyperparameters and training metrics

### OpenAI Integration

The platform integrates with OpenAI's models for:

- **Investment Analysis**: Tree-of-thought analysis of investment opportunities
- **Term Negotiation**: Assistance with term sheet negotiation
- **Document Analysis**: Extraction of key information from documents
- **Summarization**: Generation of executive summaries and reports

### Cost Guardrails

Cost control mechanisms for AI usage:

- **Rate Limiting**: Limits on the number of requests per time period
- **Token Metering**: Tracking and limiting of token usage
- **Batch Processing**: Batching of requests to optimize token usage
- **Fallback Strategies**: Less expensive alternatives for non-critical tasks

## Observability Stack

### Prometheus

Prometheus collects metrics from all services:

- **System Metrics**: CPU, memory, disk, and network usage
- **Application Metrics**: Request counts, error rates, and latencies
- **Business Metrics**: Investment volumes, deal flow, and portfolio performance
- **AI Metrics**: Token usage, model performance, and inference times

### Grafana

Grafana provides visualization of metrics and data:

- **Service Dashboards**: Real-time monitoring of service health
- **Token Usage Dashboards**: Tracking of AI token consumption
- **Investment Dashboards**: Visualizations of investment performance
- **Alert Dashboards**: Overview of triggered alerts and their statuses

### Jaeger

Jaeger enables distributed tracing:

- **Request Tracing**: End-to-end tracing of requests across services
- **Performance Analysis**: Identification of bottlenecks and performance issues
- **Error Tracking**: Tracing of error propagation across services
- **Dependency Mapping**: Visualization of service dependencies

### Alert Manager

Alert Manager handles alerting based on metric thresholds:

- **Service Alerts**: Notifications about service health issues
- **Cost Alerts**: Alerts for unusual token usage or cost spikes
- **Performance Alerts**: Notifications about performance degradation
- **Business Alerts**: Alerts related to investment opportunities or risks

## Security & Compliance Layer

### Investor Accreditation Verification

Ensures compliance with SEC regulations for accredited investors:

- **Verification API**: Interface for verifying investor accreditation status
- **Document Storage**: Secure storage of accreditation documentation
- **Renewal Tracking**: Monitoring of accreditation expiration dates
- **Audit Logs**: Records of all accreditation checks

### OFAC Sanctions Checking

Ensures compliance with sanctions regulations:

- **Name Screening**: Checking of names against sanctions lists
- **Risk Scoring**: Risk assessment based on name matches
- **False Positive Handling**: Processes for resolving false positives
- **Documentation**: Records of all sanctions checks

### Decision Payload Hashing

Ensures integrity of investment decisions:

- **SHA-256 Hashing**: Generation of secure hashes for decision payloads
- **Immutable Storage**: Storage of hashes in an append-only log
- **Verification API**: Interface for verifying decision integrity
- **Tamper Detection**: Mechanisms for detecting manipulation attempts

### Admin Override Functionality

Provides supervised exceptions to automated compliance checks:

- **Kill-Switch API**: Interface for overriding compliance checks
- **Role-Based Authorization**: Restriction of override capabilities to GPs
- **Audit Logging**: Detailed logging of all override actions
- **Justification Requirements**: Mandatory documentation of override reasons

## Data Flow Patterns

### Deal Sourcing Flow

```mermaid
sequenceDiagram
    participant User
    participant GI as Graph Ingest
    participant R as Radar
    participant S as Similarity API
    participant DB as Database
    participant Vector as Vector DB
    
    User->>GI: Submit new company data
    GI->>DB: Store structured data
    GI->>Vector: Store vector embeddings
    GI->>User: Confirmation
    
    User->>R: Request scoring
    R->>DB: Fetch company data
    R->>R: Apply rule filtering
    R->>R: Run ML scoring
    R->>User: Return score and insights
    
    User->>S: Search similar companies
    S->>Vector: Query vector database
    S->>DB: Apply filters
    S->>User: Return similar companies
```

### Investment Decision Flow

```mermaid
sequenceDiagram
    participant User
    participant R as Radar
    participant IC as IC Simulator
    participant TS as Term Sheet
    participant DB as Database
    participant ObjStore as Object Storage
    
    User->>R: Request detailed analysis
    R->>User: Return detailed scoring
    
    User->>IC: Submit for IC decision
    IC->>DB: Fetch company data
    IC->>IC: Apply rule filter
    IC->>IC: Run LLM analysis
    IC->>ObjStore: Store full analysis
    IC->>DB: Store decision
    IC->>User: Return decision with reasoning
    
    User->>TS: Generate term sheet
    TS->>DB: Fetch company and deal data
    TS->>TS: Generate document
    TS->>ObjStore: Store document
    TS->>User: Return document URL
    
    User->>TS: Start negotiation
    TS->>User: Open WebSocket connection
    User-->>TS: Send term proposals
    TS-->>User: Respond to proposals
```

### Portfolio Monitoring Flow

```mermaid
sequenceDiagram
    participant Company
    participant User
    participant PT as Portfolio Telemetry
    participant FO as Follow-On Engine
    participant DB as Database
    participant TimeSeries as Time Series DB
    
    Company->>PT: Submit metrics update
    PT->>DB: Store current metrics
    PT->>TimeSeries: Store time series data
    PT->>Company: Confirmation
    
    User->>PT: Request company dashboard
    PT->>DB: Fetch company data
    PT->>TimeSeries: Fetch historical metrics
    PT->>User: Return dashboard data
    
    PT->>PT: Scheduled health check
    PT->>FO: Analyze for follow-on opportunity
    FO->>DB: Fetch historical performance
    FO->>FO: Apply decision rules
    FO->>DB: Store recommendation
    FO->>User: Notify if follow-on opportunity
```

## Deployment Architecture

The AI.VC platform is deployed using a containerized infrastructure with Docker for development and Kubernetes for production environments.

```mermaid
flowchart TB
    subgraph "Development Environment"
        DevComp["Docker Compose"]
        DevDB[(Local PostgreSQL)]
        DevVec[(Local Qdrant)]
        DevMinio[(Local MinIO)]
    end
    
    subgraph "Production Environment"
        subgraph "Kubernetes Cluster"
            API["API Gateway"]
            CoreServices["Core Services Pods"]
            MLServices["ML Services Pods"]
            Monitoring["Monitoring Pods"]
            
            subgraph "StatefulSets"
                ProdDB[(PostgreSQL)]
                ProdVec[(Qdrant)]
                ProdRedis[(Redis)]
                ProdKafka[(Kafka)]
            end
            
            subgraph "Storage"
                ProdMinio["MinIO Operator"]
                PVC["Persistent Volume Claims"]
            end
        end
        
        CDN["Content Delivery Network"]
        Backups["Backup Storage"]
    end
    
    subgraph "CI/CD Pipeline"
        GitActions["GitHub Actions"]
        Registry["Container Registry"]
        Helm["Helm Charts"]
    end
    
    GitActions --> Registry
    Registry --> DevComp
    Registry --> Helm
    Helm --> API
    
    API --> CoreServices
    API --> MLServices
    API --> CDN
    
    CoreServices --> ProdDB
    CoreServices --> ProdVec
    CoreServices --> ProdRedis
    CoreServices --> ProdKafka
    CoreServices --> ProdMinio
    
    MLServices --> ProdDB
    MLServices --> ProdMinio
    
    Monitoring --> CoreServices
    Monitoring --> MLServices
    Monitoring --> ProdDB
    Monitoring --> ProdVec
    Monitoring --> ProdRedis
    Monitoring --> ProdKafka
    
    ProdDB --> Backups
    ProdMinio --> Backups
```

## Development Guidelines

### Code Organization

The codebase follows a monorepo structure with the polylith folder pattern:

- **/services**: Service implementations
- **/libs**: Shared libraries
- **/infra**: Infrastructure configuration
- **/docs**: Documentation
- **/scripts**: Utility scripts
- **/tests**: Tests for shared components

### Tech Stack

- **Backend**: Python 3.11 with FastAPI
- **Frontend**: TypeScript with Next.js 14
- **Data Storage**: PostgreSQL 16, Qdrant, MinIO, Redis
- **Message Broker**: Kafka
- **ML Ops**: MLflow, Scikit-learn, PyTorch
- **Observability**: Prometheus, Grafana, Jaeger
- **DevOps**: Docker, Kubernetes, GitHub Actions
- **Documentation**: Markdown, Mermaid diagrams

### API Design Principles

- RESTful API design with consistent patterns
- OpenAPI/Swagger documentation for all endpoints
- JWT-based authentication and authorization
- Standardized error responses and status codes
- Rate limiting and throttling for all public endpoints

### Testing Strategy

- Unit tests for all business logic
- Integration tests for service interactions
- E2E tests for critical user flows
- Performance testing for high-volume endpoints
- Security testing for authentication and authorization

## Conclusion

The AI.VC platform architecture is designed to provide a comprehensive investment decision support system with a focus on AI-driven analysis, compliance, and portfolio monitoring. The microservices approach allows for independent scaling and evolution of components, while the shared infrastructure ensures consistency and reliability across the platform.