"""
GPU usage monitoring and tracking.

This module provides utilities for tracking GPU usage,
implementing usage quotas, and enforcing rate limits.
"""
import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List, Any
import json
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if GPU monitoring is enabled and necessary packages are available
GPU_ENABLED = os.environ.get("GPU_ENABLED", "false").lower() == "true"

try:
    if GPU_ENABLED:
        # Try to import necessary packages for GPU monitoring
        import subprocess
        import numpy as np
except ImportError:
    logger.warning("GPU monitoring dependencies not available")
    GPU_ENABLED = False

# GPU usage storage
# In production, this would be replaced with a persistent store like Redis
class GPUUsageStore:
    """In-memory GPU usage storage with thread safety."""
    
    def __init__(self):
        self.user_memory_usage = {}  # user_id -> {date -> usage_count}
        self.user_util_usage = {}  # user_id -> {date -> usage_count}
        self.endpoint_memory_usage = {}  # endpoint -> {date -> usage_count}
        self.endpoint_util_usage = {}  # endpoint -> {date -> usage_count}
        self.lock = threading.RLock()
    
    def log_usage(self, memory_mb_seconds: float, util_percent_seconds: float, user_id: str, endpoint: str):
        """Log GPU usage for user and endpoint."""
        today = datetime.now().strftime("%Y-%m-%d")
        
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
        """Get user GPU memory usage for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.user_memory_usage.get(user_id, {}).get(date, 0) for date in dates)
    
    def get_user_util_usage(self, user_id: str, days: int = 1) -> float:
        """Get user GPU utilization usage for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.user_util_usage.get(user_id, {}).get(date, 0) for date in dates)
    
    def get_endpoint_memory_usage(self, endpoint: str, days: int = 1) -> float:
        """Get endpoint GPU memory usage for the last N days."""
        dates = self._get_date_range(days)
        with self.lock:
            return sum(self.endpoint_memory_usage.get(endpoint, {}).get(date, 0) for date in dates)
    
    def get_endpoint_util_usage(self, endpoint: str, days: int = 1) -> float:
        """Get endpoint GPU utilization usage for the last N days."""
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
    Monitor GPU usage through system tools.
    """
    
    def __init__(self):
        self.last_check_time = 0
        self.last_metrics = None
    
    def get_gpu_metrics(self) -> Dict[str, Any]:
        """
        Get current GPU metrics through nvidia-smi.
        
        Returns:
            Dictionary with GPU metrics
        """
        if not GPU_ENABLED:
            return {"error": "GPU monitoring not enabled"}
        
        # Cache results for a short period to avoid too many calls
        current_time = time.time()
        if self.last_metrics and current_time - self.last_check_time < 5:
            return self.last_metrics
        
        try:
            # Run nvidia-smi to get GPU information
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output
            gpus = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split(", ")
                    if len(parts) >= 4:
                        gpu_index = int(parts[0])
                        gpu_util = float(parts[1])
                        memory_used = float(parts[2])
                        memory_total = float(parts[3])
                        
                        gpus.append({
                            "index": gpu_index,
                            "utilization_percent": gpu_util,
                            "memory_used_mb": memory_used,
                            "memory_total_mb": memory_total,
                            "memory_used_percent": (memory_used / memory_total) * 100 if memory_total > 0 else 0
                        })
            
            # Calculate aggregates
            total_memory_used = sum(gpu["memory_used_mb"] for gpu in gpus)
            total_memory = sum(gpu["memory_total_mb"] for gpu in gpus)
            avg_utilization = sum(gpu["utilization_percent"] for gpu in gpus) / len(gpus) if gpus else 0
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "gpu_count": len(gpus),
                "gpus": gpus,
                "total_memory_used_mb": total_memory_used,
                "total_memory_mb": total_memory,
                "memory_used_percent": (total_memory_used / total_memory) * 100 if total_memory > 0 else 0,
                "average_utilization_percent": avg_utilization
            }
            
            # Cache the results
            self.last_metrics = metrics
            self.last_check_time = current_time
            
            return metrics
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running nvidia-smi: {str(e)}")
            return {"error": f"nvidia-smi error: {str(e)}"}
        
        except FileNotFoundError:
            logger.error("nvidia-smi not found, GPU monitoring not available")
            return {"error": "nvidia-smi not found"}
        
        except Exception as e:
            logger.error(f"Error getting GPU metrics: {str(e)}")
            return {"error": str(e)}
    
    def get_dcgm_metrics(self) -> Dict[str, Any]:
        """
        Get detailed GPU metrics through NVIDIA DCGM.
        
        Returns:
            Dictionary with detailed GPU metrics
        """
        if not GPU_ENABLED:
            return {"error": "GPU monitoring not enabled"}
        
        try:
            # Try to import DCGM
            import dcgm_fields
            import pydcgm
            
            # Code to get DCGM metrics would go here
            # This is a placeholder - actual implementation would use DCGM Python bindings
            
            return {"error": "DCGM metrics not implemented"}
        
        except ImportError:
            logger.warning("NVIDIA DCGM not available")
            return {"error": "NVIDIA DCGM not available"}


# Rate limiting decorator
def gpu_rate_limit(
    memory_quota: float = 0,  # MB-seconds
    util_quota: float = 0  # %-seconds
):
    """
    Decorator to enforce GPU usage rate limits on API endpoints.
    
    Args:
        memory_quota: Maximum MB-seconds per user per day
        util_quota: Maximum %-seconds per user per day
        
    Returns:
        Decorated function
    """
    if not GPU_ENABLED:
        # Return no-op decorator if GPU not enabled
        def decorator(func):
            return func
        return decorator
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
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
            
            # Check if any quota is exceeded
            if memory_quota > 0:
                memory_usage = gpu_usage_store.get_user_memory_usage(user_id)
                if memory_usage >= memory_quota:
                    logger.warning(f"GPU memory quota exceeded for {user_id}: {memory_usage}/{memory_quota}")
                    from fastapi import HTTPException
                    raise HTTPException(status_code=429, detail="Rate limit exceeded: GPU memory quota")
            
            if util_quota > 0:
                util_usage = gpu_usage_store.get_user_util_usage(user_id)
                if util_usage >= util_quota:
                    logger.warning(f"GPU utilization quota exceeded for {user_id}: {util_usage}/{util_quota}")
                    from fastapi import HTTPException
                    raise HTTPException(status_code=429, detail="Rate limit exceeded: GPU utilization quota")
            
            # Get initial GPU metrics
            monitor = GPUMonitor()
            start_metrics = monitor.get_gpu_metrics()
            start_time = time.time()
            
            # Call the original function
            response = await func(*args, **kwargs)
            
            # Get final GPU metrics and calculate usage
            end_time = time.time()
            end_metrics = monitor.get_gpu_metrics()
            duration = end_time - start_time
            
            try:
                # Calculate usage only if metrics are available (not error)
                if "error" not in start_metrics and "error" not in end_metrics:
                    # Simple approximation - average of start and end values * duration
                    memory_used_start = start_metrics.get("total_memory_used_mb", 0)
                    memory_used_end = end_metrics.get("total_memory_used_mb", 0)
                    avg_memory_used = (memory_used_start + memory_used_end) / 2
                    
                    util_start = start_metrics.get("average_utilization_percent", 0)
                    util_end = end_metrics.get("average_utilization_percent", 0)
                    avg_util = (util_start + util_end) / 2
                    
                    # Calculate MB-seconds and %-seconds
                    memory_mb_seconds = avg_memory_used * duration
                    util_percent_seconds = avg_util * duration
                    
                    # Log usage
                    gpu_usage_store.log_usage(memory_mb_seconds, util_percent_seconds, user_id, endpoint)
                    
                    logger.info(
                        f"GPU usage: memory={memory_mb_seconds:.2f} MB-s, "
                        f"util={util_percent_seconds:.2f} %-s, "
                        f"duration={duration:.2f}s, user={user_id}, endpoint={endpoint}"
                    )
            except Exception as e:
                logger.warning(f"Error calculating GPU usage: {str(e)}")
            
            return response
        
        return wrapper
    
    return decorator