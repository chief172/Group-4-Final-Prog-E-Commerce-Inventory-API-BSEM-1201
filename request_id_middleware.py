"""
Request ID Middleware - Assigns unique ID to each request for tracing
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import logging

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Request ID middleware for request tracking"""
    
    async def dispatch(self, request: Request, call_next):
        # Get request ID from header or generate new one
        request_id = request.headers.get("X-Request-ID")
        
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Add to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response