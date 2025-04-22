"""
Grafana Module for AI.VC Platform Infrastructure

This module provisions an Amazon Managed Grafana workspace for the AI.VC platform.
"""

import pulumi
import pulumi_aws as aws
from pulumi import Config

def create_grafana_workspace(name, tags):
    """
    Create an AWS Managed Grafana workspace.
    
    Args:
        name: Name prefix for the Grafana workspace
        tags: Tags to apply to all resources
        
    Returns:
        An object containing Grafana workspace resources
    """
    config = Config()
    
    # Get Grafana configuration
    admin_password = config.require_secret("grafana_admin_password")
    
    # Create IAM role for Grafana
    grafana_role = aws.iam.Role(
        f"{name}-role",
        assume_role_policy="""
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "grafana.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        """,
        tags={**tags, "Name": f"{name}-role"}
    )
    
    # Attach policies for accessing CloudWatch, Prometheus, and S3
    cloudwatch_policy_attachment = aws.iam.RolePolicyAttachment(
        f"{name}-cloudwatch-policy",
        role=grafana_role.name,
        policy_arn="arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
    )
    
    prometheus_policy = aws.iam.Policy(
        f"{name}-prometheus-policy",
        policy="""
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "aps:QueryMetrics",
                        "aps:GetLabels",
                        "aps:GetMetricMetadata",
                        "aps:GetSeries",
                        "aps:DescribeWorkspace"
                    ],
                    "Resource": "*"
                }
            ]
        }
        """,
        tags=tags
    )
    
    prometheus_policy_attachment = aws.iam.RolePolicyAttachment(
        f"{name}-prometheus-policy-attachment",
        role=grafana_role.name,
        policy_arn=prometheus_policy.arn
    )
    
    # Create the Grafana workspace
    workspace = aws.grafana.Workspace(
        name,
        account_access_type="CURRENT_ACCOUNT",
        authentication_providers=["AWS_SSO"],
        permission_type="SERVICE_MANAGED",
        role_arn=grafana_role.arn,
        name=name,
        data_sources=["CLOUDWATCH", "PROMETHEUS", "AMAZON_OPENSEARCH_SERVICE"],
        description="AI.VC Platform Observability Dashboard",
        tags={**tags, "Name": name}
    )
    
    # Create a workspace API key for automation
    api_key = aws.grafana.WorkspaceApiKey(
        f"{name}-api-key",
        key_name="automation-key",
        key_role="ADMIN",
        seconds_to_live=31536000,  # 1 year
        workspace_id=workspace.id
    )
    
    # Create Grafana service account for automated operations
    service_account = aws.grafana.WorkspaceServiceAccount(
        f"{name}-service-account",
        name="aivc-automation",
        role="ADMIN",
        workspace_id=workspace.id
    )
    
    # Create service account token for CI/CD integration
    service_account_token = aws.grafana.WorkspaceServiceAccountToken(
        f"{name}-service-account-token",
        name="cicd-token",
        seconds_to_live=31536000,  # 1 year
        service_account_id=service_account.id,
        workspace_id=workspace.id
    )
    
    # Return the Grafana workspace and access details
    return pulumi.Output.all(
        endpoint=workspace.endpoint,
        workspace_id=workspace.id,
        grafana_version=workspace.grafana_version,
        api_key_id=api_key.id,
        service_account_id=service_account.id
    )