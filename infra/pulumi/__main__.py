"""
AI.VC Platform Infrastructure as Code using Pulumi

This is the main entrypoint for the Pulumi program that provisions
the complete AWS infrastructure for the AI.VC platform.
"""

import pulumi
from pulumi import Config, export, ResourceOptions
import pulumi_aws as aws

# Import the infrastructure modules
from vpc import create_vpc
from eks import create_eks_cluster
from rds import create_rds_instance
from elasticache import create_redis_cluster
from s3 import create_s3_bucket
from grafana import create_grafana_workspace
from deployments import create_blue_green_deployment

# Load configuration
config = Config()
environment = config.require("environment")
vpc_cidr = config.require("vpc_cidr")
availability_zones = config.require_object("availability_zones")
domain_name = config.require("domain_name")

# Check if this is a production deployment
is_production = environment == "prod"

# Infrastructure tags
tags = {
    "Project": "AI.VC",
    "Environment": environment,
    "ManagedBy": "Pulumi"
}

# Create VPC
vpc = create_vpc(
    name=f"aivc-{environment}-vpc",
    cidr_block=vpc_cidr,
    availability_zones=availability_zones,
    tags=tags
)

# Create EKS cluster
eks_cluster = create_eks_cluster(
    name=f"aivc-{environment}-eks",
    vpc=vpc,
    tags=tags
)

# Create RDS PostgreSQL instance
rds_instance = create_rds_instance(
    name=f"aivc-{environment}-postgres",
    vpc=vpc,
    tags=tags
)

# Create ElastiCache Redis cluster
redis_cluster = create_redis_cluster(
    name=f"aivc-{environment}-redis",
    vpc=vpc,
    tags=tags
)

# Create S3 bucket for MinIO
s3_bucket = create_s3_bucket(
    name=f"aivc-{environment}-storage",
    tags=tags
)

# Create AWS Managed Grafana workspace
grafana_workspace = create_grafana_workspace(
    name=f"aivc-{environment}-grafana",
    tags=tags
)

# Get SSL Certificate for domain
ssl_certificate = aws.acm.get_certificate(domain=f"*.{domain_name}", most_recent=True)

# Create blue/green deployment infrastructure if in production
blue_green_deployment = None
if is_production:
    # Set certificate ARN in config for blue/green deployment
    config.set("acm_certificate_arn", ssl_certificate.arn)
    
    # Create blue/green deployment resources
    blue_green_deployment = create_blue_green_deployment(
        environment=environment,
        vpc=vpc,
        eks_cluster=eks_cluster,
        tags=tags
    )

# Export the relevant outputs
export("vpc_id", vpc.vpc_id)
export("eks_cluster_name", eks_cluster.cluster_name)
export("eks_kubeconfig", eks_cluster.kubeconfig)
export("rds_endpoint", rds_instance.endpoint)
export("redis_endpoint", redis_cluster.primary_endpoint)
export("s3_bucket_name", s3_bucket.bucket)
export("grafana_endpoint", grafana_workspace.endpoint)

# Export blue/green deployment outputs if available
if is_production and blue_green_deployment:
    export("alb_dns_name", blue_green_deployment.alb_dns_name)
    export("frontend_blue_tg_arn", blue_green_deployment.frontend_blue_tg_arn)
    export("frontend_green_tg_arn", blue_green_deployment.frontend_green_tg_arn)
    export("api_blue_tg_arn", blue_green_deployment.api_blue_tg_arn)
    export("api_green_tg_arn", blue_green_deployment.api_green_tg_arn)
    export("frontend_listener_arn", blue_green_deployment.frontend_listener_arn)
    export("api_listener_arn", blue_green_deployment.api_listener_arn)