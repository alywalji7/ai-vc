"""
RDS Module for AI.VC Platform Infrastructure

This module provisions an Amazon RDS PostgreSQL instance for the AI.VC platform.
"""

import pulumi
import pulumi_aws as aws
from pulumi import Config

def create_rds_instance(name, vpc, tags):
    """
    Create an RDS PostgreSQL instance.
    
    Args:
        name: Name prefix for the RDS instance
        vpc: Output from the VPC module
        tags: Tags to apply to all resources
        
    Returns:
        An object containing RDS instance resources
    """
    config = Config()
    
    # Get RDS configuration
    db_instance_class = config.require("rds_instance_class")
    db_allocated_storage = config.require_int("rds_allocated_storage")
    db_engine_version = config.require("rds_engine_version")
    db_multi_az = config.require_bool("rds_multi_az")
    db_username = config.require("db_master_username")
    db_password = config.require_secret("db_master_password")
    db_name = config.require("db_name")
    db_port = config.require_int("db_port")
    
    # Create a security group for RDS
    rds_sg = aws.ec2.SecurityGroup(
        f"{name}-sg",
        vpc_id=vpc["vpc_id"],
        description="Allow PostgreSQL inbound traffic",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                from_port=db_port,
                to_port=db_port,
                protocol="tcp",
                cidr_blocks=["10.0.0.0/8"]  # Allow access from within the VPC
            )
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                from_port=0,
                to_port=0,
                protocol="-1",
                cidr_blocks=["0.0.0.0/0"]
            )
        ],
        tags={**tags, "Name": f"{name}-sg"}
    )
    
    # Create a subnet group for RDS
    db_subnet_group = aws.rds.SubnetGroup(
        f"{name}-subnet-group",
        subnet_ids=vpc["private_subnet_ids"],
        tags={**tags, "Name": f"{name}-subnet-group"}
    )
    
    # Create a parameter group for PostgreSQL
    db_parameter_group = aws.rds.ParameterGroup(
        f"{name}-parameter-group",
        family=f"postgres{db_engine_version}",
        description=f"Parameter group for {name}",
        parameters=[
            aws.rds.ParameterGroupParameterArgs(
                name="log_connections",
                value="1"
            ),
            aws.rds.ParameterGroupParameterArgs(
                name="log_disconnections",
                value="1"
            ),
            aws.rds.ParameterGroupParameterArgs(
                name="log_statement",
                value="ddl"
            ),
            aws.rds.ParameterGroupParameterArgs(
                name="shared_preload_libraries",
                value="pg_stat_statements"
            )
        ],
        tags=tags
    )
    
    # Create an RDS instance with production-ready backup settings
    is_production = tags.get("Environment") == "prod"
    
    # Configure more robust backup settings for production
    backup_retention_period = 7  # 7-day retention for both staging and prod
    backup_window = "03:00-05:00"  # UTC time window for backups (low traffic period)
    maintenance_window = "sun:06:00-sun:08:00"  # UTC time window for maintenance
    
    db_instance = aws.rds.Instance(
        name,
        allocated_storage=db_allocated_storage,
        storage_type="gp2",
        engine="postgres",
        engine_version=db_engine_version,
        instance_class=db_instance_class,
        username=db_username,
        password=db_password,
        db_name=db_name,
        port=db_port,
        parameter_group_name=db_parameter_group.name,
        db_subnet_group_name=db_subnet_group.name,
        vpc_security_group_ids=[rds_sg.id],
        skip_final_snapshot=False,  # Never skip final snapshot in any environment
        final_snapshot_identifier=f"{name}-final-{pulumi.Config().require('environment')}",
        multi_az=db_multi_az,
        backup_retention_period=backup_retention_period,
        backup_window=backup_window,
        maintenance_window=maintenance_window,
        deletion_protection=True,  # Always true for both environments
        storage_encrypted=True,
        auto_minor_version_upgrade=True,
        copy_tags_to_snapshot=True,  # Ensure all tags are copied to snapshots
        performance_insights_enabled=True,  # Enable performance insights
        performance_insights_retention_period=7,  # Retain performance data for 7 days
        publicly_accessible=False,
        tags={**tags, "Name": name}
    )
    
    # Return the RDS instance
    return pulumi.Output.all(
        endpoint=db_instance.endpoint,
        address=db_instance.address,
        port=db_instance.port,
        database_name=db_instance.db_name
    )