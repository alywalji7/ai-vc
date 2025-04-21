"""
GPU usage monitoring and tracking using NVIDIA DCGM.

This module provides utilities for tracking GPU usage,
implementing resource quotas, and enforcing rate limits.
"""
import os
import time
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List, Any, Union
import json
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
GPU_ENABLED = os.environ.get("GPU_ENABLED", "false").lower() == "true"
GPU_MEMORY_QUOTA = int(os.environ.get("GPU_MEMORY_QUOTA", "2048"))  # Default 2GB per user per day
GPU_UTIL_QUOTA = int(os.environ.get("GPU_UTIL_QUOTA", "7200"))  # Default 7200 = 100% for 2 hours
NVIDIA_SMI_PATH = os.environ.get("NVIDIA_SMI_PATH", "nvidia-smi")
DCGM_PATH = os.environ.get("DCGM_PATH", "/usr/bin/dcgmi")


class GPUUsageStore:
    """In-memory GPU usage storage with thread safety."""
    
    def __init__(self):
        self.user_memory_usage = {}  # user_id -> {date -> usage_MB_seconds}
        self.user_util_usage = {}    # user_id -> {date -> usage_percent_seconds}
        self.endpoint_memory_usage = {}  # endpoint -> {date -> usage_MB_seconds}
        self.endpoint_util_usage = {}    # endpoint -> {date -> usage_percent_seconds}
        self.lock = threading.RLock()
    
    def log_usage(self, memory_mb: float, utilization_pct: float, duration_sec: float, 
                 user_id: str, endpoint: str):
        """
        Log GPU usage for user and endpoint.
        
        Args:
            memory_mb: Memory usage in MB
            utilization_pct: GPU utilization percentage (0-100)
            duration_sec: Duration of usage in seconds
            user_id: User ID
            endpoint: API endpoint
        """
        today = datetime.now().strftime("%Y-%m-%d")
        memory_mb_seconds = memory_mb * duration_sec
        util_percent_seconds = utilization_pct * duration_sec
        
        with self.lock:
            # Update user memory usage
            if user_id not in self.user_memory_usage:
                self.user_memory_usage[user_id] = {}
            if today not in self.user_memory_usage[user_id]:
                self.user_memory_usage[user_id][today] = 0
            self.user_memory_usage[user_id][today] += memory_mb_seconds
            
            # Update user utilization usage
            if user_id not in self.user_util_usage:
                self.user_util_usage[user_id] = {}
            if today not in self.user_util_usage[user_id]:
                self.user_util_usage[user_id][today] = 0
            self.user_util_usage[user_id][today] += util_percent_seconds
            
            # Update endpoint memory usage
            if endpoint not in self.endpoint_memory_usage:
                self.endpoint_memory_usage[endpoint] = {}
            if today not in self.endpoint_memory_usage[endpoint]:
                self.endpoint_memory_usage[endpoint][today] = 0
            self.endpoint_memory_usage[endpoint][today] += memory_mb_seconds
            
            # Update endpoint utilization usage
            if endpoint not in self.endpoint_util_usage:
                self.endpoint_util_usage[endpoint] = {}
            if today not in self.endpoint_util_usage[endpoint]:
                self.endpoint_util_usage[endpoint][today] = 0
            self.endpoint_util_usage[endpoint][today] += util_percent_seconds
    
    def get_user_memory_usage(self, user_id: str, days: int = 1) -> float:
        """Get user GPU memory usage (MB-seconds) for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.user_memory_usage.get(user_id, {}).get(date, 0) for date in dates)
    
    def get_user_util_usage(self, user_id: str, days: int = 1) -> float:
        """Get user GPU utilization usage (%-seconds) for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.user_util_usage.get(user_id, {}).get(date, 0) for date in dates)
    
    def get_endpoint_memory_usage(self, endpoint: str, days: int = 1) -> float:
        """Get endpoint GPU memory usage (MB-seconds) for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.endpoint_memory_usage.get(endpoint, {}).get(date, 0) for date in dates)
    
    def get_endpoint_util_usage(self, endpoint: str, days: int = 1) -> float:
        """Get endpoint GPU utilization usage (%-seconds) for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.endpoint_util_usage.get(endpoint, {}).get(date, 0) for date in dates)
    
    def _get_date_range(self, days: int) -> List[str]:
        """Get date strings for the last N days."""
        today = datetime.now()
        return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]


