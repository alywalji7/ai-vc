"""
S3 Module for AI.VC Platform Infrastructure

This module provisions an Amazon S3 bucket for MinIO replica in the AI.VC platform.
"""

import pulumi
import pulumi_aws as aws
from pulumi import Config

def create_s3_bucket(name, tags):
    """
    Create an S3 bucket for MinIO replica.
    
    Args:
        name: Name prefix for the S3 bucket
        tags: Tags to apply to all resources
        
    Returns:
        An object containing S3 bucket resources
    """
    config = Config()
    
    # Get S3 configuration
    bucket_name = config.require("s3_bucket_name")
    
    # Create an S3 bucket with enhanced versioning and backup
    is_production = tags.get("Environment") == "prod"
    
    # Configure lifecycle rules based on environment
    lifecycle_rules = [
        aws.s3.BucketLifecycleRuleArgs(
            enabled=True,
            id="cleanup-old-versions",
            # In production, keep non-current versions longer (90 days vs 30 in staging)
            noncurrent_version_expiration=aws.s3.BucketLifecycleRuleNoncurrentVersionExpirationArgs(
                days=90 if is_production else 30
            ),
            # Move non-current versions to cheaper storage after 14/7 days
            noncurrent_version_transitions=[
                aws.s3.BucketLifecycleRuleNoncurrentVersionTransitionArgs(
                    days=14 if is_production else 7,
                    storage_class="STANDARD_IA"
                ),
                aws.s3.BucketLifecycleRuleNoncurrentVersionTransitionArgs(
                    days=30 if is_production else 15,
                    storage_class="GLACIER"
                )
            ]
        ),
        # Create a rule to automatically create backups by copying to glacier
        aws.s3.BucketLifecycleRuleArgs(
            enabled=is_production,  # Only enable in production
            id="archive-for-disaster-recovery",
            transitions=[
                aws.s3.BucketLifecycleRuleTransitionArgs(
                    days=90,
                    storage_class="GLACIER"
                )
            ]
        )
    ]
    
    # Create an S3 bucket with comprehensive versioning setup
    bucket = aws.s3.Bucket(
        name,
        bucket=bucket_name,
        acl="private",
        versioning=aws.s3.BucketVersioningArgs(
            enabled=True,  # Always enable versioning in all environments
            # In production, use MFA delete for extra protection
            mfa_delete=is_production
        ),
        server_side_encryption_configuration=aws.s3.BucketServerSideEncryptionConfigurationArgs(
            rule=aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
                apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                    sse_algorithm="AES256"
                )
            )
        ),
        # Apply replication configuration for production environment (cross-region replication)
        replication_configuration=aws.s3.BucketReplicationConfigurationArgs(
            role=aws.iam.Role("s3-replication-role", assume_role_policy="""
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "s3.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            """).arn if is_production else None,
            rules=[
                aws.s3.BucketReplicationConfigurationRuleArgs(
                    id="replicate-all-objects",
                    status="Enabled",
                    prefix="",
                    destination=aws.s3.BucketReplicationConfigurationRuleDestinationArgs(
                        bucket=aws.s3.Bucket(
                            f"{name}-replica",
                            bucket=f"{bucket_name}-replica",
                            region="us-east-1",  # Different region for DR
                            tags={**tags, "Name": f"{name}-replica", "Type": "Replica"}
                        ).arn
                    )
                )
            ] if is_production else []
        ) if is_production else None,
        lifecycle_rules=lifecycle_rules,
        tags={**tags, "Name": name}
    )
    
    # Create an IAM user for MinIO to access the bucket
    minio_user = aws.iam.User(
        f"{name}-user",
        name=f"{name}-user",
        tags={**tags, "Name": f"{name}-user"}
    )
    
    # Create access keys for the IAM user
    minio_access_key = aws.iam.AccessKey(
        f"{name}-access-key",
        user=minio_user.name,
        pgp_key=None,  # In production, consider using a PGP key
        status="Active"
    )
    
    # Create an IAM policy for the MinIO user
    minio_policy = aws.iam.Policy(
        f"{name}-policy",
        name=f"{name}-policy",
        description=f"Policy for MinIO to access {bucket_name}",
        policy=pulumi.Output.all(bucket_arn=bucket.arn).apply(
            lambda args: f'''{{
                "Version": "2012-10-17",
                "Statement": [
                    {{
                        "Effect": "Allow",
                        "Action": [
                            "s3:ListBucket",
                            "s3:GetBucketLocation"
                        ],
                        "Resource": "{args["bucket_arn"]}"
                    }},
                    {{
                        "Effect": "Allow",
                        "Action": [
                            "s3:PutObject",
                            "s3:GetObject",
                            "s3:DeleteObject"
                        ],
                        "Resource": "{args["bucket_arn"]}/*"
                    }}
                ]
            }}'''
        ),
        tags=tags
    )
    
    # Attach the policy to the user
    policy_attachment = aws.iam.UserPolicyAttachment(
        f"{name}-policy-attachment",
        user=minio_user.name,
        policy_arn=minio_policy.arn
    )
    
    # Return the S3 bucket and IAM user details
    return pulumi.Output.all(
        bucket=bucket.bucket,
        bucket_arn=bucket.arn,
        user_name=minio_user.name,
        access_key_id=minio_access_key.id,
        access_key_secret=minio_access_key.secret
    )