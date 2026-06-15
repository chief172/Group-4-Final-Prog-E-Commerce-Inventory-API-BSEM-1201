"""
Logging Middleware - Logs all incoming requests and outgoing responses
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/Response logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log incoming request
        logger.info(f"→ {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = (time.time() - start_time) * 1000
        
        # Log response
        logger.info(f"← {request.method} {request.url.path} | Status: {response.status_code} | Duration: {duration:.2f}ms")
        
        # Add timing header
        response.headers["X-Response-Time-MS"] = f"{duration:.2f}"
        
        return response