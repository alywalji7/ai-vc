"""
Deployments Module for AI.VC Platform Infrastructure

This module provisions Kubernetes deployments with blue/green deployment
capabilities for the AI.VC platform.
"""

import pulumi
import pulumi_aws as aws
import pulumi_kubernetes as k8s
from pulumi import Config, ResourceOptions
import json

def create_blue_green_deployment(environment, vpc, eks_cluster, tags):
    """
    Create Kubernetes deployments with blue-green capability using AWS ALB.
    
    Args:
        environment: Deployment environment (staging, prod)
        vpc: Output from the VPC module
        eks_cluster: Output from the EKS module
        tags: Tags to apply to all resources
        
    Returns:
        An object containing ALB, target groups, and listeners
    """
    config = Config()
    domain_name = config.require("domain_name")
    acm_certificate_arn = config.require("acm_certificate_arn")
    
    # Create ALB for blue/green deployment
    alb_sg = aws.ec2.SecurityGroup(
        f"aivc-{environment}-alb-sg",
        vpc_id=vpc["vpc_id"],
        description="Allow HTTPS inbound traffic",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                from_port=443,
                to_port=443,
                protocol="tcp",
                cidr_blocks=["0.0.0.0/0"]
            ),
            aws.ec2.SecurityGroupIngressArgs(
                from_port=80,
                to_port=80,
                protocol="tcp",
                cidr_blocks=["0.0.0.0/0"]
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
        tags={**tags, "Name": f"aivc-{environment}-alb-sg"}
    )
    
    # Create Application Load Balancer
    alb = aws.lb.LoadBalancer(
        f"aivc-{environment}-alb",
        internal=False,
        load_balancer_type="application",
        security_groups=[alb_sg.id],
        subnets=vpc["public_subnet_ids"],
        enable_deletion_protection=True,
        tags={**tags, "Name": f"aivc-{environment}-alb"}
    )
    
    # Create target groups - blue for frontend
    frontend_blue_tg = aws.lb.TargetGroup(
        f"aivc-{environment}-frontend-blue-tg",
        port=80,
        protocol="HTTP",
        vpc_id=vpc["vpc_id"],
        target_type="ip",
        health_check=aws.lb.TargetGroupHealthCheckArgs(
            enabled=True,
            path="/",
            port="traffic-port",
            protocol="HTTP",
            healthy_threshold=2,
            unhealthy_threshold=2,
            timeout=5,
            interval=15,
            matcher="200-399"
        ),
        tags={**tags, "Name": f"aivc-{environment}-frontend-blue-tg", "Color": "blue"}
    )
    
    # Create target groups - green for frontend
    frontend_green_tg = aws.lb.TargetGroup(
        f"aivc-{environment}-frontend-green-tg",
        port=80,
        protocol="HTTP",
        vpc_id=vpc["vpc_id"],
        target_type="ip",
        health_check=aws.lb.TargetGroupHealthCheckArgs(
            enabled=True,
            path="/",
            port="traffic-port",
            protocol="HTTP",
            healthy_threshold=2,
            unhealthy_threshold=2,
            timeout=5,
            interval=15,
            matcher="200-399"
        ),
        tags={**tags, "Name": f"aivc-{environment}-frontend-green-tg", "Color": "green"}
    )
    
    # Create target groups - blue for backend API
    api_blue_tg = aws.lb.TargetGroup(
        f"aivc-{environment}-api-blue-tg",
        port=80,
        protocol="HTTP",
        vpc_id=vpc["vpc_id"],
        target_type="ip",
        health_check=aws.lb.TargetGroupHealthCheckArgs(
            enabled=True,
            path="/health",
            port="traffic-port",
            protocol="HTTP",
            healthy_threshold=2,
            unhealthy_threshold=2,
            timeout=5,
            interval=15,
            matcher="200-399"
        ),
        tags={**tags, "Name": f"aivc-{environment}-api-blue-tg", "Color": "blue"}
    )
    
    # Create target groups - green for backend API
    api_green_tg = aws.lb.TargetGroup(
        f"aivc-{environment}-api-green-tg",
        port=80,
        protocol="HTTP",
        vpc_id=vpc["vpc_id"],
        target_type="ip",
        health_check=aws.lb.TargetGroupHealthCheckArgs(
            enabled=True,
            path="/health",
            port="traffic-port",
            protocol="HTTP",
            healthy_threshold=2,
            unhealthy_threshold=2,
            timeout=5,
            interval=15,
            matcher="200-399"
        ),
        tags={**tags, "Name": f"aivc-{environment}-api-green-tg", "Color": "green"}
    )
    
    # Create frontend HTTPS listener
    frontend_listener = aws.lb.Listener(
        f"aivc-{environment}-frontend-https-listener",
        load_balancer_arn=alb.arn,
        port=443,
        protocol="HTTPS",
        ssl_policy="ELBSecurityPolicy-TLS13-1-2-2021-06",
        certificate_arn=acm_certificate_arn,
        default_actions=[
            aws.lb.ListenerDefaultActionArgs(
                type="forward",
                target_group_arn=frontend_blue_tg.arn
            )
        ],
        tags={**tags, "Name": f"aivc-{environment}-frontend-https-listener"}
    )
    
    # Create API HTTPS listener with host-based routing
    api_listener = aws.lb.Listener(
        f"aivc-{environment}-api-https-listener",
        load_balancer_arn=alb.arn,
        port=443,
        protocol="HTTPS",
        ssl_policy="ELBSecurityPolicy-TLS13-1-2-2021-06",
        certificate_arn=acm_certificate_arn,
        default_actions=[
            aws.lb.ListenerDefaultActionArgs(
                type="fixed-response",
                fixed_response=aws.lb.ListenerDefaultActionFixedResponseArgs(
                    content_type="text/plain",
                    message_body="Not Found",
                    status_code="404"
                )
            )
        ],
        tags={**tags, "Name": f"aivc-{environment}-api-https-listener"}
    )
    
    # Create API listener rule for host-based routing
    api_rule = aws.lb.ListenerRule(
        f"aivc-{environment}-api-rule",
        listener_arn=api_listener.arn,
        priority=100,
        conditions=[
            aws.lb.ListenerRuleConditionArgs(
                host_header=aws.lb.ListenerRuleConditionHostHeaderArgs(
                    values=[f"api.{domain_name}"]
                )
            )
        ],
        actions=[
            aws.lb.ListenerRuleActionArgs(
                type="forward",
                target_group_arn=api_blue_tg.arn
            )
        ],
        tags={**tags, "Name": f"aivc-{environment}-api-rule"}
    )
    
    # Create HTTP to HTTPS redirect listener
    http_redirect_listener = aws.lb.Listener(
        f"aivc-{environment}-http-redirect",
        load_balancer_arn=alb.arn,
        port=80,
        protocol="HTTP",
        default_actions=[
            aws.lb.ListenerDefaultActionArgs(
                type="redirect",
                redirect=aws.lb.ListenerDefaultActionRedirectArgs(
                    protocol="HTTPS",
                    port="443",
                    status_code="HTTP_301"
                )
            )
        ],
        tags={**tags, "Name": f"aivc-{environment}-http-redirect"}
    )
    
    # Return the ALB and target group resources
    return pulumi.Output.all(
        alb_arn=alb.arn,
        alb_dns_name=alb.dns_name,
        frontend_blue_tg_arn=frontend_blue_tg.arn,
        frontend_green_tg_arn=frontend_green_tg.arn,
        api_blue_tg_arn=api_blue_tg.arn,
        api_green_tg_arn=api_green_tg.arn,
        frontend_listener_arn=frontend_listener.arn,
        api_listener_arn=api_listener.arn
    )