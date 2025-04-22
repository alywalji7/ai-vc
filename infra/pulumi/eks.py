"""
EKS Module for AI.VC Platform Infrastructure

This module provisions an Amazon EKS (Elastic Kubernetes Service) cluster
with managed node groups for the AI.VC platform.
"""

import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
from pulumi import Config

def create_eks_cluster(name, vpc, tags):
    """
    Create an EKS cluster with a managed node group.
    
    Args:
        name: Name prefix for the EKS cluster
        vpc: Output from the VPC module
        tags: Tags to apply to all resources
        
    Returns:
        An object containing EKS cluster resources
    """
    config = Config()
    
    # Get node group configuration
    node_instance_type = config.require("eks_node_instance_type")
    node_min_size = config.require_int("eks_node_min_size")
    node_max_size = config.require_int("eks_node_max_size")
    node_desired_capacity = config.require_int("eks_node_desired_capacity")
    
    # Create the EKS cluster
    cluster = eks.Cluster(
        name,
        vpc_id=vpc["vpc_id"],
        public_subnet_ids=vpc["public_subnet_ids"],
        private_subnet_ids=vpc["private_subnet_ids"],
        instance_type=node_instance_type,
        desired_capacity=node_desired_capacity,
        min_size=node_min_size,
        max_size=node_max_size,
        create_oidc_provider=True,
        endpoint_private_access=True,
        endpoint_public_access=True,
        tags=tags,
        fargate=False,
        # Configure AWS auth to map IAM roles to Kubernetes RBAC
        skip_default_node_group=False,
        # Configure kubectl config generation
        provider_credential_opts=eks.KubeconfigOptionsArgs(
            profile_name="default"
        ),
        # Add Amazon Linux 2 EKS-optimized AMI with GPU support
        node_associate_public_ip_address=False,
    )
    
    # Add Kubernetes tags for AWS cloud controller manager
    cluster_tag = pulumi.Output.concat("kubernetes.io/cluster/", cluster.eks_cluster.name)
    for i, subnet_id in enumerate(vpc["private_subnet_ids"]):
        aws.ec2.Tag(
            f"{name}-private-subnet-tag-{i}",
            resource_id=subnet_id,
            key=cluster_tag,
            value="shared"
        )
    
    for i, subnet_id in enumerate(vpc["public_subnet_ids"]):
        aws.ec2.Tag(
            f"{name}-public-subnet-tag-{i}",
            resource_id=subnet_id,
            key=cluster_tag,
            value="shared"
        )
    
    # Return cluster outputs
    return pulumi.Output.all(
        cluster_name=cluster.eks_cluster.name,
        kubeconfig=cluster.kubeconfig,
        vpc_config=cluster.eks_cluster.vpc_config
    )