# Create a global GPU usage store
gpu_usage_store = GPUUsageStore()


class GPUMonitor:
    """
    Monitor GPU usage using NVIDIA tools.
    """
    
    def __init__(self):
        self.gpu_available = self._check_gpu_available()
        if not self.gpu_available:
            logger.warning("No GPU detected or NVIDIA tools not available")
    
    def _check_gpu_available(self) -> bool:
        """Check if GPU is available using nvidia-smi."""
        if not GPU_ENABLED:
            return False
            
        try:
            result = subprocess.run(
                [NVIDIA_SMI_PATH, "--query-gpu=count", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True
            )
            gpu_count = int(result.stdout.strip())
            return gpu_count > 0
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
            return False
    
    def get_gpu_metrics(self) -> Dict[str, Any]:
        """
        Get current GPU metrics using nvidia-smi.
        
        Returns:
            Dictionary with GPU metrics
        """
        if not self.gpu_available:
            return {"error": "GPU not available"}
        
        try:
            # Get GPU memory usage
            memory_result = subprocess.run(
                [
                    NVIDIA_SMI_PATH, 
                    "--query-gpu=memory.used,memory.total,utilization.gpu",
                    "--format=csv,noheader,nounits"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            memory_lines = memory_result.stdout.strip().split('\n')
            gpu_metrics = []
            
            for i, line in enumerate(memory_lines):
                values = line.split(',')
                if len(values) >= 3:
                    try:
                        memory_used = float(values[0].strip())
                        memory_total = float(values[1].strip())
                        utilization = float(values[2].strip())
                        
                        gpu_metrics.append({
                            "gpu_id": i,
                            "memory_used_mb": memory_used,
                            "memory_total_mb": memory_total,
                            "memory_percent": (memory_used / memory_total) * 100 if memory_total > 0 else 0,
                            "utilization_percent": utilization
                        })
                    except (ValueError, IndexError):
                        continue
            
            return {"gpus": gpu_metrics, "timestamp": datetime.now().isoformat()}
        
        except Exception as e:
            logger.error(f"Error getting GPU metrics: {str(e)}")
            return {"error": str(e)}
    
    def get_dcgm_metrics(self) -> Dict[str, Any]:
        """
        Get detailed GPU metrics using NVIDIA DCGM.
        
        Returns:
            Dictionary with GPU metrics
        """
        if not self.gpu_available:
            return {"error": "GPU not available"}
        
        try:
            # Check if DCGM is available
            subprocess.run([DCGM_PATH, "dmon", "-l", "1"], 
                          check=True, capture_output=True, text=True)
            
            # Get metrics using DCGM
            result = subprocess.run(
                [DCGM_PATH, "dmon", "-e", "10,14,21,155,203", "-c", "1"],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) < 3:  # Header + at least one GPU line + empty line
                raise ValueError("Not enough output lines from DCGM")
            
            header = lines[0].strip().split()
            metrics = []
            
            for i in range(1, len(lines)):
                if not lines[i].strip():
                    continue
                    
                values = lines[i].strip().split()
                if len(values) < len(header):
                    continue
                
                gpu_metrics = {}
                for j, field in enumerate(header):
                    if j < len(values):
                        try:
                            gpu_metrics[field] = float(values[j])
                        except ValueError:
                            gpu_metrics[field] = values[j]
                
                metrics.append(gpu_metrics)
            
            return {"gpus": metrics, "timestamp": datetime.now().isoformat()}
        
        except Exception as e:
            logger.error(f"Error getting DCGM metrics: {str(e)}")
            return {"error": str(e)}


# GPU usage tracer for API requests
class GPUUsageTracer:
    """
    Trace GPU usage during API requests.
    """
    
    def __init__(self, user_id: str, endpoint: str):
        self.user_id = user_id
        self.endpoint = endpoint
        self.monitor = GPUMonitor()
        self.start_time = None
        self.end_time = None
        self.start_metrics = None
        self.end_metrics = None
    
    def __enter__(self):
        """Start tracing GPU usage."""
        self.start_time = time.time()
        self.start_metrics = self.monitor.get_gpu_metrics()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop tracing GPU usage and log results."""
        self.end_time = time.time()
        self.end_metrics = self.monitor.get_gpu_metrics()
        self._log_usage()
    
    def _log_usage(self):
        """Calculate and log GPU usage."""
        if "error" in self.start_metrics or "error" in self.end_metrics:
            logger.warning("Couldn't log GPU usage: metrics error")
            return
        
        duration_sec = self.end_time - self.start_time
        
        # Calculate average memory and utilization across all GPUs
        total_memory_mb = 0
        total_utilization_pct = 0
        gpu_count = 0
        
        for start_gpu, end_gpu in zip(
            self.start_metrics.get("gpus", []),
            self.end_metrics.get("gpus", [])
        ):
            if start_gpu.get("gpu_id") != end_gpu.get("gpu_id"):
                continue
            
            # Average memory usage during the request
            avg_memory_mb = (start_gpu.get("memory_used_mb", 0) + end_gpu.get("memory_used_mb", 0)) / 2
            
            # Average utilization during the request
            avg_utilization_pct = (start_gpu.get("utilization_percent", 0) + end_gpu.get("utilization_percent", 0)) / 2
            
            total_memory_mb += avg_memory_mb
            total_utilization_pct += avg_utilization_pct
            gpu_count += 1
        
        if gpu_count > 0:
            avg_memory_mb = total_memory_mb / gpu_count
            avg_utilization_pct = total_utilization_pct / gpu_count
            
            # Log the usage
            gpu_usage_store.log_usage(
                memory_mb=avg_memory_mb,
                utilization_pct=avg_utilization_pct,
                duration_sec=duration_sec,
                user_id=self.user_id,
                endpoint=self.endpoint
            )
            
            logger.info(
                f"GPU usage: memory={avg_memory_mb:.2f}MB, utilization={avg_utilization_pct:.2f}%, "
                f"duration={duration_sec:.2f}s, user={self.user_id}, endpoint={self.endpoint}"
            )


# GPU rate limiting decorator
def gpu_rate_limit(
    memory_quota: int = GPU_MEMORY_QUOTA,
    util_quota: int = GPU_UTIL_QUOTA
):
    """
    Decorator to enforce GPU usage rate limits on API endpoints.
    
    Args:
        memory_quota: Maximum GPU memory usage in MB-seconds per user per day
        util_quota: Maximum GPU utilization in %-seconds per user per day
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not GPU_ENABLED:
                return await func(*args, **kwargs)
            
            # Extract request object
            request = kwargs.get('request')
            if not request and args and hasattr(args[0], 'client'):
                request = args[0]
            
            # Extract user ID from request if available
            user_id = "anonymous"
            if request and hasattr(request, 'state') and hasattr(request.state, 'user'):
                user_id = request.state.user.id
            
            # Get endpoint path
            endpoint = request.url.path if request and hasattr(request, 'url') else "unknown"
            
            # Check if GPU quota is exceeded
            memory_usage = gpu_usage_store.get_user_memory_usage(user_id)
            util_usage = gpu_usage_store.get_user_util_usage(user_id)
            
            if memory_usage >= memory_quota:
                logger.warning(f"GPU memory quota exceeded for {user_id}: {memory_usage}/{memory_quota}")
                from fastapi import HTTPException
                raise HTTPException(status_code=429, detail="Rate limit exceeded: GPU memory quota")
            
            if util_usage >= util_quota:
                logger.warning(f"GPU utilization quota exceeded for {user_id}: {util_usage}/{util_quota}")
                from fastapi import HTTPException
                raise HTTPException(status_code=429, detail="Rate limit exceeded: GPU utilization quota")
            
            # Trace GPU usage during the request
            with GPUUsageTracer(user_id, endpoint):
                response = await func(*args, **kwargs)
            
            return response
        
        return wrapper
    
    return decorator