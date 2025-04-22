# Cloud Staging Infrastructure

This document describes the cloud staging infrastructure for the AI.VC platform, including the deployment pipeline and infrastructure components.

## Overview

Our staging environment is hosted on AWS and uses a variety of services to provide a complete infrastructure for testing and validating the AI.VC platform before production deployment. The environment is provisioned and managed using Infrastructure as Code (IaC) with Pulumi.

## Architecture

```mermaid
graph TD
    subgraph "AWS Cloud"
        subgraph "VPC"
            subgraph "EKS Cluster"
                subgraph "Services"
                    frontend["Frontend Service"]
                    backend["Backend Service"]
                    radar["Radar Service"]
                    similarity["Similarity API"]
                    graph["Graph Ingest"]
                    ic["IC Simulator"]
                    term["Term Sheet"]
                    telemetry["Telemetry"]
                    scheduler["Scheduler"]
                end
                subgraph "Observability"
                    prometheus["Prometheus"]
                    jaeger["Jaeger"]
                end
            end
            rds["RDS (PostgreSQL)"]
            redis["ElastiCache (Redis)"]
        end
        s3["S3 Bucket"]
        ecr["ECR Repositories"]
        acm["ACM Certificates"]
        route53["Route 53"]
        grafana["Managed Grafana"]
    end
    
    github["GitHub Actions"] --> ecr
    github --> eks
    
    alb["ALB Ingress"] --> frontend
    alb --> backend
    alb --> radar
    alb --> similarity
    alb --> graph
    alb --> ic
    alb --> term
    alb --> telemetry
    
    frontend --> backend
    backend --> rds
    backend --> redis
    
    radar --> rds
    radar --> s3
    
    similarity --> rds
    
    graph --> rds
    graph --> s3
    
    ic --> rds
    ic --> s3
    
    term --> rds
    term --> s3
    
    telemetry --> rds
    
    scheduler --> rds
    scheduler --> redis
    
    services --> prometheus
    prometheus --> grafana
```

## Components

1. **VPC**: Isolated network environment with public and private subnets across multiple availability zones
2. **EKS**: Managed Kubernetes cluster for container orchestration
3. **RDS**: Managed PostgreSQL database for persistent storage
4. **ElastiCache**: Redis for caching and real-time data
5. **S3**: Object storage for files, ML models, and analysis logs
6. **ECR**: Container registry for Docker images
7. **Managed Grafana**: Metrics visualization and dashboards
8. **ALB Ingress**: Load balancer for routing external traffic to services
9. **ACM**: SSL certificate management

## Services

The following services are deployed to the EKS cluster:

| Service | Purpose | External URL |
|---------|---------|--------------|
| Frontend | UI portal | https://staging.aivc-platform.com |
| Backend | Core API | https://api.staging.aivc-platform.com |
| Radar | Scoring service | https://radar.staging.aivc-platform.com |
| Similarity API | Vector search | https://vectors.staging.aivc-platform.com |
| Graph Ingest | Knowledge graph | N/A (internal) |
| IC Simulator | Investment analysis | https://sim.staging.aivc-platform.com |
| Term Sheet | Document generation | https://terms.staging.aivc-platform.com |
| Telemetry | Portfolio monitoring | https://telemetry.staging.aivc-platform.com |
| Scheduler | ETL coordination | N/A (internal) |

## Deployment Pipeline

The deployment pipeline is managed by GitHub Actions and consists of the following steps:

1. **Validate**: Check infrastructure changes with `pulumi preview`
2. **Build**: Build Docker images for all services
3. **Push**: Push images to ECR repositories
4. **Deploy Infrastructure**: Create or update AWS resources with Pulumi
5. **Deploy Applications**: Apply Kubernetes manifests to the EKS cluster
6. **Verify**: Wait for deployments to be ready
7. **Notify**: Send deployment status to Slack

## Required Secrets

The following secrets are required for the deployment pipeline:

- `AWS_ACCESS_KEY_ID`: AWS access key for deployment
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for deployment
- `PULUMI_ACCESS_TOKEN`: Pulumi access token
- `SLACK_WEBHOOK_URL`: Slack webhook URL for notifications
- `STAGING_DATABASE_URL`: PostgreSQL connection string
- `STAGING_QDRANT_URL`: Qdrant vector database URL
- `OPENAI_API_KEY`: OpenAI API key for NLP capabilities
- `SENDGRID_API_KEY`: SendGrid API key for email notifications

## Monitoring and Observability

The staging environment includes a comprehensive monitoring and observability stack:

- **Prometheus**: Metrics collection and alerting
- **Grafana**: Metrics visualization and dashboards
- **Jaeger**: Distributed tracing
- **ELK Stack**: Log aggregation and analysis

## Scaling

Services are deployed with resource limits and requests to ensure proper scheduling and resource allocation. The EKS cluster can be scaled both horizontally (more nodes) and vertically (larger nodes) based on demand.

## Disaster Recovery

The staging environment is backed up regularly:

- **RDS**: Automated daily snapshots with 7-day retention
- **S3**: Versioning enabled to protect against accidental deletion
- **Kubernetes**: Manifests stored in Git for quick redeployment

## Security

Security measures implemented in the staging environment:

- **Network**: VPC with private subnets, security groups, and NACLs
- **Authentication**: IAM roles and service accounts for pod identity
- **Encryption**: Data at rest encryption for RDS, ElastiCache, and S3
- **TLS**: HTTPS with ACM certificates for all external endpoints
- **Secrets**: Kubernetes secrets for sensitive information

## Maintenance

Regular maintenance tasks:

- **Updates**: Weekly patching of EKS and worker nodes
- **Cleanup**: Removal of unused resources and old container images
- **Monitoring**: Regular review of logs and metrics
- **Testing**: Automated testing of the deployment pipeline