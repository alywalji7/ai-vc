"""
ElastiCache Module for AI.VC Platform Infrastructure

This module provisions an Amazon ElastiCache Redis cluster for the AI.VC platform.
"""

import pulumi
import pulumi_aws as aws
from pulumi import Config

def create_redis_cluster(name, vpc, tags):
    """
    Create an ElastiCache Redis cluster.
    
    Args:
        name: Name prefix for the Redis cluster
        vpc: Output from the VPC module
        tags: Tags to apply to all resources
        
    Returns:
        An object containing ElastiCache resources
    """
    config = Config()
    
    # Get ElastiCache configuration
    node_type = config.require("elasticache_node_type")
    num_cache_nodes = config.require_int("elasticache_num_cache_nodes")
    
    # Create a security group for ElastiCache
    redis_sg = aws.ec2.SecurityGroup(
        f"{name}-sg",
        vpc_id=vpc["vpc_id"],
        description="Allow Redis inbound traffic",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                from_port=6379,
                to_port=6379,
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
    
    # Create a subnet group for ElastiCache
    subnet_group = aws.elasticache.SubnetGroup(
        f"{name}-subnet-group",
        subnet_ids=vpc["private_subnet_ids"],
        tags={**tags, "Name": f"{name}-subnet-group"}
    )
    
    # Create a parameter group for Redis
    parameter_group = aws.elasticache.ParameterGroup(
        f"{name}-parameter-group",
        family="redis6.x",
        description=f"Parameter group for {name}",
        parameters=[
            aws.elasticache.ParameterGroupParameterArgs(
                name="maxmemory-policy",
                value="volatile-lru"
            )
        ],
        tags=tags
    )
    
    # Create a Redis cluster
    redis_cluster = aws.elasticache.Cluster(
        name,
        engine="redis",
        engine_version="6.x",
        node_type=node_type,
        num_cache_nodes=num_cache_nodes,
        parameter_group_name=parameter_group.name,
        subnet_group_name=subnet_group.name,
        security_group_ids=[redis_sg.id],
        port=6379,
        snapshot_retention_limit=7,
        snapshot_window="05:00-09:00",
        maintenance_window="sun:10:00-sun:14:00",
        apply_immediately=True,
        auto_minor_version_upgrade=True,
        tags={**tags, "Name": name}
    )
    
    # Return the Redis cluster details
    return pulumi.Output.all(
        primary_endpoint=redis_cluster.cache_nodes.apply(lambda nodes: nodes[0].address),
        port=redis_cluster.port,
        configuration_endpoint=redis_cluster.configuration_endpoint
    )