"""
VPC Module for AI.VC Platform Infrastructure

This module provisions an AWS VPC with public and private subnets
across multiple availability zones, along with NAT gateways and
route tables.
"""

import pulumi
import pulumi_aws as aws

def create_vpc(name, cidr_block, availability_zones, tags):
    """
    Create a VPC with public and private subnets.
    
    Args:
        name: Name prefix for all resources
        cidr_block: CIDR block for the VPC
        availability_zones: List of AZs to deploy into
        tags: Tags to apply to all resources
        
    Returns:
        An object containing VPC resources
    """
    # Create the VPC
    vpc = aws.ec2.Vpc(
        f"{name}",
        cidr_block=cidr_block,
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags={**tags, "Name": name}
    )
    
    # Create an Internet Gateway
    igw = aws.ec2.InternetGateway(
        f"{name}-igw",
        vpc_id=vpc.id,
        tags={**tags, "Name": f"{name}-igw"}
    )
    
    # Create public and private subnets in each AZ
    public_subnets = []
    private_subnets = []
    nat_gateways = []
    
    # Calculate subnet CIDR blocks
    num_azs = len(availability_zones)
    subnet_bits = 8  # Using /24 subnets
    total_subnets = num_azs * 2  # public + private
    
    for i, az in enumerate(availability_zones):
        # Create public subnet
        public_subnet = aws.ec2.Subnet(
            f"{name}-public-{i}",
            vpc_id=vpc.id,
            cidr_block=f"10.0.{i}.0/24",
            availability_zone=az,
            map_public_ip_on_launch=True,
            tags={**tags, "Name": f"{name}-public-{i}", "kubernetes.io/role/elb": "1"}
        )
        public_subnets.append(public_subnet)
        
        # Create private subnet
        private_subnet = aws.ec2.Subnet(
            f"{name}-private-{i}",
            vpc_id=vpc.id,
            cidr_block=f"10.0.{i + 100}.0/24",
            availability_zone=az,
            tags={**tags, "Name": f"{name}-private-{i}", "kubernetes.io/role/internal-elb": "1"}
        )
        private_subnets.append(private_subnet)
        
    # Create a route table for public subnets
    public_rt = aws.ec2.RouteTable(
        f"{name}-public-rt",
        vpc_id=vpc.id,
        tags={**tags, "Name": f"{name}-public-rt"}
    )
    
    # Create a route to the internet gateway
    public_route = aws.ec2.Route(
        f"{name}-public-route",
        route_table_id=public_rt.id,
        destination_cidr_block="0.0.0.0/0",
        gateway_id=igw.id
    )
    
    # Associate public subnets with the public route table
    for i, subnet in enumerate(public_subnets):
        aws.ec2.RouteTableAssociation(
            f"{name}-public-rta-{i}",
            subnet_id=subnet.id,
            route_table_id=public_rt.id
        )
    
    # Create a NAT Gateway in each public subnet
    for i, subnet in enumerate(public_subnets):
        eip = aws.ec2.Eip(
            f"{name}-nat-eip-{i}",
            vpc=True,
            tags={**tags, "Name": f"{name}-nat-eip-{i}"}
        )
        
        nat_gateway = aws.ec2.NatGateway(
            f"{name}-nat-gw-{i}",
            allocation_id=eip.id,
            subnet_id=subnet.id,
            tags={**tags, "Name": f"{name}-nat-gw-{i}"}
        )
        nat_gateways.append(nat_gateway)
    
    # Create private route tables and routes through the NAT gateways
    for i, subnet in enumerate(private_subnets):
        # One route table per private subnet
        private_rt = aws.ec2.RouteTable(
            f"{name}-private-rt-{i}",
            vpc_id=vpc.id,
            tags={**tags, "Name": f"{name}-private-rt-{i}"}
        )
        
        # Route through the NAT gateway in the same AZ
        private_route = aws.ec2.Route(
            f"{name}-private-route-{i}",
            route_table_id=private_rt.id,
            destination_cidr_block="0.0.0.0/0",
            nat_gateway_id=nat_gateways[i].id
        )
        
        # Associate private subnet with its route table
        aws.ec2.RouteTableAssociation(
            f"{name}-private-rta-{i}",
            subnet_id=subnet.id,
            route_table_id=private_rt.id
        )
    
    # Return the VPC and its resources
    return pulumi.Output.all(
        vpc_id=vpc.id,
        public_subnet_ids=[subnet.id for subnet in public_subnets],
        private_subnet_ids=[subnet.id for subnet in private_subnets]
    )