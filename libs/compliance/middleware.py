"""
Compliance middleware for FastAPI applications.

This module provides a middleware component that can be added to FastAPI
applications to enforce compliance checks on all requests.
"""

import json
import logging
from typing import Callable, Dict, Any, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .accreditation import verify_investor_accreditation
from .sanctions import check_ofac_sanctions
from .audit import hash_decision_payload

logger = logging.getLogger(__name__)

class ComplianceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for enforcing compliance checks and audit logging.
    
    This middleware intercepts all requests and applies appropriate
    compliance checks based on the endpoint being accessed.
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        exempt_paths: Optional[list] = None,
        enable_logging: bool = True
    ):
        """
        Initialize the compliance middleware.
        
        Args:
            app: The ASGI application
            exempt_paths: List of paths to exempt from compliance checks
            enable_logging: Whether to enable audit logging
        """
        super().__init__(app)
        self.exempt_paths = exempt_paths or ["/docs", "/redoc", "/openapi.json", "/health"]
        self.enable_logging = enable_logging
        logger.info("Compliance middleware initialized")
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process the request through the middleware.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or route handler
            
        Returns:
            Response from the application
        """
        # Check if path should be exempt from compliance checks
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await call_next(request)
        
        # Perform pre-processing compliance checks
        await self._pre_process_request(request)
        
        # Call the next middleware or route handler
        response = await call_next(request)
        
        # Perform post-processing compliance checks
        await self._post_process_response(request, response)
        
        return response
    
    async def _pre_process_request(self, request: Request) -> None:
        """
        Perform compliance checks before processing the request.
        
        Args:
            request: The incoming request
        """
        method = request.method
        path = request.url.path
        
        # Only process certain types of requests
        if method not in ["POST", "PUT", "PATCH"]:
            return
        
        # Check for investment-related endpoints
        if "investment" in path or "deal" in path:
            try:
                # Parse the request body
                body = await request.body()
                if body:
                    data = json.loads(body)
                    
                    # Check investor accreditation if applicable
                    if "investor_id" in data:
                        is_accredited, _ = verify_investor_accreditation(data["investor_id"])
                        if not is_accredited:
                            logger.warning(f"Non-accredited investor attempt: {data['investor_id']}")
                    
                    # Check founders against OFAC sanctions if applicable
                    if "founders" in data and isinstance(data["founders"], list):
                        for founder in data["founders"]:
                            name = founder.get("name", "")
                            country = founder.get("country", None)
                            if name:
                                is_sanctioned, _ = check_ofac_sanctions(name, country)
                                if is_sanctioned:
                                    logger.error(f"OFAC sanctions match found: {name} from {country}")
            
            except Exception as e:
                logger.error(f"Error in compliance pre-processing: {str(e)}")
    
    async def _post_process_response(self, request: Request, response: Response) -> None:
        """
        Perform compliance checks after processing the request.
        
        Args:
            request: The original request
            response: The response from the application
        """
        if not self.enable_logging:
            return
        
        method = request.method
        path = request.url.path
        
        # Only log certain types of responses for specific paths
        if method in ["POST", "PUT", "PATCH"] and any(x in path for x in [
            "investment", "deal", "decision", "due_diligence", "term_sheet"
        ]):
            try:
                # Check if response contains JSON data
                if response.headers.get("content-type") == "application/json":
                    response_body = response.body
                    if response_body:
                        data = json.loads(response_body)
                        
                        # Hash the decision payload for integrity
                        if isinstance(data, dict):
                            payload_hash = hash_decision_payload(data)
                            logger.info(f"Decision hash for {path}: {payload_hash}")
            
            except Exception as e:
                logger.error(f"Error in compliance post-processing: {str(e)}")


def log_compliance_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Log a compliance-related event.
    
    This is a utility function for logging compliance events outside
    of the middleware context.
    
    Args:
        event_type: Type of compliance event
        data: Event data
    """
    logger.info(f"Compliance event: {event_type}")
    
    # In a real implementation, this would log to a database
    # as well as the logging system
    try:
        payload_hash = hash_decision_payload(data)
        logger.info(f"Event hash: {payload_hash}")
    except Exception as e:
        logger.error(f"Error hashing compliance event: {str(e)}")