"""
Integration tests for Kubernetes services.

This module contains tests to verify that critical Kubernetes services
are properly deployed and configured in the cluster.
"""

import os
import sys
import pytest
from kubernetes import client, config

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Skip these tests if not running in a CI environment
pytestmark = pytest.mark.skipif(
    os.environ.get('CI') is None and os.environ.get('KUBECONFIG') is None,
    reason="Kubernetes tests only run in CI environments or with KUBECONFIG set"
)

@pytest.fixture(scope="module")
def k8s_client():
    """Set up and return a Kubernetes API client.
    
    For local testing, this will use the local kubeconfig.
    For CI/CD environments, this will use in-cluster config or
    the kubeconfig from the KUBECONFIG environment variable.
    """
    try:
        # Try to load the in-cluster configuration (for when running inside a pod)
        config.load_incluster_config()
    except config.ConfigException:
        try:
            # Try to use the kubeconfig file specified by the KUBECONFIG environment variable
            kubeconfig = os.environ.get('KUBECONFIG')
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig)
            else:
                # Default to the standard kubeconfig location
                config.load_kube_config()
        except config.ConfigException as e:
            raise RuntimeError(f"Failed to load Kubernetes configuration: {e}")
    
    return client.CoreV1Api()

def test_graph_ingest_service():
    """Test that the Graph Ingest service has a load balancer endpoint."""
    try:
        k8s = get_k8s_client()
        namespace = os.environ.get("K8S_NAMESPACE", "aivc")
        service = k8s.read_namespaced_service("graph-ingest", namespace)
        
        # Assert that the service has a LoadBalancer with an ingress point
        assert service.status.load_balancer is not None, "LoadBalancer is not configured"
        assert service.status.load_balancer.ingress is not None, "No ingress points found for LoadBalancer"
        
        # Print the endpoints for debugging
        for ingress in service.status.load_balancer.ingress:
            if hasattr(ingress, "ip") and ingress.ip:
                print(f"Graph Ingest Service accessible at IP: {ingress.ip}")
            if hasattr(ingress, "hostname") and ingress.hostname:
                print(f"Graph Ingest Service accessible at hostname: {ingress.hostname}")
        
        # Verify service port
        port_found = False
        for port in service.spec.ports:
            if port.port == 8080:
                port_found = True
                break
        assert port_found, "Expected port 8080 not found in service"
        
        print("Graph Ingest Service test passed!")
    except Exception as e:
        print(f"Error in Graph Ingest Service test: {e}")
        raise

def test_frontend_service():
    """Test that the Frontend service has a load balancer endpoint."""
    try:
        k8s = get_k8s_client()
        namespace = os.environ.get("K8S_NAMESPACE", "aivc")
        service = k8s.read_namespaced_service("frontend", namespace)
        
        # Assert that the service has a LoadBalancer with an ingress point
        assert service.status.load_balancer is not None, "LoadBalancer is not configured"
        assert service.status.load_balancer.ingress is not None, "No ingress points found for LoadBalancer"
        
        # Print the endpoints for debugging
        for ingress in service.status.load_balancer.ingress:
            if hasattr(ingress, "ip") and ingress.ip:
                print(f"Frontend Service accessible at IP: {ingress.ip}")
            if hasattr(ingress, "hostname") and ingress.hostname:
                print(f"Frontend Service accessible at hostname: {ingress.hostname}")
                
        # Verify service port (Next.js usually runs on port 3000 or 5000)
        port_found = False
        for port in service.spec.ports:
            if port.port == 3000 or port.port == 5000:
                port_found = True
                break
        assert port_found, "Expected port 3000 or 5000 not found in service"
        
        print("Frontend Service test passed!")
    except Exception as e:
        print(f"Error in Frontend Service test: {e}")
        raise
        
