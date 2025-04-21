"""
Cost guardrails and metering package for AI.VC.

This package provides utilities for:
1. Token usage monitoring and tracking (OpenAI API)
2. GPU usage monitoring and tracking (NVIDIA DCGM)
3. Request rate limiting
4. API monitoring endpoints
"""

from .rate_limiter import (
    request_limiter,
    start_cleaner_thread,
    rate_limit,
    create_cost_guardrail_middleware,
    DEFAULT_REQUESTS_PER_MINUTE,
    RATE_LIMITING_ENABLED
)

from .openai_metering import (
    token_usage_store,
    OpenAIUsageMonitor,
    token_rate_limit,
    track_openai_usage,
    DEFAULT_USER_TOKEN_QUOTA,
    DEFAULT_ENDPOINT_TOKEN_QUOTA,
    DEFAULT_ORGANIZATION_TOKEN_QUOTA
)

try:
    from .gpu_metering import (
        gpu_usage_store,
        GPUMonitor,
        gpu_rate_limit,
        GPU_ENABLED
    )
except ImportError:
    # GPU monitoring not available
    GPU_ENABLED = False

from .monitoring_api import router as metrics_router

__all__ = [
    'request_limiter',
    'start_cleaner_thread',
    'rate_limit',
    'create_cost_guardrail_middleware',
    'DEFAULT_REQUESTS_PER_MINUTE',
    'RATE_LIMITING_ENABLED',
    'token_usage_store',
    'OpenAIUsageMonitor',
    'token_rate_limit',
    'track_openai_usage',
    'DEFAULT_USER_TOKEN_QUOTA',
    'DEFAULT_ENDPOINT_TOKEN_QUOTA',
    'DEFAULT_ORGANIZATION_TOKEN_QUOTA',
    'GPU_ENABLED',
    'metrics_router'
]