def test_backend_service():
    """Test that the Backend service is properly configured."""
    try:
        k8s = get_k8s_client()
        namespace = os.environ.get("K8S_NAMESPACE", "aivc")
        service = k8s.read_namespaced_service("backend", namespace)
        
        # Verify the service has a defined selector that matches our deployment
        assert service.spec.selector is not None, "Service has no selector"
        assert "app" in service.spec.selector, "Service selector does not contain 'app' key"
        assert service.spec.selector["app"] == "backend", f"Unexpected app selector: {service.spec.selector['app']}"
        
        # Verify the service port configuration
        port_found = False
        for port in service.spec.ports:
            if port.port == 8000:
                port_found = True
                break
        assert port_found, "Expected port 8000 not found in service"
        
        print("Backend Service test passed!")
    except Exception as e:
        print(f"Error in Backend Service test: {e}")
        raise
        
def test_radar_service():
    """Test that the Radar service is properly configured."""
    try:
        k8s = get_k8s_client()
        namespace = os.environ.get("K8S_NAMESPACE", "aivc")
        service = k8s.read_namespaced_service("radar", namespace)
        
        # Verify the service has a defined selector
        assert service.spec.selector is not None, "Service has no selector"
        assert "app" in service.spec.selector, "Service selector does not contain 'app' key"
        
        # Verify the service port configuration
        port_found = False
        for port in service.spec.ports:
            if port.port == 8050:
                port_found = True
                break
        assert port_found, "Expected port 8050 not found in service"
        
        print("Radar Service test passed!")
    except Exception as e:
        print(f"Error in Radar Service test: {e}")
        raise

def test_similarity_api_service():
    """Test that the Similarity API service is properly configured."""
    try:
        k8s = get_k8s_client()
        namespace = os.environ.get("K8S_NAMESPACE", "aivc")
        service = k8s.read_namespaced_service("similarity-api", namespace)
        
        # Verify the service has a defined selector
        assert service.spec.selector is not None, "Service has no selector"
        assert "app" in service.spec.selector, "Service selector does not contain 'app' key"
        
        # Verify the service port configuration
        port_found = False
        for port in service.spec.ports:
            if port.port == 8090:
                port_found = True
                break
        assert port_found, "Expected port 8090 not found in service"
        
        print("Similarity API Service test passed!")
    except Exception as e:
        print(f"Error in Similarity API Service test: {e}")
        raise

def test_ic_simulator_service():
    """Test that the IC Simulator service is properly configured."""
    try:
        k8s = get_k8s_client()
        namespace = os.environ.get("K8S_NAMESPACE", "aivc")
        service = k8s.read_namespaced_service("ic-sim", namespace)
        
        # Verify the service has a defined selector
        assert service.spec.selector is not None, "Service has no selector"
        assert "app" in service.spec.selector, "Service selector does not contain 'app' key"
        
        # Verify the service port configuration
        port_found = False
        for port in service.spec.ports:
            if port.port == 8060:
                port_found = True
                break
        assert port_found, "Expected port 8060 not found in service"
        
        print("IC Simulator Service test passed!")
    except Exception as e:
        print(f"Error in IC Simulator Service test: {e}")
        raise
        
def test_service_health_check():
    """
    Test that all services have health check probes configured in their deployments.
    """
    try:
        k8s_apps = client.AppsV1Api()
        namespace = os.environ.get("K8S_NAMESPACE", "aivc")
        deployments = k8s_apps.list_namespaced_deployment(namespace)
        
        for deployment in deployments.items:
            name = deployment.metadata.name
            print(f"Checking health probes for deployment: {name}")
            
            # Check that containers have liveness and readiness probes
            containers = deployment.spec.template.spec.containers
            for container in containers:
                assert container.liveness_probe is not None, f"Deployment {name} container {container.name} has no liveness probe"
                assert container.readiness_probe is not None, f"Deployment {name} container {container.name} has no readiness probe"
        
        print("Service health check test passed!")
    except Exception as e:
        print(f"Error in service health check test: {e}")
        raise

if __name__ == "__main__":
    print("Running Kubernetes services integration tests...")
    # Run all test functions
    test_graph_ingest_service()
    test_frontend_service()
    test_backend_service()
    test_radar_service()
    test_similarity_api_service()
    test_ic_simulator_service()
    test_service_health_check()
    print("All Kubernetes services integration tests completed.")